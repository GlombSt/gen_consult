"""
MCP Server entry point for intents domain.

DEPRECATED: This stdio transport entry point is deprecated.
The MCP server is now integrated into the FastAPI application
and accessible via HTTP at /mcp endpoint.

For HTTP transport, run the FastAPI application:
    uvicorn app.main:app --reload

This file is kept for backwards compatibility with stdio-based clients.
"""

import asyncio

import mcp.server.stdio
from mcp.server.lowlevel import NotificationOptions
from mcp.server.models import InitializationOptions

from app.intents.mcp_server import server
from app.shared.database import init_db


async def run():
    """
    Run the MCP server with stdio transport.

    Initializes the database and starts the MCP server.
    """
    # Initialize database
    await init_db()

    # Run the server with stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="intents-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(run())
