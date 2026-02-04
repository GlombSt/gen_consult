"""
MCP Server for intents domain (V2).

Exposes intents operations as MCP tools using the service layer as the port.
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
from .repository import IntentRepository
from .schemas import (
    IntentCreateRequest,
    IntentUpdateDescriptionRequest,
    IntentUpdateNameRequest,
)

# Create MCP server instance
server = Server("intents-mcp-server")


async def _get_repository() -> tuple[IntentRepository, AsyncSession]:
    """Create a repository instance with a database session."""
    session_factory = get_session_factory()
    session = session_factory()
    repository = IntentRepository(session)
    return repository, session


def _pydantic_to_json_schema(pydantic_model: type) -> dict[str, Any]:
    """Convert a Pydantic model to JSON Schema."""
    return pydantic_model.model_json_schema(mode="serialization")  # type: ignore[no-any-return,attr-defined]


def _get_function_docstring(func) -> str:
    """Extract docstring from a function."""
    return inspect.getdoc(func) or ""


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available MCP tools for intents operations (V2)."""
    create_intent_schema = _pydantic_to_json_schema(IntentCreateRequest)
    update_name_schema = _pydantic_to_json_schema(IntentUpdateNameRequest)
    update_description_schema = _pydantic_to_json_schema(
        IntentUpdateDescriptionRequest
    )

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
    ]


def _intent_to_dict(intent) -> dict[str, Any]:
    """Convert domain model intent to dictionary for MCP response (V2)."""
    return {
        "id": intent.id,
        "name": intent.name,
        "description": intent.description,
        "created_at": intent.created_at.isoformat() if intent.created_at else None,
        "updated_at": intent.updated_at.isoformat() if intent.updated_at else None,
        "aspects": [{"id": a.id, "name": a.name} for a in intent.aspects],
        "inputs": [{"id": i.id, "name": i.name} for i in intent.inputs],
        "choices": [{"id": c.id, "name": c.name} for c in intent.choices],
        "pitfalls": [{"id": p.id} for p in intent.pitfalls],
        "assumptions": [{"id": a.id} for a in intent.assumptions],
        "qualities": [{"id": q.id} for q in intent.qualities],
        "examples": [{"id": e.id} for e in intent.examples],
        "prompts": [{"id": p.id, "version": p.version} for p in intent.prompts],
        "insights": [{"id": i.id} for i in intent.insights],
    }


@server.call_tool()
async def call_tool(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent]:
    """Handle MCP tool calls by routing to appropriate service functions (V2)."""
    repository, session = await _get_repository()

    try:
        if name == "create_intent":
            request = IntentCreateRequest(**arguments)
            created_intent = await service.create_intent(request, repository)
            result_dict = _intent_to_dict(created_intent)
            await session.commit()
            return [
                types.TextContent(
                    type="text", text=json.dumps(result_dict, indent=2)
                )
            ]

        elif name == "get_intent":
            intent_id = arguments.get("intent_id")
            if intent_id is None:
                raise ValueError("intent_id is required")
            intent_result = await service.get_intent(intent_id, repository)
            if intent_result is None:
                return [types.TextContent(type="text", text="Intent not found")]
            result_dict = _intent_to_dict(intent_result)
            return [
                types.TextContent(
                    type="text", text=json.dumps(result_dict, indent=2)
                )
            ]

        elif name == "update_intent_name":
            intent_id = arguments.get("intent_id")
            name_arg = arguments.get("name")
            if intent_id is None or name_arg is None:
                raise ValueError("intent_id and name are required")
            name_str = str(name_arg)
            intent_result = await service.update_intent_name(
                intent_id, name_str, repository
            )
            if intent_result is None:
                return [types.TextContent(type="text", text="Intent not found")]
            result_dict = _intent_to_dict(intent_result)
            await session.commit()
            return [
                types.TextContent(
                    type="text", text=json.dumps(result_dict, indent=2)
                )
            ]

        elif name == "update_intent_description":
            intent_id = arguments.get("intent_id")
            description = arguments.get("description")
            if intent_id is None or description is None:
                raise ValueError("intent_id and description are required")
            intent_result = await service.update_intent_description(
                intent_id, description, repository
            )
            if intent_result is None:
                return [types.TextContent(type="text", text="Intent not found")]
            result_dict = _intent_to_dict(intent_result)
            await session.commit()
            return [
                types.TextContent(
                    type="text", text=json.dumps(result_dict, indent=2)
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        await session.rollback()
        logger.error(
            f"Error calling tool {name}: {str(e)}",
            extra={"tool_name": name, "error": str(e)},
        )
        raise
    finally:
        await session.close()
