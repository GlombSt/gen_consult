"""
Repository layer for items domain.

Handles data access and conversion between DB models and domain models using SQLAlchemy.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db_models import ItemDBModel
from .models import Item


class ItemRepository:
    """
    Repository for item data access using SQLAlchemy.

    Uses hard deletes only (no soft delete).
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: AsyncSession instance for database operations
        """
        self.db = db

    async def find_all(self) -> List[Item]:
        """
        Get all items.

        Returns:
            List of domain model items
        """
        result = await self.db.execute(select(ItemDBModel))
        db_items = result.scalars().all()
        return [self._to_domain_model(db_item) for db_item in db_items]

    async def find_by_id(self, item_id: int) -> Optional[Item]:
        """
        Find an item by ID.

        Args:
            item_id: The item ID

        Returns:
            Domain model item if found, None otherwise
        """
        result = await self.db.execute(select(ItemDBModel).where(ItemDBModel.id == item_id))
        db_item = result.scalar_one_or_none()
        if db_item:
            return self._to_domain_model(db_item)
        return None

    async def create(self, item: Item) -> Item:
        """
        Create a new item.

        Args:
            item: Domain model item to create

        Returns:
            Created domain model item with assigned ID
        """
        db_item = self._to_db_model(item)
        self.db.add(db_item)
        await self.db.flush()  # Flush to get the ID
        await self.db.refresh(db_item)  # Refresh to get all fields
        return self._to_domain_model(db_item)

    async def update(self, item_id: int, item: Item) -> Optional[Item]:
        """
        Update an existing item.

        Args:
            item_id: The item ID to update
            item: Domain model item with updated data

        Returns:
            Updated domain model item if found, None otherwise
        """
        result = await self.db.execute(select(ItemDBModel).where(ItemDBModel.id == item_id))
        db_item = result.scalar_one_or_none()

        if not db_item:
            return None

        # Update fields (preserve created_at)
        db_item.name = item.name
        db_item.description = item.description
        db_item.price = item.price
        db_item.is_available = item.is_available
        # created_at remains unchanged
        # updated_at is automatically updated by SQLAlchemy

        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain_model(db_item)

    async def delete(self, item_id: int) -> bool:
        """
        Hard delete an item.

        Args:
            item_id: The item ID to delete

        Returns:
            True if deleted, False if not found
        """
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(sql_delete(ItemDBModel).where(ItemDBModel.id == item_id))
        await self.db.flush()
        return result.rowcount > 0

    async def search(
        self,
        name: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        available_only: bool = False,
    ) -> List[Item]:
        """
        Search items with filters.

        Args:
            name: Filter by name (case-insensitive partial match)
            min_price: Minimum price filter
            max_price: Maximum price filter
            available_only: Filter for available items only

        Returns:
            List of matching domain model items
        """
        query = select(ItemDBModel)

        if name:
            query = query.where(ItemDBModel.name.ilike(f"%{name}%"))

        if min_price is not None:
            query = query.where(ItemDBModel.price >= min_price)

        if max_price is not None:
            query = query.where(ItemDBModel.price <= max_price)

        if available_only:
            query = query.where(ItemDBModel.is_available.is_(True))

        result = await self.db.execute(query)
        db_items = result.scalars().all()
        return [self._to_domain_model(db_item) for db_item in db_items]

    def _to_domain_model(self, db_item: ItemDBModel) -> Item:
        """Convert DB model to domain model."""
        return Item(
            id=db_item.id,
            name=db_item.name,
            description=db_item.description,
            price=db_item.price,
            is_available=db_item.is_available,
            created_at=db_item.created_at,
        )

    def _to_db_model(self, item: Item) -> ItemDBModel:
        """Convert domain model to DB model."""
        return ItemDBModel(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            is_available=item.is_available,
            created_at=item.created_at,
        )
