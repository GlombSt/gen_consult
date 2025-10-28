"""
HTTP router for items domain.

Defines HTTP endpoints and handles request/response serialization.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from . import service
from .schemas import ItemCreateRequest, ItemResponse, ItemUpdateRequest

router = APIRouter(
    prefix="/items",
    tags=["items"],
)


@router.get("", response_model=List[ItemResponse])
async def get_items():
    """Get all items."""
    items = await service.get_all_items()
    return [_to_response(item) for item in items]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get a specific item by ID."""
    item = await service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _to_response(item)


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(request: ItemCreateRequest):
    """Create a new item."""
    item = await service.create_item(request)
    return _to_response(item)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, request: ItemUpdateRequest):
    """Update an existing item."""
    item = await service.update_item(item_id, request)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _to_response(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Delete an item."""
    deleted = await service.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/search/query", response_model=List[ItemResponse])
async def search_items(
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available_only: bool = False,
):
    """
    Search items with query parameters.
    Example: /items/search/query?name=laptop&min_price=100&max_price=1000&available_only=true
    """
    items = await service.search_items(name=name, min_price=min_price, max_price=max_price, available_only=available_only)
    return [_to_response(item) for item in items]


def _to_response(item) -> ItemResponse:
    """Convert domain model to response DTO."""
    return ItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available,
    )
