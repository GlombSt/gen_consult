"""
Database models for items domain.

These models represent the database schema and include all database-specific fields.
Used exclusively by the repository layer.
"""

from datetime import datetime
from typing import Optional


class ItemDBModel:
    """
    Database model for items.

    In a real application, this would use SQLAlchemy or similar ORM.
    For now, it's a simple class that represents the database schema.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        description: Optional[str] = None,
        price: float = 0.0,
        is_available: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,  # Soft delete
    ):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.is_available = is_available
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
