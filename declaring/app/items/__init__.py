"""
Items domain public API.

This module exports the public interface of the items domain.
Other domains should only import from this module, not from internal modules.
"""

from .router import router
from .schemas import (
    ItemCreateRequest,
    ItemResponse,
    ItemUpdateRequest,
)
from .service import (
    create_item,
    delete_item,
    get_all_items,
    get_item,
    search_items,
    update_item,
)

__all__ = [
    # Service functions (public API)
    "get_all_items",
    "get_item",
    "create_item",
    "update_item",
    "delete_item",
    "search_items",
    # Schemas (API contract)
    "ItemResponse",
    "ItemCreateRequest",
    "ItemUpdateRequest",
    # Router
    "router",
]
