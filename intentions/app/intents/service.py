"""
Service layer for intents domain (V2).

Contains business logic and serves as the public API for this domain.
"""

from typing import List, Optional

from app.shared.events import event_bus
from app.shared.logging_config import logger

from .events import (
    InsightCreatedEvent,
    IntentArticulationUpdatedEvent,
    IntentCreatedEvent,
    IntentDeletedEvent,
    IntentUpdatedEvent,
    OutputCreatedEvent,
    PromptCreatedEvent,
)
from .models import Aspect, Assumption, Choice, Input, Insight, Intent, Output, Pitfall, Prompt, Quality
from .repository import IntentRepository
from .schemas import (
    AspectCreate,
    AssumptionCreate,
    ChoiceCreate,
    InputCreate,
    InsightCreateRequest,
    IntentArticulationUpdateRequest,
    IntentCreateRequest,
    OutputCreateRequest,
    PitfallCreate,
    PromptCreateRequest,
    QualityCreate,
)


def _create_aspect_domain(intent_id: int, dto: AspectCreate) -> Aspect:
    return Aspect(id=None, intent_id=intent_id, name=dto.name, description=dto.description)


def _create_input_domain(intent_id: int, dto: InputCreate) -> Input:
    return Input(
        id=None,
        intent_id=intent_id,
        name=dto.name,
        description=dto.description,
        aspect_id=dto.aspect_id,
        format=dto.format,
        required=dto.required,
    )


def _create_choice_domain(intent_id: int, dto: ChoiceCreate) -> Choice:
    return Choice(
        id=None,
        intent_id=intent_id,
        name=dto.name,
        description=dto.description,
        aspect_id=dto.aspect_id,
        options=dto.options,
        selected_option=dto.selected_option,
        rationale=dto.rationale,
    )


def _create_pitfall_domain(intent_id: int, dto: PitfallCreate) -> Pitfall:
    return Pitfall(
        id=None,
        intent_id=intent_id,
        description=dto.description,
        aspect_id=dto.aspect_id,
        mitigation=dto.mitigation,
    )


def _create_assumption_domain(intent_id: int, dto: AssumptionCreate) -> Assumption:
    return Assumption(
        id=None,
        intent_id=intent_id,
        description=dto.description,
        aspect_id=dto.aspect_id,
        confidence=dto.confidence,
    )


def _create_quality_domain(intent_id: int, dto: QualityCreate) -> Quality:
    return Quality(
        id=None,
        intent_id=intent_id,
        criterion=dto.criterion,
        aspect_id=dto.aspect_id,
        measurement=dto.measurement,
        priority=dto.priority,
    )


async def create_intent(request: IntentCreateRequest, repository: IntentRepository) -> Intent:
    """Create a new intent (V2) with optional articulation (aspects, inputs, etc.)."""
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
    intent_id = created_intent.id

    for dto in request.aspects or []:
        await repository.add_aspect(intent_id, _create_aspect_domain(intent_id, dto))
    for dto in request.inputs or []:
        await repository.add_input(intent_id, _create_input_domain(intent_id, dto))
    for dto in request.choices or []:
        await repository.add_choice(intent_id, _create_choice_domain(intent_id, dto))
    for dto in request.pitfalls or []:
        await repository.add_pitfall(intent_id, _create_pitfall_domain(intent_id, dto))
    for dto in request.assumptions or []:
        await repository.add_assumption(intent_id, _create_assumption_domain(intent_id, dto))
    for dto in request.qualities or []:
        await repository.add_quality(intent_id, _create_quality_domain(intent_id, dto))

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
    return await repository.find_by_id(intent_id)


async def list_intents(repository: IntentRepository) -> List[Intent]:
    """List all intents with full composition."""
    logger.info("Listing all intents")
    return await repository.list_all()


async def delete_intent(intent_id: int, repository: IntentRepository) -> bool:
    """Delete an intent by ID. Returns True if deleted."""
    logger.info("Deleting intent", extra={"intent_id": intent_id})
    existing = await repository.find_by_id(intent_id)
    if not existing:
        logger.warning("Intent not found for delete", extra={"intent_id": intent_id})
        return False
    deleted = await repository.delete(intent_id)
    if deleted:
        await event_bus.publish(IntentDeletedEvent(intent_id=intent_id))
        logger.info("Intent deleted successfully", extra={"intent_id": intent_id})
    return deleted


async def get_intent(intent_id: int, repository: IntentRepository) -> Optional[Intent]:
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


async def update_intent_name(intent_id: int, name: str, repository: IntentRepository) -> Optional[Intent]:
    """Update an intent's name."""
    logger.info("Updating intent name", extra={"intent_id": intent_id})
    return await _update_intent_field(intent_id, "name", lambda i: setattr(i, "name", name), repository)


async def update_intent_description(intent_id: int, description: str, repository: IntentRepository) -> Optional[Intent]:
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
        await event_bus.publish(IntentUpdatedEvent(intent_id=intent_id, field_updated=field_name))
        logger.info(
            "Intent updated successfully",
            extra={"intent_id": intent_id, "field": field_name},
        )
    return updated


