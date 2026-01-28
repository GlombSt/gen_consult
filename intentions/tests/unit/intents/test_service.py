"""
Unit tests for intents service layer.

Tests business logic with mocked dependencies.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.intents.events import (
    FactAddedEvent,
    FactRemovedEvent,
    FactUpdatedEvent,
    IntentCreatedEvent,
    IntentUpdatedEvent,
)
from app.intents.schemas import IntentCreateRequest
from app.intents.service import (
    add_fact_to_intent,
    create_intent,
    get_intent,
    remove_fact_from_intent,
    update_fact_value,
    update_intent_constraints,
    update_intent_context,
    update_intent_description,
    update_intent_name,
    update_intent_output_format,
    update_intent_output_structure,
)
from tests.fixtures.intents import create_test_fact, create_test_intent


@pytest.mark.unit
class TestCreateIntent:
    """Test create_intent service function (US-000)."""

    @pytest.mark.asyncio
    async def test_create_intent_with_valid_data_returns_created_intent(self):
        """Test creating an intent with valid data."""
        # Arrange
        request = IntentCreateRequest(
            name="New Intent",
            description="Test description",
            output_format="JSON",
        )
        created_intent = create_test_intent(id=1, name="New Intent", description="Test description", output_format="JSON")

        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await create_intent(request, repository=mock_repo)

            # Assert
            assert result.id == 1
            assert result.name == "New Intent"
            assert result.description == "Test description"
            assert result.output_format == "JSON"
            mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_intent_publishes_intent_created_event(self):
        """Test creating an intent publishes IntentCreatedEvent."""
        # Arrange
        request = IntentCreateRequest(
            name="New Intent",
            description="Test description",
            output_format="JSON",
        )
        created_intent = create_test_intent(id=1, name="New Intent", description="Test description", output_format="JSON")

        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await create_intent(request, repository=mock_repo)

            # Assert
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, IntentCreatedEvent)
            assert published_event.intent_id == 1
            assert published_event.name == "New Intent"
            assert published_event.description == "Test description"
            assert published_event.output_format == "JSON"
            assert published_event.event_type == "intent.created"

    @pytest.mark.asyncio
    async def test_create_intent_with_all_fields_returns_created_intent(self):
        """Test creating an intent with all fields including optional ones."""
        # Arrange
        request = IntentCreateRequest(
            name="Complete Intent",
            description="Complete description",
            output_format="XML",
            output_structure="Structured output",
            context="Test context",
            constraints="Test constraints",
        )
        created_intent = create_test_intent(
            id=1,
            name="Complete Intent",
            description="Complete description",
            output_format="XML",
            output_structure="Structured output",
            context="Test context",
            constraints="Test constraints",
        )

        mock_repo = MagicMock()
        mock_repo.create = AsyncMock(return_value=created_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await create_intent(request, repository=mock_repo)

            # Assert
            assert result.id == 1
            assert result.name == "Complete Intent"
            assert result.output_format == "XML"
            assert result.output_structure == "Structured output"
            assert result.context == "Test context"
            assert result.constraints == "Test constraints"


@pytest.mark.unit
class TestGetIntent:
    """Test get_intent service function."""

    @pytest.mark.asyncio
    async def test_get_intent_when_exists_returns_intent(self):
        """Test getting an intent that exists."""
        # Arrange
        mock_intent = create_test_intent(id=1, name="Test Intent")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=mock_intent)

        # Act
        result = await get_intent(1, repository=mock_repo)

        # Assert
        assert result is not None
        assert result.id == 1
        assert result.name == "Test Intent"
        mock_repo.find_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_intent_when_not_found_returns_none(self):
        """Test getting an intent that doesn't exist."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=None)

        # Act
        result = await get_intent(999, repository=mock_repo)

        # Assert
        assert result is None
        mock_repo.find_by_id.assert_called_once_with(999)


