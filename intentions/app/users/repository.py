"""
Repository layer for users domain.

Handles data access and conversion between DB models and domain models using SQLAlchemy.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db_models import UserDBModel
from .models import User


class UserRepository:
    """
    Repository for user data access using SQLAlchemy.

    Uses hard deletes only (no soft delete).
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: AsyncSession instance for database operations
        """
        self.db = db

    async def find_all(self) -> List[User]:
        """
        Get all users.

        Returns:
            List of domain model users
        """
        result = await self.db.execute(select(UserDBModel))
        db_users = result.scalars().all()
        return [self._to_domain_model(db_user) for db_user in db_users]

    async def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Find a user by ID.

        Args:
            user_id: The user ID

        Returns:
            Domain model user if found, None otherwise
        """
        result = await self.db.execute(select(UserDBModel).where(UserDBModel.id == user_id))
        db_user = result.scalar_one_or_none()
        if db_user:
            return self._to_domain_model(db_user)
        return None

    async def create(self, user: User) -> User:
        """
        Create a new user.

        Args:
            user: Domain model user to create

        Returns:
            Created domain model user with assigned ID
        """
        db_user = self._to_db_model(user)
        self.db.add(db_user)
        await self.db.flush()  # Flush to get the ID
        await self.db.refresh(db_user)  # Refresh to get all fields
        return self._to_domain_model(db_user)

    async def update(self, user_id: int, user: User) -> Optional[User]:
        """
        Update an existing user.

        Args:
            user_id: The user ID to update
            user: Domain model user with updated data

        Returns:
            Updated domain model user if found, None otherwise
        """
        result = await self.db.execute(select(UserDBModel).where(UserDBModel.id == user_id))
        db_user = result.scalar_one_or_none()

        if not db_user:
            return None

        # Update fields (preserve created_at)
        db_user.username = user.username
        db_user.email = user.email
        # created_at remains unchanged
        # updated_at is automatically updated by SQLAlchemy

        await self.db.flush()
        await self.db.refresh(db_user)
        return self._to_domain_model(db_user)

    async def delete(self, user_id: int) -> bool:
        """
        Hard delete a user.

        Args:
            user_id: The user ID to delete

        Returns:
            True if deleted, False if not found
        """
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(sql_delete(UserDBModel).where(UserDBModel.id == user_id))
        await self.db.flush()
        rowcount = result.rowcount  # type: ignore[attr-defined]
        return bool(rowcount > 0)

    def _to_domain_model(self, db_user: UserDBModel) -> User:
        """Convert DB model to domain model."""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            created_at=db_user.created_at,
        )

    def _to_db_model(self, user: User) -> UserDBModel:
        """Convert domain model to DB model."""
        return UserDBModel(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
        )
