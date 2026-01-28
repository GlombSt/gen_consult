"""
Domain events for users domain.

All significant business actions must publish events.
"""

from dataclasses import dataclass
from datetime import datetime

from app.shared.events import DomainEvent


@dataclass
class UserCreatedEvent(DomainEvent):
    """Event published when a new user is created."""

    user_id: int
    username: str
    email: str

    def __init__(self, user_id: int, username: str, email: str):
        self.event_type = "user.created"
        self.timestamp = datetime.utcnow()
        self.user_id = user_id
        self.username = username
        self.email = email


@dataclass
class UserUpdatedEvent(DomainEvent):
    """Event published when a user is updated."""

    user_id: int
    username: str
    email: str

    def __init__(self, user_id: int, username: str, email: str):
        self.event_type = "user.updated"
        self.timestamp = datetime.utcnow()
        self.user_id = user_id
        self.username = username
        self.email = email


@dataclass
class UserDeletedEvent(DomainEvent):
    """Event published when a user is deleted."""

    user_id: int

    def __init__(self, user_id: int):
        self.event_type = "user.deleted"
        self.timestamp = datetime.utcnow()
        self.user_id = user_id
