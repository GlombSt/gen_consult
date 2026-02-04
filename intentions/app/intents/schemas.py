"""
API schemas/DTOs for intents domain (V2).

These define the API contract for request and response payloads.
Used by the router layer.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# --- Intent (V2) ---


class IntentCreateRequest(BaseModel):
    """Request schema for creating a new intent (V2)."""

    name: str = Field(
        ...,
        min_length=1,
        description="Short, recognizable label for the intent.",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Full articulation of what the user wants to accomplish.",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Summarize document",
                    "description": "Generate a concise summary of the given document.",
                }
            ]
        }
    }


class IntentResponse(BaseModel):
    """Response schema for intent data (V2)."""

    id: int
    name: str = Field(..., description="Short, recognizable label for the intent.")
    description: str = Field(
        ...,
        description="Full articulation of what the user wants to accomplish.",
    )
    created_at: datetime
    updated_at: datetime
    aspects: List[dict] = Field(default_factory=list, description="Aspects (ids/names).")
    inputs: List[dict] = Field(default_factory=list, description="Inputs.")
    choices: List[dict] = Field(default_factory=list, description="Choices.")
    pitfalls: List[dict] = Field(default_factory=list, description="Pitfalls.")
    assumptions: List[dict] = Field(default_factory=list, description="Assumptions.")
    qualities: List[dict] = Field(default_factory=list, description="Qualities.")
    examples: List[dict] = Field(default_factory=list, description="Examples.")
    prompts: List[dict] = Field(default_factory=list, description="Prompts.")
    insights: List[dict] = Field(default_factory=list, description="Insights.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Summarize document",
                    "description": "Generate a summary of the given document.",
                    "created_at": "2025-01-01T12:00:00Z",
                    "updated_at": "2025-01-01T12:00:00Z",
                    "aspects": [],
                    "inputs": [],
                    "choices": [],
                    "pitfalls": [],
                    "assumptions": [],
                    "qualities": [],
                    "examples": [],
                    "prompts": [],
                    "insights": [],
                }
            ]
        }
    }


class IntentUpdateNameRequest(BaseModel):
    """Request schema for updating intent name."""

    name: str = Field(..., min_length=1, description="Short label for the intent.")


class IntentUpdateDescriptionRequest(BaseModel):
    """Request schema for updating intent description."""

    description: str = Field(
        ...,
        min_length=1,
        description="Full articulation of what the user wants to accomplish.",
    )
