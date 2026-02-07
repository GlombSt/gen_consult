"""
MCP Streamable HTTP transport using the official Python SDK.

Delegates GET/POST /mcp to the SDK's StreamableHTTPSessionManager so that
clients like mcptools get the exact transport behavior they expect.
"""

import os

from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Receive, Scope, Send

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


def _normalize_accept_header(scope: Scope) -> Scope:
    if scope["type"] != "http":
        return scope

    headers = list(scope.get("headers", []))
    accept_index = None
    accept_value = None
    for i, (key, value) in enumerate(headers):
        if key.lower() == b"accept":
            accept_index = i
            accept_value = value.decode(errors="ignore").lower()
            break

    if accept_value is None:
        headers.append((b"accept", b"application/json, text/event-stream"))
    else:
        has_json = "application/json" in accept_value
        has_sse = "text/event-stream" in accept_value
        has_wildcard = "*/*" in accept_value or "application/*" in accept_value
        if not (has_json and has_sse) and (has_wildcard or has_json or has_sse):
            headers[accept_index] = (b"accept", b"application/json, text/event-stream")

    new_scope = dict(scope)
    new_scope["headers"] = headers
    return new_scope


async def mcp_sdk_asgi_app(scope: Scope, receive: Receive, send: Send) -> None:
    """ASGI app that forwards /mcp requests to the SDK's Streamable HTTP handler."""
    if scope["type"] != "http":
        from starlette.responses import Response

        response = Response(status_code=404)
        await response(scope, receive, send)
        return
    await mcp_session_manager.handle_request(_normalize_accept_header(scope), receive, send)


async def mcp_sdk_request_handler(request: Request) -> Response:
    """
    FastAPI-compatible handler for POST /mcp to avoid redirect slashes.

    This adapts the ASGI handler to a Request/Response interface.
    """
    response_status: int | None = None
    response_headers: list[tuple[bytes, bytes]] = []
    body_chunks: list[bytes] = []

    async def _send(message: dict) -> None:
        nonlocal response_status, response_headers
        if message["type"] == "http.response.start":
            response_status = message["status"]
            response_headers = message.get("headers", [])
        elif message["type"] == "http.response.body":
            body_chunks.append(message.get("body", b""))

    scope = _normalize_accept_header(request.scope)
    await mcp_session_manager.handle_request(scope, request.receive, _send)

    status = response_status or 500
    headers = {k.decode("latin-1"): v.decode("latin-1") for k, v in response_headers}
    return Response(content=b"".join(body_chunks), status_code=status, headers=headers)
