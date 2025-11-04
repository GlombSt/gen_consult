"""
Service layer for intents domain.

Contains business logic and serves as the public API for this domain.
"""

from typing import List, Optional

from app.shared.events import event_bus
from app.shared.logging_config import logger

from .events import (
    FactAddedEvent,
    FactRemovedEvent,
    FactUpdatedEvent,
    IntentCreatedEvent,
    IntentDeletedEvent,
    IntentUpdatedEvent,
)
from .models import Fact, Intent
from .repository import intent_repository
from .schemas import IntentCreateRequest


async def create_intent(request: IntentCreateRequest) -> Intent:
    """
    Create a new intent (US-000).

    Args:
        request: Intent creation request

    Returns:
        Created intent
    """
    logger.info(
        "Creating new intent",
        extra={
            "intent_name": request.name,
            "output_format": request.output_format,
        },
    )

    # Create domain model
    intent = Intent(
        id=None,
        name=request.name,
        description=request.description,
        output_format=request.output_format,
        output_structure=request.output_structure,
        context=request.context,
        constraints=request.constraints,
    )

    # Persist
    created_intent = await intent_repository.create(intent)

    # Publish domain event (MANDATORY)
    await event_bus.publish(
        IntentCreatedEvent(
            intent_id=created_intent.id,
            name=created_intent.name,
            description=created_intent.description,
            output_format=created_intent.output_format,
        )
    )

    logger.info(
        "Intent created successfully",
        extra={"intent_id": created_intent.id, "intent_name": created_intent.name}
    )

    return created_intent


async def get_all_intents() -> List[Intent]:
    """
    Get all intents.

    Returns:
        List of all intents
    """
    logger.info("Fetching all intents")
    intents = await intent_repository.find_all()
    logger.info("Intents fetched", extra={"total_intents": len(intents)})
    return intents


async def get_intent(intent_id: int) -> Optional[Intent]:
    """
    Get a specific intent by ID.

    Args:
        intent_id: The intent ID

    Returns:
        Intent if found, None otherwise
    """
    logger.info("Looking for intent", extra={"intent_id": intent_id})
    intent = await intent_repository.find_by_id(intent_id)

    if intent:
        logger.info("Intent found", extra={"intent_id": intent_id, "intent_name": intent.name})
    else:
        logger.warning("Intent not found", extra={"intent_id": intent_id})

    return intent


async def update_intent_name(intent_id: int, name: str) -> Optional[Intent]:
    """
    Update an intent's name (US-001).

    Args:
        intent_id: The intent ID to update
        name: New name value

    Returns:
        Updated intent if found, None otherwise
    """
    logger.info("Updating intent name", extra={"intent_id": intent_id})
    return await _update_intent_field(intent_id, "name", lambda intent: setattr(intent, "name", name))


async def update_intent_description(intent_id: int, description: str) -> Optional[Intent]:
    """
    Update an intent's description (US-002).

    Args:
        intent_id: The intent ID to update
        description: New description value

    Returns:
        Updated intent if found, None otherwise
    """
    logger.info("Updating intent description", extra={"intent_id": intent_id})
    return await _update_intent_field(intent_id, "description", lambda intent: setattr(intent, "description", description))


async def update_intent_output_format(intent_id: int, output_format: str) -> Optional[Intent]:
    """
    Update an intent's output format (US-003).

    Args:
        intent_id: The intent ID to update
        output_format: New output format value

    Returns:
        Updated intent if found, None otherwise
    """
    logger.info("Updating intent output format", extra={"intent_id": intent_id})
    return await _update_intent_field(intent_id, "output_format", lambda intent: setattr(intent, "output_format", output_format))


async def update_intent_output_structure(intent_id: int, output_structure: Optional[str]) -> Optional[Intent]:
    """
    Update an intent's output structure (US-004).

    Args:
        intent_id: The intent ID to update
        output_structure: New output structure value (can be None)

    Returns:
        Updated intent if found, None otherwise
    """
    logger.info("Updating intent output structure", extra={"intent_id": intent_id})
    return await _update_intent_field(intent_id, "output_structure", lambda intent: setattr(intent, "output_structure", output_structure))


async def update_intent_context(intent_id: int, context: Optional[str]) -> Optional[Intent]:
    """
    Update an intent's context (US-005).

    Args:
        intent_id: The intent ID to update
        context: New context value (can be None)

    Returns:
        Updated intent if found, None otherwise
    """
    logger.info("Updating intent context", extra={"intent_id": intent_id})
    return await _update_intent_field(intent_id, "context", lambda intent: setattr(intent, "context", context))


