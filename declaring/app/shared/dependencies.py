"""
Dependency injection functions for repositories.

Provides FastAPI dependency functions that create repository instances
with database sessions. This allows the service layer to be infrastructure-agnostic
by receiving repositories as dependencies rather than database sessions.
"""

from typing import TYPE_CHECKING

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db

if TYPE_CHECKING:
    from app.intents.repository import IntentRepository
    from app.items.repository import ItemRepository
    from app.users.repository import UserRepository


def get_item_repository(db: AsyncSession = Depends(get_db)) -> "ItemRepository":
    """
    Dependency function to get ItemRepository instance.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        ItemRepository instance configured with the database session
    """
    from app.items.repository import ItemRepository

    return ItemRepository(db)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> "UserRepository":
    """
    Dependency function to get UserRepository instance.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        UserRepository instance configured with the database session
    """
    from app.users.repository import UserRepository

    return UserRepository(db)


def get_intent_repository(db: AsyncSession = Depends(get_db)) -> "IntentRepository":
    """
    Dependency function to get IntentRepository instance.

    Args:
        db: Database session (injected by FastAPI)

    Returns:
        IntentRepository instance configured with the database session
    """
    from app.intents.repository import IntentRepository

    return IntentRepository(db)
