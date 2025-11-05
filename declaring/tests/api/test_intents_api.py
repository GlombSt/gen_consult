"""
API tests for intents endpoints.

Tests full HTTP stack with TestClient.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.shared.database import get_db


@pytest.fixture
def client(test_db_session):
    """Create a test client with test database session."""
    async def override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()




@pytest.mark.api
class TestCreateIntentEndpoint:
    """Test POST /intents endpoint (US-000)."""

    def test_create_intent_with_valid_data_returns_201(self, client):
        """Test creating an intent with valid data."""
        # Arrange
        payload = {
            "name": "New Intent",
            "description": "Test description",
            "output_format": "JSON",
        }

        # Act
        response = client.post("/intents", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == "New Intent"
        assert data["description"] == "Test description"
        assert data["output_format"] == "JSON"
        assert "facts" in data
        assert isinstance(data["facts"], list)
        assert len(data["facts"]) == 0

    def test_create_intent_with_all_fields_returns_201(self, client):
        """Test creating an intent with all fields including optional ones."""
        # Arrange
        payload = {
            "name": "Complete Intent",
            "description": "Complete description",
            "output_format": "XML",
            "output_structure": "Structured output",
            "context": "Test context",
            "constraints": "Test constraints",
        }

        # Act
        response = client.post("/intents", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Complete Intent"
        assert data["output_format"] == "XML"
        assert data["output_structure"] == "Structured output"
        assert data["context"] == "Test context"
        assert data["constraints"] == "Test constraints"

    def test_create_intent_without_name_returns_422(self, client):
        """Test creating an intent without name."""
        # Arrange
        payload = {"description": "Test description", "output_format": "JSON"}

        # Act
        response = client.post("/intents", json=payload)

        # Assert
        assert response.status_code == 422

    def test_create_intent_without_description_returns_422(self, client):
        """Test creating an intent without description."""
        # Arrange
        payload = {"name": "Test Intent", "output_format": "JSON"}

        # Act
        response = client.post("/intents", json=payload)

        # Assert
        assert response.status_code == 422

    def test_create_intent_without_output_format_returns_422(self, client):
        """Test creating an intent without output format."""
        # Arrange
        payload = {"name": "Test Intent", "description": "Test description"}

        # Act
        response = client.post("/intents", json=payload)

        # Assert
        assert response.status_code == 422

    def test_create_intent_with_minimum_fields_returns_201(self, client):
        """Test creating an intent with minimum required fields only."""
        # Arrange
        payload = {
            "name": "Minimal Intent",
            "description": "Minimal description",
            "output_format": "plain text",
        }

        # Act
        response = client.post("/intents", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Intent"
        assert data["description"] == "Minimal description"
        assert data["output_format"] == "plain text"
        assert data["output_structure"] is None
        assert data["context"] is None
        assert data["constraints"] is None


@pytest.mark.api
class TestGetIntentsEndpoint:
    """Test GET /intents endpoint."""

    def test_get_intents_when_empty_returns_empty_list(self, client):
        """Test getting intents when none exist."""
        # Act
        response = client.get("/intents")

        # Assert
        assert response.status_code == 200
        assert response.json() == []

    def test_get_intents_returns_all_intents(self, client):
        """Test getting all intents."""
        # Arrange - Create intents via API
        client.post("/intents", json={"name": "Intent 1", "description": "Desc 1", "output_format": "JSON"})
        client.post("/intents", json={"name": "Intent 2", "description": "Desc 2", "output_format": "XML"})

        # Act
        response = client.get("/intents")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(item["name"] == "Intent 1" for item in data)
        assert any(item["name"] == "Intent 2" for item in data)


@pytest.mark.api
class TestGetIntentByIdEndpoint:
    """Test GET /intents/{intent_id} endpoint."""

    def test_get_intent_when_exists_returns_intent(self, client):
        """Test getting an existing intent."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "JSON"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        # Act
        response = client.get(f"/intents/{created_intent['id']}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_intent["id"]
        assert data["name"] == "Test Intent"
        assert data["description"] == "Test description"
        assert data["output_format"] == "JSON"
        assert "facts" in data
        assert isinstance(data["facts"], list)

    def test_get_intent_when_not_exists_returns_404(self, client):
        """Test getting a non-existent intent."""
        # Act
        response = client.get("/intents/999")

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.api
class TestUpdateIntentNameEndpoint:
    """Test PATCH /intents/{intent_id}/name endpoint (US-001)."""

    def test_update_intent_name_when_exists_returns_200(self, client):
        """Test updating an existing intent's name."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Original Name", "description": "Test description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"name": "Updated Name"}

        # Act
        response = client.patch(f"/intents/{created_intent['id']}/name", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["id"] == created_intent["id"]

    def test_update_intent_name_when_not_exists_returns_404(self, client):
        """Test updating a non-existent intent's name."""
        # Arrange
        payload = {"name": "Updated Name"}

        # Act
        response = client.patch("/intents/999/name", json=payload)

        # Assert
        assert response.status_code == 404

    def test_update_intent_name_with_empty_name_returns_422(self, client):
        """Test updating intent name with empty name."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Original Name", "description": "Test description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"name": ""}

        # Act
        response = client.patch(f"/intents/{created_intent['id']}/name", json=payload)

        # Assert
        assert response.status_code == 422  # Validation error


@pytest.mark.api
class TestUpdateIntentDescriptionEndpoint:
    """Test PATCH /intents/{intent_id}/description endpoint (US-002)."""

    def test_update_intent_description_when_exists_returns_200(self, client):
        """Test updating an existing intent's description."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Original description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"description": "Updated description"}

        # Act
        response = client.patch(f"/intents/{created_intent['id']}/description", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"


@pytest.mark.api
class TestUpdateIntentOutputFormatEndpoint:
    """Test PATCH /intents/{intent_id}/output-format endpoint (US-003)."""

    def test_update_intent_output_format_when_exists_returns_200(self, client):
        """Test updating an existing intent's output format."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"output_format": "JSON"}

        # Act
        response = client.patch(f"/intents/{created_intent['id']}/output-format", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["output_format"] == "JSON"


@pytest.mark.api
class TestUpdateIntentOutputStructureEndpoint:
    """Test PATCH /intents/{intent_id}/output-structure endpoint (US-004)."""

    def test_update_intent_output_structure_when_exists_returns_200(self, client):
        """Test updating an existing intent's output structure."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text", "output_structure": "Old structure"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"output_structure": "New structure"}

        # Act
        response = client.patch(f"/intents/{created_intent['id']}/output-structure", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["output_structure"] == "New structure"

    def test_update_intent_output_structure_with_none_returns_200(self, client):
        """Test updating output structure to None."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text", "output_structure": "Old structure"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"output_structure": None}

        # Act
        response = client.patch(f"/intents/{created_intent['id']}/output-structure", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["output_structure"] is None


@pytest.mark.api
class TestUpdateIntentContextEndpoint:
    """Test PATCH /intents/{intent_id}/context endpoint (US-005)."""

    def test_update_intent_context_when_exists_returns_200(self, client):
        """Test updating an existing intent's context."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text", "context": "Old context"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"context": "New context"}

        # Act
        response = client.patch(f"/intents/{created_intent['id']}/context", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["context"] == "New context"


@pytest.mark.api
class TestUpdateIntentConstraintsEndpoint:
    """Test PATCH /intents/{intent_id}/constraints endpoint (US-006)."""

    def test_update_intent_constraints_when_exists_returns_200(self, client):
        """Test updating an existing intent's constraints."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text", "constraints": "Old constraints"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"constraints": "New constraints"}

        # Act
        response = client.patch(f"/intents/{created_intent['id']}/constraints", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["constraints"] == "New constraints"


@pytest.mark.api
class TestAddFactToIntentEndpoint:
    """Test POST /intents/{intent_id}/facts endpoint (US-008)."""

    def test_add_fact_when_intent_exists_returns_201(self, client):
        """Test adding a fact to an existing intent."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"value": "Test fact value"}

        # Act
        response = client.post(f"/intents/{created_intent['id']}/facts", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["intent_id"] == created_intent["id"]
        assert data["value"] == "Test fact value"
        assert data["id"] is not None

    def test_add_fact_when_intent_not_exists_returns_404(self, client):
        """Test adding a fact to a non-existent intent."""
        # Arrange
        payload = {"value": "Test fact value"}

        # Act
        response = client.post("/intents/999/facts", json=payload)

        # Assert
        assert response.status_code == 404

    def test_add_fact_with_empty_value_returns_422(self, client):
        """Test adding a fact with empty value."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"value": ""}

        # Act
        response = client.post(f"/intents/{created_intent['id']}/facts", json=payload)

        # Assert
        assert response.status_code == 422  # Validation error


@pytest.mark.api
class TestUpdateFactValueEndpoint:
    """Test PATCH /intents/{intent_id}/facts/{fact_id}/value endpoint (US-007)."""

    def test_update_fact_value_when_exists_returns_200(self, client):
        """Test updating an existing fact's value."""
        # Arrange - Create intent and fact via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        # Add fact
        add_fact_response = client.post(f"/intents/{created_intent['id']}/facts", json={"value": "Original value"})
        assert add_fact_response.status_code == 201
        fact = add_fact_response.json()

        payload = {"value": "Updated value"}

        # Act
        response = client.patch(f"/intents/{created_intent['id']}/facts/{fact['id']}/value", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == "Updated value"
        assert data["id"] == fact["id"]

    def test_update_fact_value_when_fact_not_exists_returns_404(self, client):
        """Test updating a non-existent fact."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        payload = {"value": "Updated value"}

        # Act
        response = client.patch(f"/intents/{created_intent['id']}/facts/999/value", json=payload)

        # Assert
        assert response.status_code == 404

    def test_update_fact_value_when_intent_not_exists_returns_404(self, client):
        """Test updating a fact for a non-existent intent."""
        # Arrange
        payload = {"value": "Updated value"}

        # Act
        response = client.patch("/intents/999/facts/1/value", json=payload)

        # Assert
        assert response.status_code == 404


@pytest.mark.api
class TestRemoveFactFromIntentEndpoint:
    """Test DELETE /intents/{intent_id}/facts/{fact_id} endpoint (US-009)."""

    def test_remove_fact_when_exists_returns_204(self, client):
        """Test removing an existing fact."""
        # Arrange - Create intent and fact via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        # Add fact
        add_fact_response = client.post(f"/intents/{created_intent['id']}/facts", json={"value": "To remove"})
        assert add_fact_response.status_code == 201
        fact = add_fact_response.json()

        # Act
        response = client.delete(f"/intents/{created_intent['id']}/facts/{fact['id']}")

        # Assert
        assert response.status_code == 204

        # Verify fact is removed
        get_response = client.get(f"/intents/{created_intent['id']}")
        assert get_response.status_code == 200
        facts = get_response.json()["facts"]
        assert len(facts) == 0

    def test_remove_fact_when_not_exists_returns_404(self, client):
        """Test removing a non-existent fact."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        # Act
        response = client.delete(f"/intents/{created_intent['id']}/facts/999")

        # Assert
        assert response.status_code == 404


@pytest.mark.api
class TestIntentEndpointsFlow:
    """Test complete user flow with intents."""

    def test_complete_intent_lifecycle(self, client):
        """Test complete flow: create, update multiple fields, add facts, update facts, remove facts."""
        # Arrange - Create intent via API
        create_response = client.post(
            "/intents",
            json={"name": "Original Name", "description": "Original description", "output_format": "plain text"}
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        # 1. Get intent
        get_response = client.get(f"/intents/{created_intent['id']}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Original Name"

        # 2. Update name
        update_name_response = client.patch(f"/intents/{created_intent['id']}/name", json={"name": "Updated Name"})
        assert update_name_response.status_code == 200
        assert update_name_response.json()["name"] == "Updated Name"

        # 3. Update description
        update_desc_response = client.patch(f"/intents/{created_intent['id']}/description", json={"description": "Updated description"})
        assert update_desc_response.status_code == 200
        assert update_desc_response.json()["description"] == "Updated description"

        # 4. Update output format
        update_format_response = client.patch(f"/intents/{created_intent['id']}/output-format", json={"output_format": "JSON"})
        assert update_format_response.status_code == 200
        assert update_format_response.json()["output_format"] == "JSON"

        # 5. Add fact
        add_fact_response = client.post(f"/intents/{created_intent['id']}/facts", json={"value": "Fact 1"})
        assert add_fact_response.status_code == 201
        fact_id = add_fact_response.json()["id"]

        # 6. Add another fact
        add_fact2_response = client.post(f"/intents/{created_intent['id']}/facts", json={"value": "Fact 2"})
        assert add_fact2_response.status_code == 201

        # 7. Get intent with facts
        get_with_facts_response = client.get(f"/intents/{created_intent['id']}")
        assert get_with_facts_response.status_code == 200
        facts = get_with_facts_response.json()["facts"]
        assert len(facts) == 2

        # 8. Update fact value
        update_fact_response = client.patch(f"/intents/{created_intent['id']}/facts/{fact_id}/value", json={"value": "Updated Fact 1"})
        assert update_fact_response.status_code == 200
        assert update_fact_response.json()["value"] == "Updated Fact 1"

        # 9. Remove fact
        remove_fact_response = client.delete(f"/intents/{created_intent['id']}/facts/{fact_id}")
        assert remove_fact_response.status_code == 204

        # 10. Verify fact removed
        final_get_response = client.get(f"/intents/{created_intent['id']}")
        assert final_get_response.status_code == 200
        final_facts = final_get_response.json()["facts"]
        assert len(final_facts) == 1
        assert final_facts[0]["value"] == "Fact 2"

