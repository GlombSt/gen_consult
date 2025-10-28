"""
Repository layer for items domain.

Handles data access and conversion between DB models and domain models.
"""

from typing import List, Optional

from .db_models import ItemDBModel
from .models import Item


class ItemRepository:
    """
    Repository for item data access.

    In a real application, this would interact with a database using SQLAlchemy or similar.
    For now, it uses in-memory storage.
    """

    def __init__(self):
        self._storage: List[ItemDBModel] = []
        self._id_counter = 1

    async def find_all(self) -> List[Item]:
        """
        Get all items.

        Returns:
            List of domain model items
        """
        return [self._to_domain_model(db_item) for db_item in self._storage]

    async def find_by_id(self, item_id: int) -> Optional[Item]:
        """
        Find an item by ID.

        Args:
            item_id: The item ID

        Returns:
            Domain model item if found, None otherwise
        """
        for db_item in self._storage:
            if db_item.id == item_id:
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
        db_item.id = self._id_counter
        self._id_counter += 1
        self._storage.append(db_item)
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
        for index, db_item in enumerate(self._storage):
            if db_item.id == item_id:
                updated_db_item = self._to_db_model(item)
                updated_db_item.id = item_id
                updated_db_item.created_at = db_item.created_at
                self._storage[index] = updated_db_item
                return self._to_domain_model(updated_db_item)
        return None

    async def delete(self, item_id: int) -> bool:
        """
        Delete an item.

        Args:
            item_id: The item ID to delete

        Returns:
            True if deleted, False if not found
        """
        for index, db_item in enumerate(self._storage):
            if db_item.id == item_id:
                self._storage.pop(index)
                return True
        return False

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
        results = self._storage.copy()

        if name:
            results = [item for item in results if name.lower() in item.name.lower()]

        if min_price is not None:
            results = [item for item in results if item.price >= min_price]

        if max_price is not None:
            results = [item for item in results if item.price <= max_price]

        if available_only:
            results = [item for item in results if item.is_available]

        return [self._to_domain_model(db_item) for db_item in results]

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


# Global repository instance
item_repository = ItemRepository()
