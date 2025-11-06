"""
MCP Authentication Middleware

Provides authentication mechanisms for MCP endpoints.
"""

import os
from fastapi import Header, HTTPException, status
from typing import Optional

from app.shared.logging_config import logger


# Load API key from environment variable
MCP_API_KEY = os.getenv("MCP_API_KEY", None)


async def verify_api_key(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify API key from Authorization header.

    Expected format: "Bearer YOUR_API_KEY"

    Args:
        authorization: Authorization header value

    Returns:
        True if authenticated

    Raises:
        HTTPException: If authentication fails
    """
    # Skip auth if no API key is configured (development mode)
    if not MCP_API_KEY:
        logger.warning("MCP_API_KEY not set - authentication disabled!")
        return True

    # Check if Authorization header is present
    if not authorization:
        logger.warning("MCP request without Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Parse Bearer token
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid authentication scheme")
    except ValueError:
        logger.warning("MCP request with invalid Authorization format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected: 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify token
    if token != MCP_API_KEY:
        logger.warning("MCP request with invalid API key", extra={"token_prefix": token[:8]})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info("MCP request authenticated successfully")
    return True


async def verify_api_key_query(api_key: Optional[str] = None) -> bool:
    """
    Verify API key from query parameter (alternative to header).

    Args:
        api_key: API key from query parameter

    Returns:
        True if authenticated

    Raises:
        HTTPException: If authentication fails
    """
    # Skip auth if no API key is configured (development mode)
    if not MCP_API_KEY:
        logger.warning("MCP_API_KEY not set - authentication disabled!")
        return True

    if not api_key or api_key != MCP_API_KEY:
        logger.warning("MCP request with invalid or missing API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    logger.info("MCP request authenticated successfully via query param")
    return True
