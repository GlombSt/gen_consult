"""
API schemas/DTOs for intents domain.

These define the API contract for request and response payloads.
Used by the router layer.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FactResponse(BaseModel):
    """Response schema for fact data."""

    id: int
    intent_id: int
    value: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": 1,
                "intent_id": 1,
                "value": "The document is from 2023",
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z",
            }]
        }
    }


class IntentCreateRequest(BaseModel):
    """Request schema for creating a new intent (US-000)."""

    name: str = Field(..., min_length=1, description="Intent name")
    description: str = Field(..., min_length=1, description="Intent description")
    output_format: str = Field(..., min_length=1, description="Output format (JSON, XML, CSV, plain text, etc.)")
    output_structure: Optional[str] = Field(None, description="Output structure")
    context: Optional[str] = Field(None, description="Intent context")
    constraints: Optional[str] = Field(None, description="Intent constraints")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "name": "Summarize document",
                "description": "Generate a summary of the given document",
                "output_format": "plain text",
                "output_structure": "Bullet points",
                "context": "Academic documents",
                "constraints": "Max 500 words",
            }]
        }
    }


class IntentResponse(BaseModel):
    """Response schema for intent data."""

    id: int
    name: str
    description: str
    output_format: str
    output_structure: Optional[str] = None
    context: Optional[str] = None
    constraints: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    facts: List[FactResponse] = []

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": 1,
                "name": "Summarize document",
                "description": "Generate a summary of the given document",
                "output_format": "plain text",
                "output_structure": "Bullet points",
                "context": "Academic documents",
                "constraints": "Max 500 words",
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z",
                "facts": [],
            }]
        }
    }


class IntentUpdateNameRequest(BaseModel):
    """Request schema for updating intent name (US-001)."""

    name: str = Field(..., min_length=1, description="Intent name")


class IntentUpdateDescriptionRequest(BaseModel):
    """Request schema for updating intent description (US-002)."""

    description: str = Field(..., min_length=1, description="Intent description")


class IntentUpdateOutputFormatRequest(BaseModel):
    """Request schema for updating intent output format (US-003)."""

    output_format: str = Field(..., min_length=1, description="Output format (JSON, XML, CSV, plain text, etc.)")


class IntentUpdateOutputStructureRequest(BaseModel):
    """Request schema for updating intent output structure (US-004)."""

    output_structure: Optional[str] = Field(None, description="Output structure")


class IntentUpdateContextRequest(BaseModel):
    """Request schema for updating intent context (US-005)."""

    context: Optional[str] = Field(None, description="Intent context")


class IntentUpdateConstraintsRequest(BaseModel):
    """Request schema for updating intent constraints (US-006)."""

    constraints: Optional[str] = Field(None, description="Intent constraints")


class FactAddRequest(BaseModel):
    """Request schema for adding a fact to an intent (US-008)."""

    value: str = Field(..., min_length=1, description="Fact value")


class FactUpdateValueRequest(BaseModel):
    """Request schema for updating a fact value (US-007)."""

    value: str = Field(..., min_length=1, description="Fact value")

