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
    value: str = Field(
        ...,
        description="The actual fact content or data point. Critical, specific information that needs to be used for generating the prompt (e.g., particular data points, explicit requirements, key details that must be incorporated, or concrete values). Facts are typically more static and explicit than context."
    )
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

    name: str = Field(
        ...,
        min_length=1,
        description="Name of the intent. Used to identify the work that the user wants to accomplish through AI interaction."
    )
    description: str = Field(
        ...,
        min_length=1,
        description="A textual description of what is to be accomplished. Work that the user wants to accomplish through AI interaction (e.g., 'summarize this document,' 'extract key dates,' 'generate creative alternatives'). The intent is most often used on multiple instances and situations. It is not a one-off but the starting point of what might be called a programme in software engineering."
    )
    output_format: str = Field(
        ...,
        min_length=1,
        description="The technical representation or encoding of the AI's response (e.g., JSON, XML, CSV, plain text, Markdown, HTML)"
    )
    output_structure: Optional[str] = Field(
        None,
        description="The organization and composition of the result's content, independent of its technical format (e.g., bullet points vs. paragraphs, table with specific columns, sections with headers, or a custom template with particular fields and their arrangement). The structure is maintained as text."
    )
    context: Optional[str] = Field(
        None,
        description="Broader, dynamic information that may be retrieved from systems or external sources to inform prompt generation (e.g., user's role and permissions, recent project activity, organizational policies, current system state, or relevant historical interactions). Context is typically more fluid and situational than facts."
    )
    constraints: Optional[str] = Field(
        None,
        description="Conditions that further describe how the intent must be achieved (e.g., word limits, tone requirements, format specifications, excluded topics, or quality criteria)"
    )

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
    name: str = Field(
        ...,
        description="Name of the intent. Used to identify the work that the user wants to accomplish through AI interaction."
    )
    description: str = Field(
        ...,
        description="A textual description of what is to be accomplished. Work that the user wants to accomplish through AI interaction (e.g., 'summarize this document,' 'extract key dates,' 'generate creative alternatives'). The intent is most often used on multiple instances and situations. It is not a one-off but the starting point of what might be called a programme in software engineering."
    )
    output_format: str = Field(
        ...,
        description="The technical representation or encoding of the AI's response (e.g., JSON, XML, CSV, plain text, Markdown, HTML)"
    )
    output_structure: Optional[str] = Field(
        None,
        description="The organization and composition of the result's content, independent of its technical format (e.g., bullet points vs. paragraphs, table with specific columns, sections with headers, or a custom template with particular fields and their arrangement). The structure is maintained as text."
    )
    context: Optional[str] = Field(
        None,
        description="Broader, dynamic information that may be retrieved from systems or external sources to inform prompt generation (e.g., user's role and permissions, recent project activity, organizational policies, current system state, or relevant historical interactions). Context is typically more fluid and situational than facts."
    )
    constraints: Optional[str] = Field(
        None,
        description="Conditions that further describe how the intent must be achieved (e.g., word limits, tone requirements, format specifications, excluded topics, or quality criteria)"
    )
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

    name: str = Field(
        ...,
        min_length=1,
        description="Name of the intent. Used to identify the work that the user wants to accomplish through AI interaction."
    )


class IntentUpdateDescriptionRequest(BaseModel):
    """Request schema for updating intent description (US-002)."""

    description: str = Field(
        ...,
        min_length=1,
        description="A textual description of what is to be accomplished. Work that the user wants to accomplish through AI interaction (e.g., 'summarize this document,' 'extract key dates,' 'generate creative alternatives'). The intent is most often used on multiple instances and situations. It is not a one-off but the starting point of what might be called a programme in software engineering."
    )


class IntentUpdateOutputFormatRequest(BaseModel):
    """Request schema for updating intent output format (US-003)."""

    output_format: str = Field(
        ...,
        min_length=1,
        description="The technical representation or encoding of the AI's response (e.g., JSON, XML, CSV, plain text, Markdown, HTML)"
    )


class IntentUpdateOutputStructureRequest(BaseModel):
    """Request schema for updating intent output structure (US-004)."""

    output_structure: Optional[str] = Field(
        None,
        description="The organization and composition of the result's content, independent of its technical format (e.g., bullet points vs. paragraphs, table with specific columns, sections with headers, or a custom template with particular fields and their arrangement). The structure is maintained as text."
    )


class IntentUpdateContextRequest(BaseModel):
    """Request schema for updating intent context (US-005)."""

    context: Optional[str] = Field(
        None,
        description="Broader, dynamic information that may be retrieved from systems or external sources to inform prompt generation (e.g., user's role and permissions, recent project activity, organizational policies, current system state, or relevant historical interactions). Context is typically more fluid and situational than facts."
    )


class IntentUpdateConstraintsRequest(BaseModel):
    """Request schema for updating intent constraints (US-006)."""

    constraints: Optional[str] = Field(
        None,
        description="Conditions that further describe how the intent must be achieved (e.g., word limits, tone requirements, format specifications, excluded topics, or quality criteria)"
    )


class FactAddRequest(BaseModel):
    """Request schema for adding a fact to an intent (US-008)."""

    value: str = Field(
        ...,
        min_length=1,
        description="The actual fact content or data point. Critical, specific information that needs to be used for generating the prompt (e.g., particular data points, explicit requirements, key details that must be incorporated, or concrete values). Facts are typically more static and explicit than context."
    )


class FactUpdateValueRequest(BaseModel):
    """Request schema for updating a fact value (US-007)."""

    value: str = Field(
        ...,
        min_length=1,
        description="The actual fact content or data point. Critical, specific information that needs to be used for generating the prompt (e.g., particular data points, explicit requirements, key details that must be incorporated, or concrete values). Facts are typically more static and explicit than context."
    )

