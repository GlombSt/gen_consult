"""
API tests for users endpoints.

Tests full HTTP stack with TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.shared.dependencies import get_user_repository
from app.users.repository import UserRepository


@pytest.fixture
def client(test_db_session):
    """Create a test client with test database session."""

    def override_get_user_repository():
        return UserRepository(test_db_session)

    app.dependency_overrides[get_user_repository] = override_get_user_repository
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.api
class TestGetUsersEndpoint:
    """Test GET /users endpoint."""

    def test_get_users_when_empty_returns_empty_list(self, client):
        """Test getting users when none exist."""
        # Act
        response = client.get("/users")

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_get_users_returns_all_users(self, client):
        """Test getting all users."""
        # Arrange - Create users
        client.post("/users", json={"username": "user1", "email": "user1@example.com"})
        client.post("/users", json={"username": "user2", "email": "user2@example.com"})

        # Act
        response = client.get("/users")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(user["username"] == "user1" for user in data)
        assert any(user["username"] == "user2" for user in data)


@pytest.mark.api
class TestGetUserByIdEndpoint:
    """Test GET /users/{user_id} endpoint."""

    def test_get_user_when_exists_returns_user(self, client):
        """Test getting an existing user."""
        # Arrange
        create_response = client.post("/users", json={"username": "testuser", "email": "test@example.com"})
        user_id = create_response.json()["id"]

        # Act
        response = client.get(f"/users/{user_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_get_user_when_not_exists_returns_404(self, client):
        """Test getting a non-existent user."""
        # Act
        response = client.get("/users/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.api
class TestCreateUserEndpoint:
    """Test POST /users endpoint."""

    def test_create_user_with_valid_data_returns_201(self, client):
        """Test creating a user with valid data."""
        # Arrange
        payload = {"username": "newuser", "email": "newuser@example.com"}

        # Act
        response = client.post("/users", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"

    def test_create_user_without_username_returns_422(self, client):
        """Test creating a user without username."""
        # Arrange
        payload = {"email": "test@example.com"}

        # Act
        response = client.post("/users", json=payload)

        # Assert
        assert response.status_code == 422

    def test_create_user_without_email_returns_422(self, client):
        """Test creating a user without email."""
        # Arrange
        payload = {"username": "testuser"}

        # Act
        response = client.post("/users", json=payload)

        # Assert
        assert response.status_code == 422


@pytest.mark.api
class TestUpdateUserEndpoint:
    """Test PUT /users/{user_id} endpoint."""

    def test_update_user_when_exists_returns_200(self, client):
        """Test updating an existing user."""
        # Arrange
        create_response = client.post("/users", json={"username": "original", "email": "original@example.com"})
        user_id = create_response.json()["id"]
        update_payload = {"username": "updated", "email": "updated@example.com"}

        # Act
        response = client.put(f"/users/{user_id}", json=update_payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updated"
        assert data["email"] == "updated@example.com"

    def test_update_user_when_not_exists_returns_404(self, client):
        """Test updating a non-existent user."""
        # Arrange
        update_payload = {"username": "updated"}

        # Act
        response = client.put("/users/999", json=update_payload)

        # Assert
        assert response.status_code == 404

    def test_update_user_partial_update_returns_200(self, client):
        """Test partial update of a user."""
        # Arrange
        create_response = client.post("/users", json={"username": "original", "email": "original@example.com"})
        user_id = create_response.json()["id"]

        # Act - Update only username
        response = client.put(f"/users/{user_id}", json={"username": "updated_only"})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "updated_only"
        assert data["email"] == "original@example.com"  # Email unchanged


@pytest.mark.api
class TestDeleteUserEndpoint:
    """Test DELETE /users/{user_id} endpoint."""

    def test_delete_user_when_exists_returns_204(self, client):
        """Test deleting an existing user."""
        # Arrange
        create_response = client.post("/users", json={"username": "todelete", "email": "delete@example.com"})
        user_id = create_response.json()["id"]

        # Act
        response = client.delete(f"/users/{user_id}")

        # Assert
        assert response.status_code == 204

        # Verify user is deleted
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_when_not_exists_returns_404(self, client):
        """Test deleting a non-existent user."""
        # Act
        response = client.delete("/users/999")

        # Assert
        assert response.status_code == 404


@pytest.mark.api
class TestUserEndpointsFlow:
    """Test complete user flow with users."""

    def test_complete_user_lifecycle(self, client):
        """Test complete CRUD flow for a user."""
        # 1. Create user
        create_response = client.post("/users", json={"username": "lifecycle_user", "email": "lifecycle@example.com"})
        assert create_response.status_code == 201
        user_id = create_response.json()["id"]

        # 2. Get user
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json()["username"] == "lifecycle_user"

        # 3. Update user
        update_response = client.put(
            f"/users/{user_id}", json={"username": "updated_lifecycle", "email": "updated@example.com"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["username"] == "updated_lifecycle"

        # 4. Verify in list
        list_response = client.get("/users")
        assert list_response.status_code == 200
        assert any(user["id"] == user_id for user in list_response.json())

        # 5. Delete user
        delete_response = client.delete(f"/users/{user_id}")
        assert delete_response.status_code == 204

        # 6. Verify deleted
        final_get = client.get(f"/users/{user_id}")
        assert final_get.status_code == 404
