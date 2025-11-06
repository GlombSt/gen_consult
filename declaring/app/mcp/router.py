"""
MCP Router - SSE Transport Adapter

Exposes MCP server over HTTP using Server-Sent Events (SSE) transport.
This is a PRIMARY ADAPTER in the hexagonal architecture.
"""

from fastapi import APIRouter, Request
from mcp.server.sse import SseServerTransport
from starlette.responses import StreamingResponse

from app.mcp.server import mcp_server
from app.shared.logging_config import logger

router = APIRouter(prefix="/mcp", tags=["MCP"])


@router.get("/sse")
async def handle_sse(request: Request):
    """
    Handle MCP connections over Server-Sent Events (SSE).

    This endpoint:
    1. Accepts SSE connections from MCP clients
    2. Handles MCP protocol messages
    3. Streams responses back to the client

    The MCP client (like Claude Code) will connect to this endpoint to
    interact with the business logic through MCP tools.
    """
    logger.info("MCP SSE connection initiated")

    async with SseServerTransport("/mcp/messages") as transport:
        await mcp_server.run(
            transport.read_stream,
            transport.write_stream,
            mcp_server.create_initialization_options()
        )


@router.post("/messages")
async def handle_messages(request: Request):
    """
    Handle MCP messages sent from the client.

    This endpoint receives POST requests from the MCP client containing
    protocol messages (tool calls, etc.).
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
