"""
Service layer for users domain.

Contains business logic and serves as the public API for this domain.
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.events import event_bus
from app.shared.logging_config import logger

from .events import UserCreatedEvent, UserDeletedEvent, UserUpdatedEvent
from .models import User
from .repository import UserRepository
from .schemas import UserCreateRequest, UserUpdateRequest


async def get_all_users(db: AsyncSession) -> List[User]:
    """
    Get all users.

    Args:
        db: Database session

    Returns:
        List of all users
    """
    logger.info("Fetching all users")
    repository = UserRepository(db)
    users = await repository.find_all()
    logger.info("Users fetched", extra={"total_users": len(users)})
    return users


async def get_user(user_id: int, db: AsyncSession) -> Optional[User]:
    """
    Get a specific user by ID.

    Args:
        user_id: The user ID
        db: Database session

    Returns:
        User if found, None otherwise
    """
    logger.info("Looking for user", extra={"user_id": user_id})
    repository = UserRepository(db)
    user = await repository.find_by_id(user_id)

    if user:
        logger.info("User found", extra={"user_id": user_id, "username": user.username})
    else:
        logger.warning("User not found", extra={"user_id": user_id})

    return user


async def create_user(request: UserCreateRequest, db: AsyncSession) -> User:
    """
    Create a new user.

    Args:
        request: User creation request
        db: Database session

    Returns:
        Created user
    """
    logger.info("Creating new user", extra={"username": request.username})

    # Create domain model
    user = User(
        id=None,
        username=request.username,
        email=request.email,
    )

    # Persist
    repository = UserRepository(db)
    created_user = await repository.create(user)

    # Publish domain event (MANDATORY)
    await event_bus.publish(
        UserCreatedEvent(
            user_id=created_user.id,
            username=created_user.username,
            email=created_user.email,
        )
    )

    logger.info(
        "User created successfully",
        extra={"user_id": created_user.id, "username": created_user.username}
    )

    return created_user


async def update_user(user_id: int, request: UserUpdateRequest, db: AsyncSession) -> Optional[User]:
    """
    Update an existing user.

    Args:
        user_id: The user ID to update
        request: User update request
        db: Database session

    Returns:
        Updated user if found, None otherwise
    """
    logger.info("Updating user", extra={"user_id": user_id})

    repository = UserRepository(db)
    # Get existing user
    existing_user = await repository.find_by_id(user_id)
    if not existing_user:
        logger.warning("User not found for update", extra={"user_id": user_id})
        return None

    # Apply updates
    if request.username is not None:
        existing_user.username = request.username
    if request.email is not None:
        existing_user.email = request.email

    # Persist
    updated_user = await repository.update(user_id, existing_user)

    # Publish domain event (MANDATORY)
    if updated_user:
        await event_bus.publish(
            UserUpdatedEvent(
                user_id=updated_user.id,
                username=updated_user.username,
                email=updated_user.email,
            )
        )

        logger.info("User updated successfully", extra={"user_id": user_id})

    return updated_user


async def delete_user(user_id: int, db: AsyncSession) -> bool:
    """
    Delete a user.

    Args:
        user_id: The user ID to delete
        db: Database session

    Returns:
        True if deleted, False if not found
    """
    logger.info("Deleting user", extra={"user_id": user_id})

    repository = UserRepository(db)
    # Check if user exists before deleting
    existing_user = await repository.find_by_id(user_id)
    if not existing_user:
        logger.warning("User not found for deletion", extra={"user_id": user_id})
        return False

    # Delete
    deleted = await repository.delete(user_id)

    # Publish domain event (MANDATORY)
    if deleted:
        await event_bus.publish(UserDeletedEvent(user_id=user_id))
        logger.info("User deleted successfully", extra={"user_id": user_id})

    return deleted