@pytest.mark.unit
class TestUpdateIntentName:
    """Test update_intent_name service function (US-001)."""

    @pytest.mark.asyncio
    async def test_update_intent_name_when_exists_returns_updated_intent(self):
        """Test updating an intent name."""
        # Arrange
        existing_intent = create_test_intent(id=1, name="Old Name")
        updated_intent = create_test_intent(id=1, name="New Name")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.update = AsyncMock(return_value=updated_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_intent_name(1, "New Name", repository=mock_repo)

            # Assert
            assert result is not None
            assert result.name == "New Name"
            mock_repo.update.assert_called_once()
            mock_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_intent_name_publishes_intent_updated_event(self):
        """Test updating intent name publishes IntentUpdatedEvent."""
        # Arrange
        existing_intent = create_test_intent(id=1, name="Old Name")
        updated_intent = create_test_intent(id=1, name="New Name")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.update = AsyncMock(return_value=updated_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await update_intent_name(1, "New Name", repository=mock_repo)

            # Assert
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, IntentUpdatedEvent)
            assert published_event.intent_id == 1
            assert published_event.field_updated == "name"


@pytest.mark.unit
class TestUpdateIntentDescription:
    """Test update_intent_description service function (US-002)."""

    @pytest.mark.asyncio
    async def test_update_intent_description_when_exists_returns_updated_intent(self):
        """Test updating an intent description."""
        # Arrange
        existing_intent = create_test_intent(id=1, description="Old description")
        updated_intent = create_test_intent(id=1, description="New description")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.update = AsyncMock(return_value=updated_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_intent_description(1, "New description", repository=mock_repo)

            # Assert
            assert result is not None
            assert result.description == "New description"
            mock_repo.update.assert_called_once()
            mock_bus.publish.assert_called_once()


@pytest.mark.unit
class TestUpdateIntentOutputFormat:
    """Test update_intent_output_format service function (US-003)."""

    @pytest.mark.asyncio
    async def test_update_intent_output_format_when_exists_returns_updated_intent(self):
        """Test updating an intent output format."""
        # Arrange
        existing_intent = create_test_intent(id=1, output_format="plain text")
        updated_intent = create_test_intent(id=1, output_format="JSON")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.update = AsyncMock(return_value=updated_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_intent_output_format(1, "JSON", repository=mock_repo)

            # Assert
            assert result is not None
            assert result.output_format == "JSON"
            mock_repo.update.assert_called_once()
            mock_bus.publish.assert_called_once()


@pytest.mark.unit
class TestUpdateIntentOutputStructure:
    """Test update_intent_output_structure service function (US-004)."""

    @pytest.mark.asyncio
    async def test_update_intent_output_structure_when_exists_returns_updated_intent(self):
        """Test updating an intent output structure."""
        # Arrange
        existing_intent = create_test_intent(id=1, output_structure="Old structure")
        updated_intent = create_test_intent(id=1, output_structure="New structure")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.update = AsyncMock(return_value=updated_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_intent_output_structure(1, "New structure", repository=mock_repo)

            # Assert
            assert result is not None
            assert result.output_structure == "New structure"
            mock_repo.update.assert_called_once()
            mock_bus.publish.assert_called_once()


@pytest.mark.unit
class TestUpdateIntentContext:
    """Test update_intent_context service function (US-005)."""

    @pytest.mark.asyncio
    async def test_update_intent_context_when_exists_returns_updated_intent(self):
        """Test updating an intent context."""
        # Arrange
        existing_intent = create_test_intent(id=1, context="Old context")
        updated_intent = create_test_intent(id=1, context="New context")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.update = AsyncMock(return_value=updated_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_intent_context(1, "New context", repository=mock_repo)

            # Assert
            assert result is not None
            assert result.context == "New context"
            mock_repo.update.assert_called_once()
            mock_bus.publish.assert_called_once()


@pytest.mark.unit
class TestUpdateIntentConstraints:
    """Test update_intent_constraints service function (US-006)."""

    @pytest.mark.asyncio
    async def test_update_intent_constraints_when_exists_returns_updated_intent(self):
        """Test updating an intent constraints."""
        # Arrange
        existing_intent = create_test_intent(id=1, constraints="Old constraints")
        updated_intent = create_test_intent(id=1, constraints="New constraints")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.update = AsyncMock(return_value=updated_intent)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_intent_constraints(1, "New constraints", repository=mock_repo)

            # Assert
            assert result is not None
            assert result.constraints == "New constraints"
            mock_repo.update.assert_called_once()
            mock_bus.publish.assert_called_once()


@pytest.mark.unit
class TestAddFactToIntent:
    """Test add_fact_to_intent service function (US-008)."""

    @pytest.mark.asyncio
    async def test_add_fact_to_intent_when_intent_exists_returns_fact(self):
        """Test adding a fact to an intent."""
        # Arrange
        existing_intent = create_test_intent(id=1)
        new_fact = create_test_fact(id=1, intent_id=1, value="New fact")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.add_fact = AsyncMock(return_value=new_fact)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await add_fact_to_intent(1, "New fact", repository=mock_repo)

            # Assert
            assert result is not None
            assert result.value == "New fact"
            mock_repo.add_fact.assert_called_once()
            mock_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_fact_to_intent_publishes_fact_added_event(self):
        """Test adding a fact publishes FactAddedEvent."""
        # Arrange
        existing_intent = create_test_intent(id=1)
        new_fact = create_test_fact(id=1, intent_id=1, value="New fact")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.add_fact = AsyncMock(return_value=new_fact)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await add_fact_to_intent(1, "New fact", repository=mock_repo)

            # Assert
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, FactAddedEvent)
            assert published_event.intent_id == 1
            assert published_event.fact_id == 1
            assert published_event.value == "New fact"


@pytest.mark.unit
class TestUpdateFactValue:
    """Test update_fact_value service function (US-007)."""

    @pytest.mark.asyncio
    async def test_update_fact_value_when_exists_returns_updated_fact(self):
        """Test updating a fact value."""
        # Arrange
        existing_intent = create_test_intent(id=1)
        existing_fact = create_test_fact(id=1, intent_id=1, value="Old value")
        updated_fact = create_test_fact(id=1, intent_id=1, value="New value")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.find_fact_by_id = AsyncMock(return_value=existing_fact)
        mock_repo.update_fact = AsyncMock(return_value=updated_fact)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await update_fact_value(1, 1, "New value", repository=mock_repo)

            # Assert
            assert result is not None
            assert result.value == "New value"
            mock_repo.update_fact.assert_called_once()
            mock_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_fact_value_publishes_fact_updated_event(self):
        """Test updating a fact publishes FactUpdatedEvent."""
        # Arrange
        existing_intent = create_test_intent(id=1)
        existing_fact = create_test_fact(id=1, intent_id=1, value="Old value")
        updated_fact = create_test_fact(id=1, intent_id=1, value="New value")

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.find_fact_by_id = AsyncMock(return_value=existing_fact)
        mock_repo.update_fact = AsyncMock(return_value=updated_fact)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await update_fact_value(1, 1, "New value", repository=mock_repo)

            # Assert
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, FactUpdatedEvent)
            assert published_event.intent_id == 1
            assert published_event.fact_id == 1


@pytest.mark.unit
class TestRemoveFactFromIntent:
    """Test remove_fact_from_intent service function (US-009)."""

    @pytest.mark.asyncio
    async def test_remove_fact_from_intent_when_exists_returns_true(self):
        """Test removing a fact from an intent."""
        # Arrange
        existing_intent = create_test_intent(id=1)
        existing_fact = create_test_fact(id=1, intent_id=1)

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.find_fact_by_id = AsyncMock(return_value=existing_fact)
        mock_repo.remove_fact = AsyncMock(return_value=True)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            result = await remove_fact_from_intent(1, 1, repository=mock_repo)

            # Assert
            assert result is True
            mock_repo.remove_fact.assert_called_once_with(1, 1)
            mock_bus.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_fact_from_intent_publishes_fact_removed_event(self):
        """Test removing a fact publishes FactRemovedEvent."""
        # Arrange
        existing_intent = create_test_intent(id=1)
        existing_fact = create_test_fact(id=1, intent_id=1)

        mock_repo = MagicMock()
        mock_repo.find_by_id = AsyncMock(return_value=existing_intent)
        mock_repo.find_fact_by_id = AsyncMock(return_value=existing_fact)
        mock_repo.remove_fact = AsyncMock(return_value=True)

        with patch("app.intents.service.event_bus") as mock_bus:
            mock_bus.publish = AsyncMock()

            # Act
            await remove_fact_from_intent(1, 1, repository=mock_repo)

            # Assert
            mock_bus.publish.assert_called_once()
            published_event = mock_bus.publish.call_args[0][0]
            assert isinstance(published_event, FactRemovedEvent)
            assert published_event.intent_id == 1
            assert published_event.fact_id == 1
