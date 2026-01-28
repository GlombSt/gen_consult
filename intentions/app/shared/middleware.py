"""
Middleware for request/response logging and processing.
"""

import time

from fastapi import Request

from .logging_config import logger


async def log_requests_middleware(request: Request, call_next):
    """
    Log all incoming requests and responses with structured data.

    Args:
        request: The FastAPI request object
        call_next: Function to call the next middleware/route handler

    Returns:
        Response from the route handler
    """
    start_time = time.time()

    # Log incoming request with structured data
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "origin": request.headers.get("origin", None),
        },
    )

    # Process the request
    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Log response with structured data
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": round(duration, 3),
            },
        )

        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            "Request failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration": round(duration, 3),
                "error_message": str(e),
            },
            exc_info=True,
        )
        raise
