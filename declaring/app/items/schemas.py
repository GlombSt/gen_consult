"""
API schemas/DTOs for items domain.

These define the API contract for request and response payloads.
Used by the router layer.
"""

from typing import Optional

from pydantic import BaseModel


class ItemCreateRequest(BaseModel):
    """Request schema for creating a new item."""

    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "name": "Laptop",
                "description": "High-performance laptop",
                "price": 999.99,
                "is_available": True
            }]
        }
    }


class ItemUpdateRequest(BaseModel):
    """Request schema for updating an item."""

    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None


class ItemResponse(BaseModel):
    """Response schema for item data."""

    id: int
    name: str
    description: Optional[str]
    price: float
    is_available: bool

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": 1,
                "name": "Laptop",
                "description": "High-performance laptop",
                "price": 999.99,
                "is_available": True
            }]
        }
    }
