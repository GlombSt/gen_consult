"""
Domain models for intents domain.

These models represent business entities and contain business logic.
Used by the service layer.
"""

from datetime import datetime
from typing import List, Optional


class Intent:
    """
    Domain model for an intent.

    Contains business logic and validation rules.
    """

    def __init__(
        self,
        id: Optional[int],
        name: str,
        description: str,
        output_format: str,
        output_structure: Optional[str] = None,
        context: Optional[str] = None,
        constraints: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        facts: List["Fact"] = [],
    ):
        # Validation
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")
        if not output_format or not output_format.strip():
            raise ValueError("Output format cannot be empty")

        self.id = id
        self.name = name.strip()
        self.description = description.strip()
        self.output_format = output_format.strip()
        self.output_structure = output_structure.strip() if output_structure else None
        self.context = context.strip() if context else None
        self.constraints = constraints.strip() if constraints else None

        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        self.facts = facts


class Fact:
    """
    Domain model for a fact.

    Contains business logic and validation rules.
    Facts are associated with an intent.
    """

    def __init__(
        self,
        id: Optional[int],
        intent_id: int,
        value: str,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        # Validation
        if not value or not value.strip():
            raise ValueError("Value cannot be empty")

        self.id = id
        self.intent_id = intent_id
        self.value = value.strip()

        now = datetime.utcnow()
        self.created_at = created_at or now
        self.updated_at = updated_at or now
