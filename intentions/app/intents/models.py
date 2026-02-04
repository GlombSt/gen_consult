"""
Domain models for intents domain.

These models represent business entities and contain business logic.
Used by the service layer.
"""

from datetime import datetime
from typing import List, Optional


def _strip(s: Optional[str]) -> Optional[str]:
    return s.strip() if s else None


def _require_non_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value.strip()


class Intent:
    """Domain model for an intent (V2)."""

    def __init__(
        self,
        id: Optional[int],
        name: str,
        description: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        aspects: Optional[List["Aspect"]] = None,
        inputs: Optional[List["Input"]] = None,
        choices: Optional[List["Choice"]] = None,
        pitfalls: Optional[List["Pitfall"]] = None,
        assumptions: Optional[List["Assumption"]] = None,
        qualities: Optional[List["Quality"]] = None,
        examples: Optional[List["Example"]] = None,
        prompts: Optional[List["Prompt"]] = None,
        insights: Optional[List["Insight"]] = None,
    ):
        self.id = id
        self.name = _require_non_empty(name, "Name")
        self.description = _require_non_empty(description, "Description")
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        self.aspects = aspects if aspects is not None else []
        self.inputs = inputs if inputs is not None else []
        self.choices = choices if choices is not None else []
        self.pitfalls = pitfalls if pitfalls is not None else []
        self.assumptions = assumptions if assumptions is not None else []
        self.qualities = qualities if qualities is not None else []
        self.examples = examples if examples is not None else []
        self.prompts = prompts if prompts is not None else []
        self.insights = insights if insights is not None else []


class Aspect:
    """Domain model for an aspect (domain/area of consideration)."""

    def __init__(
        self,
        id: Optional[int],
        intent_id: int,
        name: str,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.intent_id = intent_id
        self.name = _require_non_empty(name, "Name")
        self.description = _strip(description) if description else None
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now


class Input:
    """Domain model for an input (what the user provides)."""

    def __init__(
        self,
        id: Optional[int],
        intent_id: int,
        name: str,
        description: str,
        aspect_id: Optional[int] = None,
        format: Optional[str] = None,
        required: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.intent_id = intent_id
        self.aspect_id = aspect_id
        self.name = _require_non_empty(name, "Name")
        self.description = _require_non_empty(description, "Description")
        self.format = _strip(format) if format else None
        self.required = required
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now


class Choice:
    """Domain model for a choice (decision point)."""

    def __init__(
        self,
        id: Optional[int],
        intent_id: int,
        name: str,
        description: str,
        aspect_id: Optional[int] = None,
        options: Optional[str] = None,
        selected_option: Optional[str] = None,
        rationale: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.intent_id = intent_id
        self.aspect_id = aspect_id
        self.name = _require_non_empty(name, "Name")
        self.description = _require_non_empty(description, "Description")
        self.options = _strip(options) if options else None
        self.selected_option = _strip(selected_option) if selected_option else None
        self.rationale = _strip(rationale) if rationale else None
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now


class Pitfall:
    """Domain model for a pitfall (failure mode to avoid)."""

    def __init__(
        self,
        id: Optional[int],
        intent_id: int,
        description: str,
        aspect_id: Optional[int] = None,
        mitigation: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.intent_id = intent_id
        self.aspect_id = aspect_id
        self.description = _require_non_empty(description, "Description")
        self.mitigation = _strip(mitigation) if mitigation else None
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now


class Assumption:
    """Domain model for an assumption (implicit belief made explicit)."""

    def __init__(
        self,
        id: Optional[int],
        intent_id: int,
        description: str,
        aspect_id: Optional[int] = None,
        confidence: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.intent_id = intent_id
        self.aspect_id = aspect_id
        self.description = _require_non_empty(description, "Description")
        self.confidence = _strip(confidence) if confidence else None
        if self.confidence and self.confidence not in ("verified", "likely", "uncertain"):
            raise ValueError("confidence must be verified, likely, or uncertain")
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now


class Quality:
    """Domain model for a quality (success criterion)."""

    def __init__(
        self,
        id: Optional[int],
        intent_id: int,
        criterion: str,
        aspect_id: Optional[int] = None,
        measurement: Optional[str] = None,
        priority: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.intent_id = intent_id
        self.aspect_id = aspect_id
        self.criterion = _require_non_empty(criterion, "Criterion")
        self.measurement = _strip(measurement) if measurement else None
        self.priority = _strip(priority) if priority else None
        if self.priority and self.priority not in ("must_have", "should_have", "nice_to_have"):
            raise ValueError("priority must be must_have, should_have, or nice_to_have")
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now


class Example:
    """Domain model for an example (input→output demonstration)."""

    def __init__(
        self,
        id: Optional[int],
        intent_id: int,
        sample: str,
        aspect_id: Optional[int] = None,
        explanation: Optional[str] = None,
        source: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.intent_id = intent_id
        self.aspect_id = aspect_id
        self.sample = _require_non_empty(sample, "Sample")
        self.explanation = _strip(explanation) if explanation else None
        self.source = _strip(source) if source else None
        if self.source and self.source not in ("user_provided", "llm_generated", "from_output"):
            raise ValueError("source must be user_provided, llm_generated, or from_output")
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now


class Prompt:
    """Domain model for a prompt (generated instruction)."""

    def __init__(
        self,
        id: Optional[int],
        intent_id: int,
        content: str,
        version: int,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.intent_id = intent_id
        self.content = _require_non_empty(content, "Content")
        self.version = version
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now


class Output:
    """Domain model for an output (AI response)."""

    def __init__(
        self,
        id: Optional[int],
        prompt_id: int,
        content: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.prompt_id = prompt_id
        self.content = _require_non_empty(content, "Content")
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now


class Insight:
    """Domain model for an insight (discovery feeding back to intent)."""

    def __init__(
        self,
        id: Optional[int],
        intent_id: int,
        content: str,
        source_type: Optional[str] = None,
        source_output_id: Optional[int] = None,
        source_prompt_id: Optional[int] = None,
        source_assumption_id: Optional[int] = None,
        status: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.intent_id = intent_id
        self.content = _require_non_empty(content, "Content")
        self.source_type = _strip(source_type) if source_type else None
        self.source_output_id = source_output_id
        self.source_prompt_id = source_prompt_id
        self.source_assumption_id = source_assumption_id
        self.status = _strip(status) if status else None
        if self.source_type and self.source_type not in ("sharpening", "output", "prompt", "assumption"):
            raise ValueError("source_type must be sharpening, output, prompt, or assumption")
        if self.status and self.status not in ("pending", "incorporated", "dismissed"):
            raise ValueError("status must be pending, incorporated, or dismissed")
        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now
