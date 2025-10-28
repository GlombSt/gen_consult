"""
Integration tests for items service with real repository.

Tests service + repository integration without mocks.
"""

from unittest.mock import patch

import pytest

from app.items.events import ItemCreatedEvent
from app.items.repository import ItemRepository
from app.items.service import (
    create_item,
    delete_item,
    get_all_items,
    get_item,
    search_items,
    update_item,
)
from app.shared.events import EventBus
from tests.fixtures.items import (
    create_test_item_create_request,
    create_test_item_update_request,
)


@pytest.mark.integration
class TestItemServiceIntegration:
    """Test items service with real repository."""

    @pytest.mark.asyncio
    async def test_create_and_get_item_integration(self):
        """Test creating and retrieving an item end-to-end."""
        # Arrange
        request = create_test_item_create_request(name="Integration Test Item", price=299.99)

        with patch("app.items.service.item_repository", ItemRepository()), patch("app.items.service.event_bus", EventBus()):
            # Act - Create
            created_item = await create_item(request)

            # Act - Get
            retrieved_item = await get_item(created_item.id)

            # Assert
            assert retrieved_item is not None
            assert retrieved_item.id == created_item.id
            assert retrieved_item.name == "Integration Test Item"
            assert retrieved_item.price == 299.99

    @pytest.mark.asyncio
    async def test_create_update_get_item_integration(self):
        """Test creating, updating, and retrieving an item."""
        # Arrange
        create_request = create_test_item_create_request(name="Original Name", price=99.99)
        update_request = create_test_item_update_request(name="Updated Name", price=149.99)

        with patch("app.items.service.item_repository", ItemRepository()), patch("app.items.service.event_bus", EventBus()):
            # Act - Create
            created_item = await create_item(create_request)

            # Act - Update
            await update_item(created_item.id, update_request)

            # Act - Get
            retrieved_item = await get_item(created_item.id)

            # Assert
            assert retrieved_item is not None
            assert retrieved_item.name == "Updated Name"
            assert retrieved_item.price == 149.99

    @pytest.mark.asyncio
    async def test_create_delete_get_item_integration(self):
        """Test creating, deleting, and attempting to retrieve an item."""
        # Arrange
        request = create_test_item_create_request(name="To Delete", price=99.99)

        with patch("app.items.service.item_repository", ItemRepository()), patch("app.items.service.event_bus", EventBus()):
            # Act - Create
            created_item = await create_item(request)

            # Act - Delete
            deleted = await delete_item(created_item.id)

            # Act - Get
            retrieved_item = await get_item(created_item.id)

            # Assert
            assert deleted is True
            assert retrieved_item is None

    @pytest.mark.asyncio
    async def test_create_multiple_and_get_all_integration(self):
        """Test creating multiple items and retrieving all."""
        # Arrange
        request1 = create_test_item_create_request(name="Item 1", price=99.99)
        request2 = create_test_item_create_request(name="Item 2", price=149.99)

        with patch("app.items.service.item_repository", ItemRepository()), patch("app.items.service.event_bus", EventBus()):
            # Act - Create multiple
            await create_item(request1)
            await create_item(request2)

            # Act - Get all
            all_items = await get_all_items()

            # Assert
            assert len(all_items) == 2
            assert any(item.name == "Item 1" for item in all_items)
            assert any(item.name == "Item 2" for item in all_items)

    @pytest.mark.asyncio
    async def test_search_items_integration(self):
        """Test searching items with filters."""
        # Arrange
        with patch("app.items.service.item_repository", ItemRepository()), patch("app.items.service.event_bus", EventBus()):
            await create_item(create_test_item_create_request(name="Laptop Pro", price=999.99))
            await create_item(create_test_item_create_request(name="Laptop Air", price=799.99))
            await create_item(create_test_item_create_request(name="Desktop", price=1299.99))

            # Act - Search
            results = await search_items(name="Laptop", min_price=750.0, max_price=1000.0)

            # Assert
            assert len(results) == 2
            assert all("Laptop" in item.name for item in results)

    @pytest.mark.asyncio
    async def test_item_created_event_published_integration(self):
        """Test that ItemCreatedEvent is published when creating item."""
        # Arrange
        request = create_test_item_create_request(name="Event Test", price=99.99)
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("item.created", capture_event)

        with patch("app.items.service.item_repository", ItemRepository()), patch("app.items.service.event_bus", event_bus):
            # Act
            created_item = await create_item(request)

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], ItemCreatedEvent)
            assert published_events[0].item_id == created_item.id
            assert published_events[0].name == "Event Test"
