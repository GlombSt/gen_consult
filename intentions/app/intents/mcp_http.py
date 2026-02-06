"""
HTTP transport wrapper for MCP server.

Provides Streamable HTTP transport integration for the MCP server,
allowing it to run alongside FastAPI as an HTTP endpoint.
"""

import asyncio
import json
import os
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from mcp.server.lowlevel import NotificationOptions
from pydantic import ValidationError

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
        allowed_origins: List of allowed origins (["*"] means allow all)

    Returns:
        True if origin is valid, False otherwise
    """
    # If "*" is in allowed origins, allow all requests
    if "*" in allowed_origins:
        return True

    # If no origin header and not allowing all, reject
    # (Protects against DNS rebinding where attacker controls origin)
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
            server.get_capabilities(
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
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,  # Invalid params
                        "message": "Tool name is required",
                    },
                }

            try:
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
            except ValidationError as e:
                logger.error(f"Invalid arguments for {tool_name}", extra={"tool_name": tool_name, "errors": e.errors()})
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32602,  # Invalid params
                        "message": f"Invalid arguments for tool {tool_name}",
                        "data": e.errors(),
                    },
                }

        elif method == "notifications/initialized":
            # Notification - no response needed
            return None

        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,  # Method not found
                    "message": f"Unknown method: {method}",
                },
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling MCP request: {str(e)}", extra={"method": method, "error": str(e)})
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,  # Internal error
                "message": "Internal error",
                "data": str(e),
            },
        }


# Create router for MCP HTTP transport
router = APIRouter()


async def _sse_stream():
    """Yield SSE events so Streamable HTTP clients (e.g. mcptools) get a valid stream."""
    # Initial event so client sees the endpoint is ready
    yield "event: endpoint_ready\ndata: {}\n\n"
    # Keep stream open with heartbeats so clients that wait for an open stream don't timeout
    for _ in range(12):  # ~60s at 5s interval
        await asyncio.sleep(5)
        yield ": heartbeat\n\n"


@router.get("")
async def mcp_endpoint_get(request: Request) -> Response:
    """
    Handle GET for MCP endpoint (discovery / session setup).

    If Accept includes text/event-stream (Streamable HTTP), return an SSE stream
    so clients like mcptools get a valid stream and do not timeout. Otherwise
    return JSON for simple discovery.
    """
    accept = request.headers.get("Accept", "")
    if "text/event-stream" in accept:
        return StreamingResponse(
            _sse_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    return JSONResponse(
        content={
            "protocol": "mcp",
            "message": "Use POST with JSON-RPC 2.0 for MCP requests.",
        },
        status_code=status.HTTP_200_OK,
    )


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
    if not _validate_origin(origin, ALLOWED_ORIGINS):
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
