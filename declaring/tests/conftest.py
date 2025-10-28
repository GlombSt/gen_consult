"""
Shared test fixtures and configuration.
"""

import pytest
from fastapi.testclient import TestClient

from app.items.repository import ItemRepository
from app.main import app
from app.shared.events import EventBus
from app.users.repository import UserRepository


@pytest.fixture
def test_app():
    """Provide the FastAPI application instance for testing."""
    return app


@pytest.fixture
def test_client(test_app):
    """Provide a test client for API testing."""
    return TestClient(test_app)


@pytest.fixture
def mock_item_repository():
    """Provide a fresh item repository for each test."""
    return ItemRepository()


@pytest.fixture
def mock_user_repository():
    """Provide a fresh user repository for each test."""
    return UserRepository()


@pytest.fixture
def mock_event_bus():
    """Provide a fresh event bus for each test."""
    return EventBus()
