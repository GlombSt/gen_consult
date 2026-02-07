"""
API tests for intents endpoints (V2).

Tests full HTTP stack with TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from app.intents.repository import IntentRepository
from app.main import app
from app.shared.dependencies import get_intent_repository


@pytest.fixture
def client(test_db_session):
    """Create a test client with test database session."""

    def override_get_intent_repository():
        return IntentRepository(test_db_session)

    app.dependency_overrides[get_intent_repository] = override_get_intent_repository
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.mark.api
class TestCreateIntentEndpoint:
    """Test POST /intents endpoint (V2)."""

    def test_create_intent_with_valid_data_returns_201(self, client):
        """Test creating an intent with valid data."""
        payload = {
            "name": "New Intent",
            "description": "Test description",
        }
        response = client.post("/intents", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == "New Intent"
        assert data["description"] == "Test description"
        assert "aspects" in data
        assert isinstance(data["aspects"], list)
        assert len(data["aspects"]) == 0

    def test_create_intent_without_name_returns_422(self, client):
        """Test creating an intent without name."""
        payload = {"description": "Test description"}
        response = client.post("/intents", json=payload)
        assert response.status_code == 422

    def test_create_intent_without_description_returns_422(self, client):
        """Test creating an intent without description."""
        payload = {"name": "Test Intent"}
        response = client.post("/intents", json=payload)
        assert response.status_code == 422


@pytest.mark.api
class TestGetIntentByIdEndpoint:
    """Test GET /intents/{intent_id} endpoint."""

    def test_get_intent_when_exists_returns_intent(self, client):
        """Test getting an existing intent."""
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description"},
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        response = client.get(f"/intents/{created_intent['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_intent["id"]
        assert data["name"] == "Test Intent"
        assert data["description"] == "Test description"
        assert "aspects" in data
        assert isinstance(data["aspects"], list)

    def test_get_intent_when_not_exists_returns_404(self, client):
        """Test getting a non-existent intent."""
        response = client.get("/intents/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.api
class TestUpdateIntentNameEndpoint:
    """Test PATCH /intents/{intent_id}/name endpoint."""

    def test_update_intent_name_when_exists_returns_200(self, client):
        """Test updating an existing intent's name."""
        create_response = client.post(
            "/intents",
            json={
                "name": "Original Name",
                "description": "Test description",
            },
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"name": "Updated Name"}
        response = client.patch(f"/intents/{created_intent['id']}/name", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["id"] == created_intent["id"]

    def test_update_intent_name_when_not_exists_returns_404(self, client):
        """Test updating a non-existent intent's name."""
        payload = {"name": "Updated Name"}
        response = client.patch("/intents/999/name", json=payload)
        assert response.status_code == 404

    def test_update_intent_name_with_empty_name_returns_422(self, client):
        """Test updating intent name with empty name."""
        create_response = client.post(
            "/intents",
            json={
                "name": "Original Name",
                "description": "Test description",
            },
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"name": ""}
        response = client.patch(f"/intents/{created_intent['id']}/name", json=payload)
        assert response.status_code == 422


@pytest.mark.api
class TestUpdateIntentDescriptionEndpoint:
    """Test PATCH /intents/{intent_id}/description endpoint."""

    def test_update_intent_description_when_exists_returns_200(self, client):
        """Test updating an existing intent's description."""
        create_response = client.post(
            "/intents",
            json={
                "name": "Test Intent",
                "description": "Original description",
            },
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"description": "Updated description"}
        response = client.patch(f"/intents/{created_intent['id']}/description", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"


@pytest.mark.api
class TestIntentEndpointsFlow:
    """Test complete user flow with intents (V2)."""

    def test_complete_intent_lifecycle(self, client):
        """Test complete flow: create, get, update name, update description."""
        create_response = client.post(
            "/intents",
            json={
                "name": "Original Name",
                "description": "Original description",
            },
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        get_response = client.get(f"/intents/{created_intent['id']}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Original Name"

        update_name_response = client.patch(
            f"/intents/{created_intent['id']}/name",
            json={"name": "Updated Name"},
        )
        assert update_name_response.status_code == 200
        assert update_name_response.json()["name"] == "Updated Name"

        update_desc_response = client.patch(
            f"/intents/{created_intent['id']}/description",
            json={"description": "Updated description"},
        )
        assert update_desc_response.status_code == 200
        assert update_desc_response.json()["description"] == "Updated description"
