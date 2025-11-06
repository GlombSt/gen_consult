"""
HTTP transport wrapper for MCP server.

Provides Streamable HTTP transport integration for the MCP server,
allowing it to run alongside FastAPI as an HTTP endpoint.
"""

import json
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from mcp.server.lowlevel import NotificationOptions
from mcp.server.models import InitializationOptions

from app.shared.logging_config import logger

from .mcp_server import call_tool, list_tools, server

# Get MCP allowed origins from environment
# Default to allowing all origins in development, restrict in production
MCP_ALLOWED_ORIGINS = os.getenv("MCP_ALLOWED_ORIGINS", "*")
if MCP_ALLOWED_ORIGINS == "*":
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = [origin.strip() for origin in MCP_ALLOWED_ORIGINS.split(",") if origin.strip()]


def _validate_origin(origin: str | None, allowed_origins: list[str]) -> bool:
    """
    Validate Origin header to prevent DNS rebinding attacks.

    Args:
        origin: Origin header value
        allowed_origins: List of allowed origins

    Returns:
        True if origin is valid, False otherwise
    """
    if origin is None:
        return False
    return origin in allowed_origins


async def _handle_mcp_request(request: Request, body: dict[str, Any]) -> dict[str, Any]:
    """
    Handle MCP JSON-RPC request.

    Args:
        request: FastAPI request object
        body: Parsed JSON-RPC request body

    Returns:
        JSON-RPC response dictionary

    Raises:
        HTTPException: If request is invalid
    """
    method = body.get("method")
    params = body.get("params", {})
    request_id = body.get("id")

    try:
        if method == "initialize":
            # Return server capabilities
            capabilities = server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            )
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": False},
                    },
                    "serverInfo": {
                        "name": "intents-mcp-server",
                        "version": "1.0.0",
                    },
                },
            }

        elif method == "tools/list":
            tools = await list_tools()
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema,
                        }
                        for tool in tools
                    ],
                },
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_arguments = params.get("arguments", {})

            if not tool_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tool name is required",
                )

            result_contents = await call_tool(tool_name, tool_arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": content.type,
                            "text": content.text,
                        }
                        for content in result_contents
                    ],
                    "isError": False,
                },
            }

        elif method == "notifications/initialized":
            # Notification - no response needed
            return None

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown method: {method}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling MCP request: {str(e)}", extra={"method": method, "error": str(e)})
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e),
            },
        }


# Create router for MCP HTTP transport
router = APIRouter()


@router.post("")
async def mcp_endpoint(request: Request) -> Response:
    """
    Handle MCP Streamable HTTP transport requests.

    Supports JSON-RPC over HTTP POST for MCP protocol communication.
    Validates Origin header to prevent DNS rebinding attacks.

    Returns:
        JSON-RPC response
    """
    # Validate Origin header to prevent DNS rebinding attacks
    origin = request.headers.get("Origin")
    if ALLOWED_ORIGINS != ["*"] and not _validate_origin(origin, ALLOWED_ORIGINS):
        logger.warning(f"Invalid origin: {origin}", extra={"origin": origin, "allowed_origins": ALLOWED_ORIGINS})
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid origin",
        )

    # Parse request body
    try:
        body = await request.json()
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON: {str(e)}",
        )

    # Validate JSON-RPC structure
    if "jsonrpc" not in body or body.get("jsonrpc") != "2.0":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON-RPC request",
        )

    # Handle request
    response = await _handle_mcp_request(request, body)

    # Notifications don't return a response
    if response is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return JSONResponse(content=response)

