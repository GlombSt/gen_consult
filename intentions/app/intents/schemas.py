"""
API schemas/DTOs for intents domain (V2).

These define the API contract for request and response payloads.
Pydantic models are the semantic source of truth for the API.
Used by the router layer.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


# --- V2 entity response models (source of truth for API) ---


class AspectResponse(BaseModel):
    """Aspect: domain/area of consideration in an intent."""

    id: int = Field(..., description="Unique identifier of the aspect.")
    name: str = Field(..., description="Short label for the aspect.")
    description: Optional[str] = Field(
        None, description="Optional longer description of the aspect."
    )


class InputResponse(BaseModel):
    """Input: what the user provides for execution."""

    id: int = Field(..., description="Unique identifier of the input.")
    name: str = Field(..., description="Label for the input.")
    description: Optional[str] = Field(
        None, description="Description of what this input is for."
    )


class ChoiceResponse(BaseModel):
    """Choice: decision point with options and selected approach."""

    id: int = Field(..., description="Unique identifier of the choice.")
    name: str = Field(..., description="Label for the choice.")
    description: Optional[str] = Field(
        None, description="Description of the decision point."
    )


class PitfallResponse(BaseModel):
    """Pitfall: failure mode or anti-pattern to avoid."""

    id: int = Field(..., description="Unique identifier of the pitfall.")
    description: Optional[str] = Field(
        None, description="Description of the failure mode to avoid."
    )


class AssumptionResponse(BaseModel):
    """Assumption: implicit belief made explicit."""

    id: int = Field(..., description="Unique identifier of the assumption.")
    description: Optional[str] = Field(
        None, description="The assumption statement."
    )


class QualityResponse(BaseModel):
    """Quality: success criterion or output standard."""

    id: int = Field(..., description="Unique identifier of the quality.")
    criterion: str = Field(..., description="The success criterion.")
    priority: Optional[Literal["must_have", "should_have", "nice_to_have"]] = Field(
        None, description="Priority of this criterion."
    )


class ExampleResponse(BaseModel):
    """Example: concrete input→output demonstration."""

    id: int = Field(..., description="Unique identifier of the example.")
    sample: Optional[str] = Field(
        None, description="Sample input or input→output pair."
    )


class PromptResponse(BaseModel):
    """Prompt: generated, versioned instruction for the AI."""

    id: int = Field(..., description="Unique identifier of the prompt.")
    version: int = Field(..., description="Version number of this prompt.")
    content: Optional[str] = Field(
        None, description="The prompt text (may be omitted in list views)."
    )


class InsightResponse(BaseModel):
    """Insight: discovery that feeds back to the intent."""

    id: int = Field(..., description="Unique identifier of the insight.")
    content: Optional[str] = Field(
        None, description="The insight content."
    )
    status: Optional[Literal["pending", "incorporated", "dismissed"]] = Field(
        None, description="Current status of the insight."
    )


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
    aspects: List[AspectResponse] = Field(
        default_factory=list, description="Aspects (domains of consideration)."
    )
    inputs: List[InputResponse] = Field(
        default_factory=list, description="Inputs the user provides."
    )
    choices: List[ChoiceResponse] = Field(
        default_factory=list, description="Decision points and choices."
    )
    pitfalls: List[PitfallResponse] = Field(
        default_factory=list, description="Failure modes to avoid."
    )
    assumptions: List[AssumptionResponse] = Field(
        default_factory=list, description="Explicit assumptions."
    )
    qualities: List[QualityResponse] = Field(
        default_factory=list, description="Success criteria."
    )
    examples: List[ExampleResponse] = Field(
        default_factory=list, description="Example demonstrations."
    )
    prompts: List[PromptResponse] = Field(
        default_factory=list, description="Versioned prompts."
    )
    insights: List[InsightResponse] = Field(
        default_factory=list, description="Insights feeding back to the intent."
    )

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
