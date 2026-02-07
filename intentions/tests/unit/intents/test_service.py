"""
Unit tests for intents service layer (V2).

Tests business logic with mocked dependencies.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.intents.events import IntentCreatedEvent, IntentUpdatedEvent
from app.intents.schemas import IntentCreateRequest
from app.intents.service import (
    add_insight,
    add_output,
    add_prompt,
    create_intent,
    delete_intent,
    get_intent,
    list_intents,
    update_intent_articulation,
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
        created_intent = create_test_intent(id=1, name="New Intent", description="Test description")

        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_intent)
        mock_repo.find_by_id = AsyncMock(return_value=created_intent)

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
        created_intent = create_test_intent(id=1, name="New Intent", description="Test description")

        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_intent)
        mock_repo.find_by_id = AsyncMock(return_value=created_intent)

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

            result = await update_intent_description(1, "Updated", repository=mock_repo)

            assert result is not None
            assert result.description == "Updated"
            mock_repo.update.assert_called_once()


@pytest.mark.unit
class TestListIntents:
    """Test list_intents service function."""

    @pytest.mark.asyncio
    async def test_list_intents_returns_all_from_repository(self):
        """Test that list_intents returns result of repository.list_all."""
        mock_intents = [
            create_test_intent(id=1, name="A"),
            create_test_intent(id=2, name="B"),
        ]
        mock_repo = MagicMock()
        mock_repo.list_all = AsyncMock(return_value=mock_intents)

        result = await list_intents(repository=mock_repo)

        assert result == mock_intents
        mock_repo.list_all.assert_called_once()


@pytest.mark.unit
class TestDeleteIntent:
    """Test delete_intent service function."""

    @pytest.mark.asyncio
    async def test_delete_intent_when_exists_deletes_and_publishes_event(self):
        """Test delete when intent exists."""
        from app.intents.events import IntentDeletedEvent

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=create_test_intent(id=1, name="X"))
        mock_repo.delete = AsyncMock(return_value=True)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()
            result = await delete_intent(1, repository=mock_repo)

        assert result is True
        mock_repo.delete.assert_called_once_with(1)
        mock_bus.publish.assert_called_once()
        assert isinstance(mock_bus.publish.call_args[0][0], IntentDeletedEvent)

    @pytest.mark.asyncio
    async def test_delete_intent_when_not_exists_returns_false(self):
        """Test delete when intent does not exist."""
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        result = await delete_intent(999, repository=mock_repo)

        assert result is False
        mock_repo.delete.assert_not_called()


@pytest.mark.unit
class TestUpdateIntentArticulation:
    """Test update_intent_articulation service function."""

    @pytest.mark.asyncio
    async def test_update_intent_articulation_when_exists_replaces_and_returns_intent(self):
        """Test updating articulation when intent exists (full replace: all six fields)."""
        from app.intents.schemas import AspectCreate, IntentArticulationUpdateRequest

        existing = create_test_intent(id=1, name="X")
        existing.aspects = []
        existing.inputs = []
        existing.choices = []
        existing.pitfalls = []
        existing.assumptions = []
        existing.qualities = []
        updated_intent = create_test_intent(id=1, name="X")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(side_effect=[existing, updated_intent])
        mock_repo.delete_aspect = AsyncMock()
        mock_repo.add_aspect = AsyncMock()

        payload = IntentArticulationUpdateRequest(
            aspects=[AspectCreate(name="NewAspect", description="D")],
            inputs=[],
            choices=[],
            pitfalls=[],
            assumptions=[],
            qualities=[],
        )

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()
            result = await update_intent_articulation(1, payload, repository=mock_repo)

        assert result is updated_intent
        mock_repo.add_aspect.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_intent_articulation_when_only_aspects_supplied_succeeds(self):
        """Intent owns articulation entities; aspect_id is optional. Partial update (only aspects) is allowed."""
        from app.intents.schemas import AspectCreate, IntentArticulationUpdateRequest

        existing = create_test_intent(id=1, name="X")
        existing.aspects = []
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing)
        mock_repo.add_aspect = AsyncMock()

        payload = IntentArticulationUpdateRequest(
            aspects=[AspectCreate(name="NewAspect", description="D")],
        )

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()
            result = await update_intent_articulation(1, payload, repository=mock_repo)

        assert result is existing
        mock_repo.delete_aspect.assert_not_called()  # no existing aspects
        mock_repo.add_aspect.assert_called_once()
        mock_repo.delete_input.assert_not_called()
        mock_repo.delete_choice.assert_not_called()
        mock_repo.delete_pitfall.assert_not_called()
        mock_repo.delete_assumption.assert_not_called()
        mock_repo.delete_quality.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_intent_articulation_when_not_exists_returns_none(self):
        """Test updating articulation when intent does not exist."""
        from app.intents.schemas import IntentArticulationUpdateRequest

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        result = await update_intent_articulation(999, IntentArticulationUpdateRequest(), repository=mock_repo)

        assert result is None


@pytest.mark.unit
class TestAddPrompt:
    """Test add_prompt service function."""

    @pytest.mark.asyncio
    async def test_add_prompt_when_intent_exists_returns_prompt(self):
        """Test adding a prompt when intent exists."""
        from app.intents.schemas import PromptCreateRequest

        mock_intent = create_test_intent(id=1, name="X")
        mock_prompt = MagicMock()
        mock_prompt.id = 10
        mock_prompt.version = 1
        mock_prompt.content = "Do something"

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=mock_intent)
        mock_repo.get_next_prompt_version = AsyncMock(return_value=1)
        mock_repo.add_prompt = AsyncMock(return_value=mock_prompt)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()
            result = await add_prompt(1, PromptCreateRequest(content="Do something"), repository=mock_repo)

        assert result is mock_prompt
        mock_repo.add_prompt.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_prompt_when_intent_not_exists_returns_none(self):
        """Test adding a prompt when intent does not exist."""
        from app.intents.schemas import PromptCreateRequest

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        result = await add_prompt(999, PromptCreateRequest(content="x"), repository=mock_repo)

        assert result is None
        mock_repo.add_prompt.assert_not_called()


@pytest.mark.unit
class TestAddOutput:
    """Test add_output service function."""

    @pytest.mark.asyncio
    async def test_add_output_when_prompt_exists_returns_output(self):
        """Test adding an output when prompt exists."""
        from app.intents.schemas import OutputCreateRequest

        mock_output = MagicMock()
        mock_output.id = 5
        mock_output.content = "Result"

        mock_repo = MagicMock()
        mock_repo.add_output = AsyncMock(return_value=mock_output)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()
            result = await add_output(1, OutputCreateRequest(content="Result"), repository=mock_repo)

        assert result is mock_output
        mock_repo.add_output.assert_called_once()


@pytest.mark.unit
class TestAddInsight:
    """Test add_insight service function."""

    @pytest.mark.asyncio
    async def test_add_insight_when_intent_exists_returns_insight(self):
        """Test adding an insight when intent exists."""
        from app.intents.schemas import InsightCreateRequest

        mock_intent = create_test_intent(id=1, name="X")
        mock_insight = MagicMock()
        mock_insight.id = 7
        mock_insight.content = "Discovery"

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=mock_intent)
        mock_repo.add_insight = AsyncMock(return_value=mock_insight)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()
            result = await add_insight(1, InsightCreateRequest(content="Discovery"), repository=mock_repo)

        assert result is mock_insight
        mock_repo.add_insight.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_insight_when_intent_not_exists_returns_none(self):
        """Test adding an insight when intent does not exist."""
        from app.intents.schemas import InsightCreateRequest

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        result = await add_insight(999, InsightCreateRequest(content="x"), repository=mock_repo)

        assert result is None
        mock_repo.add_insight.assert_not_called()
