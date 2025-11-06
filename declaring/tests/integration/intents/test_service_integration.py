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
from app.shared.events import EventBus


@pytest.mark.integration
class TestIntentServiceIntegration:
    """Test intents service with real repository."""

    @pytest.mark.asyncio
    async def test_create_intent_integration(self, test_db_session):
        """Test creating an intent end-to-end."""
        # Arrange
        request = IntentCreateRequest(
            name="Integration Test Intent",
            description="Test description",
            output_format="JSON",
        )
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            # Act
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Assert
            assert created_intent.id is not None
            assert created_intent.name == "Integration Test Intent"
            assert created_intent.description == "Test description"
            assert created_intent.output_format == "JSON"

            # Verify persistence
            retrieved = await get_intent(created_intent.id, repository=repository)
            assert retrieved is not None
            assert retrieved.id == created_intent.id
            assert retrieved.name == "Integration Test Intent"

    @pytest.mark.asyncio
    async def test_create_and_get_intent_integration(self, test_db_session):
        """Test creating and retrieving an intent end-to-end."""
        # Arrange
        request = IntentCreateRequest(
            name="Test Intent",
            description="Test description",
            output_format="plain text",
        )
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            # Act - Create
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act - Get
            retrieved_intent = await get_intent(created_intent.id, repository=repository)

            # Assert
            assert retrieved_intent is not None
            assert retrieved_intent.id == created_intent.id
            assert retrieved_intent.name == "Test Intent"
            assert retrieved_intent.description == "Test description"
            assert retrieved_intent.output_format == "plain text"

    @pytest.mark.asyncio
    async def test_get_intent_integration(self, test_db_session):
        """Test getting an intent by ID end-to-end."""
        # Arrange
        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="plain text")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            # Create intent via service
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act
            retrieved = await get_intent(created.id, repository=repository)

            # Assert
            assert retrieved is not None
            assert retrieved.id == created.id
            assert retrieved.name == "Test Intent"
            assert retrieved.description == "Test description"
            assert retrieved.output_format == "plain text"

    @pytest.mark.asyncio
    async def test_update_intent_name_integration(self, test_db_session):
        """Test updating intent name end-to-end."""
        # Arrange
        request = IntentCreateRequest(name="Original Name", description="Test description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act
            updated = await update_intent_name(created.id, "Updated Name", repository=repository)
            await test_db_session.commit()

            # Assert
            assert updated is not None
            assert updated.name == "Updated Name"
            assert updated.id == created.id

            # Verify persistence
            retrieved = await get_intent(created.id, repository=repository)
            assert retrieved is not None
            assert retrieved.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_intent_description_integration(self, test_db_session):
        """Test updating intent description end-to-end."""
        # Arrange
        request = IntentCreateRequest(name="Test Intent", description="Original description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act
            updated = await update_intent_description(created.id, "Updated description", repository=repository)
            await test_db_session.commit()

            # Assert
            assert updated is not None
            assert updated.description == "Updated description"

            # Verify persistence
            retrieved = await get_intent(created.id, repository=repository)
            assert retrieved.description == "Updated description"

    @pytest.mark.asyncio
    async def test_update_intent_output_format_integration(self, test_db_session):
        """Test updating intent output format end-to-end."""
        # Arrange
        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="plain text")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act
            updated = await update_intent_output_format(created.id, "JSON", repository=repository)
            await test_db_session.commit()

            # Assert
            assert updated is not None
            assert updated.output_format == "JSON"

            # Verify persistence
            retrieved = await get_intent(created.id, repository=repository)
            assert retrieved.output_format == "JSON"

    @pytest.mark.asyncio
    async def test_update_intent_output_structure_integration(self, test_db_session):
        """Test updating intent output structure end-to-end."""
        # Arrange
        with patch("app.intents.service.event_bus", EventBus()):
            request = IntentCreateRequest(
                name="Test Intent", description="Test description", output_format="JSON", output_structure="Old structure"
            )
            repository = IntentRepository(test_db_session)
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act
            repository = IntentRepository(test_db_session)
            updated = await update_intent_output_structure(created.id, "New structure", repository=repository)
            await test_db_session.commit()

            # Assert
            assert updated is not None
            assert updated.output_structure == "New structure"

            # Verify persistence
            repository = IntentRepository(test_db_session)
            retrieved = await get_intent(created.id, repository=repository)
            assert retrieved.output_structure == "New structure"

    @pytest.mark.asyncio
    async def test_update_intent_context_integration(self, test_db_session):
        """Test updating intent context end-to-end."""
        # Arrange
        with patch("app.intents.service.event_bus", EventBus()):
            request = IntentCreateRequest(
                name="Test Intent", description="Test description", output_format="JSON", context="Old context"
            )
            repository = IntentRepository(test_db_session)
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act
            repository = IntentRepository(test_db_session)
            updated = await update_intent_context(created.id, "New context", repository=repository)
            await test_db_session.commit()

            # Assert
            assert updated is not None
            assert updated.context == "New context"

            # Verify persistence
            repository = IntentRepository(test_db_session)
            retrieved = await get_intent(created.id, repository=repository)
            assert retrieved.context == "New context"

    @pytest.mark.asyncio
    async def test_update_intent_constraints_integration(self, test_db_session):
        """Test updating intent constraints end-to-end."""
        # Arrange
        with patch("app.intents.service.event_bus", EventBus()):
            request = IntentCreateRequest(
                name="Test Intent", description="Test description", output_format="JSON", constraints="Old constraints"
            )
            repository = IntentRepository(test_db_session)
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act
            repository = IntentRepository(test_db_session)
            updated = await update_intent_constraints(created.id, "New constraints", repository=repository)
            await test_db_session.commit()

            # Assert
            assert updated is not None
            assert updated.constraints == "New constraints"

            # Verify persistence
            repository = IntentRepository(test_db_session)
            retrieved = await get_intent(created.id, repository=repository)
            assert retrieved.constraints == "New constraints"

    @pytest.mark.asyncio
    async def test_multiple_field_updates_integration(self, test_db_session):
        """Test updating multiple fields of an intent."""
        # Arrange
        with patch("app.intents.service.event_bus", EventBus()):
            request = IntentCreateRequest(name="Original", description="Test description", output_format="JSON")
            repository = IntentRepository(test_db_session)
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act - Update multiple fields
            repository = IntentRepository(test_db_session)
            await update_intent_name(created.id, "Updated Name", repository=repository)
            await test_db_session.commit()
            repository = IntentRepository(test_db_session)
            await update_intent_description(created.id, "Updated Description", repository=repository)
            await test_db_session.commit()
            repository = IntentRepository(test_db_session)
            await update_intent_output_format(created.id, "JSON", repository=repository)
            await test_db_session.commit()

            # Assert
            repository = IntentRepository(test_db_session)
            retrieved = await get_intent(created.id, repository=repository)
            assert retrieved.name == "Updated Name"
            assert retrieved.description == "Updated Description"
            assert retrieved.output_format == "JSON"


@pytest.mark.integration
class TestFactServiceIntegration:
    """Test fact operations with real repository."""

    @pytest.mark.asyncio
    async def test_add_fact_to_intent_integration(self, test_db_session):
        """Test adding a fact to an intent end-to-end."""
        # Arrange
        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act
            fact = await add_fact_to_intent(created_intent.id, "Test fact value", repository=repository)
            await test_db_session.commit()

            # Assert
            assert fact is not None
            assert fact.intent_id == created_intent.id
            assert fact.value == "Test fact value"

            # Verify persistence
            # Get facts via repository
            facts = await repository.find_facts_by_intent_id(created_intent.id)
            assert len(facts) == 1
            assert facts[0].value == "Test fact value"

    @pytest.mark.asyncio
    async def test_update_fact_value_integration(self, test_db_session):
        """Test updating a fact value end-to-end."""
        # Arrange
        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()
            fact = await add_fact_to_intent(created_intent.id, "Original value", repository=repository)
            await test_db_session.commit()

            # Act
            updated = await update_fact_value(created_intent.id, fact.id, "Updated value", repository=repository)
            await test_db_session.commit()

            # Assert
            assert updated is not None
            assert updated.value == "Updated value"

            # Verify persistence
            # Get facts via repository
            facts = await repository.find_facts_by_intent_id(created_intent.id)
            retrieved_fact = next((f for f in facts if f.id == fact.id), None)
            assert retrieved_fact is not None
            assert retrieved_fact.value == "Updated value"

    @pytest.mark.asyncio
    async def test_remove_fact_from_intent_integration(self, test_db_session):
        """Test removing a fact from an intent end-to-end."""
        # Arrange
        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()
            fact = await add_fact_to_intent(created_intent.id, "To remove", repository=repository)
            await test_db_session.commit()

            # Act
            removed = await remove_fact_from_intent(created_intent.id, fact.id, repository=repository)
            await test_db_session.commit()

            # Assert
            assert removed is True

            # Verify fact is removed
            facts = await repository.find_facts_by_intent_id(created_intent.id)
            retrieved_fact = next((f for f in facts if f.id == fact.id), None)
            assert retrieved_fact is None

    @pytest.mark.asyncio
    async def test_multiple_facts_integration(self, test_db_session):
        """Test adding multiple facts to an intent."""
        # Arrange
        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act - Add multiple facts
            await add_fact_to_intent(created_intent.id, "Fact 1", repository=repository)
            await test_db_session.commit()
            await add_fact_to_intent(created_intent.id, "Fact 2", repository=repository)
            await test_db_session.commit()
            await add_fact_to_intent(created_intent.id, "Fact 3", repository=repository)
            await test_db_session.commit()

            # Assert
            # Get facts via repository
            facts = await repository.find_facts_by_intent_id(created_intent.id)
            assert len(facts) == 3
            assert any(f.value == "Fact 1" for f in facts)
            assert any(f.value == "Fact 2" for f in facts)
            assert any(f.value == "Fact 3" for f in facts)

    @pytest.mark.asyncio
    async def test_fact_operations_with_intent_updates_integration(self, test_db_session):
        """Test fact operations combined with intent updates."""
        # Arrange
        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act - Add fact, update intent, update fact
            fact = await add_fact_to_intent(created_intent.id, "Original fact", repository=repository)
            await test_db_session.commit()
            await update_intent_name(created_intent.id, "Updated Intent", repository=repository)
            await test_db_session.commit()
            await update_fact_value(created_intent.id, fact.id, "Updated fact", repository=repository)
            await test_db_session.commit()

            # Assert
            retrieved_intent = await get_intent(created_intent.id, repository=repository)
            assert retrieved_intent.name == "Updated Intent"

            # Get facts via repository
            facts = await repository.find_facts_by_intent_id(created_intent.id)
            retrieved_fact = next((f for f in facts if f.id == fact.id), None)
            assert retrieved_fact is not None
            assert retrieved_fact.value == "Updated fact"


@pytest.mark.integration
class TestEventPublishingIntegration:
    """Test event publishing with real repository."""

    @pytest.mark.asyncio
    async def test_intent_created_event_published_integration(self, test_db_session):
        """Test that IntentCreatedEvent is published when creating intent."""
        # Arrange
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("intent.created", capture_event)

        request = IntentCreateRequest(
            name="Event Test Intent",
            description="Test description",
            output_format="JSON",
        )
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", event_bus):
            # Act
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], IntentCreatedEvent)
            assert published_events[0].intent_id == created_intent.id
            assert published_events[0].name == "Event Test Intent"
            assert published_events[0].description == "Test description"
            assert published_events[0].output_format == "JSON"

    @pytest.mark.asyncio
    async def test_intent_updated_event_published_integration(self, test_db_session):
        """Test that IntentUpdatedEvent is published when updating intent."""
        # Arrange
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("intent.updated", capture_event)

        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", event_bus):
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act
            await update_intent_name(created.id, "Updated Name", repository=repository)
            await test_db_session.commit()

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], IntentUpdatedEvent)
            assert published_events[0].intent_id == created.id
            assert published_events[0].field_updated == "name"

    @pytest.mark.asyncio
    async def test_fact_added_event_published_integration(self, test_db_session):
        """Test that FactAddedEvent is published when adding fact."""
        # Arrange
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("fact.added", capture_event)

        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", event_bus):
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()

            # Act
            fact = await add_fact_to_intent(created_intent.id, "Test fact", repository=repository)
            await test_db_session.commit()

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], FactAddedEvent)
            assert published_events[0].intent_id == created_intent.id
            assert published_events[0].fact_id == fact.id
            assert published_events[0].value == "Test fact"

    @pytest.mark.asyncio
    async def test_fact_updated_event_published_integration(self, test_db_session):
        """Test that FactUpdatedEvent is published when updating fact."""
        # Arrange
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("fact.updated", capture_event)

        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", event_bus):
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()
            fact = await add_fact_to_intent(created_intent.id, "Original value", repository=repository)
            await test_db_session.commit()

            # Act
            await update_fact_value(created_intent.id, fact.id, "Updated value", repository=repository)
            await test_db_session.commit()

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], FactUpdatedEvent)
            assert published_events[0].intent_id == created_intent.id
            assert published_events[0].fact_id == fact.id

    @pytest.mark.asyncio
    async def test_fact_removed_event_published_integration(self, test_db_session):
        """Test that FactRemovedEvent is published when removing fact."""
        # Arrange
        event_bus = EventBus()
        published_events = []

        async def capture_event(event):
            published_events.append(event)

        event_bus.subscribe("fact.removed", capture_event)

        request = IntentCreateRequest(name="Test Intent", description="Test description", output_format="JSON")
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", event_bus):
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()
            fact = await add_fact_to_intent(created_intent.id, "To remove", repository=repository)
            await test_db_session.commit()

            # Act
            await remove_fact_from_intent(created_intent.id, fact.id, repository=repository)
            await test_db_session.commit()

            # Assert
            assert len(published_events) == 1
            assert isinstance(published_events[0], FactRemovedEvent)
            assert published_events[0].intent_id == created_intent.id
            assert published_events[0].fact_id == fact.id
