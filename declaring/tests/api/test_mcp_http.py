"""
API tests for MCP HTTP transport endpoint.

Tests the MCP server HTTP transport integration at /mcp endpoint.
"""

import json

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
class TestMCPHTTPEndpoint:
    """Test MCP HTTP transport endpoint."""

    def test_initialize_request(self, client):
        """Test MCP initialize request."""
        # Arrange
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }

        # Act
        response = client.post("/mcp", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data
        assert data["result"]["protocolVersion"] == "2024-11-05"
        assert data["result"]["serverInfo"]["name"] == "intents-mcp-server"
        assert data["result"]["serverInfo"]["version"] == "1.0.0"

    def test_tools_list_request(self, client):
        """Test MCP tools/list request."""
        # Arrange
        request_data = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        }

        # Act
        response = client.post("/mcp", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 2
        assert "result" in data
        assert "tools" in data["result"]
        assert len(data["result"]["tools"]) > 0

        # Verify tool structure
        tool_names = [tool["name"] for tool in data["result"]["tools"]]
        assert "create_intent" in tool_names
        assert "get_intent" in tool_names
        assert "add_fact_to_intent" in tool_names

    @pytest.mark.asyncio
    async def test_tools_call_request(self, client, test_db_session):
        """Test MCP tools/call request."""
        # Arrange - first create an intent via service
        from app.intents import service
        from app.intents.repository import IntentRepository
        from app.intents.schemas import IntentCreateRequest

        repository = IntentRepository(test_db_session)
        create_request = IntentCreateRequest(
            name="Test Intent",
            description="Test description",
            output_format="JSON",
        )
        intent = await service.create_intent(create_request, repository)
        await test_db_session.commit()

        request_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_intent",
                "arguments": {"intent_id": intent.id},
            },
        }

        # Act
        response = client.post("/mcp", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 3
        assert "result" in data
        assert "content" in data["result"]
        assert len(data["result"]["content"]) > 0
        assert data["result"]["content"][0]["type"] == "text"

        # Verify intent data in response
        intent_data = json.loads(data["result"]["content"][0]["text"])
        assert intent_data["id"] == intent.id
        assert intent_data["name"] == "Test Intent"

    def test_notification_request(self, client):
        """Test MCP notification request (no response)."""
        # Arrange
        request_data = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        # Act
        response = client.post("/mcp", json=request_data)

        # Assert - notifications return 204 No Content
        assert response.status_code == 204

    def test_invalid_json_rpc_version(self, client):
        """Test request with invalid JSON-RPC version."""
        # Arrange
        request_data = {
            "jsonrpc": "1.0",
            "id": 1,
            "method": "initialize",
            "params": {},
        }

        # Act
        response = client.post("/mcp", json=request_data)

        # Assert
        assert response.status_code == 400
        assert "Invalid JSON-RPC request" in response.json()["detail"]

    def test_invalid_method(self, client):
        """Test request with invalid method."""
        # Arrange
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "invalid/method",
            "params": {},
        }

        # Act
        response = client.post("/mcp", json=request_data)

        # Assert
        assert response.status_code == 400
        assert "Unknown method" in response.json()["detail"]

    def test_invalid_json(self, client):
        """Test request with invalid JSON."""
        # Act
        response = client.post(
            "/mcp",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

        # Assert
        assert response.status_code == 400
        assert "Invalid JSON" in response.json()["detail"]

    def test_tools_call_missing_tool_name(self, client):
        """Test tools/call request with missing tool name."""
        # Arrange
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "arguments": {},
            },
        }

        # Act
        response = client.post("/mcp", json=request_data)

        # Assert
        assert response.status_code == 400
        assert "Tool name is required" in response.json()["detail"]

