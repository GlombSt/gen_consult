"""
API schemas/DTOs for users domain.

These define the API contract for request and response payloads.
Used by the router layer.
"""

from typing import Optional

from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    """Request schema for creating a new user."""

    username: str
    email: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"username": "john_doe", "email": "john.doe@example.com"}]
        }
    }


class UserUpdateRequest(BaseModel):
    """Request schema for updating a user."""

    username: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    """Response schema for user data."""

    id: int
    username: str
    email: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"id": 1, "username": "john_doe", "email": "john.doe@example.com"}]
        }
    }
