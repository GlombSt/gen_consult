"""
Unit tests for items domain models.

Tests domain logic and validation rules.
"""

from datetime import datetime

import pytest

from app.items.models import Item


@pytest.mark.unit
class TestItem:
    """Test Item domain model."""

    def test_create_item_with_valid_data_creates_instance(self):
        """Test creating an item with valid data."""
        # Arrange & Act
        item = Item(id=1, name="Laptop", description="High-performance laptop", price=999.99, is_available=True)

        # Assert
        assert item.id == 1
        assert item.name == "Laptop"
        assert item.description == "High-performance laptop"
        assert item.price == 999.99
        assert item.is_available is True
        assert isinstance(item.created_at, datetime)

    def test_create_item_without_id_sets_none(self):
        """Test creating an item without ID sets it to None."""
        # Arrange & Act
        item = Item(id=None, name="Laptop", description="Test", price=999.99)

        # Assert
        assert item.id is None

    def test_create_item_with_none_description_accepts_none(self):
        """Test creating an item with None description."""
        # Arrange & Act
        item = Item(id=1, name="Laptop", description=None, price=999.99)

        # Assert
        assert item.description is None

    def test_create_item_without_created_at_sets_default(self):
        """Test creating an item without created_at sets default."""
        # Arrange & Act
        before = datetime.utcnow()
        item = Item(id=1, name="Laptop", description="Test", price=999.99)
        after = datetime.utcnow()

        # Assert
        assert before <= item.created_at <= after

    def test_create_item_with_created_at_uses_provided_value(self):
        """Test creating an item with provided created_at."""
        # Arrange
        custom_date = datetime(2025, 1, 1, 12, 0, 0)

        # Act
        item = Item(id=1, name="Laptop", description="Test", price=999.99, created_at=custom_date)

        # Assert
        assert item.created_at == custom_date

    def test_create_item_with_is_available_false_sets_false(self):
        """Test creating an item with is_available=False."""
        # Arrange & Act
        item = Item(id=1, name="Laptop", description="Test", price=999.99, is_available=False)

        # Assert
        assert item.is_available is False

    def test_create_item_with_default_is_available_sets_true(self):
        """Test creating an item with default is_available."""
        # Arrange & Act
        item = Item(id=1, name="Laptop", description="Test", price=999.99)

        # Assert
        assert item.is_available is True

    def test_create_item_with_zero_price_accepts_zero(self):
        """Test creating an item with zero price."""
        # Arrange & Act
        item = Item(id=1, name="Free Item", description="Test", price=0.0)

        # Assert
        assert item.price == 0.0

    def test_create_item_with_negative_price_accepts_value(self):
        """Test creating an item with negative price (no validation in model)."""
        # Arrange & Act
        item = Item(id=1, name="Discount", description="Test", price=-10.0)

        # Assert
        assert item.price == -10.0
