# Testing Guide

**Companion to:** [TESTING_STANDARDS.md](./TESTING_STANDARDS.md)
**Version:** 1.0
**Last Updated:** November 6, 2025
**Status:** REFERENCE - Detailed examples and patterns
**Audience:** Developers and Coding Agents

This guide provides complete, copy-paste-ready examples for writing tests in this codebase. For rules and requirements, see [TESTING_STANDARDS.md](./TESTING_STANDARDS.md).

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Unit Tests](#unit-tests)
   - [Testing Models](#testing-models)
   - [Testing Schemas](#testing-schemas)
   - [Testing Services](#testing-services)
   - [Testing Repositories](#testing-repositories)
4. [Integration Tests](#integration-tests)
5. [API Tests](#api-tests)
6. [Event Testing](#event-testing)
7. [Cross-Domain Testing](#cross-domain-testing)
8. [Fixtures and Test Data](#fixtures-and-test-data)
9. [Mocking Patterns](#mocking-patterns)
10. [Common Patterns](#common-patterns)

---

## Quick Start

### Running Tests

```bash
# All tests
pytest

# Unit tests only (fast feedback)
pytest tests/unit -m unit

# Integration tests
pytest tests/integration -m integration

# API tests
pytest tests/api -m api

# Specific domain
pytest tests/unit/items

# With coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Stop on first failure (useful during TDD)
pytest -x

# Verbose output
pytest -v

# Run specific test
pytest tests/unit/items/test_service.py::TestCreateItem::test_create_item_with_valid_data_returns_created_item
```

### Test Discovery

```bash
# See what tests pytest will run
pytest --collect-only

# Count tests by type
pytest --collect-only -m unit | grep "tests collected"
pytest --collect-only -m integration | grep "tests collected"
pytest --collect-only -m api | grep "tests collected"
```

---

## Test Structure

All tests follow the **Arrange-Act-Assert** pattern:

```python
def test_something_does_something():
    """Test description explaining what we're testing."""
    # Arrange - Set up test data and dependencies
    mock_repo = MagicMock()
    test_data = create_test_item()

    # Act - Perform the action being tested
    result = do_something(test_data, mock_repo)

    # Assert - Verify the results
    assert result.expected_field == "expected_value"
    mock_repo.method.assert_called_once()
```

### Test Naming Convention

```python
# Format: test_{method_name}_{scenario}_{expected_result}

# Good examples:
def test_create_item_with_valid_data_returns_item()
def test_create_item_with_negative_price_raises_error()
def test_get_item_when_not_found_returns_none()
def test_update_item_when_exists_returns_updated_item()

# Bad examples:
def test_item()  # Too vague
def test_create()  # Unclear what's being tested
def test_1()  # No meaning
```

---

## Unit Tests

Unit tests are **fast, isolated tests** that mock external dependencies. They test a single function or class method in isolation.

### Testing Models

**Location:** `tests/unit/{domain}/test_models.py`
**Purpose:** Test domain logic, validation, and business rules
**Mocks:** None (pure domain objects)

```python
"""
Unit tests for items domain models.

Tests domain logic and validation rules.
"""

from datetime import datetime

import pytest

from app.items.models import Item


@pytest.mark.unit
class TestItem:
    """Test Item domain model."""

    def test_create_item_with_valid_data_creates_instance(self):
        """Test creating an item with valid data."""
        # Arrange & Act
        item = Item(
            id=1,
            name="Laptop",
            description="High-performance laptop",
            price=999.99,
            is_available=True
        )

        # Assert
        assert item.id == 1
        assert item.name == "Laptop"
        assert item.description == "High-performance laptop"
        assert item.price == 999.99
        assert item.is_available is True
        assert isinstance(item.created_at, datetime)

    def test_create_item_without_created_at_sets_default(self):
        """Test creating an item without created_at sets default."""
        # Arrange & Act
        before = datetime.utcnow()
        item = Item(id=1, name="Laptop", description="Test", price=999.99)
        after = datetime.utcnow()

        # Assert
        assert before <= item.created_at <= after

    def test_create_item_with_zero_price_accepts_zero(self):
        """Test creating an item with zero price."""
        # Arrange & Act
        item = Item(id=1, name="Free Item", description="Test", price=0.0)

        # Assert
        assert item.price == 0.0

    # Test edge cases
    def test_create_item_with_none_description_accepts_none(self):
        """Test creating an item with None description."""
        # Arrange & Act
        item = Item(id=1, name="Laptop", description=None, price=999.99)

        # Assert
        assert item.description is None

    # Test defaults
    def test_create_item_with_default_is_available_sets_true(self):
        """Test creating an item with default is_available."""
        # Arrange & Act
        item = Item(id=1, name="Laptop", description="Test", price=999.99)

        # Assert
        assert item.is_available is True


# If your model has business logic methods, test them:
@pytest.mark.unit
class TestItemBusinessLogic:
    """Test Item business logic methods."""

    def test_apply_discount_reduces_price_by_percentage(self):
        """Test applying a discount reduces price."""
        # Arrange
        item = Item(id=1, name="Laptop", description="Test", price=100.0)

        # Act
        item.apply_discount(10)  # 10% discount

        # Assert
        assert item.price == 90.0

    def test_apply_discount_with_zero_does_nothing(self):
        """Test applying zero discount doesn't change price."""
        # Arrange
        item = Item(id=1, name="Laptop", description="Test", price=100.0)

        # Act
        item.apply_discount(0)

        # Assert
        assert item.price == 100.0
```

### Testing Schemas

**Location:** `tests/unit/{domain}/test_schemas.py`
**Purpose:** Test Pydantic validation, serialization, and `from_domain_model()` methods
**Mocks:** None

```python
"""
Unit tests for items schemas.

Tests API DTO validation and serialization.
"""

import pytest
from pydantic import ValidationError

from app.items.models import Item
from app.items.schemas import ItemCreateRequest, ItemResponse, ItemUpdateRequest


@pytest.mark.unit
class TestItemCreateRequest:
    """Test ItemCreateRequest schema."""

    def test_create_request_with_valid_data_succeeds(self):
        """Test creating request with valid data."""
        # Arrange & Act
        request = ItemCreateRequest(
            name="Laptop",
            description="Test",
            price=999.99,
            is_available=True
        )

        # Assert
        assert request.name == "Laptop"
        assert request.description == "Test"
        assert request.price == 999.99
        assert request.is_available is True

    def test_create_request_without_name_raises_validation_error(self):
        """Test creating request without required name field."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                description="Test",
                price=999.99
            )

        assert "name" in str(exc_info.value)

    def test_create_request_with_negative_price_raises_validation_error(self):
        """Test creating request with negative price."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(
                name="Laptop",
                price=-10.0
            )

        assert "price" in str(exc_info.value)

    def test_create_request_with_defaults_sets_expected_values(self):
        """Test default values are set correctly."""
        # Arrange & Act
        request = ItemCreateRequest(
            name="Laptop",
            price=999.99
        )

        # Assert
        assert request.is_available is True  # default
        assert request.description is None  # default


@pytest.mark.unit
class TestItemUpdateRequest:
    """Test ItemUpdateRequest schema."""

    def test_update_request_with_partial_data_succeeds(self):
        """Test updating with only some fields."""
        # Arrange & Act
        request = ItemUpdateRequest(name="New Name")

        # Assert
        assert request.name == "New Name"
        assert request.description is None
        assert request.price is None
        assert request.is_available is None

    def test_update_request_with_all_fields_succeeds(self):
        """Test updating with all fields."""
        # Arrange & Act
        request = ItemUpdateRequest(
            name="New Name",
            description="New Description",
            price=149.99,
            is_available=False
        )

        # Assert
        assert request.name == "New Name"
        assert request.description == "New Description"
        assert request.price == 149.99
        assert request.is_available is False


@pytest.mark.unit
class TestItemResponse:
    """Test ItemResponse schema."""

    def test_from_domain_model_converts_correctly(self):
        """Test converting domain model to response DTO."""
        # Arrange
        domain_item = Item(
            id=1,
            name="Laptop",
            description="Test",
            price=999.99,
            is_available=True
        )

        # Act
        response = ItemResponse.from_domain_model(domain_item)

        # Assert
        assert response.id == 1
        assert response.name == "Laptop"
        assert response.description == "Test"
        assert response.price == 999.99
        assert response.is_available is True
        assert response.created_at == domain_item.created_at

    def test_response_excludes_sensitive_fields(self):
        """Test that sensitive fields are not exposed."""
        # Arrange
        domain_item = Item(
            id=1,
            name="Laptop",
            description="Test",
            price=999.99
        )

        # Act
        response = ItemResponse.from_domain_model(domain_item)
        response_dict = response.model_dump()

        # Assert - verify sensitive fields are NOT in response
        assert "internal_id" not in response_dict
        assert "deleted_at" not in response_dict
```

### Testing Services

**Location:** `tests/unit/{domain}/test_service.py`
**Purpose:** Test business logic with mocked repository and event bus
**Mocks:** Repository, event bus, external APIs

```python
"""
Unit tests for items service layer.

Tests business logic with mocked dependencies.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.items.events import ItemCreatedEvent, ItemDeletedEvent, ItemUpdatedEvent
from app.items.service import create_item, delete_item, get_all_items, get_item, update_item
from tests.fixtures.items import create_test_item, create_test_item_create_request, create_test_item_update_request


@pytest.mark.unit
class TestGetAllItems:
    """Test get_all_items service function."""

    @pytest.mark.asyncio
    async def test_get_all_items_returns_all_items(self):
        """Test getting all items returns repository results."""
        # Arrange
        mock_items = [
            create_test_item(id=1, name="Item 1"),
            create_test_item(id=2, name="Item 2")
        ]
        mock_repo = MagicMock()
        mock_repo.find_all = AsyncMock(return_value=mock_items)

        # Act
        result = await get_all_items(mock_repo)

        # Assert
        assert len(result) == 2
        assert result[0].name == "Item 1"
        assert result[1].name == "Item 2"
        mock_repo.find_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_items_with_empty_repository_returns_empty_list(self):
        """Test getting all items from empty repository."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.find_all = AsyncMock(return_value=[])

        # Act
        result = await get_all_items(mock_repo)

        # Assert
        assert result == []
        mock_repo.find_all.assert_called_once()


@pytest.mark.unit
class TestGetItem:
    """Test get_item service function."""

    @pytest.mark.asyncio
    async def test_get_item_when_exists_returns_item(self):
        """Test getting an item that exists."""
        # Arrange
        mock_item = create_test_item(id=1, name="Test Item")
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=mock_item)

        # Act
        result = await get_item(1, mock_repo)

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.name == "Test Item"
        mock_repo.find_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_item_when_not_found_returns_none(self):
        """Test getting an item that doesn't exist."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        # Act
        result = await get_item(999, mock_repo)

        # Assert
        assert result is None
        mock_repo.find_by_id.assert_called_once_with(999)


@pytest.mark.unit
class TestCreateItem:
    """Test create_item service function."""

    @pytest.mark.asyncio
    async def test_create_item_with_valid_data_returns_created_item(self):
        """Test creating an item with valid data."""
        # Arrange
        request = create_test_item_create_request(name="New Item", price=199.99)
        created_item = create_test_item(id=1, name="New Item", price=199.99)
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_item)

        with patch("app.items.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await create_item(request, mock_repo)

            # Assert
            assert result.id == 1
            assert result.name == "New Item"
            assert result.price == 199.99
            mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_item_publishes_item_created_event(self):
        """Test creating an item publishes ItemCreatedEvent."""
        # Arrange
        request = create_test_item_create_request(name="New Item", price=199.99)
        created_item = create_test_item(id=1, name="New Item", price=199.99)
        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_item)

        with patch("app.items.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await create_item(request, mock_repo)

            # Assert - MANDATORY event testing
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, ItemCreatedEvent)
            assert published_event.item_id == 1
            assert published_event.name == "New Item"
            assert published_event.price == 199.99
            assert published_event.event_type == "item.created"


@pytest.mark.unit
class TestUpdateItem:
    """Test update_item service function."""

    @pytest.mark.asyncio
    async def test_update_item_when_exists_returns_updated_item(self):
        """Test updating an existing item."""
        # Arrange
        existing_item = create_test_item(id=1, name="Old Name", price=99.99)
        updated_item = create_test_item(id=1, name="New Name", price=99.99)
        request = create_test_item_update_request(name="New Name")
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_item)
        mock_repo.update = AsyncMock(return_value=updated_item)

        with patch("app.items.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_item(1, request, mock_repo)

            # Assert
            assert result is not None
            assert result.name == "New Name"
            mock_repo.find_by_id.assert_called_once_with(1)
            mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_item_when_not_found_returns_none(self):
        """Test updating a non-existent item."""
        # Arrange
        request = create_test_item_update_request(name="New Name")
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        with patch("app.items.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_item(999, request, mock_repo)

            # Assert
            assert result is None
            mock_repo.find_by_id.assert_called_once_with(999)
            mock_bus.publish.assert_not_called()  # No event if not found

    @pytest.mark.asyncio
    async def test_update_item_publishes_item_updated_event(self):
        """Test updating an item publishes ItemUpdatedEvent."""
        # Arrange
        existing_item = create_test_item(id=1, name="Old Name")
        updated_item = create_test_item(id=1, name="New Name")
        request = create_test_item_update_request(name="New Name")
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_item)
        mock_repo.update = AsyncMock(return_value=updated_item)

        with patch("app.items.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await update_item(1, request, mock_repo)

            # Assert - MANDATORY event testing
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, ItemUpdatedEvent)
            assert published_event.item_id == 1
            assert published_event.event_type == "item.updated"


@pytest.mark.unit
class TestDeleteItem:
    """Test delete_item service function."""

    @pytest.mark.asyncio
    async def test_delete_item_when_exists_returns_true(self):
        """Test deleting an existing item."""
        # Arrange
        existing_item = create_test_item(id=1)
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_item)
        mock_repo.delete = AsyncMock(return_value=True)

        with patch("app.items.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await delete_item(1, mock_repo)

            # Assert
            assert result is True
            mock_repo.find_by_id.assert_called_once_with(1)
            mock_repo.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_item_when_not_found_returns_false(self):
        """Test deleting a non-existent item."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        with patch("app.items.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await delete_item(999, mock_repo)

            # Assert
            assert result is False
            mock_repo.find_by_id.assert_called_once_with(999)
            mock_bus.publish.assert_not_called()  # No event if not found

    @pytest.mark.asyncio
    async def test_delete_item_publishes_item_deleted_event(self):
        """Test deleting an item publishes ItemDeletedEvent."""
        # Arrange
        existing_item = create_test_item(id=1)
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_item)
        mock_repo.delete = AsyncMock(return_value=True)

        with patch("app.items.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await delete_item(1, mock_repo)

            # Assert - MANDATORY event testing
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, ItemDeletedEvent)
            assert published_event.item_id == 1
            assert published_event.event_type == "item.deleted"
```

### Testing Repositories

**Location:** `tests/unit/{domain}/test_repository.py`
**Purpose:** Test CRUD operations and model conversions with test database
**Mocks:** Uses real test database (in-memory SQLite)

```python
"""
Unit tests for items repository layer.

Tests data access and model conversions with database.
"""

from datetime import datetime

import pytest

from app.items.repository import ItemRepository
from tests.fixtures.items import create_test_item


@pytest.mark.unit
class TestItemRepositoryFindAll:
    """Test ItemRepository.find_all method."""

    @pytest.mark.asyncio
    async def test_find_all_with_items_returns_all_items(self, test_db_session):
        """Test finding all items when items exist."""
        # Arrange
        repo = ItemRepository(test_db_session)
        item1 = create_test_item(id=None, name="Item 1")
        item2 = create_test_item(id=None, name="Item 2")
        await repo.create(item1)
        await repo.create(item2)
        await test_db_session.commit()

        # Act
        result = await repo.find_all()

        # Assert
        assert len(result) == 2
        assert result[0].name == "Item 1"
        assert result[1].name == "Item 2"

    @pytest.mark.asyncio
    async def test_find_all_with_empty_storage_returns_empty_list(self, test_db_session):
        """Test finding all items when storage is empty."""
        # Arrange
        repo = ItemRepository(test_db_session)

        # Act
        result = await repo.find_all()

        # Assert
        assert result == []


@pytest.mark.unit
class TestItemRepositoryFindById:
    """Test ItemRepository.find_by_id method."""

    @pytest.mark.asyncio
    async def test_find_by_id_when_exists_returns_item(self, test_db_session):
        """Test finding an item by ID when it exists."""
        # Arrange
        repo = ItemRepository(test_db_session)
        item = create_test_item(id=None, name="Test Item")
        created = await repo.create(item)
        await test_db_session.commit()

        # Act
        result = await repo.find_by_id(created.id)

        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.name == "Test Item"

    @pytest.mark.asyncio
    async def test_find_by_id_when_not_exists_returns_none(self, test_db_session):
        """Test finding an item by ID when it doesn't exist."""
        # Arrange
        repo = ItemRepository(test_db_session)

        # Act
        result = await repo.find_by_id(999)

        # Assert
        assert result is None


@pytest.mark.unit
class TestItemRepositoryCreate:
    """Test ItemRepository.create method."""

    @pytest.mark.asyncio
    async def test_create_item_assigns_id_and_returns_item(self, test_db_session):
        """Test creating an item assigns ID and returns domain model."""
        # Arrange
        repo = ItemRepository(test_db_session)
        item = create_test_item(id=None, name="New Item", price=99.99)

        # Act
        result = await repo.create(item)
        await test_db_session.commit()

        # Assert
        assert result.id is not None
        assert result.id == 1
        assert result.name == "New Item"
        assert result.price == 99.99

    @pytest.mark.asyncio
    async def test_create_multiple_items_increments_id(self, test_db_session):
        """Test creating multiple items increments ID counter."""
        # Arrange
        repo = ItemRepository(test_db_session)
        item1 = create_test_item(id=None, name="Item 1")
        item2 = create_test_item(id=None, name="Item 2")

        # Act
        result1 = await repo.create(item1)
        await test_db_session.commit()
        result2 = await repo.create(item2)
        await test_db_session.commit()

        # Assert
        assert result1.id == 1
        assert result2.id == 2


@pytest.mark.unit
class TestItemRepositoryUpdate:
    """Test ItemRepository.update method."""

    @pytest.mark.asyncio
    async def test_update_item_when_exists_returns_updated_item(self, test_db_session):
        """Test updating an existing item."""
        # Arrange
        repo = ItemRepository(test_db_session)
        item = create_test_item(id=None, name="Old Name", price=99.99)
        created = await repo.create(item)
        await test_db_session.commit()

        # Modify the item
        created.name = "New Name"
        created.price = 149.99

        # Act
        result = await repo.update(created.id, created)
        await test_db_session.commit()

        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.name == "New Name"
        assert result.price == 149.99

    @pytest.mark.asyncio
    async def test_update_item_when_not_exists_returns_none(self, test_db_session):
        """Test updating a non-existent item."""
        # Arrange
        repo = ItemRepository(test_db_session)
        item = create_test_item(id=999, name="Test")

        # Act
        result = await repo.update(999, item)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_item_preserves_created_at(self, test_db_session):
        """Test updating an item preserves created_at timestamp."""
        # Arrange
        repo = ItemRepository(test_db_session)
        original_date = datetime(2025, 1, 1, 12, 0, 0)
        item = create_test_item(id=None, name="Test", created_at=original_date)
        created = await repo.create(item)
        await test_db_session.commit()

        # Modify the item
        created.name = "Updated"

        # Act
        result = await repo.update(created.id, created)
        await test_db_session.commit()

        # Assert
        assert result.created_at == original_date


@pytest.mark.unit
class TestItemRepositoryDelete:
    """Test ItemRepository.delete method."""

    @pytest.mark.asyncio
    async def test_delete_item_when_exists_returns_true(self, test_db_session):
        """Test deleting an existing item."""
        # Arrange
        repo = ItemRepository(test_db_session)
        item = create_test_item(id=None, name="Test Item")
        created = await repo.create(item)
        await test_db_session.commit()

        # Act
        result = await repo.delete(created.id)
        await test_db_session.commit()

        # Assert
        assert result is True
        # Verify item is actually deleted
        found = await repo.find_by_id(created.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_delete_item_when_not_exists_returns_false(self, test_db_session):
        """Test deleting a non-existent item."""
        # Arrange
        repo = ItemRepository(test_db_session)

        # Act
        result = await repo.delete(999)

        # Assert
        assert result is False
```

---

## Integration Tests

**Location:** `tests/integration/{domain}/test_service_integration.py`
**Purpose:** Test service + repository working together with real database
**Mocks:** Only external APIs (database is real)

```python
"""
Integration tests for items service with real repository.

Tests service + repository integration without mocks.
"""

from unittest.mock import patch

import pytest

from app.items.events import ItemCreatedEvent
from app.items.repository import ItemRepository
from app.items.service import create_item, delete_item, get_all_items, get_item, update_item
from app.shared.events import EventBus
from tests.fixtures.items import create_test_item_create_request, create_test_item_update_request


@pytest.mark.integration
class TestItemServiceIntegration:
    """Test items service with real repository."""

    @pytest.mark.asyncio
    async def test_create_and_get_item_integration(self, test_db_session):
        """Test creating and retrieving an item end-to-end."""
        # Arrange
        request = create_test_item_create_request(
            name="Integration Test Item",
            price=299.99
        )
        repository = ItemRepository(test_db_session)

        with patch("app.items.service.event_bus", EventBus()):
            # Act - Create
            created_item = await create_item(request, repository=repository)
            await test_db_session.commit()

            # Act - Get
            retrieved_item = await get_item(created_item.id, repository=repository)
            await test_db_session.commit()

            # Assert
            assert retrieved_item is not None
            assert retrieved_item.id == created_item.id
            assert retrieved_item.name == "Integration Test Item"
            assert retrieved_item.price == 299.99

    @pytest.mark.asyncio
    async def test_create_update_get_item_integration(self, test_db_session):
        """Test creating, updating, and retrieving an item."""
        # Arrange
        create_request = create_test_item_create_request(
            name="Original Name",
            price=99.99
        )
        update_request = create_test_item_update_request(
            name="Updated Name",
            price=149.99
        )
        repository = ItemRepository(test_db_session)

        with patch("app.items.service.event_bus", EventBus()):
            # Act - Create
            created_item = await create_item(create_request, repository=repository)
            await test_db_session.commit()

            # Act - Update
            await update_item(created_item.id, update_request, repository=repository)
            await test_db_session.commit()

            # Act - Get
            retrieved_item = await get_item(created_item.id, repository=repository)
            await test_db_session.commit()

            # Assert
            assert retrieved_item is not None
            assert retrieved_item.name == "Updated Name"
            assert retrieved_item.price == 149.99

    @pytest.mark.asyncio
    async def test_create_delete_get_item_integration(self, test_db_session):
        """Test creating, deleting, and attempting to retrieve an item."""
        # Arrange
        request = create_test_item_create_request(name="To Delete", price=99.99)
        repository = ItemRepository(test_db_session)

        with patch("app.items.service.event_bus", EventBus()):
            # Act - Create
            created_item = await create_item(request, repository=repository)
            await test_db_session.commit()

            # Act - Delete
            deleted = await delete_item(created_item.id, repository=repository)
            await test_db_session.commit()

            # Act - Get
            retrieved_item = await get_item(created_item.id, repository=repository)
            await test_db_session.commit()

            # Assert
            assert deleted is True
            assert retrieved_item is None

    @pytest.mark.asyncio
    async def test_create_multiple_and_get_all_integration(self, test_db_session):
        """Test creating multiple items and retrieving all."""
        # Arrange
        request1 = create_test_item_create_request(name="Item 1", price=99.99)
        request2 = create_test_item_create_request(name="Item 2", price=149.99)
        repository = ItemRepository(test_db_session)

        with patch("app.items.service.event_bus", EventBus()):
            # Act - Create multiple
            await create_item(request1, repository=repository)
            await test_db_session.commit()
            await create_item(request2, repository=repository)
            await test_db_session.commit()

            # Act - Get all
            all_items = await get_all_items(repository=repository)
            await test_db_session.commit()

            # Assert
            assert len(all_items) == 2
            assert any(item.name == "Item 1" for item in all_items)
            assert any(item.name == "Item 2" for item in all_items)

    @pytest.mark.asyncio
    async def test_item_created_event_published_integration(self, test_db_session):
        """Test that ItemCreatedEvent is published when creating item."""
        # Arrange
        request = create_test_item_create_request(name="Event Test", price=99.99)
        repository = ItemRepository(test_db_session)
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("item.created", capture_event)

        with patch("app.items.service.event_bus", event_bus):
            # Act
            created_item = await create_item(request, repository=repository)
            await test_db_session.commit()

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], ItemCreatedEvent)
            assert published_events[0].item_id == created_item.id
            assert published_events[0].name == "Event Test"
```

---

## API Tests

**Location:** `tests/api/test_{domain}_api.py`
**Purpose:** Test full HTTP stack with TestClient
**Mocks:** Only external APIs (HTTP stack and database are real)

```python
"""
API tests for items endpoints.

Tests full HTTP stack with TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from app.items.repository import ItemRepository
from app.main import app
from app.shared.dependencies import get_item_repository


@pytest.fixture
def client(test_db_session):
    """Create a test client with test database session."""

    def override_get_item_repository():
        return ItemRepository(test_db_session)

    app.dependency_overrides[get_item_repository] = override_get_item_repository
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.api
class TestGetItemsEndpoint:
    """Test GET /items endpoint."""

    def test_get_items_when_empty_returns_empty_list(self, client):
        """Test getting items when none exist."""
        # Act
        response = client.get("/items")

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_get_items_returns_all_items(self, client):
        """Test getting all items."""
        # Arrange - Create items
        client.post("/items", json={"name": "Item 1", "price": 99.99})
        client.post("/items", json={"name": "Item 2", "price": 149.99})

        # Act
        response = client.get("/items")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(item["name"] == "Item 1" for item in data)
        assert any(item["name"] == "Item 2" for item in data)


@pytest.mark.api
class TestGetItemByIdEndpoint:
    """Test GET /items/{item_id} endpoint."""

    def test_get_item_when_exists_returns_item(self, client):
        """Test getting an existing item."""
        # Arrange
        create_response = client.post(
            "/items",
            json={"name": "Test Item", "price": 99.99}
        )
        item_id = create_response.json()["id"]

        # Act
        response = client.get(f"/items/{item_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == "Test Item"
        assert data["price"] == 99.99

    def test_get_item_when_not_exists_returns_404(self, client):
        """Test getting a non-existent item."""
        # Act
        response = client.get("/items/999")

        # Assert
        assert response.status_code == 404
        assert "detail" in response.json()


@pytest.mark.api
class TestCreateItemEndpoint:
    """Test POST /items endpoint."""

    def test_create_item_with_valid_data_returns_201(self, client):
        """Test creating an item with valid data."""
        # Arrange
        request_data = {
            "name": "New Laptop",
            "description": "High-performance laptop",
            "price": 999.99,
            "is_available": True
        }

        # Act
        response = client.post("/items", json=request_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Laptop"
        assert data["price"] == 999.99
        assert "id" in data
        assert "created_at" in data

    def test_create_item_without_name_returns_422(self, client):
        """Test creating an item without required name field."""
        # Arrange
        request_data = {
            "price": 999.99
        }

        # Act
        response = client.post("/items", json=request_data)

        # Assert
        assert response.status_code == 422

    def test_create_item_with_negative_price_returns_422(self, client):
        """Test creating an item with negative price."""
        # Arrange
        request_data = {
            "name": "Test",
            "price": -10.0
        }

        # Act
        response = client.post("/items", json=request_data)

        # Assert
        assert response.status_code == 422


@pytest.mark.api
class TestUpdateItemEndpoint:
    """Test PUT /items/{item_id} endpoint."""

    def test_update_item_when_exists_returns_200(self, client):
        """Test updating an existing item."""
        # Arrange - Create item
        create_response = client.post(
            "/items",
            json={"name": "Original", "price": 99.99}
        )
        item_id = create_response.json()["id"]

        # Act
        response = client.put(
            f"/items/{item_id}",
            json={"name": "Updated", "price": 149.99}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["price"] == 149.99

    def test_update_item_with_partial_data_updates_only_provided_fields(self, client):
        """Test partial update only changes specified fields."""
        # Arrange
        create_response = client.post(
            "/items",
            json={"name": "Original", "price": 99.99}
        )
        item_id = create_response.json()["id"]

        # Act - Only update name
        response = client.put(
            f"/items/{item_id}",
            json={"name": "Updated Name"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["price"] == 99.99  # Unchanged

    def test_update_item_when_not_exists_returns_404(self, client):
        """Test updating a non-existent item."""
        # Act
        response = client.put(
            "/items/999",
            json={"name": "Updated"}
        )

        # Assert
        assert response.status_code == 404


@pytest.mark.api
class TestDeleteItemEndpoint:
    """Test DELETE /items/{item_id} endpoint."""

    def test_delete_item_when_exists_returns_204(self, client):
        """Test deleting an existing item."""
        # Arrange
        create_response = client.post(
            "/items",
            json={"name": "To Delete", "price": 99.99}
        )
        item_id = create_response.json()["id"]

        # Act
        response = client.delete(f"/items/{item_id}")

        # Assert
        assert response.status_code == 204

        # Verify item is gone
        get_response = client.get(f"/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_item_when_not_exists_returns_404(self, client):
        """Test deleting a non-existent item."""
        # Act
        response = client.delete("/items/999")

        # Assert
        assert response.status_code == 404


@pytest.mark.api
class TestItemFlows:
    """Test complete user journeys."""

    def test_complete_crud_flow(self, client):
        """Test complete create-read-update-delete flow."""
        # Create
        create_response = client.post(
            "/items",
            json={"name": "Laptop", "price": 999.99}
        )
        assert create_response.status_code == 201
        item_id = create_response.json()["id"]

        # Read
        get_response = client.get(f"/items/{item_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Laptop"

        # Update
        update_response = client.put(
            f"/items/{item_id}",
            json={"name": "Gaming Laptop", "price": 1299.99}
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Gaming Laptop"

        # Delete
        delete_response = client.delete(f"/items/{item_id}")
        assert delete_response.status_code == 204

        # Verify deleted
        final_get = client.get(f"/items/{item_id}")
        assert final_get.status_code == 404
```

---

## Event Testing

**MANDATORY:** All business actions that publish events MUST have tests verifying event publication.

### Testing Event Publication (Unit Test)

```python
@pytest.mark.asyncio
async def test_create_item_publishes_item_created_event(self):
    """Test creating an item publishes ItemCreatedEvent."""
    # Arrange
    request = create_test_item_create_request(name="New Item", price=199.99)
    created_item = create_test_item(id=1, name="New Item", price=199.99)
    mock_repo = MagicMock()
    mock_repo.create = AsyncMock(return_value=created_item)

    with patch("app.items.service.event_bus") as mock_bus:
        mock_bus.publish = AsyncMock()

        # Act
        await create_item(request, mock_repo)

        # Assert - Verify event was published
        mock_bus.publish.assert_called_once()

        # Assert - Verify event type
        published_event = mock_bus.publish.call_args[0][0]
        assert isinstance(published_event, ItemCreatedEvent)

        # Assert - Verify event data
        assert published_event.item_id == 1
        assert published_event.name == "New Item"
        assert published_event.price == 199.99
        assert published_event.event_type == "item.created"
```

### Testing Event Handling (Integration Test)

```python
@pytest.mark.asyncio
async def test_item_created_event_triggers_analytics(self, test_db_session):
    """Test that ItemCreatedEvent triggers analytics handler."""
    # Arrange
    request = create_test_item_create_request(name="Event Test", price=99.99)
    repository = ItemRepository(test_db_session)
    event_bus = EventBus()
    analytics_calls = []

    async def analytics_handler(event):
        analytics_calls.append(event)

    event_bus.subscribe("item.created", analytics_handler)

    with patch("app.items.service.event_bus", event_bus):
        # Act
        created_item = await create_item(request, repository=repository)
        await test_db_session.commit()

        # Assert
        assert len(analytics_calls) == 1
        assert analytics_calls[0].item_id == created_item.id
```

### Testing Event Not Published on Failure

```python
@pytest.mark.asyncio
async def test_update_item_when_not_found_does_not_publish_event(self):
    """Test updating non-existent item doesn't publish event."""
    # Arrange
    request = create_test_item_update_request(name="New Name")
    mock_repo = MagicMock()
    mock_repo.find_by_id = AsyncMock(return_value=None)

    with patch("app.items.service.event_bus") as mock_bus:
        mock_bus.publish = AsyncMock()

        # Act
        result = await update_item(999, request, mock_repo)

        # Assert
        assert result is None
        mock_bus.publish.assert_not_called()  # No event on failure
```

---

## Cross-Domain Testing

**MANDATORY:** All cross-domain interactions must use service APIs and have integration tests.

### Testing Cross-Domain Service Calls

```python
"""
Integration tests for cross-domain interactions.
"""

from unittest.mock import patch

import pytest

from app.items import service as item_service
from app.users import service as user_service
from app.items.repository import ItemRepository
from app.users.repository import UserRepository
from app.shared.events import EventBus
from tests.fixtures.items import create_test_item_create_request
from tests.fixtures.users import create_test_user_create_request


@pytest.mark.integration
class TestCrossDomainInteractions:
    """Test interactions between domains."""

    @pytest.mark.asyncio
    async def test_user_can_create_item(self, test_db_session):
        """Test user creating an item (cross-domain operation)."""
        # Arrange
        user_repo = UserRepository(test_db_session)
        item_repo = ItemRepository(test_db_session)

        with patch("app.users.service.event_bus", EventBus()):
            with patch("app.items.service.event_bus", EventBus()):
                # Create user
                user_request = create_test_user_create_request(
                    username="testuser",
                    email="test@example.com"
                )
                user = await user_service.create_user(user_request, repository=user_repo)
                await test_db_session.commit()

                # User creates item
                item_request = create_test_item_create_request(
                    name="User's Item",
                    price=99.99
                )
                item = await item_service.create_item(item_request, repository=item_repo)
                await test_db_session.commit()

                # Assert
                assert user is not None
                assert item is not None
                # Verify we can retrieve both
                retrieved_user = await user_service.get_user(user.id, repository=user_repo)
                retrieved_item = await item_service.get_item(item.id, repository=item_repo)
                assert retrieved_user is not None
                assert retrieved_item is not None
```

### ❌ Wrong Way (Direct Repository Access)

```python
# ❌ WRONG - Don't do this!
from app.items.repository import item_repository
from app.items.models import Item

# Direct access to another domain's internals
item = await item_repository.find_by_id(item_id)
```

### ✅ Right Way (Through Service Port)

```python
# ✅ CORRECT - Use service layer
from app.items import service as item_service

# Call through public service API
item = await item_service.get_item(item_id, repository=item_repo)
```

---

## Fixtures and Test Data

**Location:** `tests/fixtures/{domain}.py`

### Creating Test Data Factories

```python
"""
Test data fixtures for items domain.
"""

from datetime import datetime

from app.items.models import Item
from app.items.schemas import ItemCreateRequest, ItemUpdateRequest


def create_test_item(
    id: int = 1,
    name: str = "Test Item",
    description: str = "Test description",
    price: float = 99.99,
    is_available: bool = True,
    created_at: datetime = None,
) -> Item:
    """Create a test item domain model."""
    return Item(
        id=id,
        name=name,
        description=description,
        price=price,
        is_available=is_available,
        created_at=created_at or datetime(2025, 1, 1, 12, 0, 0),
    )


def create_test_item_create_request(
    name: str = "New Item",
    description: str = "New description",
    price: float = 149.99,
    is_available: bool = True,
) -> ItemCreateRequest:
    """Create a test item create request."""
    return ItemCreateRequest(
        name=name,
        description=description,
        price=price,
        is_available=is_available
    )


def create_test_item_update_request(
    name: str = None,
    description: str = None,
    price: float = None,
    is_available: bool = None,
) -> ItemUpdateRequest:
    """Create a test item update request."""
    return ItemUpdateRequest(
        name=name,
        description=description,
        price=price,
        is_available=is_available
    )


# Builder pattern for complex objects
class ItemBuilder:
    """Builder for creating test items with fluent interface."""

    def __init__(self):
        self.id = 1
        self.name = "Test Item"
        self.description = "Test description"
        self.price = 99.99
        self.is_available = True
        self.created_at = datetime(2025, 1, 1, 12, 0, 0)

    def with_id(self, id: int):
        self.id = id
        return self

    def with_name(self, name: str):
        self.name = name
        return self

    def with_price(self, price: float):
        self.price = price
        return self

    def unavailable(self):
        self.is_available = False
        return self

    def build(self) -> Item:
        return Item(
            id=self.id,
            name=self.name,
            description=self.description,
            price=self.price,
            is_available=self.is_available,
            created_at=self.created_at,
        )


# Usage:
# item = ItemBuilder().with_name("Laptop").with_price(999.99).unavailable().build()
```

---

## Mocking Patterns

### Mocking Async Functions

```python
from unittest.mock import AsyncMock, MagicMock

# Create mock repository
mock_repo = MagicMock()
mock_repo.find_by_id = AsyncMock(return_value=test_item)
mock_repo.create = AsyncMock(return_value=created_item)

# Use it
result = await mock_repo.find_by_id(1)
```

### Mocking Event Bus

```python
from unittest.mock import patch, AsyncMock

with patch("app.items.service.event_bus") as mock_bus:
    mock_bus.publish = AsyncMock()

    # Your test code
    await create_item(request, mock_repo)

    # Verify event was published
    mock_bus.publish.assert_called_once()
    published_event = mock_bus.publish.call_args[0][0]
```

### Mocking External APIs

```python
from unittest.mock import patch, AsyncMock

@patch("app.external.api_client.fetch_data")
async def test_with_external_api(mock_fetch):
    # Arrange
    mock_fetch.return_value = {"data": "mocked"}

    # Act
    result = await my_function()

    # Assert
    assert result == expected
    mock_fetch.assert_called_once()
```

---

## Common Patterns

### Testing Pagination

```python
def test_get_items_with_pagination(self, client):
    """Test paginated results."""
    # Arrange - Create 25 items
    for i in range(25):
        client.post("/items", json={"name": f"Item {i}", "price": 99.99})

    # Act - Get first page
    response = client.get("/items?page=1&page_size=10")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 25
    assert data["page"] == 1
```

### Testing Search/Filtering

```python
@pytest.mark.asyncio
async def test_search_items_with_multiple_filters(self, test_db_session):
    """Test searching with multiple filters."""
    # Arrange
    repo = ItemRepository(test_db_session)
    await repo.create(create_test_item(id=None, name="Laptop Pro", price=150.0, is_available=True))
    await repo.create(create_test_item(id=None, name="Laptop Air", price=250.0, is_available=True))
    await repo.create(create_test_item(id=None, name="Desktop Pro", price=150.0, is_available=False))
    await test_db_session.commit()

    # Act
    result = await repo.search(
        name="Laptop",
        min_price=100.0,
        available_only=True
    )

    # Assert
    assert len(result) == 2
    assert all("Laptop" in item.name for item in result)
```

### Testing Error Handling

```python
def test_create_item_with_duplicate_name_returns_409(self, client):
    """Test creating item with duplicate name returns conflict."""
    # Arrange
    client.post("/items", json={"name": "Unique", "price": 99.99})

    # Act - Try to create duplicate
    response = client.post("/items", json={"name": "Unique", "price": 99.99})

    # Assert
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()
```

### Testing Authentication/Authorization

```python
def test_create_item_without_auth_returns_401(self, client):
    """Test creating item without authentication."""
    # Act
    response = client.post(
        "/items",
        json={"name": "Test", "price": 99.99}
    )

    # Assert
    assert response.status_code == 401


def test_delete_item_without_permission_returns_403(self, client, auth_token):
    """Test deleting item without permission."""
    # Arrange
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Act
    response = client.delete("/items/1", headers=headers)

    # Assert
    assert response.status_code == 403
```

---

## Quick Reference Checklist

When adding a new feature, create tests in this order:

- [ ] **Models** - `tests/unit/{domain}/test_models.py`
  - [ ] Test valid creation
  - [ ] Test defaults
  - [ ] Test edge cases
  - [ ] Test business logic methods

- [ ] **Schemas** - `tests/unit/{domain}/test_schemas.py`
  - [ ] Test valid requests
  - [ ] Test validation errors
  - [ ] Test `from_domain_model()` conversion
  - [ ] Test sensitive field exclusion

- [ ] **Service** - `tests/unit/{domain}/test_service.py`
  - [ ] Test happy path
  - [ ] Test not found cases
  - [ ] Test event publishing (MANDATORY)
  - [ ] Test error cases

- [ ] **Repository** - `tests/unit/{domain}/test_repository.py`
  - [ ] Test CRUD operations
  - [ ] Test search/filters
  - [ ] Test not found cases
  - [ ] Test model conversions

- [ ] **Integration** - `tests/integration/{domain}/`
  - [ ] Test service + repository together
  - [ ] Test event handlers
  - [ ] Test cross-domain interactions (if applicable)

- [ ] **API** - `tests/api/test_{domain}_api.py`
  - [ ] Test all endpoints
  - [ ] Test status codes
  - [ ] Test validation errors
  - [ ] Test complete user journeys

---

## Coverage Commands

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term

# View in browser
open htmlcov/index.html

# Fail if coverage below 80%
pytest --cov=app --cov-fail-under=80

# Show missing lines
pytest --cov=app --cov-report=term-missing
```

---

## Tips for Coding Agents

1. **Always use fixtures** - Don't create test data inline
2. **Follow the naming convention** - `test_{method}_{scenario}_{result}`
3. **Test one thing per test** - Don't combine unrelated assertions
4. **Mock external dependencies** in unit tests
5. **Use real database** in integration tests
6. **Always test event publishing** for business actions
7. **Use Arrange-Act-Assert** pattern consistently
8. **Test both happy path and error cases**
9. **Verify coverage** after writing tests
10. **Run tests before committing** - `pytest -x`

---

**For rules and standards, see:** [TESTING_STANDARDS.md](./TESTING_STANDARDS.md)
**For architecture guidance, see:** [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md)
