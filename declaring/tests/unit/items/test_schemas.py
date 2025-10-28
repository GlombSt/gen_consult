"""
Unit tests for items schemas/DTOs.

Tests field validation and serialization.
"""

import pytest
from pydantic import ValidationError

from app.items.schemas import ItemCreateRequest, ItemResponse, ItemUpdateRequest


@pytest.mark.unit
class TestItemCreateRequest:
    """Test ItemCreateRequest schema."""

    def test_create_request_with_valid_data_validates(self):
        """Test creating request with valid data."""
        # Arrange & Act
        request = ItemCreateRequest(name="Laptop", description="High-performance laptop", price=999.99, is_available=True)

        # Assert
        assert request.name == "Laptop"
        assert request.description == "High-performance laptop"
        assert request.price == 999.99
        assert request.is_available is True

    def test_create_request_with_minimum_required_fields_validates(self):
        """Test creating request with only required fields."""
        # Arrange & Act
        request = ItemCreateRequest(name="Laptop", price=999.99)

        # Assert
        assert request.name == "Laptop"
        assert request.price == 999.99
        assert request.description is None
        assert request.is_available is True

    def test_create_request_without_name_raises_validation_error(self):
        """Test creating request without name raises error."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(price=999.99)

        assert "name" in str(exc_info.value)

    def test_create_request_without_price_raises_validation_error(self):
        """Test creating request without price raises error."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemCreateRequest(name="Laptop")

        assert "price" in str(exc_info.value)

    def test_create_request_with_none_description_validates(self):
        """Test creating request with None description."""
        # Arrange & Act
        request = ItemCreateRequest(name="Laptop", price=999.99, description=None)

        # Assert
        assert request.description is None


@pytest.mark.unit
class TestItemUpdateRequest:
    """Test ItemUpdateRequest schema."""

    def test_update_request_with_all_fields_validates(self):
        """Test update request with all fields."""
        # Arrange & Act
        request = ItemUpdateRequest(
            name="Updated Laptop", description="Updated description", price=1099.99, is_available=False
        )

        # Assert
        assert request.name == "Updated Laptop"
        assert request.description == "Updated description"
        assert request.price == 1099.99
        assert request.is_available is False

    def test_update_request_with_no_fields_validates(self):
        """Test update request with no fields."""
        # Arrange & Act
        request = ItemUpdateRequest()

        # Assert
        assert request.name is None
        assert request.description is None
        assert request.price is None
        assert request.is_available is None

    def test_update_request_with_single_field_validates(self):
        """Test update request with single field."""
        # Arrange & Act
        request = ItemUpdateRequest(name="New Name")

        # Assert
        assert request.name == "New Name"
        assert request.description is None
        assert request.price is None
        assert request.is_available is None


@pytest.mark.unit
class TestItemResponse:
    """Test ItemResponse schema."""

    def test_response_with_valid_data_validates(self):
        """Test response with valid data."""
        # Arrange & Act
        response = ItemResponse(id=1, name="Laptop", description="High-performance laptop", price=999.99, is_available=True)

        # Assert
        assert response.id == 1
        assert response.name == "Laptop"
        assert response.description == "High-performance laptop"
        assert response.price == 999.99
        assert response.is_available is True

    def test_response_without_id_raises_validation_error(self):
        """Test response without ID raises error."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ItemResponse(name="Laptop", description="Test", price=999.99, is_available=True)

        assert "id" in str(exc_info.value)

    def test_response_with_none_description_validates(self):
        """Test response with None description."""
        # Arrange & Act
        response = ItemResponse(id=1, name="Laptop", description=None, price=999.99, is_available=True)

        # Assert
        assert response.description is None
