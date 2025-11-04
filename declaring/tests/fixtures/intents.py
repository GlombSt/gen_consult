"""
Test data fixtures for intents domain.
"""

from datetime import datetime

from app.intents.models import Fact, Intent


def create_test_intent(
    id: int = 1,
    name: str = "Test Intent",
    description: str = "Test description",
    output_format: str = "plain text",
    output_structure: str = None,
    context: str = None,
    constraints: str = None,
    created_at: datetime = None,
    updated_at: datetime = None,
) -> Intent:
    """Create a test intent domain model."""
    return Intent(
        id=id,
        name=name,
        description=description,
        output_format=output_format,
        output_structure=output_structure,
        context=context,
        constraints=constraints,
        created_at=created_at or datetime(2025, 1, 1, 12, 0, 0),
        updated_at=updated_at or datetime(2025, 1, 1, 12, 0, 0),
    )


def create_test_fact(
    id: int = 1,
    intent_id: int = 1,
    value: str = "Test fact value",
    created_at: datetime = None,
    updated_at: datetime = None,
) -> Fact:
    """Create a test fact domain model."""
    return Fact(
        id=id,
        intent_id=intent_id,
        value=value,
        created_at=created_at or datetime(2025, 1, 1, 12, 0, 0),
        updated_at=updated_at or datetime(2025, 1, 1, 12, 0, 0),
    )

