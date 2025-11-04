"""
Domain events for intents domain.

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
    output_format: str

    def __init__(self, intent_id: int, name: str, description: str, output_format: str):
        self.event_type = "intent.created"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.name = name
        self.description = description
        self.output_format = output_format


@dataclass
class IntentUpdatedEvent(DomainEvent):
    """Event published when an intent is updated."""

    intent_id: int
    field_updated: str  # e.g., "name", "description", "output_format", etc.

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
class FactAddedEvent(DomainEvent):
    """Event published when a fact is added to an intent."""

    intent_id: int
    fact_id: int
    value: str

    def __init__(self, intent_id: int, fact_id: int, value: str):
        self.event_type = "fact.added"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.fact_id = fact_id
        self.value = value


@dataclass
class FactUpdatedEvent(DomainEvent):
    """Event published when a fact is updated."""

    intent_id: int
    fact_id: int

    def __init__(self, intent_id: int, fact_id: int):
        self.event_type = "fact.updated"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.fact_id = fact_id


@dataclass
class FactRemovedEvent(DomainEvent):
    """Event published when a fact is removed from an intent."""

    intent_id: int
    fact_id: int

    def __init__(self, intent_id: int, fact_id: int):
        self.event_type = "fact.removed"
        self.timestamp = datetime.utcnow()
        self.intent_id = intent_id
        self.fact_id = fact_id

