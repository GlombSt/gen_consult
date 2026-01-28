"""
Unit tests for intents domain models.

Tests business logic and validation rules for Intent and Fact domain models.
"""

from datetime import datetime

import pytest


@pytest.mark.unit
class TestIntent:
    """Test Intent domain model."""

    def test_create_intent_with_required_fields(self):
        """Test creating an intent with all required fields."""
        # This test will fail until we implement the Intent model
        # Arrange
        from app.intents.models import Intent

        # Act
        intent = Intent(
            id=None,
            name="Summarize document",
            description="Generate a summary of the given document",
            output_format="plain text",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        # Assert
        assert intent.id is None
        assert intent.name == "Summarize document"
        assert intent.description == "Generate a summary of the given document"
        assert intent.output_format == "plain text"
        assert intent.output_structure is None
        assert intent.context is None
        assert intent.constraints is None
        assert intent.created_at == datetime(2025, 1, 1, 12, 0, 0)

    def test_create_intent_with_all_fields(self):
        """Test creating an intent with all fields including optional ones."""
        # Arrange
        from app.intents.models import Intent

        # Act
        intent = Intent(
            id=1,
            name="Extract dates",
            description="Extract key dates from the document",
            output_format="JSON",
            output_structure="List of dates with descriptions",
            context="Academic documents",
            constraints="Include only dates after 2020",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 2, 12, 0, 0),
        )

        # Assert
        assert intent.id == 1
        assert intent.name == "Extract dates"
        assert intent.description == "Extract key dates from the document"
        assert intent.output_format == "JSON"
        assert intent.output_structure == "List of dates with descriptions"
        assert intent.context == "Academic documents"
        assert intent.constraints == "Include only dates after 2020"
        assert intent.created_at == datetime(2025, 1, 1, 12, 0, 0)
        assert intent.updated_at == datetime(2025, 1, 2, 12, 0, 0)

    def test_create_intent_with_empty_name_raises_error(self):
        """Test that creating an intent with empty name raises validation error."""
        # Arrange
        from app.intents.models import Intent

        # Act & Assert
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Intent(
                id=None,
                name="",
                description="Test description",
                output_format="plain text",
            )

    def test_create_intent_with_empty_description_raises_error(self):
        """Test that creating an intent with empty description raises validation error."""
        # Arrange
        from app.intents.models import Intent

        # Act & Assert
        with pytest.raises(ValueError, match="Description cannot be empty"):
            Intent(
                id=None,
                name="Test Intent",
                description="",
                output_format="plain text",
            )

    def test_create_intent_with_empty_output_format_raises_error(self):
        """Test that creating an intent with empty output format raises validation error."""
        # Arrange
        from app.intents.models import Intent

        # Act & Assert
        with pytest.raises(ValueError, match="Output format cannot be empty"):
            Intent(
                id=None,
                name="Test Intent",
                description="Test description",
                output_format="",
            )

    def test_create_intent_auto_sets_timestamps(self):
        """Test that creating an intent auto-sets created_at and updated_at if not provided."""
        # Arrange
        from app.intents.models import Intent

        # Act
        intent = Intent(
            id=None,
            name="Test Intent",
            description="Test description",
            output_format="plain text",
        )

        # Assert
        assert intent.created_at is not None
        assert isinstance(intent.created_at, datetime)
        assert intent.updated_at is not None
        assert isinstance(intent.updated_at, datetime)
        assert intent.updated_at >= intent.created_at

    def test_intent_facts_default_to_empty_list_not_shared(self):
        """
        Test that each Intent instance gets its own empty facts list.

        This test prevents the mutable default argument bug where all Intent
        instances would share the same list object if facts parameter used
        a default value of [].
        """
        # Arrange
        from app.intents.models import Fact, Intent

        # Act - Create two intents without explicitly passing facts
        intent1 = Intent(
            id=1,
            name="Intent 1",
            description="Description 1",
            output_format="plain text",
        )
        intent2 = Intent(
            id=2,
            name="Intent 2",
            description="Description 2",
            output_format="plain text",
        )

        # Assert - Both should have empty facts lists
        assert intent1.facts == []
        assert intent2.facts == []
        # Critical: Verify they are different list objects (not shared)
        assert intent1.facts is not intent2.facts

        # Act - Add a fact to intent1
        fact = Fact(id=1, intent_id=1, value="Fact for intent 1")
        intent1.facts.append(fact)

        # Assert - intent1 should have the fact, intent2 should still be empty
        assert len(intent1.facts) == 1
        assert intent1.facts[0].value == "Fact for intent 1"
        assert len(intent2.facts) == 0  # Should still be empty, not shared


@pytest.mark.unit
class TestFact:
    """Test Fact domain model."""

    def test_create_fact_with_required_fields(self):
        """Test creating a fact with all required fields."""
        # Arrange
        from app.intents.models import Fact

        # Act
        fact = Fact(
            id=None,
            intent_id=1,
            value="The document is from 2023",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        )

        # Assert
        assert fact.id is None
        assert fact.intent_id == 1
        assert fact.value == "The document is from 2023"
        assert fact.created_at == datetime(2025, 1, 1, 12, 0, 0)

    def test_create_fact_with_updated_at(self):
        """Test creating a fact with updated_at timestamp."""
        # Arrange
        from app.intents.models import Fact

        # Act
        fact = Fact(
            id=1,
            intent_id=1,
            value="The document is from 2023",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
            updated_at=datetime(2025, 1, 2, 12, 0, 0),
        )

        # Assert
        assert fact.id == 1
        assert fact.intent_id == 1
        assert fact.value == "The document is from 2023"
        assert fact.created_at == datetime(2025, 1, 1, 12, 0, 0)
        assert fact.updated_at == datetime(2025, 1, 2, 12, 0, 0)

    def test_create_fact_with_empty_value_raises_error(self):
        """Test that creating a fact with empty value raises validation error."""
        # Arrange
        from app.intents.models import Fact

        # Act & Assert
        with pytest.raises(ValueError, match="Value cannot be empty"):
            Fact(
                id=None,
                intent_id=1,
                value="",
            )

    def test_create_fact_auto_sets_timestamps(self):
        """Test that creating a fact auto-sets created_at and updated_at if not provided."""
        # Arrange
        from app.intents.models import Fact

        # Act
        fact = Fact(
            id=None,
            intent_id=1,
            value="Test fact value",
        )

        # Assert
        assert fact.created_at is not None
        assert isinstance(fact.created_at, datetime)
        assert fact.updated_at is not None
        assert isinstance(fact.updated_at, datetime)
        assert fact.updated_at >= fact.created_at
