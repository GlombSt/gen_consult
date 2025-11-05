"""
HTTP router for intents domain.

Defines HTTP endpoints and handles request/response serialization.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db
from . import service
from .repository import IntentRepository
from .schemas import (
    FactAddRequest,
    FactResponse,
    FactUpdateValueRequest,
    IntentCreateRequest,
    IntentResponse,
    IntentUpdateConstraintsRequest,
    IntentUpdateContextRequest,
    IntentUpdateDescriptionRequest,
    IntentUpdateNameRequest,
    IntentUpdateOutputFormatRequest,
    IntentUpdateOutputStructureRequest,
)

router = APIRouter(
    prefix="/intents",
    tags=["intents"],
)


@router.post("", response_model=IntentResponse, status_code=status.HTTP_201_CREATED)
async def create_intent(request: IntentCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create a new intent (US-000)."""
    intent = await service.create_intent(request, db)

    # Get facts for this intent (will be empty for new intent)
    repository = IntentRepository(db)
    facts = await repository.find_facts_by_intent_id(intent.id)

    return _to_intent_response(intent, facts)


@router.get("", response_model=List[IntentResponse])
async def get_intents(db: AsyncSession = Depends(get_db)):
    """Get all intents."""
    intents = await service.get_all_intents(db)
    return [_to_intent_response(intent) for intent in intents]


@router.get("/{intent_id}", response_model=IntentResponse)
async def get_intent(
    intent_id: int = Path(..., description="The unique identifier of the intent to retrieve"),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific intent by ID (US-010)."""
    intent = await service.get_intent(intent_id, db)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    # Get facts for this intent
    repository = IntentRepository(db)
    facts = await repository.find_facts_by_intent_id(intent_id)

    return _to_intent_response(intent, facts)


@router.patch("/{intent_id}/name", response_model=IntentResponse)
async def update_intent_name(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateNameRequest = ...,
    db: AsyncSession = Depends(get_db),
):
    """Update an intent's name (US-001)."""
    intent = await service.update_intent_name(intent_id, request.name, db)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    # Get facts for this intent
    repository = IntentRepository(db)
    facts = await repository.find_facts_by_intent_id(intent_id)

    return _to_intent_response(intent, facts)


@router.patch("/{intent_id}/description", response_model=IntentResponse)
async def update_intent_description(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateDescriptionRequest = ...,
    db: AsyncSession = Depends(get_db),
):
    """Update an intent's description (US-002)."""
    intent = await service.update_intent_description(intent_id, request.description, db)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    # Get facts for this intent
    repository = IntentRepository(db)
    facts = await repository.find_facts_by_intent_id(intent_id)

    return _to_intent_response(intent, facts)


@router.patch("/{intent_id}/output-format", response_model=IntentResponse)
async def update_intent_output_format(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateOutputFormatRequest = ...,
    db: AsyncSession = Depends(get_db),
):
    """Update an intent's output format (US-003)."""
    intent = await service.update_intent_output_format(intent_id, request.output_format, db)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    # Get facts for this intent
    repository = IntentRepository(db)
    facts = await repository.find_facts_by_intent_id(intent_id)

    return _to_intent_response(intent, facts)


@router.patch("/{intent_id}/output-structure", response_model=IntentResponse)
async def update_intent_output_structure(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateOutputStructureRequest = ...,
    db: AsyncSession = Depends(get_db),
):
    """Update an intent's output structure (US-004)."""
    intent = await service.update_intent_output_structure(intent_id, request.output_structure, db)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    # Get facts for this intent
    repository = IntentRepository(db)
    facts = await repository.find_facts_by_intent_id(intent_id)

    return _to_intent_response(intent, facts)


@router.patch("/{intent_id}/context", response_model=IntentResponse)
async def update_intent_context(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateContextRequest = ...,
    db: AsyncSession = Depends(get_db),
):
    """Update an intent's context (US-005)."""
    intent = await service.update_intent_context(intent_id, request.context, db)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    # Get facts for this intent
    repository = IntentRepository(db)
    facts = await repository.find_facts_by_intent_id(intent_id)

    return _to_intent_response(intent, facts)


@router.patch("/{intent_id}/constraints", response_model=IntentResponse)
async def update_intent_constraints(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateConstraintsRequest = ...,
    db: AsyncSession = Depends(get_db),
):
    """Update an intent's constraints (US-006)."""
    intent = await service.update_intent_constraints(intent_id, request.constraints, db)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    # Get facts for this intent
    repository = IntentRepository(db)
    facts = await repository.find_facts_by_intent_id(intent_id)

    return _to_intent_response(intent, facts)


@router.post("/{intent_id}/facts", response_model=FactResponse, status_code=status.HTTP_201_CREATED)
async def add_fact_to_intent(
    intent_id: int = Path(..., description="The unique identifier of the intent to add the fact to"),
    request: FactAddRequest = ...,
    db: AsyncSession = Depends(get_db),
):
    """Add a new fact to an intent (US-008)."""
    fact = await service.add_fact_to_intent(intent_id, request.value, db)
    if not fact:
        raise HTTPException(status_code=404, detail="Intent not found")
    return _to_fact_response(fact)


@router.patch("/{intent_id}/facts/{fact_id}/value", response_model=FactResponse)
async def update_fact_value(
    intent_id: int = Path(..., description="The unique identifier of the intent that owns the fact"),
    fact_id: int = Path(..., description="The unique identifier of the fact to update"),
    request: FactUpdateValueRequest = ...,
    db: AsyncSession = Depends(get_db),
):
    """Update a fact's value (US-007)."""
    fact = await service.update_fact_value(intent_id, fact_id, request.value, db)
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")
    return _to_fact_response(fact)


@router.delete("/{intent_id}/facts/{fact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_fact_from_intent(
    intent_id: int = Path(..., description="The unique identifier of the intent that owns the fact"),
    fact_id: int = Path(..., description="The unique identifier of the fact to remove"),
    db: AsyncSession = Depends(get_db),
):
    """Remove a fact from an intent (US-009)."""
    removed = await service.remove_fact_from_intent(intent_id, fact_id, db)
    if not removed:
        raise HTTPException(status_code=404, detail="Fact not found")


def _to_intent_response(intent, facts=None) -> IntentResponse:
    """Convert domain model to response DTO."""
    if facts is None:
        facts = []
    return IntentResponse(
        id=intent.id,
        name=intent.name,
        description=intent.description,
        output_format=intent.output_format,
        output_structure=intent.output_structure,
        context=intent.context,
        constraints=intent.constraints,
        created_at=intent.created_at,
        updated_at=intent.updated_at,
        facts=[_to_fact_response(fact) for fact in facts],
    )


def _to_fact_response(fact) -> FactResponse:
    """Convert domain model to response DTO."""
    return FactResponse(
        id=fact.id,
        intent_id=fact.intent_id,
        value=fact.value,
        created_at=fact.created_at,
        updated_at=fact.updated_at,
    )
