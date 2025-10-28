"""
Users domain public API.

This module exports the public interface of the users domain.
Other domains should only import from this module, not from internal modules.
"""

from .router import router
from .schemas import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from .service import (
    create_user,
    delete_user,
    get_all_users,
    get_user,
    update_user,
)

__all__ = [
    # Service functions (public API)
    "get_all_users",
    "get_user",
    "create_user",
    "update_user",
    "delete_user",
    # Schemas (API contract)
    "UserResponse",
    "UserCreateRequest",
    "UserUpdateRequest",
    # Router
    "router",
]
