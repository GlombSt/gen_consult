"""
Service layer for intents domain (V2).

Contains business logic and serves as the public API for this domain.
"""

from typing import Optional

from app.shared.events import event_bus
from app.shared.logging_config import logger

from .events import IntentCreatedEvent, IntentUpdatedEvent
from .models import Intent
from .repository import IntentRepository
from .schemas import IntentCreateRequest


async def create_intent(
    request: IntentCreateRequest, repository: IntentRepository
) -> Intent:
    """Create a new intent (V2)."""
    logger.info(
        "Creating new intent",
        extra={"intent_name": request.name},
    )
    intent = Intent(
        id=None,
        name=request.name,
        description=request.description,
    )
    created_intent = await repository.create(intent)
    assert created_intent.id is not None, "Intent ID should be set after creation"
    await event_bus.publish(
        IntentCreatedEvent(
            intent_id=created_intent.id,
            name=created_intent.name,
            description=created_intent.description,
        )
    )
    logger.info(
        "Intent created successfully",
        extra={"intent_id": created_intent.id, "intent_name": created_intent.name},
    )
    return created_intent


async def get_intent(
    intent_id: int, repository: IntentRepository
) -> Optional[Intent]:
    """Get a specific intent by ID."""
    logger.info("Looking for intent", extra={"intent_id": intent_id})
    intent = await repository.find_by_id(intent_id)
    if intent:
        logger.info(
            "Intent found",
            extra={"intent_id": intent_id, "intent_name": intent.name},
        )
    else:
        logger.warning("Intent not found", extra={"intent_id": intent_id})
    return intent


async def update_intent_name(
    intent_id: int, name: str, repository: IntentRepository
) -> Optional[Intent]:
    """Update an intent's name."""
    logger.info("Updating intent name", extra={"intent_id": intent_id})
    return await _update_intent_field(
        intent_id, "name", lambda i: setattr(i, "name", name), repository
    )


async def update_intent_description(
    intent_id: int, description: str, repository: IntentRepository
) -> Optional[Intent]:
    """Update an intent's description."""
    logger.info("Updating intent description", extra={"intent_id": intent_id})
    return await _update_intent_field(
        intent_id,
        "description",
        lambda i: setattr(i, "description", description),
        repository,
    )


async def _update_intent_field(
    intent_id: int,
    field_name: str,
    update_func,
    repository: IntentRepository,
) -> Optional[Intent]:
    existing = await repository.find_by_id(intent_id)
    if not existing:
        logger.warning("Intent not found for update", extra={"intent_id": intent_id})
        return None
    update_func(existing)
    updated = await repository.update(intent_id, existing)
    if updated:
        await event_bus.publish(
            IntentUpdatedEvent(intent_id=intent_id, field_updated=field_name)
        )
        logger.info(
            "Intent updated successfully",
            extra={"intent_id": intent_id, "field": field_name},
        )
    return updated
