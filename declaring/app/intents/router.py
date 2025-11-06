"""
HTTP router for intents domain.

Defines HTTP endpoints and handles request/response serialization.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.shared.dependencies import get_intent_repository

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
async def create_intent(request: IntentCreateRequest, repository: IntentRepository = Depends(get_intent_repository)):
    """Create a new intent (US-000)."""
    intent = await service.create_intent(request, repository)

    return _to_intent_response(intent)


@router.get("/{intent_id}", response_model=IntentResponse)
async def get_intent(
    intent_id: int = Path(..., description="The unique identifier of the intent to retrieve"),
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Get a specific intent by ID (US-010)."""
    intent = await service.get_intent(intent_id, repository)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    return _to_intent_response(intent)


@router.patch("/{intent_id}/name", response_model=IntentResponse)
async def update_intent_name(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateNameRequest = ...,
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Update an intent's name (US-001)."""
    intent = await service.update_intent_name(intent_id, request.name, repository)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    return _to_intent_response(intent)


@router.patch("/{intent_id}/description", response_model=IntentResponse)
async def update_intent_description(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateDescriptionRequest = ...,
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Update an intent's description (US-002)."""
    intent = await service.update_intent_description(intent_id, request.description, repository)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    return _to_intent_response(intent)


@router.patch("/{intent_id}/output-format", response_model=IntentResponse)
async def update_intent_output_format(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateOutputFormatRequest = ...,
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Update an intent's output format (US-003)."""
    intent = await service.update_intent_output_format(intent_id, request.output_format, repository)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    return _to_intent_response(intent)


@router.patch("/{intent_id}/output-structure", response_model=IntentResponse)
async def update_intent_output_structure(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateOutputStructureRequest = ...,
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Update an intent's output structure (US-004)."""
    intent = await service.update_intent_output_structure(intent_id, request.output_structure, repository)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    return _to_intent_response(intent)


@router.patch("/{intent_id}/context", response_model=IntentResponse)
async def update_intent_context(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateContextRequest = ...,
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Update an intent's context (US-005)."""
    intent = await service.update_intent_context(intent_id, request.context, repository)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    return _to_intent_response(intent)


@router.patch("/{intent_id}/constraints", response_model=IntentResponse)
async def update_intent_constraints(
    intent_id: int = Path(..., description="The unique identifier of the intent to update"),
    request: IntentUpdateConstraintsRequest = ...,
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Update an intent's constraints (US-006)."""
    intent = await service.update_intent_constraints(intent_id, request.constraints, repository)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")

    return _to_intent_response(intent)


@router.post("/{intent_id}/facts", response_model=FactResponse, status_code=status.HTTP_201_CREATED)
async def add_fact_to_intent(
    intent_id: int = Path(..., description="The unique identifier of the intent to add the fact to"),
    request: FactAddRequest = ...,
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Add a new fact to an intent (US-008)."""
    fact = await service.add_fact_to_intent(intent_id, request.value, repository)
    if not fact:
        raise HTTPException(status_code=404, detail="Intent not found")
    return _to_fact_response(fact)


@router.patch("/{intent_id}/facts/{fact_id}/value", response_model=FactResponse)
async def update_fact_value(
    intent_id: int = Path(..., description="The unique identifier of the intent that owns the fact"),
    fact_id: int = Path(..., description="The unique identifier of the fact to update"),
    request: FactUpdateValueRequest = ...,
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Update a fact's value (US-007)."""
    fact = await service.update_fact_value(intent_id, fact_id, request.value, repository)
    if not fact:
        raise HTTPException(status_code=404, detail="Fact not found")
    return _to_fact_response(fact)


@router.delete("/{intent_id}/facts/{fact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_fact_from_intent(
    intent_id: int = Path(..., description="The unique identifier of the intent that owns the fact"),
    fact_id: int = Path(..., description="The unique identifier of the fact to remove"),
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Remove a fact from an intent (US-009)."""
    removed = await service.remove_fact_from_intent(intent_id, fact_id, repository)
    if not removed:
        raise HTTPException(status_code=404, detail="Fact not found")


def _to_intent_response(intent) -> IntentResponse:
    """Convert domain model to response DTO."""
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
        facts=[_to_fact_response(fact) for fact in intent.facts],
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
