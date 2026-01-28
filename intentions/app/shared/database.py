"""
Database configuration and session management.

Handles SQLAlchemy async engine setup, session management, and database initialization.
Supports SQLite (in-memory) for development and PostgreSQL for production.
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from .logging_config import logger

# Base class for all ORM models
Base = declarative_base()

# Global variables for engine and session factory
_engine = None
_session_factory = None


def get_database_url() -> str:
    """
    Get database URL based on environment configuration.

    Returns:
        Database connection URL string
    """
    database_url = os.getenv("DATABASE_URL")
    database_type = os.getenv("DATABASE_TYPE", "sqlite").lower()

    # Production: Use PostgreSQL from DATABASE_URL
    if database_url and database_type == "postgresql":
        # Ensure asyncpg driver is used
        if database_url.startswith("postgresql://"):
            return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgres://"):
            return database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        return database_url

    # Development/Test: Use in-memory SQLite
    return "sqlite+aiosqlite:///:memory:"


def get_engine():
    """
    Get or create the async SQLAlchemy engine.

    Returns:
        AsyncEngine instance
    """
    global _engine
    if _engine is None:
        database_url = get_database_url()
        is_sqlite = database_url.startswith("sqlite")

        # SQLite-specific configuration
        if is_sqlite:
            _engine = create_async_engine(
                database_url,
                echo=False,  # Set to True for SQL query logging
                poolclass=StaticPool,
                connect_args={"check_same_thread": False},
            )
        else:
            # PostgreSQL configuration
            _engine = create_async_engine(
                database_url,
                echo=False,  # Set to True for SQL query logging
                pool_pre_ping=True,  # Verify connections before using
                pool_size=5,
                max_overflow=10,
            )

        logger.info(
            "Database engine created",
            extra={
                "database_type": "sqlite" if is_sqlite else "postgresql",
                "database_url": database_url.split("@")[-1] if "@" in database_url else "in-memory",
            },
        )

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get or create the session factory.

    Returns:
        AsyncSessionMaker instance
    """
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.info("Session factory created")

    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function for FastAPI to get database session.

    **Transaction Management:**
    - This function automatically commits transactions on successful completion
    - If an exception occurs, the transaction is automatically rolled back
    - The session is closed after the request completes
    - For complex operations requiring multiple operations in a single transaction,
      all operations within a single request will share the same session and transaction

    **Note:** The auto-commit behavior means that each HTTP request gets its own
    transaction boundary. If you need to perform multiple operations atomically
    across multiple requests, you'll need to implement a different transaction
    management strategy.

    Yields:
        AsyncSession instance
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.

    This should be called on application startup.
    Only creates tables in development (SQLite). In production, use Alembic migrations.
    """
    engine = get_engine()
    database_url = get_database_url()

    # Only auto-create tables for SQLite (development)
    if database_url.startswith("sqlite"):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created (SQLite)")
    else:
        logger.info("Database tables should be created via Alembic migrations (PostgreSQL)")


async def close_db() -> None:
    """
    Close database connections.

    This should be called on application shutdown.
    """
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None
        logger.info("Database engine closed")
