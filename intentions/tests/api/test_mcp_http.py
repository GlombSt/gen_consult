"""
API tests for MCP HTTP transport endpoint.

Tests the MCP server HTTP transport integration at /mcp endpoint.
"""

import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.intents import mcp_sdk_http
from app.intents.repository import IntentRepository
from app.main import app
from app.shared.dependencies import get_intent_repository


@pytest.fixture
def client(test_db_session: AsyncSession) -> TestClient:
    """Create a test client with test database session."""

    def override_get_intent_repository() -> IntentRepository:
        return IntentRepository(test_db_session)

    # Patch MCP server's _get_repository to use test session
    async def mock_get_repository() -> tuple[IntentRepository, AsyncSession]:
        repository = IntentRepository(test_db_session)
        return repository, test_db_session

    app.dependency_overrides[get_intent_repository] = override_get_intent_repository
    with patch("app.intents.mcp_server._get_repository", side_effect=mock_get_repository):
        # Fresh manager per test to avoid reusing run() across TestClient lifespans.
        mcp_sdk_http.mcp_session_manager = mcp_sdk_http.StreamableHTTPSessionManager(
            app=mcp_sdk_http.server,
            json_response=True,
            stateless=True,
            security_settings=mcp_sdk_http._SECURITY_SETTINGS,
        )
        with TestClient(app) as test_client:
            yield test_client
    app.dependency_overrides.clear()


@pytest.mark.api
class TestMCPHTTPEndpoint:
    """Test MCP HTTP transport endpoint."""

    def test_initialize_request(self, client: TestClient) -> None:
        """Test MCP initialize request."""
        # Arrange
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "tests", "version": "0.1"},
            },
        }

        # Act
        response = client.post("/mcp", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data
        assert "protocolVersion" in data["result"]
        assert data["result"]["serverInfo"]["name"] == "intents-mcp-server"
        assert data["result"]["serverInfo"]["version"]

    def test_tools_list_request(self, client: TestClient) -> None:
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

        # Verify tool structure (V2)
        tool_names = [tool["name"] for tool in data["result"]["tools"]]
        assert "create_intent" in tool_names
        assert "get_intent" in tool_names
        assert "update_intent_name" in tool_names
        assert "update_intent_description" in tool_names
        assert "add_fact_to_intent" not in tool_names

    def test_tools_call_request(self, client: TestClient) -> None:
        """Test MCP tools/call request."""
        # Arrange - first create an intent via API (V2)
        create_response = client.post(
            "/intents",
            json={
                "name": "Test Intent",
                "description": "Test description",
            },
        )
        assert create_response.status_code == 201
        created_intent = create_response.json()

        request_data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_intent",
                "arguments": {"intent_id": created_intent["id"]},
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
        assert intent_data["id"] == created_intent["id"]
        assert intent_data["name"] == "Test Intent"

    def test_notification_request(self, client: TestClient) -> None:
        """Test MCP notification request (no response)."""
        # Arrange
        request_data = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        # Act
        response = client.post("/mcp", json=request_data)

        # Assert - notifications return no content or accepted
        assert response.status_code in {200, 202, 204}

    def test_invalid_json_rpc_version(self, client: TestClient) -> None:
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
        data = response.json()
        if response.status_code == 400 and "detail" in data:
            assert "Invalid" in data["detail"]
        else:
            assert data["jsonrpc"] == "2.0"
            assert "error" in data

    def test_invalid_method(self, client: TestClient) -> None:
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

        # Assert - should return JSON-RPC error response
        assert response.status_code in {200, 400}
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "error" in data
        assert data["error"]["code"] in {-32601, -32600, -32602}

    def test_invalid_json(self, client: TestClient) -> None:
        """Test request with invalid JSON."""
        # Act
        response = client.post(
            "/mcp",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

        # Assert
        data = response.json()
        if response.status_code == 400 and "detail" in data:
            assert "Invalid" in data["detail"]
        else:
            assert "error" in data

    def test_tools_call_missing_tool_name(self, client: TestClient) -> None:
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

        # Assert - should return JSON-RPC error response
        assert response.status_code in {200, 400}
        data = response.json()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "error" in data
        assert data["error"]["code"] in {-32602, -32600}
