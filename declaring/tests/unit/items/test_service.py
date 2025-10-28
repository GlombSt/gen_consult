"""
Unit tests for items service layer.

Tests business logic with mocked dependencies.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.items.events import ItemCreatedEvent, ItemDeletedEvent, ItemUpdatedEvent
from app.items.service import create_item, delete_item, get_all_items, get_item, search_items, update_item
from tests.fixtures.items import create_test_item, create_test_item_create_request, create_test_item_update_request


@pytest.mark.unit
class TestGetAllItems:
    """Test get_all_items service function."""

    @pytest.mark.asyncio
    async def test_get_all_items_returns_all_items(self):
        """Test getting all items returns repository results."""
        # Arrange
        mock_items = [create_test_item(id=1, name="Item 1"), create_test_item(id=2, name="Item 2")]

        with patch("app.items.service.item_repository") as mock_repo:
            mock_repo.find_all = AsyncMock(return_value=mock_items)

            # Act
            result = await get_all_items()

            # Assert
            assert len(result) == 2
            assert result[0].name == "Item 1"
            assert result[1].name == "Item 2"
            mock_repo.find_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_items_with_empty_repository_returns_empty_list(self):
        """Test getting all items from empty repository."""
        # Arrange
        with patch("app.items.service.item_repository") as mock_repo:
            mock_repo.find_all = AsyncMock(return_value=[])

            # Act
            result = await get_all_items()

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

        with patch("app.items.service.item_repository") as mock_repo:
            mock_repo.find_by_id = AsyncMock(return_value=mock_item)

            # Act
            result = await get_item(1)

            # Assert
            assert result is not None
            assert result.id == 1
            assert result.name == "Test Item"
            mock_repo.find_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_item_when_not_found_returns_none(self):
        """Test getting an item that doesn't exist."""
        # Arrange
        with patch("app.items.service.item_repository") as mock_repo:
            mock_repo.find_by_id = AsyncMock(return_value=None)

            # Act
            result = await get_item(999)

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

        with patch("app.items.service.item_repository") as mock_repo, patch("app.items.service.event_bus") as mock_bus:
            mock_repo.create = AsyncMock(return_value=created_item)
            mock_bus.publish = AsyncMock()

            # Act
            result = await create_item(request)

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

        with patch("app.items.service.item_repository") as mock_repo, patch("app.items.service.event_bus") as mock_bus:
            mock_repo.create = AsyncMock(return_value=created_item)
            mock_bus.publish = AsyncMock()

            # Act
            await create_item(request)

            # Assert
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

        with patch("app.items.service.item_repository") as mock_repo, patch("app.items.service.event_bus") as mock_bus:
            mock_repo.find_by_id = AsyncMock(return_value=existing_item)
            mock_repo.update = AsyncMock(return_value=updated_item)
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_item(1, request)

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

        with patch("app.items.service.item_repository") as mock_repo, patch("app.items.service.event_bus") as mock_bus:
            mock_repo.find_by_id = AsyncMock(return_value=None)
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_item(999, request)

            # Assert
            assert result is None
            mock_repo.find_by_id.assert_called_once_with(999)
            mock_bus.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_item_publishes_item_updated_event(self):
        """Test updating an item publishes ItemUpdatedEvent."""
        # Arrange
        existing_item = create_test_item(id=1, name="Old Name")
        updated_item = create_test_item(id=1, name="New Name")
        request = create_test_item_update_request(name="New Name")

        with patch("app.items.service.item_repository") as mock_repo, patch("app.items.service.event_bus") as mock_bus:
            mock_repo.find_by_id = AsyncMock(return_value=existing_item)
            mock_repo.update = AsyncMock(return_value=updated_item)
            mock_bus.publish = AsyncMock()

            # Act
            await update_item(1, request)

            # Assert
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

        with patch("app.items.service.item_repository") as mock_repo, patch("app.items.service.event_bus") as mock_bus:
            mock_repo.find_by_id = AsyncMock(return_value=existing_item)
            mock_repo.delete = AsyncMock(return_value=True)
            mock_bus.publish = AsyncMock()

            # Act
            result = await delete_item(1)

            # Assert
            assert result is True
            mock_repo.find_by_id.assert_called_once_with(1)
            mock_repo.delete.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_item_when_not_found_returns_false(self):
        """Test deleting a non-existent item."""
        # Arrange
        with patch("app.items.service.item_repository") as mock_repo, patch("app.items.service.event_bus") as mock_bus:
            mock_repo.find_by_id = AsyncMock(return_value=None)
            mock_bus.publish = AsyncMock()

            # Act
            result = await delete_item(999)

            # Assert
            assert result is False
            mock_repo.find_by_id.assert_called_once_with(999)
            mock_bus.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_item_publishes_item_deleted_event(self):
        """Test deleting an item publishes ItemDeletedEvent."""
        # Arrange
        existing_item = create_test_item(id=1)

        with patch("app.items.service.item_repository") as mock_repo, patch("app.items.service.event_bus") as mock_bus:
            mock_repo.find_by_id = AsyncMock(return_value=existing_item)
            mock_repo.delete = AsyncMock(return_value=True)
            mock_bus.publish = AsyncMock()

            # Act
            await delete_item(1)

            # Assert
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, ItemDeletedEvent)
            assert published_event.item_id == 1
            assert published_event.event_type == "item.deleted"


@pytest.mark.unit
class TestSearchItems:
    """Test search_items service function."""

    @pytest.mark.asyncio
    async def test_search_items_with_filters_returns_results(self):
        """Test searching items with filters."""
        # Arrange
        mock_items = [create_test_item(id=1, name="Laptop")]

        with patch("app.items.service.item_repository") as mock_repo:
            mock_repo.search = AsyncMock(return_value=mock_items)

            # Act
            result = await search_items(name="Laptop", min_price=100.0, max_price=2000.0, available_only=True)

            # Assert
            assert len(result) == 1
            assert result[0].name == "Laptop"
            mock_repo.search.assert_called_once_with(name="Laptop", min_price=100.0, max_price=2000.0, available_only=True)

    @pytest.mark.asyncio
    async def test_search_items_with_no_results_returns_empty_list(self):
        """Test searching items with no results."""
        # Arrange
        with patch("app.items.service.item_repository") as mock_repo:
            mock_repo.search = AsyncMock(return_value=[])

            # Act
            result = await search_items(name="Nonexistent")

            # Assert
            assert result == []
