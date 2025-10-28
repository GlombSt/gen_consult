"""
Domain events for items domain.

All significant business actions must publish events.
"""

from dataclasses import dataclass
from datetime import datetime

from app.shared.events import DomainEvent


@dataclass
class ItemCreatedEvent(DomainEvent):
    """Event published when a new item is created."""

    item_id: int
    name: str
    price: float
    is_available: bool

    def __init__(self, item_id: int, name: str, price: float, is_available: bool):
        self.event_type = "item.created"
        self.timestamp = datetime.utcnow()
        self.item_id = item_id
        self.name = name
        self.price = price
        self.is_available = is_available


@dataclass
class ItemUpdatedEvent(DomainEvent):
    """Event published when an item is updated."""

    item_id: int
    name: str
    price: float
    is_available: bool

    def __init__(self, item_id: int, name: str, price: float, is_available: bool):
        self.event_type = "item.updated"
        self.timestamp = datetime.utcnow()
        self.item_id = item_id
        self.name = name
        self.price = price
        self.is_available = is_available


@dataclass
class ItemDeletedEvent(DomainEvent):
    """Event published when an item is deleted."""

    item_id: int

    def __init__(self, item_id: int):
        self.event_type = "item.deleted"
        self.timestamp = datetime.utcnow()
        self.item_id = item_id
