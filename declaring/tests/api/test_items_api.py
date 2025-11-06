"""
API tests for items endpoints.

Tests full HTTP stack with TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from app.items.repository import ItemRepository
from app.main import app
from app.shared.dependencies import get_item_repository


@pytest.fixture
def client(test_db_session):
    """Create a test client with test database session."""

    def override_get_item_repository():
        return ItemRepository(test_db_session)

    app.dependency_overrides[get_item_repository] = override_get_item_repository
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.api
class TestGetItemsEndpoint:
    """Test GET /items endpoint."""

    def test_get_items_when_empty_returns_empty_list(self, client):
        """Test getting items when none exist."""
        # Act
        response = client.get("/items")

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_get_items_returns_all_items(self, client):
        """Test getting all items."""
        # Arrange - Create items
        client.post("/items", json={"name": "Item 1", "price": 99.99})
        client.post("/items", json={"name": "Item 2", "price": 149.99})

        # Act
        response = client.get("/items")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(item["name"] == "Item 1" for item in data)
        assert any(item["name"] == "Item 2" for item in data)


@pytest.mark.api
class TestGetItemByIdEndpoint:
    """Test GET /items/{item_id} endpoint."""

    def test_get_item_when_exists_returns_item(self, client):
        """Test getting an existing item."""
        # Arrange
        create_response = client.post("/items", json={"name": "Test Item", "price": 99.99})
        item_id = create_response.json()["id"]

        # Act
        response = client.get(f"/items/{item_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == "Test Item"
        assert data["price"] == 99.99

    def test_get_item_when_not_exists_returns_404(self, client):
        """Test getting a non-existent item."""
        # Act
        response = client.get("/items/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.api
class TestCreateItemEndpoint:
    """Test POST /items endpoint."""

    def test_create_item_with_valid_data_returns_201(self, client):
        """Test creating an item with valid data."""
        # Arrange
        payload = {"name": "New Item", "description": "Test description", "price": 199.99, "is_available": True}

        # Act
        response = client.post("/items", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == "New Item"
        assert data["description"] == "Test description"
        assert data["price"] == 199.99
        assert data["is_available"] is True

    def test_create_item_without_name_returns_422(self, client):
        """Test creating an item without name."""
        # Arrange
        payload = {"price": 199.99}

        # Act
        response = client.post("/items", json=payload)

        # Assert
        assert response.status_code == 422

    def test_create_item_without_price_returns_422(self, client):
        """Test creating an item without price."""
        # Arrange
        payload = {"name": "Test Item"}

        # Act
        response = client.post("/items", json=payload)

        # Assert
        assert response.status_code == 422

    def test_create_item_with_minimum_fields_returns_201(self, client):
        """Test creating an item with minimum required fields."""
        # Arrange
        payload = {"name": "Minimal Item", "price": 99.99}

        # Act
        response = client.post("/items", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Item"
        assert data["price"] == 99.99
        assert data["is_available"] is True  # Default value


@pytest.mark.api
class TestUpdateItemEndpoint:
    """Test PUT /items/{item_id} endpoint."""

    def test_update_item_when_exists_returns_200(self, client):
        """Test updating an existing item."""
        # Arrange
        create_response = client.post("/items", json={"name": "Original", "price": 99.99})
        item_id = create_response.json()["id"]
        update_payload = {"name": "Updated", "price": 149.99}

        # Act
        response = client.put(f"/items/{item_id}", json=update_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["price"] == 149.99

    def test_update_item_when_not_exists_returns_404(self, client):
        """Test updating a non-existent item."""
        # Arrange
        update_payload = {"name": "Updated"}

        # Act
        response = client.put("/items/999", json=update_payload)

        # Assert
        assert response.status_code == 404

    def test_update_item_partial_update_returns_200(self, client):
        """Test partial update of an item."""
        # Arrange
        create_response = client.post("/items", json={"name": "Original", "price": 99.99})
        item_id = create_response.json()["id"]

        # Act - Update only name
        response = client.put(f"/items/{item_id}", json={"name": "Updated Name Only"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name Only"
        assert data["price"] == 99.99  # Price unchanged


@pytest.mark.api
class TestDeleteItemEndpoint:
    """Test DELETE /items/{item_id} endpoint."""

    def test_delete_item_when_exists_returns_204(self, client):
        """Test deleting an existing item."""
        # Arrange
        create_response = client.post("/items", json={"name": "To Delete", "price": 99.99})
        item_id = create_response.json()["id"]

        # Act
        response = client.delete(f"/items/{item_id}")

        # Assert
        assert response.status_code == 204

        # Verify item is deleted
        get_response = client.get(f"/items/{item_id}")
        assert get_response.status_code == 404

    def test_delete_item_when_not_exists_returns_404(self, client):
        """Test deleting a non-existent item."""
        # Act
        response = client.delete("/items/999")

        # Assert
        assert response.status_code == 404


@pytest.mark.api
class TestSearchItemsEndpoint:
    """Test GET /items/search/query endpoint."""

    def test_search_items_by_name_returns_matches(self, client):
        """Test searching items by name."""
        # Arrange
        client.post("/items", json={"name": "Laptop Pro", "price": 999.99})
        client.post("/items", json={"name": "Laptop Air", "price": 799.99})
        client.post("/items", json={"name": "Desktop", "price": 1299.99})

        # Act
        response = client.get("/items/search/query?name=Laptop")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("Laptop" in item["name"] for item in data)

    def test_search_items_by_price_range_returns_matches(self, client):
        """Test searching items by price range."""
        # Arrange
        client.post("/items", json={"name": "Cheap", "price": 50.0})
        client.post("/items", json={"name": "Medium", "price": 150.0})
        client.post("/items", json={"name": "Expensive", "price": 250.0})

        # Act
        response = client.get("/items/search/query?min_price=100&max_price=200")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Medium"

    def test_search_items_available_only_returns_available(self, client):
        """Test searching for available items only."""
        # Arrange
        client.post("/items", json={"name": "Available", "price": 99.99, "is_available": True})
        client.post("/items", json={"name": "Unavailable", "price": 99.99, "is_available": False})

        # Act
        response = client.get("/items/search/query?available_only=true")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["is_available"] is True

    def test_search_items_with_no_matches_returns_empty_list(self, client):
        """Test searching with no matches."""
        # Arrange
        client.post("/items", json={"name": "Laptop", "price": 999.99})

        # Act
        response = client.get("/items/search/query?name=Nonexistent")

        # Assert
        assert response.status_code == 200
        assert response.json() == []


@pytest.mark.api
class TestItemEndpointsFlow:
    """Test complete user flow with items."""

    def test_complete_item_lifecycle(self, client):
        """Test complete CRUD flow for an item."""
        # 1. Create item
        create_response = client.post(
            "/items",
            json={"name": "Lifecycle Item", "description": "Testing full lifecycle", "price": 99.99, "is_available": True},
        )
        assert create_response.status_code == 201
        item_id = create_response.json()["id"]

        # 2. Get item
        get_response = client.get(f"/items/{item_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Lifecycle Item"

        # 3. Update item
        update_response = client.put(f"/items/{item_id}", json={"name": "Updated Lifecycle Item", "price": 149.99})
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Lifecycle Item"

        # 4. Verify in list
        list_response = client.get("/items")
        assert list_response.status_code == 200
        assert any(item["id"] == item_id for item in list_response.json())

        # 5. Delete item
        delete_response = client.delete(f"/items/{item_id}")
        assert delete_response.status_code == 204

        # 6. Verify deleted
        final_get = client.get(f"/items/{item_id}")
        assert final_get.status_code == 404
