"""
Custom exception handlers for the FastAPI application.
"""

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .logging_config import logger
from .schemas import ErrorResponse


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


async def authentication_exception_handler(request: Request, exc: HTTPException):
    """
    Custom handler for authentication errors (401).

    Logs authentication failures and returns a consistent error response using ErrorResponse format.
    Only handles 401 Unauthorized errors; other HTTPExceptions should be handled by http_exception_handler.

    Args:
        request: The FastAPI request object
        exc: The HTTPException

    Returns:
        JSONResponse with ErrorResponse format (only for 401 errors)
    """
    # Only handle 401 Unauthorized errors
    if exc.status_code != 401:
        # For non-401 errors, delegate to http_exception_handler
        return await http_exception_handler(request, exc)

    # Log the authentication failure with structured data
    logger.warning(
        "Authentication failed",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "error_detail": exc.detail,
        },
    )

    # Create ErrorResponse for 401 errors
    error_response = ErrorResponse(
        type="https://httpstatuses.com/401",
        title="Unauthorized",
        status=401,
        detail=str(exc.detail) if exc.detail else None,
        instance=str(request.url.path),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True),
        headers=exc.headers if hasattr(exc, "headers") and exc.headers else None,
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    General handler for HTTP exceptions using RFC 7807 Problem Details format.

    Converts HTTPException to ErrorResponse format for consistent API error responses.
    This handler should be registered after specific handlers (like authentication_exception_handler).

    Args:
        request: The FastAPI request object
        exc: The HTTPException

    Returns:
        JSONResponse with ErrorResponse format
    """
    # Map status codes to titles
    status_titles = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
    }

    title = status_titles.get(exc.status_code, "Error")
    error_type = f"https://httpstatuses.com/{exc.status_code}"

    # Create ErrorResponse
    error_response = ErrorResponse(
        type=error_type,
        title=title,
        status=exc.status_code,
        detail=str(exc.detail) if exc.detail else None,
        instance=str(request.url.path),
    )

    # Log the error
    logger.warning(
        "HTTP exception raised",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "status_code": exc.status_code,
            "client_ip": request.client.host if request.client else "unknown",
            "error_detail": exc.detail,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(exclude_none=True),
        headers=exc.headers if hasattr(exc, "headers") and exc.headers else None,
    )
