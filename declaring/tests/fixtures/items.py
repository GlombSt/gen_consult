"""
Test data fixtures for items domain.
"""

from datetime import datetime

from app.items.models import Item
from app.items.schemas import ItemCreateRequest, ItemUpdateRequest


def create_test_item(
    id: int = 1,
    name: str = "Test Item",
    description: str = "Test description",
    price: float = 99.99,
    is_available: bool = True,
    created_at: datetime = None,
) -> Item:
    """Create a test item domain model."""
    return Item(
        id=id,
        name=name,
        description=description,
        price=price,
        is_available=is_available,
        created_at=created_at or datetime(2025, 1, 1, 12, 0, 0),
    )


def create_test_item_create_request(
    name: str = "New Item", description: str = "New description", price: float = 149.99, is_available: bool = True
) -> ItemCreateRequest:
    """Create a test item create request."""
    return ItemCreateRequest(name=name, description=description, price=price, is_available=is_available)


def create_test_item_update_request(
    name: str = None, description: str = None, price: float = None, is_available: bool = None
) -> ItemUpdateRequest:
    """Create a test item update request."""
    return ItemUpdateRequest(name=name, description=description, price=price, is_available=is_available)
