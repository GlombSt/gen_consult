"""
Repository layer for intents domain.

Handles data access and conversion between DB models and domain models.
"""

from typing import List, Optional

from .db_models import FactDBModel, IntentDBModel
from .models import Fact, Intent


class IntentRepository:
    """
    Repository for intent and fact data access.

    In a real application, this would interact with a database using SQLAlchemy or similar.
    For now, it uses in-memory storage.
    """

    def __init__(self):
        self._intent_storage: List[IntentDBModel] = []
        self._fact_storage: List[FactDBModel] = []
        self._intent_id_counter = 1
        self._fact_id_counter = 1

    async def find_all(self) -> List[Intent]:
        """
        Get all intents.

        Returns:
            List of domain model intents
        """
        return [self._to_intent_domain_model(db_intent) for db_intent in self._intent_storage]

    async def find_by_id(self, intent_id: int) -> Optional[Intent]:
        """
        Find an intent by ID.

        Args:
            intent_id: The intent ID

        Returns:
            Domain model intent if found, None otherwise
        """
        for db_intent in self._intent_storage:
            if db_intent.id == intent_id:
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
        db_intent.id = self._intent_id_counter
        self._intent_id_counter += 1
        self._intent_storage.append(db_intent)
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
        for index, db_intent in enumerate(self._intent_storage):
            if db_intent.id == intent_id:
                updated_db_intent = self._to_intent_db_model(intent)
                updated_db_intent.id = intent_id
                updated_db_intent.created_at = db_intent.created_at
                self._intent_storage[index] = updated_db_intent
                return self._to_intent_domain_model(updated_db_intent)
        return None

    async def delete(self, intent_id: int) -> bool:
        """
        Delete an intent.

        Args:
            intent_id: The intent ID to delete

        Returns:
            True if deleted, False if not found
        """
        for index, db_intent in enumerate(self._intent_storage):
            if db_intent.id == intent_id:
                self._intent_storage.pop(index)
                # Also delete all facts associated with this intent
                self._fact_storage = [f for f in self._fact_storage if f.intent_id != intent_id]
                return True
        return False

    async def add_fact(self, intent_id: int, fact: Fact) -> Fact:
        """
        Add a fact to an intent.

        Args:
            intent_id: The intent ID to add the fact to
            fact: Domain model fact to add

        Returns:
            Created domain model fact with assigned ID
        """
        # Verify intent exists
        intent = await self.find_by_id(intent_id)
        if not intent:
            raise ValueError(f"Intent with id {intent_id} not found")

        db_fact = self._to_fact_db_model(fact)
        db_fact.id = self._fact_id_counter
        db_fact.intent_id = intent_id
        self._fact_id_counter += 1
        self._fact_storage.append(db_fact)
        return self._to_fact_domain_model(db_fact)

    async def find_facts_by_intent_id(self, intent_id: int) -> List[Fact]:
        """
        Find all facts for an intent.

        Args:
            intent_id: The intent ID

        Returns:
            List of domain model facts for the intent
        """
        facts = [f for f in self._fact_storage if f.intent_id == intent_id]
        return [self._to_fact_domain_model(db_fact) for db_fact in facts]

    async def find_fact_by_id(self, intent_id: int, fact_id: int) -> Optional[Fact]:
        """
        Find a fact by ID within an intent.

        Args:
            intent_id: The intent ID
            fact_id: The fact ID

        Returns:
            Domain model fact if found, None otherwise
        """
        for db_fact in self._fact_storage:
            if db_fact.id == fact_id and db_fact.intent_id == intent_id:
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
        for index, db_fact in enumerate(self._fact_storage):
            if db_fact.id == fact_id and db_fact.intent_id == intent_id:
                updated_db_fact = self._to_fact_db_model(fact)
                updated_db_fact.id = fact_id
                updated_db_fact.intent_id = intent_id
                updated_db_fact.created_at = db_fact.created_at
                self._fact_storage[index] = updated_db_fact
                return self._to_fact_domain_model(updated_db_fact)
        return None

    async def remove_fact(self, intent_id: int, fact_id: int) -> bool:
        """
        Remove a fact from an intent.

        Args:
            intent_id: The intent ID
            fact_id: The fact ID to remove

        Returns:
            True if removed, False if not found
        """
        for index, db_fact in enumerate(self._fact_storage):
            if db_fact.id == fact_id and db_fact.intent_id == intent_id:
                self._fact_storage.pop(index)
                return True
        return False

    def _to_intent_domain_model(self, db_intent: IntentDBModel) -> Intent:
        """Convert DB model to domain model."""
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


# Global repository instance
intent_repository = IntentRepository()

