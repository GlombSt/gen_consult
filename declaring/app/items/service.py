"""
Service layer for items domain.

Contains business logic and serves as the public API for this domain.
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.events import event_bus
from app.shared.logging_config import logger

from .events import ItemCreatedEvent, ItemDeletedEvent, ItemUpdatedEvent
from .models import Item
from .repository import ItemRepository
from .schemas import ItemCreateRequest, ItemUpdateRequest


async def get_all_items(db: AsyncSession) -> List[Item]:
    """
    Get all items.

    Args:
        db: Database session

    Returns:
        List of all items
    """
    logger.info("Fetching all items")
    repository = ItemRepository(db)
    items = await repository.find_all()
    logger.info("Items fetched", extra={"total_items": len(items)})
    return items


async def get_item(item_id: int, db: AsyncSession) -> Optional[Item]:
    """
    Get a specific item by ID.

    Args:
        item_id: The item ID
        db: Database session

    Returns:
        Item if found, None otherwise
    """
    logger.info("Looking for item", extra={"item_id": item_id})
    repository = ItemRepository(db)
    item = await repository.find_by_id(item_id)

    if item:
        logger.info("Item found", extra={"item_id": item_id, "item_name": item.name})
    else:
        logger.warning("Item not found", extra={"item_id": item_id})

    return item


async def create_item(request: ItemCreateRequest, db: AsyncSession) -> Item:
    """
    Create a new item.

    Args:
        request: Item creation request
        db: Database session

    Returns:
        Created item
    """
    logger.info(
        "Creating new item",
        extra={
            "item_name": request.name,
            "item_price": request.price,
            "is_available": request.is_available,
        },
    )

    # Create domain model
    item = Item(
        id=None,
        name=request.name,
        description=request.description,
        price=request.price,
        is_available=request.is_available,
    )

    # Persist
    repository = ItemRepository(db)
    created_item = await repository.create(item)

    # Publish domain event (MANDATORY)
    await event_bus.publish(
        ItemCreatedEvent(
            item_id=created_item.id,
            name=created_item.name,
            price=created_item.price,
            is_available=created_item.is_available,
        )
    )

    logger.info("Item created successfully", extra={"item_id": created_item.id, "item_name": created_item.name})

    return created_item


async def update_item(item_id: int, request: ItemUpdateRequest, db: AsyncSession) -> Optional[Item]:
    """
    Update an existing item.

    Args:
        item_id: The item ID to update
        request: Item update request
        db: Database session

    Returns:
        Updated item if found, None otherwise
    """
    logger.info("Updating item", extra={"item_id": item_id})

    repository = ItemRepository(db)
    # Get existing item
    existing_item = await repository.find_by_id(item_id)
    if not existing_item:
        logger.warning("Item not found for update", extra={"item_id": item_id})
        return None

    # Apply updates
    if request.name is not None:
        existing_item.name = request.name
    if request.description is not None:
        existing_item.description = request.description
    if request.price is not None:
        existing_item.price = request.price
    if request.is_available is not None:
        existing_item.is_available = request.is_available

    # Persist
    updated_item = await repository.update(item_id, existing_item)

    # Publish domain event (MANDATORY)
    if updated_item:
        await event_bus.publish(
            ItemUpdatedEvent(
                item_id=updated_item.id,
                name=updated_item.name,
                price=updated_item.price,
                is_available=updated_item.is_available,
            )
        )

        logger.info("Item updated successfully", extra={"item_id": item_id})

    return updated_item


async def delete_item(item_id: int, db: AsyncSession) -> bool:
    """
    Delete an item.

    Args:
        item_id: The item ID to delete
        db: Database session

    Returns:
        True if deleted, False if not found
    """
    logger.info("Deleting item", extra={"item_id": item_id})

    repository = ItemRepository(db)
    # Check if item exists before deleting
    existing_item = await repository.find_by_id(item_id)
    if not existing_item:
        logger.warning("Item not found for deletion", extra={"item_id": item_id})
        return False

    # Delete
    deleted = await repository.delete(item_id)

    # Publish domain event (MANDATORY)
    if deleted:
        await event_bus.publish(ItemDeletedEvent(item_id=item_id))
        logger.info("Item deleted successfully", extra={"item_id": item_id})

    return deleted


async def search_items(
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available_only: bool = False,
    db: AsyncSession = None,
) -> List[Item]:
    """
    Search items with filters.

    Args:
        name: Filter by name (case-insensitive partial match)
        min_price: Minimum price filter
        max_price: Maximum price filter
        available_only: Filter for available items only
        db: Database session

    Returns:
        List of matching items
    """
    logger.info(
        "Searching items",
        extra={
            "name_filter": name,
            "min_price": min_price,
            "max_price": max_price,
            "available_only": available_only,
        },
    )

    repository = ItemRepository(db)
    results = await repository.search(name=name, min_price=min_price, max_price=max_price, available_only=available_only)

    logger.info("Search completed", extra={"results_count": len(results)})
    return results
