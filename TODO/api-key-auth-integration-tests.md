# API Key Authentication Integration Tests Failing

## Problem Description

Six API integration tests for API key authentication are currently failing in the test suite. These tests are located in `declaring/tests/api/test_api_key_auth.py` in the `TestApiKeyAuthenticationEnabled` class.

### Failing Tests

1. `test_get_users_with_invalid_key_returns_401` - Should return 401 when invalid API key is provided
2. `test_get_users_with_valid_bearer_token_succeeds` - Should succeed with valid Bearer token
3. `test_get_users_with_valid_direct_key_succeeds` - Should succeed with valid direct API key
4. `test_create_user_with_valid_key_succeeds` - Should succeed when creating user with valid API key
5. `test_get_intents_with_valid_key_succeeds` - Should succeed when getting intents with valid API key
6. `test_create_intent_with_valid_key_succeeds` - Should succeed when creating intent with valid API key

### Current Behavior

All six tests are failing with 401 Unauthorized responses even when valid API keys are provided. The tests are using a `client_with_auth` fixture that creates a new FastAPI application instance with API key authentication enabled.

### Root Cause

The `client_with_auth` fixture attempts to:
1. Create a new FastAPI application instance
2. Override database dependencies to use the test database session
3. Override repository dependencies
4. Override the `verify_api_key` dependency to use a test API key
5. Include routers with API key authentication dependency

However, the dependency overrides are not being properly applied when the routers are included with router-level dependencies. The FastAPI dependency injection system is not recognizing the overridden `verify_api_key` function when it's used as a router-level dependency.

### Impact

- **Security**: While the unit tests (15 tests) comprehensively cover the `verify_api_key` function logic, the integration tests would verify end-to-end authentication flow in the actual application
- **Test Coverage**: The unit tests provide 82.81% coverage, but the integration tests would ensure the authentication works correctly in the full request/response cycle
- **CI/CD**: These failing tests prevent the CI pipeline from passing completely

### Context

- Unit tests for `verify_api_key` are passing (11 tests in `test_dependencies.py`)
- Unit tests for exception handlers are passing (3 tests in `test_exception_handlers.py`)
- The authentication logic itself is correct and secure (uses `secrets.compare_digest()` for constant-time comparison)
- The issue is purely with the test setup, not the implementation

### Related Files

- `declaring/tests/api/test_api_key_auth.py` - Contains the failing tests
- `declaring/app/shared/dependencies.py` - Contains the `verify_api_key` function
- `declaring/app/main.py` - Shows how routers are included with dependencies in the main app
- `declaring/tests/conftest.py` - Contains shared test fixtures including `test_db_session`

