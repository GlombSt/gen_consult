"""
Repository layer for users domain.

Handles data access and conversion between DB models and domain models.
"""

from typing import List, Optional

from .db_models import UserDBModel
from .models import User


class UserRepository:
    """
    Repository for user data access.

    In a real application, this would interact with a database using SQLAlchemy or similar.
    For now, it uses in-memory storage.
    """

    def __init__(self):
        self._storage: List[UserDBModel] = []
        self._id_counter = 1

    async def find_all(self) -> List[User]:
        """
        Get all users.

        Returns:
            List of domain model users
        """
        return [self._to_domain_model(db_user) for db_user in self._storage]

    async def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Find a user by ID.

        Args:
            user_id: The user ID

        Returns:
            Domain model user if found, None otherwise
        """
        for db_user in self._storage:
            if db_user.id == user_id:
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
        db_user.id = self._id_counter
        self._id_counter += 1
        self._storage.append(db_user)
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
        for index, db_user in enumerate(self._storage):
            if db_user.id == user_id:
                updated_db_user = self._to_db_model(user)
                updated_db_user.id = user_id
                updated_db_user.created_at = db_user.created_at
                self._storage[index] = updated_db_user
                return self._to_domain_model(updated_db_user)
        return None

    async def delete(self, user_id: int) -> bool:
        """
        Delete a user.

        Args:
            user_id: The user ID to delete

        Returns:
            True if deleted, False if not found
        """
        for index, db_user in enumerate(self._storage):
            if db_user.id == user_id:
                self._storage.pop(index)
                return True
        return False

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


# Global repository instance
user_repository = UserRepository()
