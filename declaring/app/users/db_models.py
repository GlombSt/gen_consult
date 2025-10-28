"""
Database models for users domain.

These models represent the database schema and include all database-specific fields.
Used exclusively by the repository layer.
"""

from datetime import datetime
from typing import Optional


class UserDBModel:
    """
    Database model for users.

    In a real application, this would use SQLAlchemy or similar ORM.
    For now, it's a simple class that represents the database schema.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        username: str = "",
        email: str = "",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None,  # Soft delete
    ):
        self.id = id
        self.username = username
        self.email = email
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
