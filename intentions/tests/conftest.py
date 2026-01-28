"""
Shared test fixtures and configuration.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.intents.db_models import FactDBModel, IntentDBModel  # noqa: F401

# Import all DB models so Base.metadata knows about them
from app.main import app
from app.shared.database import Base
from app.shared.events import EventBus
from app.users.db_models import UserDBModel  # noqa: F401


@pytest.fixture
def test_app():
    """Provide the FastAPI application instance for testing."""
    return app


@pytest.fixture
def test_client(test_app):
    """Provide a test client for API testing."""
    return TestClient(test_app)


@pytest.fixture(scope="function")
async def test_db_session():
    """
    Provide a database session for testing.

    Creates an in-memory SQLite database, creates all tables,
    and yields a session. After the test, rolls back all changes
    and drops tables.
    """
    # Create in-memory SQLite database for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # Create all tables synchronously
    def create_tables(conn):
        Base.metadata.create_all(bind=conn)

    def drop_tables(conn):
        Base.metadata.drop_all(bind=conn)

    # Create session factory
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(create_tables)

    # Create session for test
    async with async_session_maker() as session:
        yield session
        # Rollback any uncommitted changes
        await session.rollback()

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(drop_tables)

    # Close engine
    await engine.dispose()


@pytest.fixture
async def mock_user_repository(test_db_session):
    """
    Provide a fresh user repository for each test.

    Note: This fixture requires test_db_session, which is async.
    Use this in async tests.
    """
    from app.users.repository import UserRepository

    return UserRepository(test_db_session)


@pytest.fixture
async def mock_intent_repository(test_db_session):
    """
    Provide a fresh intent repository for each test.

    Note: This fixture requires test_db_session, which is async.
    Use this in async tests.
    """
    from app.intents.repository import IntentRepository

    return IntentRepository(test_db_session)


@pytest.fixture
def mock_event_bus():
    """Provide a fresh event bus for each test."""
    return EventBus()
