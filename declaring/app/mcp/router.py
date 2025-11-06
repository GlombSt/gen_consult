"""
MCP Router - SSE Transport Adapter

Exposes MCP server over HTTP using Server-Sent Events (SSE) transport.
This is a PRIMARY ADAPTER in the hexagonal architecture.
"""

from fastapi import APIRouter, Depends, Request
from mcp.server.sse import SseServerTransport
from starlette.responses import StreamingResponse

from app.mcp.auth import verify_api_key
from app.mcp.server import mcp_server
from app.shared.logging_config import logger

router = APIRouter(prefix="/mcp", tags=["MCP"])


@router.get("/sse")
async def handle_sse(
    request: Request,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Handle MCP connections over Server-Sent Events (SSE).

    This endpoint:
    1. Authenticates the request (if MCP_API_KEY is set)
    2. Accepts SSE connections from MCP clients
    3. Handles MCP protocol messages
    4. Streams responses back to the client

    The MCP client (like Claude Code) will connect to this endpoint to
    interact with the business logic through MCP tools.

    Authentication:
        Requires Bearer token in Authorization header if MCP_API_KEY env var is set.
        Example: Authorization: Bearer your-secret-key
    """
    logger.info("MCP SSE connection initiated (authenticated)")

    async with SseServerTransport("/mcp/messages") as transport:
        await mcp_server.run(
            transport.read_stream,
            transport.write_stream,
            mcp_server.create_initialization_options()
        )


@router.post("/messages")
async def handle_messages(
    request: Request,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Handle MCP messages sent from the client.

    This endpoint receives POST requests from the MCP client containing
    protocol messages (tool calls, etc.).

    Authentication:
        Requires Bearer token in Authorization header if MCP_API_KEY env var is set.
    """
    # This is handled by the SSE transport
    # The actual implementation depends on the mcp library's SSE transport
    pass


@router.get("/health")
async def health_check():
    """Check if MCP server is healthy"""
    return {
        "status": "healthy",
        "server": "gen-consult-backend",
        "transport": "SSE",
    }
