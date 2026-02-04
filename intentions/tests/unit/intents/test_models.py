"""
Unit tests for intents domain models (V2).

Tests business logic and validation rules for Intent and V2 entity models.
"""

from datetime import datetime

import pytest


@pytest.mark.unit
class TestIntent:
    """Test Intent domain model (V2)."""

    def test_create_intent_with_required_fields(self):
        """Test creating an intent with all required fields."""
        from app.intents.models import Intent

        intent = Intent(
            id=None,
            name="Summarize document",
            description="Generate a summary of the given document",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )
        assert intent.id is None
        assert intent.name == "Summarize document"
        assert intent.description == "Generate a summary of the given document"
        assert intent.created_at == datetime(2025, 1, 1, 12, 0, 0)
        assert intent.aspects == []
        assert intent.inputs == []

    def test_create_intent_with_all_fields(self):
        """Test creating an intent with timestamps."""
        from app.intents.models import Intent

        intent = Intent(
            id=1,
            name="Extract dates",
            description="Extract key dates from the document",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 2, 12, 0, 0),
        )
        assert intent.id == 1
        assert intent.name == "Extract dates"
        assert intent.description == "Extract key dates from the document"
        assert intent.created_at == datetime(2025, 1, 1, 12, 0, 0)
        assert intent.updated_at == datetime(2025, 1, 2, 12, 0, 0)

    def test_create_intent_with_empty_name_raises_error(self):
        """Test that creating an intent with empty name raises validation error."""
        from app.intents.models import Intent

        with pytest.raises(ValueError, match="Name cannot be empty"):
            Intent(
                id=None,
                name="",
                description="Test description",
            )

    def test_create_intent_with_empty_description_raises_error(self):
        """Test that creating an intent with empty description raises validation error."""
        from app.intents.models import Intent

        with pytest.raises(ValueError, match="Description cannot be empty"):
            Intent(
                id=None,
                name="Test Intent",
                description="",
            )

    def test_create_intent_auto_sets_timestamps(self):
        """Test that creating an intent auto-sets created_at and updated_at if not provided."""
        from app.intents.models import Intent

        intent = Intent(
            id=None,
            name="Test Intent",
            description="Test description",
        )
        assert intent.created_at is not None
        assert isinstance(intent.created_at, datetime)
        assert intent.updated_at is not None
        assert isinstance(intent.updated_at, datetime)
        assert intent.updated_at >= intent.created_at

    def test_intent_aspects_default_to_empty_list_not_shared(self):
        """Test that each Intent instance gets its own empty aspects list."""
        from app.intents.models import Aspect, Intent

        intent1 = Intent(id=1, name="Intent 1", description="Description 1")
        intent2 = Intent(id=2, name="Intent 2", description="Description 2")
        assert intent1.aspects == []
        assert intent2.aspects == []
        assert intent1.aspects is not intent2.aspects

        aspect = Aspect(id=1, intent_id=1, name="SEO")
        intent1.aspects.append(aspect)
        assert len(intent1.aspects) == 1
        assert intent1.aspects[0].name == "SEO"
        assert len(intent2.aspects) == 0


@pytest.mark.unit
class TestAspect:
    """Test Aspect domain model."""

    def test_create_aspect_with_required_fields(self):
        """Test creating an aspect with required fields."""
        from app.intents.models import Aspect

        aspect = Aspect(
            id=None,
            intent_id=1,
            name="SEO",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )
        assert aspect.id is None
        assert aspect.intent_id == 1
        assert aspect.name == "SEO"
        assert aspect.description is None

    def test_create_aspect_with_empty_name_raises_error(self):
        """Test that creating an aspect with empty name raises validation error."""
        from app.intents.models import Aspect

        with pytest.raises(ValueError, match="Name cannot be empty"):
            Aspect(id=None, intent_id=1, name="")
