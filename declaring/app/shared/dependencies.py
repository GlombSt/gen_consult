"""
Dependency injection functions for repositories and authentication.

Provides FastAPI dependency functions that create repository instances
with database sessions. This allows the service layer to be infrastructure-agnostic
by receiving repositories as dependencies rather than database sessions.
"""

import os
from typing import TYPE_CHECKING, Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db

if TYPE_CHECKING:
    from app.intents.repository import IntentRepository
    from app.users.repository import UserRepository


def get_user_repository(db: AsyncSession = Depends(get_db)) -> "UserRepository":
    """
    Dependency function to get UserRepository instance.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        UserRepository instance configured with the database session
    """
    from app.users.repository import UserRepository

    return UserRepository(db)


def get_intent_repository(db: AsyncSession = Depends(get_db)) -> "IntentRepository":
    """
    Dependency function to get IntentRepository instance.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        IntentRepository instance configured with the database session
    """
    from app.intents.repository import IntentRepository

    return IntentRepository(db)


def verify_api_key(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Verify API key from Authorization header.

    Supports two formats:
    - `Authorization: Bearer <api-key>`
    - `Authorization: <api-key>`

    Args:
        authorization: Authorization header value

    Returns:
        The API key if valid

    Raises:
        HTTPException: 401 if API key is missing or invalid
    """
    # Check if API key authentication is enabled
    enable_auth = os.getenv("ENABLE_API_KEY_AUTH", "false").lower() == "true"
    if not enable_auth:
        # If not enabled, return None (no authentication required)
        return None

    # Get expected API key from environment
    expected_api_key = os.getenv("API_KEY")
    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key authentication is enabled but API_KEY environment variable is not set",
        )

    # Check if Authorization header is present
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract API key from Authorization header
    # Support both "Bearer <key>" and "<key>" formats
    api_key = None
    if authorization.startswith("Bearer "):
        api_key = authorization[7:].strip()
    else:
        api_key = authorization.strip()

    # Verify API key
    if not api_key or api_key != expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return api_key
