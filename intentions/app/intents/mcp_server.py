"""
MCP Server for intents domain.

Exposes intents operations as MCP tools using the service layer as the port.
Uses schemas.py for parameter documentation and service.py docstrings for operation descriptions.
"""

import inspect
import json
from typing import Any

import mcp.types as types
from mcp.server.lowlevel import Server
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_session_factory
from app.shared.logging_config import logger

from . import service
from .models import Intent
from .repository import IntentRepository
from .schemas import (
    FactAddRequest,
    FactUpdateValueRequest,
    IntentCreateRequest,
    IntentUpdateConstraintsRequest,
    IntentUpdateContextRequest,
    IntentUpdateDescriptionRequest,
    IntentUpdateNameRequest,
    IntentUpdateOutputFormatRequest,
    IntentUpdateOutputStructureRequest,
)

# Create MCP server instance
server = Server("intents-mcp-server")


async def _get_repository() -> tuple[IntentRepository, AsyncSession]:
    """
    Create a repository instance with a database session.

    Returns:
        Tuple of (IntentRepository instance, AsyncSession)
    """
    session_factory = get_session_factory()
    # Create a new session for this tool call
    session = session_factory()
    repository = IntentRepository(session)
    return repository, session


def _pydantic_to_json_schema(pydantic_model: type) -> dict[str, Any]:
    """
    Convert a Pydantic model to JSON Schema.

    Args:
        pydantic_model: Pydantic model class

    Returns:
        JSON Schema dictionary
    """
    # Type ignore: Pydantic models have model_json_schema method
    return pydantic_model.model_json_schema(mode="serialization")  # type: ignore[no-any-return,attr-defined]


def _get_function_docstring(func) -> str:
    """
    Extract docstring from a function.

    Args:
        func: Function to extract docstring from

    Returns:
        Docstring or empty string
    """
    return inspect.getdoc(func) or ""


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """
    List available MCP tools for intents operations.

    Returns:
        List of MCP Tool definitions
    """
    # Convert Pydantic schemas to JSON Schema for tool parameters
    create_intent_schema = _pydantic_to_json_schema(IntentCreateRequest)
    update_name_schema = _pydantic_to_json_schema(IntentUpdateNameRequest)
    update_description_schema = _pydantic_to_json_schema(IntentUpdateDescriptionRequest)
    update_output_format_schema = _pydantic_to_json_schema(IntentUpdateOutputFormatRequest)
    update_output_structure_schema = _pydantic_to_json_schema(IntentUpdateOutputStructureRequest)
    update_context_schema = _pydantic_to_json_schema(IntentUpdateContextRequest)
    update_constraints_schema = _pydantic_to_json_schema(IntentUpdateConstraintsRequest)
    add_fact_schema = _pydantic_to_json_schema(FactAddRequest)
    update_fact_value_schema = _pydantic_to_json_schema(FactUpdateValueRequest)

    # Get docstrings from service functions for tool descriptions
    return [
        types.Tool(
            name="create_intent",
            description=_get_function_docstring(service.create_intent),
            inputSchema=create_intent_schema,
        ),
        types.Tool(
            name="get_intent",
            description=_get_function_docstring(service.get_intent),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {
                        "type": "integer",
                        "description": "The intent ID",
                    }
                },
                "required": ["intent_id"],
            },
        ),
        types.Tool(
            name="update_intent_name",
            description=_get_function_docstring(service.update_intent_name),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {
                        "type": "integer",
                        "description": "The intent ID to update",
                    },
                    **update_name_schema["properties"],
                },
                "required": ["intent_id", "name"],
            },
        ),
        types.Tool(
            name="update_intent_description",
            description=_get_function_docstring(service.update_intent_description),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {
                        "type": "integer",
                        "description": "The intent ID to update",
                    },
                    **update_description_schema["properties"],
                },
                "required": ["intent_id", "description"],
            },
        ),
        types.Tool(
            name="update_intent_output_format",
            description=_get_function_docstring(service.update_intent_output_format),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {
                        "type": "integer",
                        "description": "The intent ID to update",
                    },
                    **update_output_format_schema["properties"],
                },
                "required": ["intent_id", "output_format"],
            },
        ),
        types.Tool(
            name="update_intent_output_structure",
            description=_get_function_docstring(service.update_intent_output_structure),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {
                        "type": "integer",
                        "description": "The intent ID to update",
                    },
                    **update_output_structure_schema["properties"],
                },
                "required": ["intent_id"],
            },
        ),
        types.Tool(
            name="update_intent_context",
            description=_get_function_docstring(service.update_intent_context),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {
                        "type": "integer",
                        "description": "The intent ID to update",
                    },
                    **update_context_schema["properties"],
                },
                "required": ["intent_id"],
            },
        ),
        types.Tool(
            name="update_intent_constraints",
            description=_get_function_docstring(service.update_intent_constraints),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {
                        "type": "integer",
                        "description": "The intent ID to update",
                    },
                    **update_constraints_schema["properties"],
                },
                "required": ["intent_id"],
            },
        ),
        types.Tool(
            name="add_fact_to_intent",
            description=_get_function_docstring(service.add_fact_to_intent),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {
                        "type": "integer",
                        "description": "The intent ID to add the fact to",
                    },
                    **add_fact_schema["properties"],
                },
                "required": ["intent_id", "value"],
            },
        ),
        types.Tool(
            name="update_fact_value",
            description=_get_function_docstring(service.update_fact_value),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {
                        "type": "integer",
                        "description": "The intent ID",
                    },
                    "fact_id": {
                        "type": "integer",
                        "description": "The fact ID to update",
                    },
                    **update_fact_value_schema["properties"],
                },
                "required": ["intent_id", "fact_id", "value"],
            },
        ),
        types.Tool(
            name="remove_fact_from_intent",
            description=_get_function_docstring(service.remove_fact_from_intent),
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {
                        "type": "integer",
                        "description": "The intent ID",
                    },
                    "fact_id": {
                        "type": "integer",
                        "description": "The fact ID to remove",
                    },
                },
                "required": ["intent_id", "fact_id"],
            },
        ),
    ]


