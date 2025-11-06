"""
MCP Server Implementation

This module implements an MCP (Model Context Protocol) server as a PRIMARY ADAPTER
in the hexagonal architecture. It exposes business logic through MCP tools that
call the service layer (ports).

Architecture:
    MCP Client → MCP Server (adapter) → Service Layer (ports) → Business Logic
"""

from typing import Any

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
import mcp.types as types

from app.items import (
    get_all_items,
    get_item,
    create_item,
    ItemCreateRequest,
)
from app.users import (
    get_all_users,
    get_user,
    create_user,
    UserCreateRequest,
)
from app.shared.logging_config import logger


# Create MCP server instance
mcp_server = Server("gen-consult-backend")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available MCP tools.

    These tools expose business logic from the hexagon core through service ports.
    """
    return [
        Tool(
            name="list_items",
            description="List all items from the inventory. Returns item ID, name, description, and price.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_item",
            description="Get details of a specific item by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "integer",
                        "description": "The ID of the item to retrieve",
                    }
                },
                "required": ["item_id"],
            },
        ),
        Tool(
            name="create_item",
            description="Create a new item in the inventory",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the item",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the item",
                    },
                    "price": {
                        "type": "number",
                        "description": "Price of the item",
                    },
                },
                "required": ["name", "description", "price"],
            },
        ),
        Tool(
            name="list_users",
            description="List all users in the system. Returns user ID, name, and email.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_user",
            description="Get details of a specific user by their ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "integer",
                        "description": "The ID of the user to retrieve",
                    }
                },
                "required": ["user_id"],
            },
        ),
        Tool(
            name="create_user",
            description="Create a new user in the system",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the user",
                    },
                    "email": {
                        "type": "string",
                        "description": "Email address of the user",
                    },
                },
                "required": ["name", "email"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle tool execution by calling the appropriate service layer function.

    This function acts as the adapter between MCP protocol and the hexagon core.
    All business logic is delegated to the service layer (ports).
    """
    try:
        logger.info(f"MCP tool called: {name}", extra={"arguments": arguments})

        # Items domain tools
        if name == "list_items":
            items = await get_all_items()
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(items)} items:\n" +
                         "\n".join([
                             f"- ID {item.id}: {item.name} (${item.price}) - {item.description}"
                             for item in items
                         ])
                )
            ]

        elif name == "get_item":
            item_id = arguments.get("item_id")
            item = await get_item(item_id)
            return [
                TextContent(
                    type="text",
                    text=f"Item Details:\n"
                         f"ID: {item.id}\n"
                         f"Name: {item.name}\n"
                         f"Description: {item.description}\n"
                         f"Price: ${item.price}"
                )
            ]

        elif name == "create_item":
            item_data = ItemCreateRequest(**arguments)
            item = await create_item(item_data)
            return [
                TextContent(
                    type="text",
                    text=f"Successfully created item:\n"
                         f"ID: {item.id}\n"
                         f"Name: {item.name}\n"
                         f"Description: {item.description}\n"
                         f"Price: ${item.price}"
                )
            ]

        # Users domain tools
        elif name == "list_users":
            users = await get_all_users()
            return [
                TextContent(
                    type="text",
                    text=f"Found {len(users)} users:\n" +
                         "\n".join([
                             f"- ID {user.id}: {user.name} ({user.email})"
                             for user in users
                         ])
                )
            ]

        elif name == "get_user":
            user_id = arguments.get("user_id")
            user = await get_user(user_id)
            return [
                TextContent(
                    type="text",
                    text=f"User Details:\n"
                         f"ID: {user.id}\n"
                         f"Name: {user.name}\n"
                         f"Email: {user.email}"
                )
            ]

        elif name == "create_user":
            user_data = UserCreateRequest(**arguments)
            user = await create_user(user_data)
            return [
                TextContent(
                    type="text",
                    text=f"Successfully created user:\n"
                         f"ID: {user.id}\n"
                         f"Name: {user.name}\n"
                         f"Email: {user.email}"
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error executing MCP tool {name}: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]
