"""
Domain models for users domain.

These models represent business entities and contain business logic.
Used by the service layer.
"""

from datetime import datetime
from typing import Optional


class User:
    """
    Domain model for a user.

    Contains business logic and validation rules.
    """

    def __init__(
        self,
        id: Optional[int],
        username: str,
        email: str,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.username = username
        self.email = email
        self.created_at = created_at or datetime.utcnow()
