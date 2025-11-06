"""
Unit tests for shared dependencies.

Tests dependency injection functions including API key authentication.
"""

import os
from unittest.mock import patch

import pytest
from fastapi import HTTPException, status

from app.shared.dependencies import verify_api_key


@pytest.mark.unit
class TestVerifyApiKey:
    """Test verify_api_key dependency function."""

    def test_verify_api_key_when_disabled_returns_none(self):
        """Test verify_api_key returns None when authentication is disabled."""
        # Arrange
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "false"}, clear=False):
            # Act
            result = verify_api_key(authorization=None)

            # Assert
            assert result is None

    def test_verify_api_key_when_enabled_but_no_api_key_env_raises_500(self):
        """Test verify_api_key raises 500 when enabled but API_KEY not set."""
        # Arrange
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "true"}, clear=False):
            # Remove API_KEY if it exists
            env = os.environ.copy()
            env.pop("API_KEY", None)

            with patch.dict(os.environ, env, clear=False):
                # Act & Assert
                with pytest.raises(HTTPException) as exc_info:
                    verify_api_key(authorization="Bearer test-key")

                assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert "API_KEY environment variable is not set" in exc_info.value.detail

    def test_verify_api_key_when_missing_authorization_header_raises_401(self):
        """Test verify_api_key raises 401 when Authorization header is missing."""
        # Arrange
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "true", "API_KEY": "test-secret-key"}, clear=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(authorization=None)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Authorization header is required" in exc_info.value.detail
            assert "WWW-Authenticate" in exc_info.value.headers

    def test_verify_api_key_with_invalid_key_raises_401(self):
        """Test verify_api_key raises 401 when API key is invalid."""
        # Arrange
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "true", "API_KEY": "correct-key"}, clear=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(authorization="Bearer wrong-key")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid API key" in exc_info.value.detail
            assert "WWW-Authenticate" in exc_info.value.headers

    def test_verify_api_key_with_valid_bearer_token_returns_key(self):
        """Test verify_api_key returns key when valid Bearer token is provided."""
        # Arrange
        test_key = "test-secret-key-123"
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "true", "API_KEY": test_key}, clear=False):
            # Act
            result = verify_api_key(authorization=f"Bearer {test_key}")

            # Assert
            assert result == test_key

    def test_verify_api_key_with_valid_direct_key_returns_key(self):
        """Test verify_api_key returns key when valid direct API key is provided."""
        # Arrange
        test_key = "test-secret-key-123"
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "true", "API_KEY": test_key}, clear=False):
            # Act
            result = verify_api_key(authorization=test_key)

            # Assert
            assert result == test_key

    def test_verify_api_key_with_empty_key_raises_401(self):
        """Test verify_api_key raises 401 when API key is empty."""
        # Arrange
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "true", "API_KEY": "correct-key"}, clear=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(authorization="Bearer ")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid API key" in exc_info.value.detail

    def test_verify_api_key_with_bearer_token_strips_whitespace(self):
        """Test verify_api_key handles whitespace in Bearer token."""
        # Arrange
        test_key = "test-secret-key-123"
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "true", "API_KEY": test_key}, clear=False):
            # Act
            result = verify_api_key(authorization=f"Bearer  {test_key}  ")

            # Assert
            assert result == test_key

    def test_verify_api_key_with_direct_key_strips_whitespace(self):
        """Test verify_api_key handles whitespace in direct API key."""
        # Arrange
        test_key = "test-secret-key-123"
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "true", "API_KEY": test_key}, clear=False):
            # Act
            result = verify_api_key(authorization=f"  {test_key}  ")

            # Assert
            assert result == test_key

