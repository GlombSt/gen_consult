"""
FastAPI Application Entry Point
"""

import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.intents.router import router as intents_router
from app.items.router import router as items_router
from app.shared.database import close_db, init_db
from app.shared.exception_handlers import validation_exception_handler
from app.shared.logging_config import logger
from app.shared.middleware import log_requests_middleware
from app.users.router import router as users_router

# Get configuration from environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

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


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(title="My First FastAPI App", description="A simple FastAPI backend for learning", version="1.0.0")

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
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Include routers
    app.include_router(items_router)
    app.include_router(users_router)
    app.include_router(intents_router)

    return app


# Create the application instance
app = create_application()


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(
        "Application starting",
        extra={
            "environment": ENVIRONMENT,
            "log_level": LOG_LEVEL,
            "cors_origins_count": len(CORS_ORIGINS),
        },
    )
    # Initialize database (create tables for SQLite)
    await init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown"""
    await close_db()
    logger.info("Application shutting down")


@app.get("/")
async def root():
    """Welcome endpoint"""
    return {"message": "Welcome to your FastAPI backend!", "docs": "/docs", "redoc": "/redoc"}


@app.get("/health")
async def health_check():
    """Check if the API is running"""
    return {"status": "healthy"}
