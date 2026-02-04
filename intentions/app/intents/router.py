"""
HTTP router for intents domain (V2).

Defines HTTP endpoints and handles request/response serialization.
"""

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status

from app.shared import ErrorResponse
from app.shared.dependencies import get_intent_repository

from . import service
from .repository import IntentRepository
from .schemas import (
    IntentCreateRequest,
    IntentResponse,
    IntentUpdateDescriptionRequest,
    IntentUpdateNameRequest,
)

router = APIRouter(
    prefix="/intents",
    tags=["intents"],
)


@router.post(
    "",
    response_model=IntentResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="createIntent",
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
    },
)
async def create_intent(
    request: IntentCreateRequest,
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Create a new intent (V2)."""
    intent = await service.create_intent(request, repository)
    return _to_intent_response(intent)


@router.get(
    "/{intent_id}",
    response_model=IntentResponse,
    operation_id="getIntent",
    responses={
        404: {"model": ErrorResponse, "description": "Intent not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def get_intent(
    intent_id: int = Path(
        ..., description="The unique identifier of the intent to retrieve"
    ),
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Get a specific intent by ID."""
    intent = await service.get_intent(intent_id, repository)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    return _to_intent_response(intent)


@router.patch(
    "/{intent_id}/name",
    response_model=IntentResponse,
    operation_id="updateIntentName",
    responses={
        404: {"model": ErrorResponse, "description": "Intent not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
    },
)
async def update_intent_name(
    intent_id: int = Path(
        ..., description="The unique identifier of the intent to update"
    ),
    request: IntentUpdateNameRequest = Body(...),
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Update an intent's name."""
    intent = await service.update_intent_name(intent_id, request.name, repository)
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    return _to_intent_response(intent)


@router.patch(
    "/{intent_id}/description",
    response_model=IntentResponse,
    operation_id="updateIntentDescription",
    responses={
        404: {"model": ErrorResponse, "description": "Intent not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
    },
)
async def update_intent_description(
    intent_id: int = Path(
        ..., description="The unique identifier of the intent to update"
    ),
    request: IntentUpdateDescriptionRequest = Body(...),
    repository: IntentRepository = Depends(get_intent_repository),
):
    """Update an intent's description."""
    intent = await service.update_intent_description(
        intent_id, request.description, repository
    )
    if not intent:
        raise HTTPException(status_code=404, detail="Intent not found")
    return _to_intent_response(intent)


def _to_intent_response(intent) -> IntentResponse:
    """Convert domain model to response DTO (V2)."""
    return IntentResponse(
        id=intent.id,
        name=intent.name,
        description=intent.description,
        created_at=intent.created_at,
        updated_at=intent.updated_at,
        aspects=[{"id": a.id, "name": a.name} for a in intent.aspects],
        inputs=[{"id": i.id, "name": i.name} for i in intent.inputs],
        choices=[{"id": c.id, "name": c.name} for c in intent.choices],
        pitfalls=[{"id": p.id} for p in intent.pitfalls],
        assumptions=[{"id": a.id} for a in intent.assumptions],
        qualities=[{"id": q.id, "criterion": q.criterion} for q in intent.qualities],
        examples=[{"id": e.id} for e in intent.examples],
        prompts=[{"id": p.id, "version": p.version} for p in intent.prompts],
        insights=[{"id": i.id} for i in intent.insights],
    )
