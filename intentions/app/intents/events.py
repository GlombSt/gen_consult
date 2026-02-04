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
