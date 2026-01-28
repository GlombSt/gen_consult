"""
Repository layer for intents domain.

Handles data access and conversion between DB models and domain models using SQLAlchemy.
"""

from typing import Optional

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .db_models import FactDBModel, IntentDBModel
from .models import Fact, Intent


class IntentRepository:
    """
    Repository for intent and fact data access using SQLAlchemy.

    Uses hard deletes only (no soft delete).
    Facts are automatically deleted when intent is deleted (cascade delete).
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: AsyncSession instance for database operations
        """
        self.db = db

    async def find_by_id(self, intent_id: int) -> Optional[Intent]:
        """
        Find an intent by ID.

        Args:
            intent_id: The intent ID

        Returns:
            Domain model intent if found, None otherwise
        """
        result = await self.db.execute(
            select(IntentDBModel).options(selectinload(IntentDBModel.facts)).where(IntentDBModel.id == intent_id)
        )
        db_intent = result.scalar_one_or_none()
        if db_intent:
            return self._to_intent_domain_model(db_intent)
        return None

    async def create(self, intent: Intent) -> Intent:
        """
        Create a new intent.

        Args:
            intent: Domain model intent to create

        Returns:
            Created domain model intent with assigned ID
        """
        db_intent = self._to_intent_db_model(intent)
        self.db.add(db_intent)
        await self.db.flush()  # Flush to get the ID
        await self.db.refresh(db_intent)  # Refresh to get all fields
        # For new intents, facts will be empty, so _to_intent_domain_model() will handle it
        return self._to_intent_domain_model(db_intent)

    async def update(self, intent_id: int, intent: Intent) -> Optional[Intent]:
        """
        Update an existing intent.

        Args:
            intent_id: The intent ID to update
            intent: Domain model intent with updated data

        Returns:
            Updated domain model intent if found, None otherwise
        """
        result = await self.db.execute(
            select(IntentDBModel).options(selectinload(IntentDBModel.facts)).where(IntentDBModel.id == intent_id)
        )
        db_intent = result.scalar_one_or_none()

        if not db_intent:
            return None

        # Update fields (preserve created_at)
        db_intent.name = intent.name
        db_intent.description = intent.description
        db_intent.output_format = intent.output_format
        db_intent.output_structure = intent.output_structure
        db_intent.context = intent.context
        db_intent.constraints = intent.constraints
        # created_at remains unchanged
        # updated_at is automatically updated by SQLAlchemy

        await self.db.flush()
        await self.db.refresh(db_intent)
        # Facts are already loaded via selectinload in the query above
        return self._to_intent_domain_model(db_intent)

    async def delete(self, intent_id: int) -> bool:
        """
        Hard delete an intent (facts are cascade deleted).

        Args:
            intent_id: The intent ID to delete

        Returns:
            True if deleted, False if not found
        """
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(sql_delete(IntentDBModel).where(IntentDBModel.id == intent_id))
        await self.db.flush()
        rowcount: int = result.rowcount  # type: ignore[attr-defined]
        return rowcount > 0

    async def add_fact(self, intent_id: int, fact: Fact) -> Fact:
        """
        Add a fact to an intent.

        Args:
            intent_id: The intent ID to add the fact to
            fact: Domain model fact to add

        Returns:
            Created domain model fact with assigned ID

        Raises:
            ValueError: If intent not found
        """
        # Verify intent exists
        intent_result = await self.db.execute(select(IntentDBModel).where(IntentDBModel.id == intent_id))
        db_intent = intent_result.scalar_one_or_none()
        if not db_intent:
            raise ValueError(f"Intent with id {intent_id} not found")

        db_fact = self._to_fact_db_model(fact)
        db_fact.intent_id = intent_id
        self.db.add(db_fact)
        await self.db.flush()  # Flush to get the ID
        await self.db.refresh(db_fact)  # Refresh to get all fields
        return self._to_fact_domain_model(db_fact)

    async def find_fact_by_id(self, intent_id: int, fact_id: int) -> Optional[Fact]:
        """
        Find a fact by ID within an intent.

        Args:
            intent_id: The intent ID
            fact_id: The fact ID

        Returns:
            Domain model fact if found, None otherwise
        """
        result = await self.db.execute(
            select(FactDBModel).where(FactDBModel.id == fact_id, FactDBModel.intent_id == intent_id)
        )
        db_fact = result.scalar_one_or_none()
        if db_fact:
            return self._to_fact_domain_model(db_fact)
        return None

    async def update_fact(self, intent_id: int, fact_id: int, fact: Fact) -> Optional[Fact]:
        """
        Update an existing fact.

        Args:
            intent_id: The intent ID
            fact_id: The fact ID to update
            fact: Domain model fact with updated data

        Returns:
            Updated domain model fact if found, None otherwise
        """
        result = await self.db.execute(
            select(FactDBModel).where(FactDBModel.id == fact_id, FactDBModel.intent_id == intent_id)
        )
        db_fact = result.scalar_one_or_none()

        if not db_fact:
            return None

        # Update fields (preserve created_at)
        db_fact.value = fact.value
        # intent_id remains unchanged
        # created_at remains unchanged
        # updated_at is automatically updated by SQLAlchemy

        await self.db.flush()
        await self.db.refresh(db_fact)
        return self._to_fact_domain_model(db_fact)

    async def remove_fact(self, intent_id: int, fact_id: int) -> bool:
        """
        Hard delete a fact.

        Args:
            intent_id: The intent ID
            fact_id: The fact ID to remove

        Returns:
            True if removed, False if not found
        """
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(
            sql_delete(FactDBModel).where(FactDBModel.id == fact_id, FactDBModel.intent_id == intent_id)
        )
        await self.db.flush()
        return bool(result.rowcount > 0)

    def _to_intent_domain_model(self, db_intent: IntentDBModel) -> Intent:
        """Convert DB model to domain model."""
        # Convert facts from DB models to domain models
        # Safely access facts - check if relationship is loaded using SQLAlchemy inspect
        facts: list[Fact] = []
        try:
            # Check if facts relationship is loaded
            state = inspect(db_intent)
            if hasattr(state, "unloaded") and "facts" in state.unloaded:
                # Relationship not loaded, use empty list
                facts = []
            else:
                # Relationship is loaded (or doesn't exist), try to access it
                db_facts = db_intent.facts
                if db_facts is not None:
                    facts = [self._to_fact_domain_model(db_fact) for db_fact in db_facts]
        except (AttributeError, KeyError):
            # If inspection or relationship access fails, use empty list
            # Only catch specific exceptions related to relationship access
            # Let other exceptions (database errors, programming errors) bubble up
            facts = []

        return Intent(
            id=db_intent.id,
            name=db_intent.name,
            description=db_intent.description,
            output_format=db_intent.output_format,
            output_structure=db_intent.output_structure,
            context=db_intent.context,
            constraints=db_intent.constraints,
            created_at=db_intent.created_at,
            updated_at=db_intent.updated_at,
            facts=facts,
        )

    def _to_intent_db_model(self, intent: Intent) -> IntentDBModel:
        """Convert domain model to DB model."""
        return IntentDBModel(
            id=intent.id,
            name=intent.name,
            description=intent.description,
            output_format=intent.output_format,
            output_structure=intent.output_structure,
            context=intent.context,
            constraints=intent.constraints,
            created_at=intent.created_at,
            updated_at=intent.updated_at,
        )

    def _to_fact_domain_model(self, db_fact: FactDBModel) -> Fact:
        """Convert DB model to domain model."""
        return Fact(
            id=db_fact.id,
            intent_id=db_fact.intent_id,
            value=db_fact.value,
            created_at=db_fact.created_at,
            updated_at=db_fact.updated_at,
        )

    def _to_fact_db_model(self, fact: Fact) -> FactDBModel:
        """Convert domain model to DB model."""
        return FactDBModel(
            id=fact.id,
            intent_id=fact.intent_id,
            value=fact.value,
            created_at=fact.created_at,
            updated_at=fact.updated_at,
        )
