"""
API schemas/DTOs for intents domain (V2).

These define the API contract for request and response payloads.
Pydantic models are the semantic source of truth for the API.
Used by the router layer.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

# Enums for articulation entities (aligned with INTENTS_DOMAIN_V2.md)
AssumptionConfidence = Literal["verified", "likely", "uncertain"]
QualityPriority = Literal["must_have", "should_have", "nice_to_have"]
InsightSourceType = Literal["sharpening", "output", "prompt", "assumption"]
InsightStatus = Literal["pending", "incorporated", "dismissed"]


# --- Nested create types for intent composition (no Example) ---


class AspectCreate(BaseModel):
    """Aspect: domain/area of consideration in an intent."""

    name: str = Field(..., min_length=1, description="Short label for the aspect.")
    description: Optional[str] = Field(None, description="Optional description.")


class InputCreate(BaseModel):
    """Input: what the user provides for execution."""

    name: str = Field(..., min_length=1, description="Label for the input.")
    description: str = Field(..., min_length=1, description="What this input is for.")
    aspect_id: Optional[int] = Field(None, description="Aspect this input was discovered for.")
    format: Optional[str] = Field(None, description="Expected structure or encoding.")
    required: bool = Field(True, description="Whether the input is mandatory.")


class ChoiceCreate(BaseModel):
    """Choice: decision point with options and selected approach."""

    name: str = Field(..., min_length=1, description="Label for the decision point.")
    description: str = Field(..., min_length=1, description="The decision and why it matters.")
    aspect_id: Optional[int] = Field(None, description="Aspect this choice was discovered for.")
    options: Optional[str] = Field(None, description="Available alternatives (JSON or prose).")
    selected_option: Optional[str] = Field(None, description="The chosen approach.")
    rationale: Optional[str] = Field(None, description="Justification for the selection.")


class PitfallCreate(BaseModel):
    """Pitfall: failure mode or anti-pattern to avoid."""

    description: str = Field(..., min_length=1, description="Failure mode or anti-pattern to avoid.")
    aspect_id: Optional[int] = Field(None, description="Aspect this pitfall was discovered for.")
    mitigation: Optional[str] = Field(None, description="How to prevent or handle this pitfall.")


class AssumptionCreate(BaseModel):
    """Assumption: implicit belief made explicit."""

    description: str = Field(..., min_length=1, description="The implicit belief made explicit.")
    aspect_id: Optional[int] = Field(None, description="Aspect this assumption was discovered for.")
    confidence: Optional[AssumptionConfidence] = Field(
        None, description="Certainty level: verified, likely, uncertain."
    )


class QualityCreate(BaseModel):
    """Quality: success criterion or output standard. Use field 'criterion', not name/description."""

    criterion: str = Field(..., min_length=1, description="The standard that defines success.")
    aspect_id: Optional[int] = Field(None, description="Aspect this quality was discovered for.")
    measurement: Optional[str] = Field(None, description="How to verify the criterion is met.")
    priority: Optional[QualityPriority] = Field(
        None, description="Importance: must_have, should_have, nice_to_have."
    )


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
    """Request schema for creating a new intent (V2) with optional articulation."""

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
    aspects: Optional[List[AspectCreate]] = Field(
        default_factory=list,
        description="Optional aspects to create with the intent.",
    )
    inputs: Optional[List[InputCreate]] = Field(
        default_factory=list,
        description="Optional inputs to create with the intent.",
    )
    choices: Optional[List[ChoiceCreate]] = Field(
        default_factory=list,
        description="Optional choices to create with the intent.",
    )
    pitfalls: Optional[List[PitfallCreate]] = Field(
        default_factory=list,
        description="Optional pitfalls to create with the intent.",
    )
    assumptions: Optional[List[AssumptionCreate]] = Field(
        default_factory=list,
        description="Optional assumptions to create with the intent.",
    )
    qualities: Optional[List[QualityCreate]] = Field(
        default_factory=list,
        description="Optional qualities to create with the intent.",
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


class IntentArticulationUpdateRequest(BaseModel):
    """Request schema for replacing the full articulation composition of an intent. Empty array clears that entity type."""

    aspects: Optional[List[AspectCreate]] = Field(None, description="Replace aspects (omit to leave unchanged).")
    inputs: Optional[List[InputCreate]] = Field(None, description="Replace inputs.")
    choices: Optional[List[ChoiceCreate]] = Field(None, description="Replace choices.")
    pitfalls: Optional[List[PitfallCreate]] = Field(None, description="Replace pitfalls.")
    assumptions: Optional[List[AssumptionCreate]] = Field(None, description="Replace assumptions.")
    qualities: Optional[List[QualityCreate]] = Field(None, description="Replace qualities.")


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


class IntentResponseForMCP(BaseModel):
    """Intent response for MCP (full composition, examples omitted)."""

    id: int
    name: str = Field(..., description="Short, recognizable label for the intent.")
    description: str = Field(..., description="Full articulation of what the user wants to accomplish.")
    created_at: datetime
    updated_at: datetime
    aspects: List[AspectResponse] = Field(default_factory=list)
    inputs: List[InputResponse] = Field(default_factory=list)
    choices: List[ChoiceResponse] = Field(default_factory=list)
    pitfalls: List[PitfallResponse] = Field(default_factory=list)
    assumptions: List[AssumptionResponse] = Field(default_factory=list)
    qualities: List[QualityResponse] = Field(default_factory=list)
    prompts: List[PromptResponse] = Field(default_factory=list)
    insights: List[InsightResponse] = Field(default_factory=list)


class PromptCreateRequest(BaseModel):
    """Request schema for adding a prompt to an intent."""

    content: str = Field(..., min_length=1, description="The complete instruction text for the AI executor.")


class OutputCreateRequest(BaseModel):
    """Request schema for adding an output to a prompt."""

    content: str = Field(
        ...,
        min_length=1,
        description="The AI executor's response content.",
    )


class InsightCreateRequest(BaseModel):
    """Request schema for adding an insight to an intent."""

    content: str = Field(..., min_length=1, description="The discovery or learning being captured.")
    source_type: Optional[InsightSourceType] = Field(
        None,
        description="What triggered the insight: sharpening, output, prompt, assumption.",
    )
    source_output_id: Optional[int] = Field(None, description="Output that surfaced this insight.")
    source_prompt_id: Optional[int] = Field(None, description="Prompt that surfaced this insight.")
    source_assumption_id: Optional[int] = Field(None, description="Assumption that was challenged.")
    status: Optional[InsightStatus] = Field(
        None,
        description="Processing state: pending, incorporated, dismissed.",
    )
