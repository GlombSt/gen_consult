"""
Database models for intents domain.

These models represent the database schema and include all database-specific fields.
Used exclusively by the repository layer.
"""

from datetime import datetime
from typing import Optional


class IntentDBModel:
    """
    Database model for intents.

    In a real application, this would use SQLAlchemy or similar ORM.
    For now, it's a simple class that represents the database schema.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        description: str = "",
        output_format: str = "",
        output_structure: Optional[str] = None,
        context: Optional[str] = None,
        constraints: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,  # Soft delete
    ):
        self.id = id
        self.name = name
        self.description = description
        self.output_format = output_format
        self.output_structure = output_structure
        self.context = context
        self.constraints = constraints
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at


class FactDBModel:
    """
    Database model for facts.

    In a real application, this would use SQLAlchemy or similar ORM.
    For now, it's a simple class that represents the database schema.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        intent_id: int = 0,
        value: str = "",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,  # Soft delete
    ):
        self.id = id
        self.intent_id = intent_id
        self.value = value
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