async def update_intent_constraints(intent_id: int, constraints: Optional[str]) -> Optional[Intent]:
    """
    Update an intent's constraints (US-006).

    Args:
        intent_id: The intent ID to update
        constraints: New constraints value (can be None)

    Returns:
        Updated intent if found, None otherwise
    """
    logger.info("Updating intent constraints", extra={"intent_id": intent_id})
    return await _update_intent_field(intent_id, "constraints", lambda intent: setattr(intent, "constraints", constraints))


async def _update_intent_field(intent_id: int, field_name: str, update_func) -> Optional[Intent]:
    """
    Helper function to update an intent field.

    Args:
        intent_id: The intent ID to update
        field_name: Name of the field being updated (for event)
        update_func: Function to update the field

    Returns:
        Updated intent if found, None otherwise
    """
    # Get existing intent
    existing_intent = await intent_repository.find_by_id(intent_id)
    if not existing_intent:
        logger.warning("Intent not found for update", extra={"intent_id": intent_id})
        return None

    # Apply update
    update_func(existing_intent)

    # Persist
    updated_intent = await intent_repository.update(intent_id, existing_intent)

    # Publish domain event (MANDATORY)
    if updated_intent:
        await event_bus.publish(IntentUpdatedEvent(intent_id=intent_id, field_updated=field_name))
        logger.info("Intent updated successfully", extra={"intent_id": intent_id, "field": field_name})

    return updated_intent


async def add_fact_to_intent(intent_id: int, value: str) -> Optional[Fact]:
    """
    Add a new fact to an intent (US-008).

    Args:
        intent_id: The intent ID to add the fact to
        value: The fact value

    Returns:
        Created fact if intent exists, None otherwise
    """
    logger.info("Adding fact to intent", extra={"intent_id": intent_id, "fact_value": value})

    # Verify intent exists
    intent = await intent_repository.find_by_id(intent_id)
    if not intent:
        logger.warning("Intent not found for adding fact", extra={"intent_id": intent_id})
        return None

    # Create fact domain model
    fact = Fact(id=None, intent_id=intent_id, value=value)

    # Persist
    created_fact = await intent_repository.add_fact(intent_id, fact)

    # Publish domain event (MANDATORY)
    await event_bus.publish(
        FactAddedEvent(intent_id=intent_id, fact_id=created_fact.id, value=created_fact.value)
    )

    logger.info("Fact added successfully", extra={"intent_id": intent_id, "fact_id": created_fact.id})

    return created_fact


async def update_fact_value(intent_id: int, fact_id: int, value: str) -> Optional[Fact]:
    """
    Update a fact's value (US-007).

    Args:
        intent_id: The intent ID
        fact_id: The fact ID to update
        value: New fact value

    Returns:
        Updated fact if found, None otherwise
    """
    logger.info("Updating fact value", extra={"intent_id": intent_id, "fact_id": fact_id})

    # Verify intent exists
    intent = await intent_repository.find_by_id(intent_id)
    if not intent:
        logger.warning("Intent not found for updating fact", extra={"intent_id": intent_id})
        return None

    # Get existing fact
    existing_fact = await intent_repository.find_fact_by_id(intent_id, fact_id)
    if not existing_fact:
        logger.warning("Fact not found for update", extra={"intent_id": intent_id, "fact_id": fact_id})
        return None

    # Apply update
    existing_fact.value = value

    # Persist
    updated_fact = await intent_repository.update_fact(intent_id, fact_id, existing_fact)

    # Publish domain event (MANDATORY)
    if updated_fact:
        await event_bus.publish(FactUpdatedEvent(intent_id=intent_id, fact_id=fact_id))
        logger.info("Fact updated successfully", extra={"intent_id": intent_id, "fact_id": fact_id})

    return updated_fact


async def remove_fact_from_intent(intent_id: int, fact_id: int) -> bool:
    """
    Remove a fact from an intent (US-009).

    Args:
        intent_id: The intent ID
        fact_id: The fact ID to remove

    Returns:
        True if removed, False if not found
    """
    logger.info("Removing fact from intent", extra={"intent_id": intent_id, "fact_id": fact_id})

    # Verify intent exists
    intent = await intent_repository.find_by_id(intent_id)
    if not intent:
        logger.warning("Intent not found for removing fact", extra={"intent_id": intent_id})
        return False

    # Verify fact exists
    fact = await intent_repository.find_fact_by_id(intent_id, fact_id)
    if not fact:
        logger.warning("Fact not found for removal", extra={"intent_id": intent_id, "fact_id": fact_id})
        return False

    # Remove
    removed = await intent_repository.remove_fact(intent_id, fact_id)

    # Publish domain event (MANDATORY)
    if removed:
        await event_bus.publish(FactRemovedEvent(intent_id=intent_id, fact_id=fact_id))
        logger.info("Fact removed successfully", extra={"intent_id": intent_id, "fact_id": fact_id})

    return removed

