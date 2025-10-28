"""
Custom exception handlers for the FastAPI application.
"""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .logging_config import logger


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for request validation errors.
    Logs detailed validation errors for debugging.

    Args:
        request: The FastAPI request object
        exc: The validation exception

    Returns:
        JSONResponse with validation error details
    """
    # Extract request body from the exception or request
    body_str = None
    try:
        # Try to get body from exception first
        if hasattr(exc, "body"):
            body_str = exc.body.decode("utf-8") if isinstance(exc.body, bytes) else str(exc.body)
    except Exception:
        pass

    # Format validation errors with full details
    validation_errors = []
    for error in exc.errors():
        error_detail = {
            "field": ".".join(str(x) for x in error.get("loc", [])),
            "message": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        # Include input if available
        if "input" in error:
            error_detail["input"] = error.get("input")
        validation_errors.append(error_detail)

    # Log the validation error with structured data
    logger.error(
        "Request validation failed",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": request.client.host if request.client else "unknown",
            "request_body": body_str,
            "validation_errors": validation_errors,
            "error_count": len(validation_errors),
            "raw_errors": exc.errors(),  # Include raw errors for complete info
        },
    )

    # Return standard FastAPI validation error response
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
