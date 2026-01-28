"""
Unit tests for shared event system.

Tests event bus and domain events.
"""

from datetime import datetime

import pytest

from app.shared.events import EventBus
from app.users.events import UserCreatedEvent


@pytest.mark.unit
class TestDomainEvent:
    """Test DomainEvent base class."""

    def test_to_dict_includes_timestamp_and_event_type(self):
        """Test to_dict includes timestamp and event_type."""
        # Arrange
        event = UserCreatedEvent(user_id=1, username="testuser", email="test@example.com")

        # Act
        result = event.to_dict()

        # Assert
        assert "timestamp" in result
        assert "event_type" in result
        assert result["event_type"] == "user.created"

    def test_to_dict_includes_all_event_attributes(self):
        """Test to_dict includes all event-specific attributes."""
        # Arrange
        event = UserCreatedEvent(user_id=1, username="testuser", email="test@example.com")

        # Act
        result = event.to_dict()

        # Assert
        assert result["user_id"] == 1
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"

    def test_to_dict_converts_datetime_to_isoformat(self):
        """Test to_dict converts datetime fields to ISO format."""
        # Arrange
        event = UserCreatedEvent(user_id=1, username="testuser", email="test@example.com")

        # Act
        result = event.to_dict()

        # Assert
        assert isinstance(result["timestamp"], str)
        # Verify it's a valid ISO format
        datetime.fromisoformat(result["timestamp"])


@pytest.mark.unit
class TestEventBus:
    """Test EventBus class."""

    @pytest.mark.asyncio
    async def test_subscribe_adds_handler_for_event_type(self):
        """Test subscribing a handler to an event type."""
        # Arrange
        event_bus = EventBus()
        handler_called = []

        async def handler(event):
            handler_called.append(event)

        # Act
        event_bus.subscribe("test.event", handler)

        # Assert - handler is registered
        assert "test.event" in event_bus._handlers
        assert handler in event_bus._handlers["test.event"]

    @pytest.mark.asyncio
    async def test_publish_calls_subscribed_handler(self):
        """Test publishing an event calls subscribed handler."""
        # Arrange
        event_bus = EventBus()
        handler_called = []

        async def handler(event):
            handler_called.append(event)

        event_bus.subscribe("user.created", handler)
        event = UserCreatedEvent(user_id=1, username="testuser", email="test@example.com")

        # Act
        await event_bus.publish(event)

        # Assert
        assert len(handler_called) == 1
        assert handler_called[0] == event

    @pytest.mark.asyncio
    async def test_publish_calls_multiple_handlers(self):
        """Test publishing an event calls all subscribed handlers."""
        # Arrange
        event_bus = EventBus()
        handler1_called = []
        handler2_called = []

        async def handler1(event):
            handler1_called.append(event)

        async def handler2(event):
            handler2_called.append(event)

        event_bus.subscribe("user.created", handler1)
        event_bus.subscribe("user.created", handler2)
        event = UserCreatedEvent(user_id=1, username="testuser", email="test@example.com")

        # Act
        await event_bus.publish(event)

        # Assert
        assert len(handler1_called) == 1
        assert len(handler2_called) == 1

    @pytest.mark.asyncio
    async def test_publish_without_handlers_does_not_raise_error(self):
        """Test publishing an event with no handlers doesn't raise error."""
        # Arrange
        event_bus = EventBus()
        event = UserCreatedEvent(user_id=1, username="testuser", email="test@example.com")

        # Act & Assert - should not raise
        await event_bus.publish(event)

    @pytest.mark.asyncio
    async def test_publish_handles_handler_exception(self):
        """Test publishing continues even if handler raises exception."""
        # Arrange
        event_bus = EventBus()
        handler_called = []

        async def failing_handler(event):
            raise Exception("Handler error")

        async def successful_handler(event):
            handler_called.append(event)

        event_bus.subscribe("user.created", failing_handler)
        event_bus.subscribe("user.created", successful_handler)
        event = UserCreatedEvent(user_id=1, username="testuser", email="test@example.com")

        # Act
        await event_bus.publish(event)

        # Assert - successful handler still called
        assert len(handler_called) == 1

    @pytest.mark.asyncio
    async def test_publish_supports_sync_handlers(self):
        """Test publishing supports synchronous handlers."""
        # Arrange
        event_bus = EventBus()
        handler_called = []

        def sync_handler(event):
            handler_called.append(event)

        event_bus.subscribe("user.created", sync_handler)
        event = UserCreatedEvent(user_id=1, username="testuser", email="test@example.com")

        # Act
        await event_bus.publish(event)

        # Assert
        assert len(handler_called) == 1


@pytest.mark.unit
class TestUserEvents:
    """Test user domain events."""

    def test_user_created_event_has_correct_type(self):
        """Test UserCreatedEvent has correct event type."""
        # Arrange & Act
        event = UserCreatedEvent(user_id=1, username="testuser", email="test@example.com")

        # Assert
        assert event.event_type == "user.created"
        assert isinstance(event.timestamp, datetime)
