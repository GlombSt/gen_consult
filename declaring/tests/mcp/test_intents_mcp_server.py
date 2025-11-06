"""
Integration tests for intents MCP server.

Tests MCP server functionality with real database and service layer.
"""

import json
from unittest.mock import patch

import pytest
from mcp.types import TextContent

from app.intents.mcp_server import (
    _fact_to_dict,
    _get_function_docstring,
    _intent_to_dict,
    _pydantic_to_json_schema,
    call_tool,
    list_tools,
)
from app.intents.repository import IntentRepository
from app.intents.schemas import IntentCreateRequest


@pytest.mark.integration
class TestIntentsMCPServer:
    """Test intents MCP server functionality."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_all_tools(self):
        """Test that list_tools returns all available tools."""
        # Act
        tools = await list_tools()

        # Assert
        assert len(tools) > 0
        tool_names = [tool.name for tool in tools]
        assert "create_intent" in tool_names
        assert "get_intent" in tool_names
        assert "update_intent_name" in tool_names
        assert "add_fact_to_intent" in tool_names
        assert "update_fact_value" in tool_names
        assert "remove_fact_from_intent" in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_has_descriptions(self):
        """Test that all tools have descriptions."""
        # Act
        tools = await list_tools()

        # Assert
        for tool in tools:
            assert tool.description is not None
            assert len(tool.description) > 0

    @pytest.mark.asyncio
    async def test_list_tools_has_input_schemas(self):
        """Test that all tools have input schemas."""
        # Act
        tools = await list_tools()

        # Assert
        for tool in tools:
            assert tool.inputSchema is not None
            assert "type" in tool.inputSchema
            assert tool.inputSchema["type"] == "object"

    @pytest.mark.asyncio
    async def test_call_tool_create_intent(self, test_db_session):
        """Test creating an intent via MCP tool."""
        # Arrange
        repository = IntentRepository(test_db_session)
        arguments = {
            "name": "Test Intent",
            "description": "Test description",
            "output_format": "JSON",
        }

        # Mock _get_repository to use test session
        async def mock_get_repository():
            return repository, test_db_session

        # Act
        with patch("app.intents.mcp_server._get_repository", side_effect=mock_get_repository):
            result = await call_tool("create_intent", arguments)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].type == "text"
        result_data = json.loads(result[0].text)
        assert result_data["name"] == "Test Intent"
        assert result_data["description"] == "Test description"
        assert result_data["output_format"] == "JSON"
        assert "id" in result_data

        # Verify intent was created in database
        await test_db_session.commit()
        created_intent = await repository.find_by_id(result_data["id"])
        assert created_intent is not None
        assert created_intent.name == "Test Intent"

    @pytest.mark.asyncio
    async def test_call_tool_get_intent(self, test_db_session):
        """Test getting an intent via MCP tool."""
        # Arrange
        repository = IntentRepository(test_db_session)
        create_request = IntentCreateRequest(
            name="Test Intent",
            description="Test description",
            output_format="JSON",
        )
        from app.intents import service

        created_intent = await service.create_intent(create_request, repository)
        await test_db_session.commit()

        arguments = {"intent_id": created_intent.id}

        # Mock _get_repository to use test session
        async def mock_get_repository():
            return repository, test_db_session

        # Act
        with patch("app.intents.mcp_server._get_repository", side_effect=mock_get_repository):
            result = await call_tool("get_intent", arguments)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        result_data = json.loads(result[0].text)
        assert result_data["id"] == created_intent.id
        assert result_data["name"] == "Test Intent"

    @pytest.mark.asyncio
    async def test_call_tool_get_intent_not_found(self, test_db_session):
        """Test getting a non-existent intent via MCP tool."""
        # Arrange
        repository = IntentRepository(test_db_session)
        arguments = {"intent_id": 99999}

        # Mock _get_repository to use test session
        async def mock_get_repository():
            return repository, test_db_session

        # Act
        with patch("app.intents.mcp_server._get_repository", side_effect=mock_get_repository):
            result = await call_tool("get_intent", arguments)

        # Assert
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "Intent not found"

    @pytest.mark.asyncio
    async def test_call_tool_update_intent_name(self, test_db_session):
        """Test updating intent name via MCP tool."""
        # Arrange
        repository = IntentRepository(test_db_session)
        create_request = IntentCreateRequest(
            name="Original Name",
            description="Test description",
            output_format="JSON",
        )
        from app.intents import service

        created_intent = await service.create_intent(create_request, repository)
        await test_db_session.commit()

        arguments = {"intent_id": created_intent.id, "name": "Updated Name"}

        # Mock _get_repository to use test session
        async def mock_get_repository():
            return repository, test_db_session

        # Act
        with patch("app.intents.mcp_server._get_repository", side_effect=mock_get_repository):
            result = await call_tool("update_intent_name", arguments)

        # Assert
        assert len(result) == 1
        result_data = json.loads(result[0].text)
        assert result_data["name"] == "Updated Name"

        # Verify update in database
        await test_db_session.commit()
        updated_intent = await repository.find_by_id(created_intent.id)
        assert updated_intent.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_call_tool_add_fact_to_intent(self, test_db_session):
        """Test adding a fact to an intent via MCP tool."""
        # Arrange
        repository = IntentRepository(test_db_session)
        create_request = IntentCreateRequest(
            name="Test Intent",
            description="Test description",
            output_format="JSON",
        )
        from app.intents import service

        created_intent = await service.create_intent(create_request, repository)
        await test_db_session.commit()

        arguments = {"intent_id": created_intent.id, "value": "Test fact value"}

        # Mock _get_repository to use test session
        async def mock_get_repository():
            return repository, test_db_session

        # Act
        with patch("app.intents.mcp_server._get_repository", side_effect=mock_get_repository):
            result = await call_tool("add_fact_to_intent", arguments)

        # Assert
        assert len(result) == 1
        result_data = json.loads(result[0].text)
        assert result_data["value"] == "Test fact value"
        assert result_data["intent_id"] == created_intent.id
        assert "id" in result_data

        # Verify fact was added
        await test_db_session.commit()
        intent_with_facts = await repository.find_by_id(created_intent.id)
        assert len(intent_with_facts.facts) == 1
        assert intent_with_facts.facts[0].value == "Test fact value"

    @pytest.mark.asyncio
    async def test_call_tool_invalid_tool_name(self, test_db_session):
        """Test calling an invalid tool name."""
        # Arrange
        repository = IntentRepository(test_db_session)
        arguments = {}

        # Mock _get_repository to use test session
        async def mock_get_repository():
            return repository, test_db_session

        # Act & Assert
        with patch("app.intents.mcp_server._get_repository", side_effect=mock_get_repository):
            with pytest.raises(ValueError, match="Unknown tool"):
                await call_tool("invalid_tool", arguments)

    @pytest.mark.asyncio
    async def test_call_tool_missing_required_argument(self, test_db_session):
        """Test calling a tool with missing required arguments."""
        # Arrange
        repository = IntentRepository(test_db_session)
        arguments = {}  # Missing intent_id

        # Mock _get_repository to use test session
        async def mock_get_repository():
            return repository, test_db_session

        # Act & Assert
        with patch("app.intents.mcp_server._get_repository", side_effect=mock_get_repository):
            with pytest.raises(ValueError, match="intent_id is required"):
                await call_tool("get_intent", arguments)

    @pytest.mark.asyncio
    async def test_pydantic_to_json_schema(self):
        """Test Pydantic to JSON Schema conversion."""
        # Act
        schema = _pydantic_to_json_schema(IntentCreateRequest)

        # Assert
        assert schema is not None
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "name" in schema["properties"]
        assert "description" in schema["properties"]

    @pytest.mark.asyncio
    async def test_get_function_docstring(self):
        """Test docstring extraction from service functions."""
        # Arrange
        from app.intents import service

        # Act
        docstring = _get_function_docstring(service.create_intent)

        # Assert
        assert docstring is not None
        assert len(docstring) > 0
        assert "Create" in docstring or "create" in docstring

    @pytest.mark.asyncio
    async def test_intent_to_dict(self, test_db_session):
        """Test intent to dictionary conversion."""
        # Arrange
        repository = IntentRepository(test_db_session)
        create_request = IntentCreateRequest(
            name="Test Intent",
            description="Test description",
            output_format="JSON",
        )
        from app.intents import service

        created_intent = await service.create_intent(create_request, repository)
        await test_db_session.commit()

        # Act
        result_dict = _intent_to_dict(created_intent)

        # Assert
        assert result_dict["id"] == created_intent.id
        assert result_dict["name"] == "Test Intent"
        assert result_dict["description"] == "Test description"
        assert result_dict["output_format"] == "JSON"
        assert "created_at" in result_dict
        assert "updated_at" in result_dict
        assert "facts" in result_dict
        assert isinstance(result_dict["facts"], list)

    @pytest.mark.asyncio
    async def test_fact_to_dict(self, test_db_session):
        """Test fact to dictionary conversion."""
        # Arrange
        repository = IntentRepository(test_db_session)
        create_request = IntentCreateRequest(
            name="Test Intent",
            description="Test description",
            output_format="JSON",
        )
        from app.intents import service

        created_intent = await service.create_intent(create_request, repository)
        await test_db_session.commit()

        fact = await service.add_fact_to_intent(created_intent.id, "Test fact", repository)
        await test_db_session.commit()

        # Act
        result_dict = _fact_to_dict(fact)

        # Assert
        assert result_dict["id"] == fact.id
        assert result_dict["intent_id"] == fact.intent_id
        assert result_dict["value"] == "Test fact"
        assert "created_at" in result_dict
        assert "updated_at" in result_dict

    @pytest.mark.asyncio
    async def test_database_session_management(self, test_db_session):
        """Test that database sessions are properly managed."""
        # Arrange
        repository = IntentRepository(test_db_session)
        arguments = {
            "name": "Session Test Intent",
            "description": "Test description",
            "output_format": "JSON",
        }

        # Mock _get_repository to use test session
        async def mock_get_repository():
            return repository, test_db_session

        # Act
        with patch("app.intents.mcp_server._get_repository", side_effect=mock_get_repository):
            result = await call_tool("create_intent", arguments)

        # Assert - session should be committed and closed
        assert len(result) == 1
        result_data = json.loads(result[0].text)
        intent_id = result_data["id"]

        # Verify intent is accessible in a new session
        await test_db_session.commit()
        new_repository = IntentRepository(test_db_session)
        retrieved_intent = await new_repository.find_by_id(intent_id)
        assert retrieved_intent is not None
        assert retrieved_intent.name == "Session Test Intent"
