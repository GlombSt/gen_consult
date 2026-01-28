"""
Unit tests for shared exception handlers.

Tests custom exception handlers including authentication error handling.
"""

import pytest
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.shared.exception_handlers import authentication_exception_handler, validation_exception_handler


@pytest.mark.unit
class TestAuthenticationExceptionHandler:
    """Test authentication_exception_handler."""

    @pytest.mark.asyncio
    async def test_authentication_handler_with_401_returns_json_response(self):
        """Test authentication handler returns JSON response for 401 errors using ErrorResponse format."""
        # Arrange
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/users",
                "headers": [],
                "scheme": "http",
                "server": ("localhost", 8000),
            }
        )
        exc = HTTPException(status_code=401, detail="Invalid API key")

        # Act
        response = await authentication_exception_handler(request, exc)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        content = response.body.decode()
        assert "Invalid API key" in content
        # Check ErrorResponse format (RFC 7807 Problem Details)
        assert "type" in content
        assert "title" in content
        assert "status" in content
        assert "detail" in content
        assert "instance" in content

    @pytest.mark.asyncio
    async def test_authentication_handler_with_non_401_returns_error_response(self):
        """Test authentication handler delegates to http_exception_handler for non-401 errors."""
        # Arrange
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/users",
                "headers": [],
                "scheme": "http",
                "server": ("localhost", 8000),
            }
        )
        exc = HTTPException(status_code=404, detail="Not found")

        # Act
        response = await authentication_exception_handler(request, exc)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 404
        content = response.body.decode()
        assert "Not found" in content
        # Check ErrorResponse format (RFC 7807 Problem Details)
        assert "type" in content
        assert "title" in content
        assert "status" in content
        assert "detail" in content
        assert "instance" in content

    @pytest.mark.asyncio
    async def test_authentication_handler_includes_www_authenticate_header(self):
        """Test authentication handler includes WWW-Authenticate header for 401 errors."""
        # Arrange
        request = Request(
            scope={
                "type": "http",
                "method": "GET",
                "path": "/users",
                "headers": [],
                "scheme": "http",
                "server": ("localhost", 8000),
            }
        )
        exc = HTTPException(
            status_code=401, detail="Authorization header is required", headers={"WWW-Authenticate": "Bearer"}
        )

        # Act
        response = await authentication_exception_handler(request, exc)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.unit
class TestValidationExceptionHandler:
    """Test validation_exception_handler."""

    @pytest.mark.asyncio
    async def test_validation_handler_returns_json_response(self):
        """Test validation handler returns JSON response with ErrorResponse format."""
        # Arrange
        request = Request(
            scope={
                "type": "http",
                "method": "POST",
                "path": "/users",
                "headers": [],
                "scheme": "http",
                "server": ("localhost", 8000),
            }
        )
        errors = [{"loc": ["body", "username"], "msg": "field required", "type": "value_error.missing"}]
        exc = RequestValidationError(errors)

        # Act
        response = await validation_exception_handler(request, exc)

        # Assert
        assert isinstance(response, JSONResponse)
        assert response.status_code == 422
        content = response.body.decode()
        # Check ErrorResponse format (RFC 7807 Problem Details)
        assert "type" in content
        assert "title" in content
        assert "status" in content
        assert "detail" in content
        assert "instance" in content
        assert "Request validation failed" in content
        assert "username" in content

