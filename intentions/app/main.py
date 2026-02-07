"""
FastAPI Application Entry Point
"""

import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.intents import mcp_sdk_http
from app.intents.router import router as intents_router
from app.shared.database import close_db, init_db
from app.shared.dependencies import verify_api_key
from app.shared.exception_handlers import (
    authentication_exception_handler,
    validation_exception_handler,
)
from app.shared.logging_config import logger
from app.shared.middleware import log_requests_middleware
from app.users.router import router as users_router

# Get configuration from environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
ENABLE_API_KEY_AUTH = os.getenv("ENABLE_API_KEY_AUTH", "false").lower() == "true"

# CORS origins configuration
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",  # Common React/Next.js port
    "http://localhost:3001",
    "http://localhost:5173",  # Common Vite port
    "http://localhost:5174",
    "http://localhost:8080",  # Common Vue/general dev port
    "http://localhost:8081",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Application lifespan: init DB, run MCP session manager, then cleanup."""
    logger.info(
        "Application starting",
        extra={
            "environment": os.getenv("ENVIRONMENT", "development"),
            "log_level": os.getenv("LOG_LEVEL", "DEBUG").upper(),
            "cors_origins_count": len(CORS_ORIGINS),
        },
    )
    await init_db()
    logger.info("Database initialized")
    async with mcp_sdk_http.mcp_session_manager.run():
        logger.info("MCP Streamable HTTP session manager started")
        yield
    await close_db()
    logger.info("Application shutting down")


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="My First FastAPI App",
        description="A simple FastAPI backend for learning",
        version="1.0.0",
        lifespan=app_lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.middleware("http")(log_requests_middleware)

    # Add exception handlers
    # Note: authentication_exception_handler handles 401 errors specifically,
    # and delegates other HTTPExceptions to http_exception_handler
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, authentication_exception_handler)

    # Include routers with API key authentication if enabled
    # Public endpoints (/, /health, /docs, /redoc, /openapi.json) are defined directly
    # and will not require authentication
    router_dependencies = []
    if ENABLE_API_KEY_AUTH:
        router_dependencies = [Depends(verify_api_key)]

    app.include_router(users_router, dependencies=router_dependencies)
    app.include_router(intents_router, dependencies=router_dependencies)

    # MCP Streamable HTTP endpoint.
    # Handle POST /mcp directly to avoid 307 redirects from mounted sub-app.
    app.add_api_route("/mcp", mcp_sdk_http.mcp_sdk_request_handler, methods=["GET", "POST"])
    app.mount("/mcp", mcp_sdk_http.mcp_sdk_asgi_app)

    return app


# Create the application instance
app = create_application()


@app.get("/")
async def root():
    """Welcome endpoint"""
    return {"message": "Welcome to your FastAPI backend!", "docs": "/docs", "redoc": "/redoc"}


@app.get("/health")
async def health_check():
    """Check if the API is running"""
    return {"status": "healthy"}
