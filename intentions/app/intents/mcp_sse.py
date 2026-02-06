"""
Legacy MCP HTTP+SSE transport for backward compatibility (2024-11-05 spec).

This is primarily for clients like older mcptools versions that still use the
deprecated HTTP+SSE transport. Newer clients should use the Streamable HTTP
endpoint at /mcp.
"""

import asyncio
import json
import os
import uuid
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, StreamingResponse

from app.shared.logging_config import logger

from .mcp_http import _handle_mcp_request, _validate_origin

# Get MCP allowed origins from environment
MCP_ALLOWED_ORIGINS = os.getenv("MCP_ALLOWED_ORIGINS", "*")
if MCP_ALLOWED_ORIGINS == "*":
    ALLOWED_ORIGINS = ["*"]
else:
    ALLOWED_ORIGINS = [origin.strip() for origin in MCP_ALLOWED_ORIGINS.split(",") if origin.strip()]


@dataclass
class _SseSession:
    session_id: str
    queue: asyncio.Queue[str]


_sessions: dict[str, _SseSession] = {}
_sessions_lock = asyncio.Lock()

router = APIRouter()


async def _register_session() -> _SseSession:
    session_id = str(uuid.uuid4())
    session = _SseSession(session_id=session_id, queue=asyncio.Queue())
    async with _sessions_lock:
        _sessions[session_id] = session
    return session


async def _unregister_session(session_id: str) -> None:
    async with _sessions_lock:
        _sessions.pop(session_id, None)


async def _get_session(session_id: str) -> _SseSession | None:
    async with _sessions_lock:
        return _sessions.get(session_id)


async def _sse_stream(session: _SseSession):
    """
    Yield SSE events:
    - endpoint: tells client where to POST JSON-RPC messages
    - message: JSON-RPC responses (JSON encoded)
    """
    try:
        # endpoint event required by HTTP+SSE spec (2024-11-05)
        yield f"event: endpoint\ndata: /message?sessionId={session.session_id}\n\n"
        while True:
            try:
                payload = await asyncio.wait_for(session.queue.get(), timeout=10)
                yield f"event: message\ndata: {payload}\n\n"
            except asyncio.TimeoutError:
                # Keep-alive heartbeat
                yield ": heartbeat\n\n"
    finally:
        await _unregister_session(session.session_id)


@router.get("/sse")
async def sse_endpoint(request: Request) -> Response:
    """SSE endpoint for legacy HTTP+SSE transport."""
    origin = request.headers.get("Origin")
    if not _validate_origin(origin, ALLOWED_ORIGINS):
        logger.warning("Invalid origin for SSE endpoint", extra={"origin": origin, "allowed_origins": ALLOWED_ORIGINS})
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid origin")

    session = await _register_session()
    return StreamingResponse(
        _sse_stream(session),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/message")
async def sse_message_endpoint(request: Request) -> Response:
    """Message endpoint for legacy HTTP+SSE transport."""
    origin = request.headers.get("Origin")
    if not _validate_origin(origin, ALLOWED_ORIGINS):
        logger.warning(
            "Invalid origin for SSE message endpoint",
            extra={"origin": origin, "allowed_origins": ALLOWED_ORIGINS},
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid origin")

    session_id = request.query_params.get("sessionId")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing sessionId")

    session = await _get_session(session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown session")

    try:
        body: dict[str, Any] = await request.json()
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON: {str(e)}")

    # Validate JSON-RPC structure
    if "jsonrpc" not in body or body.get("jsonrpc") != "2.0":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON-RPC request")

    response = await _handle_mcp_request(request, body)

    # Notifications get no response (202 Accepted)
    if response is None:
        return Response(status_code=status.HTTP_202_ACCEPTED)

    await session.queue.put(json.dumps(response))
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post("/sse/message")
async def sse_message_endpoint_compat(request: Request) -> Response:
    """
    Compatibility endpoint for clients that incorrectly prefix /sse to message paths.
    """
    return await sse_message_endpoint(request)


@router.get("/health")
async def sse_health() -> Response:
    """Simple health check for the legacy SSE transport."""
    return JSONResponse(content={"status": "ok", "transport": "sse"})
