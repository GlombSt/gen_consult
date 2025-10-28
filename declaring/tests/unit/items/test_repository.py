"""
Unit tests for items repository layer.

Tests data access and model conversions with mocked database.
"""

from datetime import datetime

import pytest

from app.items.repository import ItemRepository
from tests.fixtures.items import create_test_item


@pytest.mark.unit
class TestItemRepositoryFindAll:
    """Test ItemRepository.find_all method."""

    @pytest.mark.asyncio
    async def test_find_all_with_items_returns_all_items(self):
        """Test finding all items when items exist."""
        # Arrange
        repo = ItemRepository()
        item1 = create_test_item(id=None, name="Item 1")
        item2 = create_test_item(id=None, name="Item 2")
        await repo.create(item1)
        await repo.create(item2)

        # Act
        result = await repo.find_all()

        # Assert
        assert len(result) == 2
        assert result[0].name == "Item 1"
        assert result[1].name == "Item 2"

    @pytest.mark.asyncio
    async def test_find_all_with_empty_storage_returns_empty_list(self):
        """Test finding all items when storage is empty."""
        # Arrange
        repo = ItemRepository()

        # Act
        result = await repo.find_all()

        # Assert
        assert result == []


@pytest.mark.unit
class TestItemRepositoryFindById:
    """Test ItemRepository.find_by_id method."""

    @pytest.mark.asyncio
    async def test_find_by_id_when_exists_returns_item(self):
        """Test finding an item by ID when it exists."""
        # Arrange
        repo = ItemRepository()
        item = create_test_item(id=None, name="Test Item")
        created = await repo.create(item)

        # Act
        result = await repo.find_by_id(created.id)

        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.name == "Test Item"

    @pytest.mark.asyncio
    async def test_find_by_id_when_not_exists_returns_none(self):
        """Test finding an item by ID when it doesn't exist."""
        # Arrange
        repo = ItemRepository()

        # Act
        result = await repo.find_by_id(999)

        # Assert
        assert result is None


@pytest.mark.unit
class TestItemRepositoryCreate:
    """Test ItemRepository.create method."""

    @pytest.mark.asyncio
    async def test_create_item_assigns_id_and_returns_item(self):
        """Test creating an item assigns ID and returns domain model."""
        # Arrange
        repo = ItemRepository()
        item = create_test_item(id=None, name="New Item", price=99.99)

        # Act
        result = await repo.create(item)

        # Assert
        assert result.id is not None
        assert result.id == 1
        assert result.name == "New Item"
        assert result.price == 99.99

    @pytest.mark.asyncio
    async def test_create_multiple_items_increments_id(self):
        """Test creating multiple items increments ID counter."""
        # Arrange
        repo = ItemRepository()
        item1 = create_test_item(id=None, name="Item 1")
        item2 = create_test_item(id=None, name="Item 2")

        # Act
        result1 = await repo.create(item1)
        result2 = await repo.create(item2)

        # Assert
        assert result1.id == 1
        assert result2.id == 2


@pytest.mark.unit
class TestItemRepositoryUpdate:
    """Test ItemRepository.update method."""

    @pytest.mark.asyncio
    async def test_update_item_when_exists_returns_updated_item(self):
        """Test updating an existing item."""
        # Arrange
        repo = ItemRepository()
        item = create_test_item(id=None, name="Old Name", price=99.99)
        created = await repo.create(item)

        # Modify the item
        created.name = "New Name"
        created.price = 149.99

        # Act
        result = await repo.update(created.id, created)

        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.name == "New Name"
        assert result.price == 149.99

    @pytest.mark.asyncio
    async def test_update_item_when_not_exists_returns_none(self):
        """Test updating a non-existent item."""
        # Arrange
        repo = ItemRepository()
        item = create_test_item(id=999, name="Test")

        # Act
        result = await repo.update(999, item)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_item_preserves_created_at(self):
        """Test updating an item preserves created_at timestamp."""
        # Arrange
        repo = ItemRepository()
        original_date = datetime(2025, 1, 1, 12, 0, 0)
        item = create_test_item(id=None, name="Test", created_at=original_date)
        created = await repo.create(item)

        # Modify the item
        created.name = "Updated"

        # Act
        result = await repo.update(created.id, created)

        # Assert
        assert result.created_at == original_date


@pytest.mark.unit
class TestItemRepositoryDelete:
    """Test ItemRepository.delete method."""

    @pytest.mark.asyncio
    async def test_delete_item_when_exists_returns_true(self):
        """Test deleting an existing item."""
        # Arrange
        repo = ItemRepository()
        item = create_test_item(id=None, name="Test Item")
        created = await repo.create(item)

        # Act
        result = await repo.delete(created.id)

        # Assert
        assert result is True
        # Verify item is actually deleted
        found = await repo.find_by_id(created.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_delete_item_when_not_exists_returns_false(self):
        """Test deleting a non-existent item."""
        # Arrange
        repo = ItemRepository()

        # Act
        result = await repo.delete(999)

        # Assert
        assert result is False


@pytest.mark.unit
class TestItemRepositorySearch:
    """Test ItemRepository.search method."""

    @pytest.mark.asyncio
    async def test_search_by_name_returns_matching_items(self):
        """Test searching items by name."""
        # Arrange
        repo = ItemRepository()
        await repo.create(create_test_item(id=None, name="Laptop Pro"))
        await repo.create(create_test_item(id=None, name="Laptop Air"))
        await repo.create(create_test_item(id=None, name="Desktop"))

        # Act
        result = await repo.search(name="Laptop")

        # Assert
        assert len(result) == 2
        assert all("Laptop" in item.name for item in result)

    @pytest.mark.asyncio
    async def test_search_by_price_range_returns_matching_items(self):
        """Test searching items by price range."""
        # Arrange
        repo = ItemRepository()
        await repo.create(create_test_item(id=None, name="Item 1", price=50.0))
        await repo.create(create_test_item(id=None, name="Item 2", price=150.0))
        await repo.create(create_test_item(id=None, name="Item 3", price=250.0))

        # Act
        result = await repo.search(min_price=100.0, max_price=200.0)

        # Assert
        assert len(result) == 1
        assert result[0].price == 150.0

    @pytest.mark.asyncio
    async def test_search_available_only_returns_available_items(self):
        """Test searching for available items only."""
        # Arrange
        repo = ItemRepository()
        await repo.create(create_test_item(id=None, name="Available", is_available=True))
        await repo.create(create_test_item(id=None, name="Unavailable", is_available=False))

        # Act
        result = await repo.search(available_only=True)

        # Assert
        assert len(result) == 1
        assert result[0].is_available is True

    @pytest.mark.asyncio
    async def test_search_with_multiple_filters_returns_matching_items(self):
        """Test searching with multiple filters."""
        # Arrange
        repo = ItemRepository()
        await repo.create(create_test_item(id=None, name="Laptop Pro", price=150.0, is_available=True))
        await repo.create(create_test_item(id=None, name="Laptop Air", price=250.0, is_available=True))
        await repo.create(create_test_item(id=None, name="Desktop Pro", price=150.0, is_available=False))

        # Act
        result = await repo.search(name="Laptop", min_price=100.0, available_only=True)

        # Assert
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_search_with_no_matches_returns_empty_list(self):
        """Test searching with no matches."""
        # Arrange
        repo = ItemRepository()
        await repo.create(create_test_item(id=None, name="Laptop"))

        # Act
        result = await repo.search(name="Nonexistent")

        # Assert
        assert result == []
