"""
Domain events for intents domain (V2).

All significant business actions must publish events.
"""

from dataclasses import dataclass
from datetime import datetime

from app.shared.events import DomainEvent


@dataclass
class IntentCreatedEvent(DomainEvent):
    """Event published when a new intent is created."""

    intent_id: int
    name: str
    description: str

    def __init__(self, intent_id: int, name: str, description: str):
        self.event_type = "intent.created"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.name = name
        self.description = description


@dataclass
class IntentUpdatedEvent(DomainEvent):
    """Event published when an intent is updated."""

    intent_id: int
    field_updated: str

    def __init__(self, intent_id: int, field_updated: str):
        self.event_type = "intent.updated"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.field_updated = field_updated


@dataclass
class IntentDeletedEvent(DomainEvent):
    """Event published when an intent is deleted."""

    intent_id: int

    def __init__(self, intent_id: int):
        self.event_type = "intent.deleted"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id


@dataclass
class IntentArticulationUpdatedEvent(DomainEvent):
    """Event published when an intent's articulation composition is replaced."""

    intent_id: int

    def __init__(self, intent_id: int):
        self.event_type = "intent.articulation_updated"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id


@dataclass
class PromptCreatedEvent(DomainEvent):
    """Event published when a prompt is added to an intent."""

    intent_id: int
    prompt_id: int
    version: int

    def __init__(self, intent_id: int, prompt_id: int, version: int):
        self.event_type = "prompt.created"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.prompt_id = prompt_id
        self.version = version


@dataclass
class OutputCreatedEvent(DomainEvent):
    """Event published when an output is added to a prompt."""

    prompt_id: int
    output_id: int

    def __init__(self, prompt_id: int, output_id: int):
        self.event_type = "output.created"
        self.timestamp = datetime.utcnow()
        self.prompt_id = prompt_id
        self.output_id = output_id


@dataclass
class InsightCreatedEvent(DomainEvent):
    """Event published when an insight is added to an intent."""

    intent_id: int
    insight_id: int

    def __init__(self, intent_id: int, insight_id: int):
        self.event_type = "insight.created"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.insight_id = insight_id
