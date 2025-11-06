"""
API tests for API key authentication.

Tests API key authentication integration with endpoints.
"""

import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app, create_application
from app.shared.dependencies import get_intent_repository, get_user_repository, verify_api_key
from app.intents.repository import IntentRepository
from app.users.repository import UserRepository


@pytest.fixture
def client(test_db_session):
    """Create a test client with test database session."""
    def override_get_user_repository():
        return UserRepository(test_db_session)

    def override_get_intent_repository():
        return IntentRepository(test_db_session)

    app.dependency_overrides[get_user_repository] = override_get_user_repository
    app.dependency_overrides[get_intent_repository] = override_get_intent_repository
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_auth(test_db_session):
    """Create a test client with API key authentication enabled."""
    from fastapi import Depends
    from app.intents.router import router as intents_router
    from app.users.router import router as users_router
    from app.shared.database import get_db
    
    # Create a new app instance with minimal setup
    test_app = FastAPI(title="Test App")
    
    # Add exception handlers
    from app.shared.exception_handlers import authentication_exception_handler, validation_exception_handler
    from fastapi.exceptions import RequestValidationError
    from fastapi import HTTPException
    test_app.add_exception_handler(RequestValidationError, validation_exception_handler)
    test_app.add_exception_handler(HTTPException, authentication_exception_handler)
    
    # Override database dependency
    async def override_get_db():
        yield test_db_session
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    # Override repository dependencies
    def override_get_user_repository():
        return UserRepository(test_db_session)

    def override_get_intent_repository():
        return IntentRepository(test_db_session)
    
    test_app.dependency_overrides[get_user_repository] = override_get_user_repository
    test_app.dependency_overrides[get_intent_repository] = override_get_intent_repository
    
    # Override verify_api_key BEFORE including routers
    def override_verify_api_key(authorization: str = None):
        if not authorization:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Extract key from Bearer token or direct
        api_key = authorization[7:].strip() if authorization.startswith("Bearer ") else authorization.strip()
        # Validate format (prevent injection)
        if not api_key or any(char in api_key for char in [" ", "\n", "\r", "\t"]):
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Use constant-time comparison
        import secrets
        if not secrets.compare_digest(api_key, "test-secret-api-key-12345"):
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return api_key

    test_app.dependency_overrides[verify_api_key] = override_verify_api_key
    
    # Add routers with auth dependency AFTER override is set
    test_app.include_router(users_router, dependencies=[Depends(verify_api_key)])
    test_app.include_router(intents_router, dependencies=[Depends(verify_api_key)])
    
    yield TestClient(test_app)
    test_app.dependency_overrides.clear()


@pytest.mark.api
class TestApiKeyAuthenticationDisabled:
    """Test API endpoints when API key authentication is disabled (default)."""

    def test_get_users_without_auth_when_disabled_succeeds(self, client):
        """Test GET /users succeeds without auth when authentication is disabled."""
        # Arrange
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "false"}, clear=False):
            # Act
            response = client.get("/users")

            # Assert
            assert response.status_code == 200

    def test_create_user_without_auth_when_disabled_succeeds(self, client):
        """Test POST /users succeeds without auth when authentication is disabled."""
        # Arrange
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "false"}, clear=False):
            # Act
            response = client.post("/users", json={"username": "testuser", "email": "test@example.com"})

            # Assert
            assert response.status_code == 201

    def test_public_endpoints_always_accessible(self, client):
        """Test public endpoints are always accessible regardless of auth setting."""
        # Arrange
        with patch.dict(os.environ, {"ENABLE_API_KEY_AUTH": "true", "API_KEY": "test-key"}, clear=False):
            # Act & Assert
            response = client.get("/")
            assert response.status_code == 200

            response = client.get("/health")
            assert response.status_code == 200

            response = client.get("/docs")
            assert response.status_code == 200


@pytest.mark.api
class TestApiKeyAuthenticationEnabled:
    """Test API endpoints when API key authentication is enabled."""

    @pytest.fixture
    def api_key(self):
        """Provide a test API key."""
        return "test-secret-api-key-12345"

    def test_get_users_without_auth_when_enabled_returns_401(self, client_with_auth):
        """Test GET /users returns 401 when auth is enabled but no API key provided."""
        # Act
        response = client_with_auth.get("/users")

        # Assert
        assert response.status_code == 401
        assert "error" in response.json() or "detail" in response.json()

    def test_get_users_with_invalid_key_returns_401(self, client_with_auth):
        """Test GET /users returns 401 when invalid API key is provided."""
        # Act
        response = client_with_auth.get("/users", headers={"Authorization": "Bearer wrong-key"})

        # Assert
        assert response.status_code == 401
        response_json = response.json()
        assert "Invalid API key" in response_json.get("error", "") or "Invalid API key" in response_json.get("detail", "")

    def test_get_users_with_valid_bearer_token_succeeds(self, client_with_auth, api_key):
        """Test GET /users succeeds with valid Bearer token."""
        # Act
        response = client_with_auth.get("/users", headers={"Authorization": f"Bearer {api_key}"})

        # Assert
        assert response.status_code == 200

    def test_get_users_with_valid_direct_key_succeeds(self, client_with_auth, api_key):
        """Test GET /users succeeds with valid direct API key."""
        # Act
        response = client_with_auth.get("/users", headers={"Authorization": api_key})

        # Assert
        assert response.status_code == 200

    def test_create_user_with_valid_key_succeeds(self, client_with_auth, api_key):
        """Test POST /users succeeds with valid API key."""
        # Act
        response = client_with_auth.post(
            "/users",
            json={"username": "testuser", "email": "test@example.com"},
            headers={"Authorization": f"Bearer {api_key}"},
        )

        # Assert
        assert response.status_code == 201

    def test_get_intents_with_valid_key_succeeds(self, client_with_auth, api_key):
        """Test GET /intents succeeds with valid API key."""
        # Act
        response = client_with_auth.get("/intents", headers={"Authorization": f"Bearer {api_key}"})

        # Assert
        assert response.status_code == 200

    def test_create_intent_with_valid_key_succeeds(self, client_with_auth, api_key):
        """Test POST /intents succeeds with valid API key."""
        # Act
        response = client_with_auth.post(
            "/intents",
            json={"name": "Test Intent", "description": "Test description", "output_format": "JSON"},
            headers={"Authorization": f"Bearer {api_key}"},
        )

        # Assert
        assert response.status_code == 201

