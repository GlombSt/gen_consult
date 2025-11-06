"""
MCP (Model Context Protocol) Adapter

This module implements an MCP server as a PRIMARY ADAPTER in the hexagonal architecture.
It exposes business logic from the hexagon core through MCP tools.

Architecture:
    - router.py: HTTP/SSE endpoints (FastAPI routes)
    - server.py: MCP server instance and tool implementations
    - Tools call service layer functions (ports)
    - Service layer contains business logic (hexagon core)

Export:
    - router: FastAPI router to be included in main.py
"""

from app.mcp.router import router

__all__ = ["router"]
