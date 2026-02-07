"""
MCP Server for intents domain (V2).

Exposes intents operations as MCP tools using the service layer as the port.
Intent responses omit examples per plan.
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
    AspectResponse,
    AssumptionResponse,
    ChoiceResponse,
    InputResponse,
    InsightCreateRequest,
    InsightResponse,
    IntentArticulationUpdateRequest,
    IntentCreateRequest,
    IntentResponseForMCP,
    IntentUpdateDescriptionRequest,
    IntentUpdateNameRequest,
    OutputCreateRequest,
    PitfallResponse,
    PromptCreateRequest,
    PromptResponse,
    QualityResponse,
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


def _intent_to_dict_for_mcp(intent) -> dict[str, Any]:
    """Convert domain model to IntentResponseForMCP (no examples) and dump to dict for MCP."""
    response = IntentResponseForMCP(
        id=intent.id,
        name=intent.name,
        description=intent.description,
        created_at=intent.created_at,
        updated_at=intent.updated_at,
        aspects=[AspectResponse(id=a.id, name=a.name, description=a.description) for a in intent.aspects],
        inputs=[InputResponse(id=i.id, name=i.name, description=i.description) for i in intent.inputs],
        choices=[ChoiceResponse(id=c.id, name=c.name, description=c.description) for c in intent.choices],
        pitfalls=[PitfallResponse(id=p.id, description=p.description) for p in intent.pitfalls],
        assumptions=[AssumptionResponse(id=a.id, description=a.description) for a in intent.assumptions],
        qualities=[QualityResponse(id=q.id, criterion=q.criterion, priority=q.priority) for q in intent.qualities],
        prompts=[PromptResponse(id=p.id, version=p.version, content=p.content) for p in intent.prompts],
        insights=[InsightResponse(id=i.id, content=i.content, status=i.status) for i in intent.insights],
    )
    return response.model_dump(mode="json")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available MCP tools for intents operations (V2). Intent as composition; no separate articulation-entity tools."""
    create_intent_schema = _pydantic_to_json_schema(IntentCreateRequest)
    update_name_schema = _pydantic_to_json_schema(IntentUpdateNameRequest)
    update_description_schema = _pydantic_to_json_schema(IntentUpdateDescriptionRequest)
    articulation_schema = _pydantic_to_json_schema(IntentArticulationUpdateRequest)
    prompt_create_schema = _pydantic_to_json_schema(PromptCreateRequest)
    output_create_schema = _pydantic_to_json_schema(OutputCreateRequest)
    insight_create_schema = _pydantic_to_json_schema(InsightCreateRequest)

    return [
        types.Tool(
            name="create_intent",
            description="Create a new intent with name and description; optionally include aspects, inputs, choices, pitfalls, assumptions, qualities (no examples).",
            inputSchema=create_intent_schema,
        ),
        types.Tool(
            name="get_intent",
            description="Get an intent by ID. Returns full composition (aspects, inputs, choices, pitfalls, assumptions, qualities, prompts, insights). Examples omitted.",
            inputSchema={
                "type": "object",
                "properties": {"intent_id": {"type": "integer", "description": "The intent ID"}},
                "required": ["intent_id"],
            },
        ),
        types.Tool(
            name="list_intents",
            description="List all intents with full composition. Examples omitted.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="delete_intent",
            description="Delete an intent by ID.",
            inputSchema={
                "type": "object",
                "properties": {"intent_id": {"type": "integer", "description": "The intent ID to delete"}},
                "required": ["intent_id"],
            },
        ),
        types.Tool(
            name="update_intent_name",
            description="Update an intent's name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {"type": "integer", "description": "The intent ID to update"},
                    **update_name_schema["properties"],
                },
                "required": ["intent_id", "name"],
            },
        ),
        types.Tool(
            name="update_intent_description",
            description="Update an intent's description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {"type": "integer", "description": "The intent ID to update"},
                    **update_description_schema["properties"],
                },
                "required": ["intent_id", "description"],
            },
        ),
        types.Tool(
            name="update_intent_articulation",
            description="Update articulation for an intent. Intent owns all entities; you may supply any subset (e.g. only aspects or only qualities). Fields: aspects, inputs, choices, pitfalls, assumptions, qualities. Omitted fields unchanged; empty array clears that type. No examples. Quality uses 'criterion' (required), not name/description.",
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {"type": "integer", "description": "The intent ID"},
                    **articulation_schema["properties"],
                },
                "required": ["intent_id"],
            },
        ),
        types.Tool(
            name="add_prompt",
            description="Add a prompt (versioned instruction) to an intent.",
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {"type": "integer", "description": "The intent ID"},
                    **prompt_create_schema["properties"],
                },
                "required": ["intent_id", "content"],
            },
        ),
        types.Tool(
            name="add_output",
            description="Add an output (AI response) to a prompt.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt_id": {"type": "integer", "description": "The prompt ID"},
                    **output_create_schema["properties"],
                },
                "required": ["prompt_id", "content"],
            },
        ),
        types.Tool(
            name="add_insight",
            description="Add an insight (discovery) to an intent. Optional: source_type, source_output_id, source_prompt_id, source_assumption_id, status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "intent_id": {"type": "integer", "description": "The intent ID"},
                    **insight_create_schema["properties"],
                },
                "required": ["intent_id", "content"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle MCP tool calls by routing to appropriate service functions (V2)."""
    repository, session = await _get_repository()

    def _intent_result(intent) -> list[types.TextContent]:
        return [types.TextContent(type="text", text=json.dumps(_intent_to_dict_for_mcp(intent), indent=2))]

    try:
        if name == "create_intent":
            request = IntentCreateRequest(**arguments)
            created_intent = await service.create_intent(request, repository)
            await session.commit()
            return _intent_result(created_intent)

        elif name == "get_intent":
            intent_id = arguments.get("intent_id")
            if intent_id is None:
                raise ValueError("intent_id is required")
            intent_result = await service.get_intent(intent_id, repository)
            if intent_result is None:
                return [types.TextContent(type="text", text="Intent not found")]
            return _intent_result(intent_result)

        elif name == "list_intents":
            intents = await service.list_intents(repository)
            result_list = [_intent_to_dict_for_mcp(i) for i in intents]
            return [types.TextContent(type="text", text=json.dumps(result_list, indent=2))]

        elif name == "delete_intent":
            intent_id = arguments.get("intent_id")
            if intent_id is None:
                raise ValueError("intent_id is required")
            deleted = await service.delete_intent(intent_id, repository)
            await session.commit()
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"deleted": deleted, "intent_id": intent_id}),
                )
            ]

        elif name == "update_intent_name":
            intent_id = arguments.get("intent_id")
            name_arg = arguments.get("name")
            if intent_id is None or name_arg is None:
                raise ValueError("intent_id and name are required")
            intent_result = await service.update_intent_name(intent_id, str(name_arg), repository)
            if intent_result is None:
                return [types.TextContent(type="text", text="Intent not found")]
            await session.commit()
            return _intent_result(intent_result)

        elif name == "update_intent_description":
            intent_id = arguments.get("intent_id")
            description = arguments.get("description")
            if intent_id is None or description is None:
                raise ValueError("intent_id and description are required")
            intent_result = await service.update_intent_description(intent_id, description, repository)
            if intent_result is None:
                return [types.TextContent(type="text", text="Intent not found")]
            await session.commit()
            return _intent_result(intent_result)

        elif name == "update_intent_articulation":
            intent_id = arguments.get("intent_id")
            if intent_id is None:
                raise ValueError("intent_id is required")
            payload_dict = {
                k: arguments.get(k)
                for k in (
                    "aspects",
                    "inputs",
                    "choices",
                    "pitfalls",
                    "assumptions",
                    "qualities",
                )
                if k in arguments
            }
            payload = IntentArticulationUpdateRequest(**payload_dict)
            intent_result = await service.update_intent_articulation(intent_id, payload, repository)
            if intent_result is None:
                return [types.TextContent(type="text", text="Intent not found")]
            await session.commit()
            return _intent_result(intent_result)

        elif name == "add_prompt":
            intent_id = arguments.get("intent_id")
            content = arguments.get("content")
            if intent_id is None or content is None:
                raise ValueError("intent_id and content are required")
            prompt_request = PromptCreateRequest(content=content)
            created = await service.add_prompt(intent_id, prompt_request, repository)
            if created is None:
                return [types.TextContent(type="text", text="Intent not found")]
            await session.commit()
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "id": created.id,
                            "intent_id": intent_id,
                            "version": created.version,
                            "content": created.content,
                        },
                        indent=2,
                    ),
                )
            ]

        elif name == "add_output":
            prompt_id = arguments.get("prompt_id")
            content = arguments.get("content")
            if prompt_id is None or content is None:
                raise ValueError("prompt_id and content are required")
            output_request = OutputCreateRequest(content=content)
            created = await service.add_output(prompt_id, output_request, repository)
            if created is None:
                return [types.TextContent(type="text", text="Prompt not found")]
            await session.commit()
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {"id": created.id, "prompt_id": prompt_id, "content": created.content},
                        indent=2,
                    ),
                )
            ]

        elif name == "add_insight":
            intent_id = arguments.get("intent_id")
            content = arguments.get("content")
            if intent_id is None or content is None:
                raise ValueError("intent_id and content are required")
            insight_request = InsightCreateRequest(
                content=content,
                source_type=arguments.get("source_type"),
                source_output_id=arguments.get("source_output_id"),
                source_prompt_id=arguments.get("source_prompt_id"),
                source_assumption_id=arguments.get("source_assumption_id"),
                status=arguments.get("status"),
            )
            created = await service.add_insight(intent_id, insight_request, repository)
            if created is None:
                return [types.TextContent(type="text", text="Intent not found")]
            await session.commit()
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "id": created.id,
                            "intent_id": intent_id,
                            "content": created.content,
                            "status": created.status,
                        },
                        indent=2,
                    ),
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
