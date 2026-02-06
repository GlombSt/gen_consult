"""
MCP Streamable HTTP transport using the official Python SDK.

Delegates GET/POST /mcp to the SDK's StreamableHTTPSessionManager so that
clients like mcptools get the exact transport behavior they expect.
"""

import os

from starlette.types import Receive, Scope, Send

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings

from .mcp_server import server

# Security: allow all origins in development, restrict in production
_MCP_ALLOWED_ORIGINS = os.getenv("MCP_ALLOWED_ORIGINS", "*")
if _MCP_ALLOWED_ORIGINS == "*":
    _SECURITY_SETTINGS = TransportSecuritySettings(enable_dns_rebinding_protection=False)
else:
    _SECURITY_SETTINGS = TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_origins=[o.strip() for o in _MCP_ALLOWED_ORIGINS.split(",") if o.strip()],
    )

# One session manager per process; run() is called from app lifespan
mcp_session_manager = StreamableHTTPSessionManager(
    app=server,
    json_response=True,
    stateless=True,
    security_settings=_SECURITY_SETTINGS,
)


async def mcp_sdk_asgi_app(scope: Scope, receive: Receive, send: Send) -> None:
    """ASGI app that forwards /mcp requests to the SDK's Streamable HTTP handler."""
    if scope["type"] != "http":
        from starlette.responses import Response

        response = Response(status_code=404)
        await response(scope, receive, send)
        return
    await mcp_session_manager.handle_request(scope, receive, send)
