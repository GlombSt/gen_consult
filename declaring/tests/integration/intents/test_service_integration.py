"""
Integration tests for intents service with real repository.

Tests service + repository integration without mocks.
"""

from unittest.mock import patch

import pytest

from app.intents.events import (
    FactAddedEvent,
    FactRemovedEvent,
    FactUpdatedEvent,
    IntentCreatedEvent,
    IntentUpdatedEvent,
)
from app.intents.repository import IntentRepository
from app.intents.service import (
    add_fact_to_intent,
    create_intent,
    get_all_intents,
    get_intent,
    remove_fact_from_intent,
    update_intent_constraints,
    update_intent_context,
    update_intent_description,
    update_intent_name,
    update_intent_output_format,
    update_intent_output_structure,
    update_fact_value,
)
from app.intents.schemas import IntentCreateRequest
from app.shared.events import EventBus
from tests.fixtures.intents import create_test_intent


@pytest.mark.integration
class TestIntentServiceIntegration:
    """Test intents service with real repository."""

    @pytest.mark.asyncio
    async def test_create_intent_integration(self):
        """Test creating an intent end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            request = IntentCreateRequest(
                name="Integration Test Intent",
                description="Test description",
                output_format="JSON",
            )

            # Act
            created_intent = await create_intent(request)

            # Assert
            assert created_intent.id is not None
            assert created_intent.name == "Integration Test Intent"
            assert created_intent.description == "Test description"
            assert created_intent.output_format == "JSON"

            # Verify persistence
            retrieved = await get_intent(created_intent.id)
            assert retrieved is not None
            assert retrieved.id == created_intent.id
            assert retrieved.name == "Integration Test Intent"

    @pytest.mark.asyncio
    async def test_create_and_get_intent_integration(self):
        """Test creating and retrieving an intent end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            request = IntentCreateRequest(
                name="Test Intent",
                description="Test description",
                output_format="plain text",
            )

            # Act - Create
            created_intent = await create_intent(request)

            # Act - Get
            retrieved_intent = await get_intent(created_intent.id)

            # Assert
            assert retrieved_intent is not None
            assert retrieved_intent.id == created_intent.id
            assert retrieved_intent.name == "Test Intent"
            assert retrieved_intent.description == "Test description"
            assert retrieved_intent.output_format == "plain text"

    @pytest.mark.asyncio
    async def test_get_all_intents_integration(self):
        """Test getting all intents end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            # Create intents directly in repository
            intent1 = create_test_intent(id=None, name="Intent 1", description="Desc 1", output_format="JSON")
            intent2 = create_test_intent(id=None, name="Intent 2", description="Desc 2", output_format="XML")
            await repo.create(intent1)
            await repo.create(intent2)

            # Act
            all_intents = await get_all_intents()

            # Assert
            assert len(all_intents) == 2
            assert any(i.name == "Intent 1" for i in all_intents)
            assert any(i.name == "Intent 2" for i in all_intents)

    @pytest.mark.asyncio
    async def test_get_intent_integration(self):
        """Test getting an intent by ID end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            # Create intent directly in repository
            intent = create_test_intent(id=None, name="Test Intent", description="Test description", output_format="plain text")
            created = await repo.create(intent)

            # Act
            retrieved = await get_intent(created.id)

            # Assert
            assert retrieved is not None
            assert retrieved.id == created.id
            assert retrieved.name == "Test Intent"
            assert retrieved.description == "Test description"
            assert retrieved.output_format == "plain text"

    @pytest.mark.asyncio
    async def test_update_intent_name_integration(self):
        """Test updating intent name end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, name="Original Name")
            created = await repo.create(intent)

            # Act
            updated = await update_intent_name(created.id, "Updated Name")

            # Assert
            assert updated is not None
            assert updated.name == "Updated Name"
            assert updated.id == created.id

            # Verify persistence
            retrieved = await get_intent(created.id)
            assert retrieved is not None
            assert retrieved.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_intent_description_integration(self):
        """Test updating intent description end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, description="Original description")
            created = await repo.create(intent)

            # Act
            updated = await update_intent_description(created.id, "Updated description")

            # Assert
            assert updated is not None
            assert updated.description == "Updated description"

            # Verify persistence
            retrieved = await get_intent(created.id)
            assert retrieved.description == "Updated description"

    @pytest.mark.asyncio
    async def test_update_intent_output_format_integration(self):
        """Test updating intent output format end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, output_format="plain text")
            created = await repo.create(intent)

            # Act
            updated = await update_intent_output_format(created.id, "JSON")

            # Assert
            assert updated is not None
            assert updated.output_format == "JSON"

            # Verify persistence
            retrieved = await get_intent(created.id)
            assert retrieved.output_format == "JSON"

    @pytest.mark.asyncio
    async def test_update_intent_output_structure_integration(self):
        """Test updating intent output structure end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, output_structure="Old structure")
            created = await repo.create(intent)

            # Act
            updated = await update_intent_output_structure(created.id, "New structure")

            # Assert
            assert updated is not None
            assert updated.output_structure == "New structure"

            # Verify persistence
            retrieved = await get_intent(created.id)
            assert retrieved.output_structure == "New structure"

    @pytest.mark.asyncio
    async def test_update_intent_context_integration(self):
        """Test updating intent context end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, context="Old context")
            created = await repo.create(intent)

            # Act
            updated = await update_intent_context(created.id, "New context")

            # Assert
            assert updated is not None
            assert updated.context == "New context"

            # Verify persistence
            retrieved = await get_intent(created.id)
            assert retrieved.context == "New context"

    @pytest.mark.asyncio
    async def test_update_intent_constraints_integration(self):
        """Test updating intent constraints end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, constraints="Old constraints")
            created = await repo.create(intent)

            # Act
            updated = await update_intent_constraints(created.id, "New constraints")

            # Assert
            assert updated is not None
            assert updated.constraints == "New constraints"

            # Verify persistence
            retrieved = await get_intent(created.id)
            assert retrieved.constraints == "New constraints"

    @pytest.mark.asyncio
    async def test_multiple_field_updates_integration(self):
        """Test updating multiple fields of an intent."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, name="Original", description="Original desc", output_format="plain text")
            created = await repo.create(intent)

            # Act - Update multiple fields
            await update_intent_name(created.id, "Updated Name")
            await update_intent_description(created.id, "Updated Description")
            await update_intent_output_format(created.id, "JSON")

            # Assert
            retrieved = await get_intent(created.id)
            assert retrieved.name == "Updated Name"
            assert retrieved.description == "Updated Description"
            assert retrieved.output_format == "JSON"


@pytest.mark.integration
class TestFactServiceIntegration:
    """Test fact operations with real repository."""

    @pytest.mark.asyncio
    async def test_add_fact_to_intent_integration(self):
        """Test adding a fact to an intent end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, name="Test Intent")
            created_intent = await repo.create(intent)

            # Act
            fact = await add_fact_to_intent(created_intent.id, "Test fact value")

            # Assert
            assert fact is not None
            assert fact.intent_id == created_intent.id
            assert fact.value == "Test fact value"

            # Verify persistence
            facts = await repo.find_facts_by_intent_id(created_intent.id)
            assert len(facts) == 1
            assert facts[0].value == "Test fact value"

    @pytest.mark.asyncio
    async def test_update_fact_value_integration(self):
        """Test updating a fact value end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, name="Test Intent")
            created_intent = await repo.create(intent)
            fact = await add_fact_to_intent(created_intent.id, "Original value")

            # Act
            updated = await update_fact_value(created_intent.id, fact.id, "Updated value")

            # Assert
            assert updated is not None
            assert updated.value == "Updated value"

            # Verify persistence
            retrieved_fact = await repo.find_fact_by_id(created_intent.id, fact.id)
            assert retrieved_fact.value == "Updated value"

    @pytest.mark.asyncio
    async def test_remove_fact_from_intent_integration(self):
        """Test removing a fact from an intent end-to-end."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, name="Test Intent")
            created_intent = await repo.create(intent)
            fact = await add_fact_to_intent(created_intent.id, "To remove")

            # Act
            removed = await remove_fact_from_intent(created_intent.id, fact.id)

            # Assert
            assert removed is True

            # Verify fact is removed
            from app.intents.repository import intent_repository
            retrieved_fact = await intent_repository.find_fact_by_id(created_intent.id, fact.id)
            assert retrieved_fact is None

    @pytest.mark.asyncio
    async def test_multiple_facts_integration(self):
        """Test adding multiple facts to an intent."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, name="Test Intent")
            created_intent = await repo.create(intent)

            # Act - Add multiple facts
            fact1 = await add_fact_to_intent(created_intent.id, "Fact 1")
            fact2 = await add_fact_to_intent(created_intent.id, "Fact 2")
            fact3 = await add_fact_to_intent(created_intent.id, "Fact 3")

            # Assert
            facts = await repo.find_facts_by_intent_id(created_intent.id)
            assert len(facts) == 3
            assert any(f.value == "Fact 1" for f in facts)
            assert any(f.value == "Fact 2" for f in facts)
            assert any(f.value == "Fact 3" for f in facts)

    @pytest.mark.asyncio
    async def test_fact_operations_with_intent_updates_integration(self):
        """Test fact operations combined with intent updates."""
        # Arrange
        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", EventBus()):
            intent = create_test_intent(id=None, name="Test Intent")
            created_intent = await repo.create(intent)

            # Act - Add fact, update intent, update fact
            fact = await add_fact_to_intent(created_intent.id, "Original fact")
            await update_intent_name(created_intent.id, "Updated Intent")
            await update_fact_value(created_intent.id, fact.id, "Updated fact")

            # Assert
            retrieved_intent = await get_intent(created_intent.id)
            assert retrieved_intent.name == "Updated Intent"

            retrieved_fact = await repo.find_fact_by_id(created_intent.id, fact.id)
            assert retrieved_fact.value == "Updated fact"


@pytest.mark.integration
class TestEventPublishingIntegration:
    """Test event publishing with real repository."""

    @pytest.mark.asyncio
    async def test_intent_created_event_published_integration(self):
        """Test that IntentCreatedEvent is published when creating intent."""
        # Arrange
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("intent.created", capture_event)

        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", event_bus):
            request = IntentCreateRequest(
                name="Event Test Intent",
                description="Test description",
                output_format="JSON",
            )

            # Act
            created_intent = await create_intent(request)

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], IntentCreatedEvent)
            assert published_events[0].intent_id == created_intent.id
            assert published_events[0].name == "Event Test Intent"
            assert published_events[0].description == "Test description"
            assert published_events[0].output_format == "JSON"

    @pytest.mark.asyncio
    async def test_intent_updated_event_published_integration(self):
        """Test that IntentUpdatedEvent is published when updating intent."""
        # Arrange
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("intent.updated", capture_event)

        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", event_bus):
            intent = create_test_intent(id=None, name="Test Intent")
            created = await repo.create(intent)

            # Act
            await update_intent_name(created.id, "Updated Name")

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], IntentUpdatedEvent)
            assert published_events[0].intent_id == created.id
            assert published_events[0].field_updated == "name"

    @pytest.mark.asyncio
    async def test_fact_added_event_published_integration(self):
        """Test that FactAddedEvent is published when adding fact."""
        # Arrange
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("fact.added", capture_event)

        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", event_bus):
            intent = create_test_intent(id=None, name="Test Intent")
            created_intent = await repo.create(intent)

            # Act
            fact = await add_fact_to_intent(created_intent.id, "Test fact")

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], FactAddedEvent)
            assert published_events[0].intent_id == created_intent.id
            assert published_events[0].fact_id == fact.id
            assert published_events[0].value == "Test fact"

    @pytest.mark.asyncio
    async def test_fact_updated_event_published_integration(self):
        """Test that FactUpdatedEvent is published when updating fact."""
        # Arrange
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("fact.updated", capture_event)

        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", event_bus):
            intent = create_test_intent(id=None, name="Test Intent")
            created_intent = await repo.create(intent)
            fact = await add_fact_to_intent(created_intent.id, "Original value")

            # Act
            await update_fact_value(created_intent.id, fact.id, "Updated value")

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], FactUpdatedEvent)
            assert published_events[0].intent_id == created_intent.id
            assert published_events[0].fact_id == fact.id

    @pytest.mark.asyncio
    async def test_fact_removed_event_published_integration(self):
        """Test that FactRemovedEvent is published when removing fact."""
        # Arrange
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("fact.removed", capture_event)

        repo = IntentRepository()
        with patch("app.intents.service.intent_repository", repo), patch("app.intents.service.event_bus", event_bus):
            intent = create_test_intent(id=None, name="Test Intent")
            created_intent = await repo.create(intent)
            fact = await add_fact_to_intent(created_intent.id, "To remove")

            # Act
            await remove_fact_from_intent(created_intent.id, fact.id)

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], FactRemovedEvent)
            assert published_events[0].intent_id == created_intent.id
            assert published_events[0].fact_id == fact.id

