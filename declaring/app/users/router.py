"""
HTTP router for users domain.

Defines HTTP endpoints and handles request/response serialization.
"""

from typing import List

from fastapi import APIRouter, HTTPException, status

from . import service
from .schemas import UserCreateRequest, UserResponse, UserUpdateRequest

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("", response_model=List[UserResponse])
async def get_users():
    """Get all users."""
    users = await service.get_all_users()
    return [_to_response(user) for user in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """Get a specific user by ID."""
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _to_response(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(request: UserCreateRequest):
    """Create a new user."""
    user = await service.create_user(request)
    return _to_response(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, request: UserUpdateRequest):
    """Update an existing user."""
    user = await service.update_user(user_id, request)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return _to_response(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete a user."""
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")


def _to_response(user) -> UserResponse:
    """Convert domain model to response DTO."""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
    )
