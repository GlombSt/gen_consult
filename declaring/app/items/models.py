"""
Domain models for items domain.

These models represent business entities and contain business logic.
Used by the service layer.
"""

from datetime import datetime
from typing import Optional


class Item:
    """
    Domain model for an item.

    Contains business logic and validation rules.
    """

    def __init__(
        self,
        id: Optional[int],
        name: str,
        description: Optional[str],
        price: float,
        is_available: bool = True,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.is_available = is_available
        self.created_at = created_at or datetime.utcnow()
