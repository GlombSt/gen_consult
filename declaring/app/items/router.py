"""
HTTP router for items domain.

Defines HTTP endpoints and handles request/response serialization.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.database import get_db
from . import service
from .schemas import ItemCreateRequest, ItemResponse, ItemUpdateRequest

router = APIRouter(
    prefix="/items",
    tags=["items"],
)


@router.get("", response_model=List[ItemResponse])
async def get_items(db: AsyncSession = Depends(get_db)):
    """Get all items."""
    items = await service.get_all_items(db)
    return [_to_response(item) for item in items]


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific item by ID."""
    item = await service.get_item(item_id, db)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _to_response(item)


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(request: ItemCreateRequest, db: AsyncSession = Depends(get_db)):
    """Create a new item."""
    item = await service.create_item(request, db)
    return _to_response(item)


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, request: ItemUpdateRequest, db: AsyncSession = Depends(get_db)):
    """Update an existing item."""
    item = await service.update_item(item_id, request, db)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return _to_response(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an item."""
    deleted = await service.delete_item(item_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/search/query", response_model=List[ItemResponse])
async def search_items(
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """
    Search items with query parameters.
    Example: /items/search/query?name=laptop&min_price=100&max_price=1000&available_only=true
    """
    items = await service.search_items(
        name=name,
        min_price=min_price,
        max_price=max_price,
        available_only=available_only,
        db=db,
    )
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
