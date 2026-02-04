"""
Test data fixtures for intents domain (V2).
"""

from datetime import datetime
from typing import List, Optional

from app.intents.models import Aspect, Intent


def create_test_intent(
    id: int = 1,
    name: str = "Test Intent",
    description: str = "Test description",
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    aspects: Optional[List[Aspect]] = None,
) -> Intent:
    """Create a test intent domain model (V2)."""
    return Intent(
        id=id,
        name=name,
        description=description,
        created_at=created_at or datetime(2025, 1, 1, 12, 0, 0),
        updated_at=updated_at or datetime(2025, 1, 1, 12, 0, 0),
        aspects=aspects or [],
    )
