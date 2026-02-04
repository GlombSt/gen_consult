"""
Integration tests for intents service with real repository (V2).

Tests service + repository integration without mocks.
"""

from unittest.mock import patch

import pytest

from app.intents.events import IntentCreatedEvent, IntentUpdatedEvent
from app.intents.repository import IntentRepository
from app.intents.schemas import IntentCreateRequest
from app.intents.service import (
    create_intent,
    get_intent,
    update_intent_description,
    update_intent_name,
)
from app.shared.events import EventBus


@pytest.mark.integration
class TestIntentServiceIntegration:
    """Test intents service with real repository (V2)."""

    @pytest.mark.asyncio
    async def test_create_intent_integration(self, test_db_session):
        """Test creating an intent end-to-end."""
        request = IntentCreateRequest(
            name="Integration Test Intent",
            description="Test description",
        )
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()

            assert created_intent.id is not None
            assert created_intent.name == "Integration Test Intent"
            assert created_intent.description == "Test description"

            retrieved = await get_intent(
                created_intent.id, repository=repository
            )
            assert retrieved is not None
            assert retrieved.id == created_intent.id
            assert retrieved.name == "Integration Test Intent"

    @pytest.mark.asyncio
    async def test_create_and_get_intent_integration(self, test_db_session):
        """Test creating and retrieving an intent end-to-end."""
        request = IntentCreateRequest(
            name="Test Intent",
            description="Test description",
        )
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created_intent = await create_intent(request, repository=repository)
            await test_db_session.commit()

            retrieved_intent = await get_intent(
                created_intent.id, repository=repository
            )

            assert retrieved_intent is not None
            assert retrieved_intent.id == created_intent.id
            assert retrieved_intent.name == "Test Intent"
            assert retrieved_intent.description == "Test description"

    @pytest.mark.asyncio
    async def test_update_intent_name_integration(self, test_db_session):
        """Test updating intent name end-to-end."""
        request = IntentCreateRequest(
            name="Original Name", description="Test description"
        )
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            updated = await update_intent_name(
                created.id, "Updated Name", repository=repository
            )
            await test_db_session.commit()

            assert updated is not None
            assert updated.name == "Updated Name"
            assert updated.id == created.id

            retrieved = await get_intent(created.id, repository=repository)
            assert retrieved is not None
            assert retrieved.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_intent_description_integration(self, test_db_session):
        """Test updating intent description end-to-end."""
        request = IntentCreateRequest(
            name="Test Intent", description="Original description"
        )
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            updated = await update_intent_description(
                created.id, "Updated description", repository=repository
            )
            await test_db_session.commit()

            assert updated is not None
            assert updated.description == "Updated description"

            retrieved = await get_intent(created.id, repository=repository)
            assert retrieved.description == "Updated description"

    @pytest.mark.asyncio
    async def test_intent_created_event_published(self, test_db_session):
        """Test that IntentCreatedEvent is published when creating intent."""
        request = IntentCreateRequest(
            name="Event Test Intent",
            description="Test description",
        )
        repository = IntentRepository(test_db_session)
        event_bus = EventBus()
        published_events = []

        async def capture(event):
            published_events.append(event)

        event_bus.subscribe(capture)

        with patch("app.intents.service.event_bus", event_bus):
            await create_intent(request, repository=repository)
            await test_db_session.commit()

        assert len(published_events) == 1
        assert isinstance(published_events[0], IntentCreatedEvent)
        assert published_events[0].name == "Event Test Intent"

    @pytest.mark.asyncio
    async def test_intent_updated_event_published(self, test_db_session):
        """Test that IntentUpdatedEvent is published when updating intent."""
        request = IntentCreateRequest(
            name="Test Intent", description="Test description"
        )
        repository = IntentRepository(test_db_session)
        event_bus = EventBus()
        published_events = []

        async def capture(event):
            published_events.append(event)

        event_bus.subscribe(capture)

        with patch("app.intents.service.event_bus", event_bus):
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()
            await update_intent_name(
                created.id, "Updated Intent", repository=repository
            )
            await test_db_session.commit()

        assert len(published_events) >= 2
        assert isinstance(published_events[1], IntentUpdatedEvent)


@pytest.mark.integration
class TestAspectRepositoryIntegration:
    """Test adding aspects to an intent (V2)."""

    @pytest.mark.asyncio
    async def test_add_aspect_to_intent_integration(self, test_db_session):
        """Test adding an aspect to an intent end-to-end."""
        from app.intents.models import Aspect

        request = IntentCreateRequest(
            name="Test Intent", description="Test description"
        )
        repository = IntentRepository(test_db_session)

        with patch("app.intents.service.event_bus", EventBus()):
            created = await create_intent(request, repository=repository)
            await test_db_session.commit()

            aspect = Aspect(
                id=None,
                intent_id=created.id,
                name="SEO",
                description="Search engine optimization",
            )
            added = await repository.add_aspect(created.id, aspect)
            await test_db_session.commit()

            assert added.id is not None
            assert added.name == "SEO"

            retrieved = await repository.find_by_id(created.id)
            assert len(retrieved.aspects) == 1
            assert retrieved.aspects[0].name == "SEO"