def _intent_to_dict(intent) -> dict[str, Any]:
    """
    Convert domain model intent to dictionary for MCP response.

    Args:
        intent: Domain model Intent instance

    Returns:
        Dictionary representation
    """
    return {
        "id": intent.id,
        "name": intent.name,
        "description": intent.description,
        "output_format": intent.output_format,
        "output_structure": intent.output_structure,
        "context": intent.context,
        "constraints": intent.constraints,
        "created_at": intent.created_at.isoformat() if intent.created_at else None,
        "updated_at": intent.updated_at.isoformat() if intent.updated_at else None,
        "facts": [
            {
                "id": fact.id,
                "intent_id": fact.intent_id,
                "value": fact.value,
                "created_at": fact.created_at.isoformat() if fact.created_at else None,
                "updated_at": fact.updated_at.isoformat() if fact.updated_at else None,
            }
            for fact in intent.facts
        ],
    }


def _fact_to_dict(fact) -> dict[str, Any]:
    """
    Convert domain model fact to dictionary for MCP response.

    Args:
        fact: Domain model Fact instance

    Returns:
        Dictionary representation
    """
    return {
        "id": fact.id,
        "intent_id": fact.intent_id,
        "value": fact.value,
        "created_at": fact.created_at.isoformat() if fact.created_at else None,
        "updated_at": fact.updated_at.isoformat() if fact.updated_at else None,
    }


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """
    Handle MCP tool calls by routing to appropriate service functions.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        List of TextContent with tool results

    Raises:
        ValueError: If tool name is unknown or required arguments are missing

    Note:
        Database session is properly managed:
        - Committed on successful operations
        - Rolled back on errors
        - Always closed in finally block
    """
    repository, session = await _get_repository()

    try:
        if name == "create_intent":
            request = IntentCreateRequest(**arguments)
            created_intent = await service.create_intent(request, repository)
            result_dict = _intent_to_dict(created_intent)
            await session.commit()
            return [types.TextContent(type="text", text=json.dumps(result_dict, indent=2))]

        elif name == "get_intent":
            intent_id = arguments.get("intent_id")
            if intent_id is None:
                raise ValueError("intent_id is required")
            intent_result = await service.get_intent(intent_id, repository)
            if intent_result is None:
                # Read operation - no commit needed, just close in finally
                return [types.TextContent(type="text", text="Intent not found")]
            # Type narrowing: intent is not None here (already checked above)
            result_dict = _intent_to_dict(intent_result)
            # Read operation - no commit needed, just close in finally
            return [types.TextContent(type="text", text=json.dumps(result_dict, indent=2))]

        elif name == "update_intent_name":
            intent_id = arguments.get("intent_id")
            name_arg = arguments.get("name")
            if intent_id is None or name_arg is None:
                raise ValueError("intent_id and name are required")
            # Type narrowing: name is not None here (already checked above)
            assert name_arg is not None
            name_str = str(name_arg)
            intent_result = await service.update_intent_name(intent_id, name_str, repository)
            if intent_result is None:
                # Not found - no changes to commit
                return [types.TextContent(type="text", text="Intent not found")]
            # Type narrowing: intent is not None here (already checked above)
            result_dict = _intent_to_dict(intent_result)
            await session.commit()
            return [types.TextContent(type="text", text=json.dumps(result_dict, indent=2))]

        elif name == "update_intent_description":
            intent_id = arguments.get("intent_id")
            description = arguments.get("description")
            if intent_id is None or description is None:
                raise ValueError("intent_id and description are required")
            intent_result = await service.update_intent_description(intent_id, description, repository)
            if intent_result is None:
                # Not found - no changes to commit
                return [types.TextContent(type="text", text="Intent not found")]
            # Type narrowing: intent is not None here (already checked above)
            result_dict = _intent_to_dict(intent_result)
            await session.commit()
            return [types.TextContent(type="text", text=json.dumps(result_dict, indent=2))]

        elif name == "update_intent_output_format":
            intent_id = arguments.get("intent_id")
            output_format = arguments.get("output_format")
            if intent_id is None or output_format is None:
                raise ValueError("intent_id and output_format are required")
            intent_result = await service.update_intent_output_format(intent_id, output_format, repository)
            if intent_result is None:
                # Not found - no changes to commit
                return [types.TextContent(type="text", text="Intent not found")]
            # Type narrowing: intent is not None here (already checked above)
            result_dict = _intent_to_dict(intent_result)
            await session.commit()
            return [types.TextContent(type="text", text=json.dumps(result_dict, indent=2))]

        elif name == "update_intent_output_structure":
            intent_id = arguments.get("intent_id")
            output_structure = arguments.get("output_structure")
            if intent_id is None:
                raise ValueError("intent_id is required")
            intent_result = await service.update_intent_output_structure(intent_id, output_structure, repository)
            if intent_result is None:
                # Not found - no changes to commit
                return [types.TextContent(type="text", text="Intent not found")]
            # Type narrowing: intent is not None here (already checked above)
            result_dict = _intent_to_dict(intent_result)
            await session.commit()
            return [types.TextContent(type="text", text=json.dumps(result_dict, indent=2))]

        elif name == "update_intent_context":
            intent_id = arguments.get("intent_id")
            context = arguments.get("context")
            if intent_id is None:
                raise ValueError("intent_id is required")
            intent_result = await service.update_intent_context(intent_id, context, repository)
            if intent_result is None:
                # Not found - no changes to commit
                return [types.TextContent(type="text", text="Intent not found")]
            # Type narrowing: intent is not None here (already checked above)
            result_dict = _intent_to_dict(intent_result)
            await session.commit()
            return [types.TextContent(type="text", text=json.dumps(result_dict, indent=2))]

        elif name == "update_intent_constraints":
            intent_id = arguments.get("intent_id")
            constraints = arguments.get("constraints")
            if intent_id is None:
                raise ValueError("intent_id is required")
            intent_result = await service.update_intent_constraints(intent_id, constraints, repository)
            if intent_result is None:
                # Not found - no changes to commit
                return [types.TextContent(type="text", text="Intent not found")]
            # Type narrowing: intent is not None here (already checked above)
            result_dict = _intent_to_dict(intent_result)
            await session.commit()
            return [types.TextContent(type="text", text=json.dumps(result_dict, indent=2))]

        elif name == "add_fact_to_intent":
            intent_id = arguments.get("intent_id")
            value = arguments.get("value")
            if intent_id is None or value is None:
                raise ValueError("intent_id and value are required")
            fact = await service.add_fact_to_intent(intent_id, value, repository)
            if fact is None:
                # Not found - no changes to commit
                return [types.TextContent(type="text", text="Intent not found")]
            result_dict = _fact_to_dict(fact)
            await session.commit()
            return [types.TextContent(type="text", text=json.dumps(result_dict, indent=2))]

        elif name == "update_fact_value":
            intent_id = arguments.get("intent_id")
            fact_id = arguments.get("fact_id")
            value = arguments.get("value")
            if intent_id is None or fact_id is None or value is None:
                raise ValueError("intent_id, fact_id, and value are required")
            fact = await service.update_fact_value(intent_id, fact_id, value, repository)
            if fact is None:
                # Not found - no changes to commit
                return [types.TextContent(type="text", text="Fact not found")]
            result_dict = _fact_to_dict(fact)
            await session.commit()
            return [types.TextContent(type="text", text=json.dumps(result_dict, indent=2))]

        elif name == "remove_fact_from_intent":
            intent_id = arguments.get("intent_id")
            fact_id = arguments.get("fact_id")
            if intent_id is None or fact_id is None:
                raise ValueError("intent_id and fact_id are required")
            removed = await service.remove_fact_from_intent(intent_id, fact_id, repository)
            if not removed:
                # Not found - no changes to commit
                return [types.TextContent(type="text", text="Fact not found")]
            await session.commit()
            return [types.TextContent(type="text", text="Fact removed successfully")]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        await session.rollback()
        logger.error(f"Error calling tool {name}: {str(e)}", extra={"tool_name": name, "error": str(e)})
        raise
    finally:
        await session.close()
