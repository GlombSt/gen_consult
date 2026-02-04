"""
Unit tests for intents service layer (V2).

Tests business logic with mocked dependencies.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.intents.events import IntentCreatedEvent, IntentUpdatedEvent
from app.intents.schemas import IntentCreateRequest
from app.intents.service import (
    create_intent,
    get_intent,
    update_intent_description,
    update_intent_name,
)
from tests.fixtures.intents import create_test_intent


@pytest.mark.unit
class TestCreateIntent:
    """Test create_intent service function (V2)."""

    @pytest.mark.asyncio
    async def test_create_intent_with_valid_data_returns_created_intent(self):
        """Test creating an intent with valid data."""
        request = IntentCreateRequest(
            name="New Intent",
            description="Test description",
        )
        created_intent = create_test_intent(
            id=1, name="New Intent", description="Test description"
        )

        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            result = await create_intent(request, repository=mock_repo)

            assert result.id == 1
            assert result.name == "New Intent"
            assert result.description == "Test description"
            mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_intent_publishes_intent_created_event(self):
        """Test creating an intent publishes IntentCreatedEvent."""
        request = IntentCreateRequest(
            name="New Intent",
            description="Test description",
        )
        created_intent = create_test_intent(
            id=1, name="New Intent", description="Test description"
        )

        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            await create_intent(request, repository=mock_repo)

            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, IntentCreatedEvent)
            assert published_event.intent_id == 1
            assert published_event.name == "New Intent"
            assert published_event.description == "Test description"
            assert published_event.event_type == "intent.created"


@pytest.mark.unit
class TestGetIntent:
    """Test get_intent service function."""

    @pytest.mark.asyncio
    async def test_get_intent_when_exists_returns_intent(self):
        """Test getting an intent that exists."""
        mock_intent = create_test_intent(id=1, name="Test Intent")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=mock_intent)

        result = await get_intent(1, repository=mock_repo)

        assert result is not None
        assert result.name == "Test Intent"

    @pytest.mark.asyncio
    async def test_get_intent_when_not_exists_returns_none(self):
        """Test getting an intent that does not exist."""
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        result = await get_intent(999, repository=mock_repo)

        assert result is None


@pytest.mark.unit
class TestUpdateIntentName:
    """Test update_intent_name service function."""

    @pytest.mark.asyncio
    async def test_update_intent_name_when_exists_returns_updated_intent(self):
        """Test updating intent name when intent exists."""
        existing = create_test_intent(id=1, name="Original")
        updated = create_test_intent(id=1, name="Updated")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing)
        mock_repo.update = AsyncMock(return_value=updated)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            result = await update_intent_name(1, "Updated", repository=mock_repo)

            assert result is not None
            assert result.name == "Updated"
            mock_repo.update.assert_called_once()
            mock_bus.publish.assert_called_once()
            assert isinstance(mock_bus.publish.call_args[0][0], IntentUpdatedEvent)

    @pytest.mark.asyncio
    async def test_update_intent_name_when_not_exists_returns_none(self):
        """Test updating intent name when intent does not exist."""
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        result = await update_intent_name(1, "Updated", repository=mock_repo)

        assert result is None
        mock_repo.update.assert_not_called()


@pytest.mark.unit
class TestUpdateIntentDescription:
    """Test update_intent_description service function."""

    @pytest.mark.asyncio
    async def test_update_intent_description_when_exists_returns_updated_intent(
        self,
    ):
        """Test updating intent description when intent exists."""
        existing = create_test_intent(id=1, description="Original")
        updated = create_test_intent(id=1, description="Updated")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing)
        mock_repo.update = AsyncMock(return_value=updated)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            result = await update_intent_description(
                1, "Updated", repository=mock_repo
            )

            assert result is not None
            assert result.description == "Updated"
            mock_repo.update.assert_called_once()