async def update_intent_articulation(
    intent_id: int,
    payload: IntentArticulationUpdateRequest,
    repository: IntentRepository,
) -> Optional[Intent]:
    """Update the articulation composition for an intent.

    Intent owns all articulation entities; aspect_id on them is optional (discovered-for).
    Omitted fields leave existing data unchanged; empty list clears that entity type.
    You may supply any subset (e.g. only aspects, or only qualities). When aspects are
    replaced, articulation entities that referenced a removed aspect get aspect_id set
    to NULL by the DB (ON DELETE SET NULL); the entities remain.
    In a single request, aspect_id in inputs/choices/etc. can only reference existing
    aspect IDs (before this update); newly created aspects get IDs after the call.
    Delete order: articulation entities first (when replacing them), then aspects.
    """
    existing = await repository.find_by_id(intent_id)
    if not existing:
        logger.warning("Intent not found for articulation update", extra={"intent_id": intent_id})
        return None

    # Replace only the entity types that were supplied. Articulation entities are owned by intent; aspect_id is optional.
    if payload.inputs is not None:
        for i in existing.inputs:
            await repository.delete_input(intent_id, i.id)
        for dto in payload.inputs:
            await repository.add_input(intent_id, _create_input_domain(intent_id, dto))
    if payload.choices is not None:
        for c in existing.choices:
            await repository.delete_choice(intent_id, c.id)
        for dto in payload.choices:
            await repository.add_choice(intent_id, _create_choice_domain(intent_id, dto))
    if payload.pitfalls is not None:
        for p in existing.pitfalls:
            await repository.delete_pitfall(intent_id, p.id)
        for dto in payload.pitfalls:
            await repository.add_pitfall(intent_id, _create_pitfall_domain(intent_id, dto))
    if payload.assumptions is not None:
        for a in existing.assumptions:
            await repository.delete_assumption(intent_id, a.id)
        for dto in payload.assumptions:
            await repository.add_assumption(intent_id, _create_assumption_domain(intent_id, dto))
    if payload.qualities is not None:
        for q in existing.qualities:
            await repository.delete_quality(intent_id, q.id)
        for dto in payload.qualities:
            await repository.add_quality(intent_id, _create_quality_domain(intent_id, dto))
    if payload.aspects is not None:
        for a in existing.aspects:
            await repository.delete_aspect(intent_id, a.id)
        for dto in payload.aspects:
            await repository.add_aspect(intent_id, _create_aspect_domain(intent_id, dto))

    await event_bus.publish(IntentArticulationUpdatedEvent(intent_id=intent_id))
    logger.info("Intent articulation updated", extra={"intent_id": intent_id})
    return await repository.find_by_id(intent_id)


async def add_prompt(
    intent_id: int,
    request: PromptCreateRequest,
    repository: IntentRepository,
) -> Optional[Prompt]:
    """Add a prompt to an intent. Returns the created prompt or None if intent not found."""
    existing = await repository.find_by_id(intent_id)
    if not existing:
        logger.warning("Intent not found for add_prompt", extra={"intent_id": intent_id})
        return None
    version = await repository.get_next_prompt_version(intent_id)
    prompt = Prompt(id=None, intent_id=intent_id, content=request.content, version=version)
    created = await repository.add_prompt(intent_id, prompt)
    await event_bus.publish(PromptCreatedEvent(intent_id=intent_id, prompt_id=created.id, version=created.version))
    logger.info("Prompt added", extra={"intent_id": intent_id, "prompt_id": created.id})
    return created


async def add_output(
    prompt_id: int,
    request: OutputCreateRequest,
    repository: IntentRepository,
) -> Optional[Output]:
    """Add an output to a prompt. Returns the created output or None if prompt not found."""
    output = Output(id=None, prompt_id=prompt_id, content=request.content)
    try:
        created = await repository.add_output(prompt_id, output)
    except ValueError:
        logger.warning("Prompt not found for add_output", extra={"prompt_id": prompt_id})
        return None
    await event_bus.publish(OutputCreatedEvent(prompt_id=prompt_id, output_id=created.id))
    logger.info("Output added", extra={"prompt_id": prompt_id, "output_id": created.id})
    return created


async def add_insight(
    intent_id: int,
    request: InsightCreateRequest,
    repository: IntentRepository,
) -> Optional[Insight]:
    """Add an insight to an intent. Returns the created insight or None if intent not found.
    Validates source_prompt_id, source_output_id, source_assumption_id when provided.
    """
    existing = await repository.find_by_id(intent_id)
    if not existing:
        logger.warning("Intent not found for add_insight", extra={"intent_id": intent_id})
        return None

    if request.source_prompt_id is not None:
        prompt = await repository.find_prompt_by_id(intent_id, request.source_prompt_id)
        if prompt is None:
            raise ValueError(f"source_prompt_id {request.source_prompt_id} not found or does not belong to intent")
    if request.source_assumption_id is not None:
        assumption = await repository.find_assumption_by_id(intent_id, request.source_assumption_id)
        if assumption is None:
            raise ValueError(f"source_assumption_id {request.source_assumption_id} not found or does not belong to intent")
    if request.source_output_id is not None:
        output_prompt_id = await repository.get_prompt_id_for_output(request.source_output_id)
        if output_prompt_id is None:
            raise ValueError(f"source_output_id {request.source_output_id} not found")
        intent_prompt_ids = [p.id for p in existing.prompts]
        if output_prompt_id not in intent_prompt_ids:
            raise ValueError(f"source_output_id {request.source_output_id} does not belong to this intent")

    insight = Insight(
        id=None,
        intent_id=intent_id,
        content=request.content,
        source_type=request.source_type,
        source_output_id=request.source_output_id,
        source_prompt_id=request.source_prompt_id,
        source_assumption_id=request.source_assumption_id,
        status=request.status,
    )
    created = await repository.add_insight(intent_id, insight)
    await event_bus.publish(InsightCreatedEvent(intent_id=intent_id, insight_id=created.id))
    logger.info("Insight added", extra={"intent_id": intent_id, "insight_id": created.id})
    return created
