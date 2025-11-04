"""
Unit tests for intents repository layer.

Tests data access and model conversions with mocked database.
"""

from datetime import datetime

import pytest

from app.intents.repository import IntentRepository
from tests.fixtures.intents import create_test_fact, create_test_intent


@pytest.mark.unit
class TestIntentRepositoryFindAll:
    """Test IntentRepository.find_all method."""

    @pytest.mark.asyncio
    async def test_find_all_with_intents_returns_all_intents(self):
        """Test finding all intents when intents exist."""
        # Arrange
        repo = IntentRepository()
        intent1 = create_test_intent(id=None, name="Intent 1")
        intent2 = create_test_intent(id=None, name="Intent 2")
        await repo.create(intent1)
        await repo.create(intent2)

        # Act
        result = await repo.find_all()

        # Assert
        assert len(result) == 2
        assert result[0].name == "Intent 1"
        assert result[1].name == "Intent 2"

    @pytest.mark.asyncio
    async def test_find_all_with_empty_storage_returns_empty_list(self):
        """Test finding all intents when storage is empty."""
        # Arrange
        repo = IntentRepository()

        # Act
        result = await repo.find_all()

        # Assert
        assert result == []


@pytest.mark.unit
class TestIntentRepositoryFindById:
    """Test IntentRepository.find_by_id method."""

    @pytest.mark.asyncio
    async def test_find_by_id_when_exists_returns_intent(self):
        """Test finding an intent by ID when it exists."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created = await repo.create(intent)

        # Act
        result = await repo.find_by_id(created.id)

        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.name == "Test Intent"

    @pytest.mark.asyncio
    async def test_find_by_id_when_not_exists_returns_none(self):
        """Test finding an intent by ID when it doesn't exist."""
        # Arrange
        repo = IntentRepository()

        # Act
        result = await repo.find_by_id(999)

        # Assert
        assert result is None


@pytest.mark.unit
class TestIntentRepositoryCreate:
    """Test IntentRepository.create method."""

    @pytest.mark.asyncio
    async def test_create_intent_assigns_id_and_returns_intent(self):
        """Test creating an intent assigns ID and returns domain model."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(
            id=None,
            name="New Intent",
            description="New description",
            output_format="JSON",
        )

        # Act
        result = await repo.create(intent)

        # Assert
        assert result.id is not None
        assert result.id == 1
        assert result.name == "New Intent"
        assert result.description == "New description"
        assert result.output_format == "JSON"

    @pytest.mark.asyncio
    async def test_create_multiple_intents_increments_id(self):
        """Test creating multiple intents increments ID counter."""
        # Arrange
        repo = IntentRepository()
        intent1 = create_test_intent(id=None, name="Intent 1")
        intent2 = create_test_intent(id=None, name="Intent 2")

        # Act
        result1 = await repo.create(intent1)
        result2 = await repo.create(intent2)

        # Assert
        assert result1.id == 1
        assert result2.id == 2


@pytest.mark.unit
class TestIntentRepositoryUpdate:
    """Test IntentRepository.update method."""

    @pytest.mark.asyncio
    async def test_update_intent_when_exists_returns_updated_intent(self):
        """Test updating an existing intent."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Old Name", description="Old description")
        created = await repo.create(intent)

        # Modify the intent
        created.name = "New Name"
        created.description = "New description"

        # Act
        result = await repo.update(created.id, created)

        # Assert
        assert result is not None
        assert result.id == created.id
        assert result.name == "New Name"
        assert result.description == "New description"

    @pytest.mark.asyncio
    async def test_update_intent_when_not_exists_returns_none(self):
        """Test updating a non-existent intent."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=999, name="Test")

        # Act
        result = await repo.update(999, intent)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_intent_preserves_created_at(self):
        """Test updating an intent preserves created_at timestamp."""
        # Arrange
        repo = IntentRepository()
        original_date = datetime(2025, 1, 1, 12, 0, 0)
        intent = create_test_intent(id=None, name="Test", created_at=original_date)
        created = await repo.create(intent)

        # Modify the intent
        created.name = "Updated"

        # Act
        result = await repo.update(created.id, created)

        # Assert
        assert result.created_at == original_date


@pytest.mark.unit
class TestIntentRepositoryDelete:
    """Test IntentRepository.delete method."""

    @pytest.mark.asyncio
    async def test_delete_intent_when_exists_returns_true(self):
        """Test deleting an existing intent."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created = await repo.create(intent)

        # Act
        result = await repo.delete(created.id)

        # Assert
        assert result is True
        # Verify intent is actually deleted
        found = await repo.find_by_id(created.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_delete_intent_when_not_exists_returns_false(self):
        """Test deleting a non-existent intent."""
        # Arrange
        repo = IntentRepository()

        # Act
        result = await repo.delete(999)

        # Assert
        assert result is False


@pytest.mark.unit
class TestFactRepository:
    """Test Fact repository operations."""

    @pytest.mark.asyncio
    async def test_add_fact_to_intent_assigns_id_and_returns_fact(self):
        """Test adding a fact to an intent assigns ID and returns domain model."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        fact = create_test_fact(id=None, intent_id=created_intent.id, value="Test fact")

        # Act
        result = await repo.add_fact(created_intent.id, fact)

        # Assert
        assert result.id is not None
        assert result.intent_id == created_intent.id
        assert result.value == "Test fact"

    @pytest.mark.asyncio
    async def test_find_facts_by_intent_id_returns_all_facts(self):
        """Test finding facts by intent ID returns all facts for that intent."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        fact1 = create_test_fact(id=None, intent_id=created_intent.id, value="Fact 1")
        fact2 = create_test_fact(id=None, intent_id=created_intent.id, value="Fact 2")
        await repo.add_fact(created_intent.id, fact1)
        await repo.add_fact(created_intent.id, fact2)

        # Act
        result = await repo.find_facts_by_intent_id(created_intent.id)

        # Assert
        assert len(result) == 2
        assert any(f.value == "Fact 1" for f in result)
        assert any(f.value == "Fact 2" for f in result)

    @pytest.mark.asyncio
    async def test_find_facts_by_intent_id_when_no_facts_returns_empty_list(self):
        """Test finding facts for an intent with no facts returns empty list."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)

        # Act
        result = await repo.find_facts_by_intent_id(created_intent.id)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_find_fact_by_id_when_exists_returns_fact(self):
        """Test finding a fact by ID when it exists."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        fact = create_test_fact(id=None, intent_id=created_intent.id, value="Test fact")
        created_fact = await repo.add_fact(created_intent.id, fact)

        # Act
        result = await repo.find_fact_by_id(created_intent.id, created_fact.id)

        # Assert
        assert result is not None
        assert result.id == created_fact.id
        assert result.value == "Test fact"

    @pytest.mark.asyncio
    async def test_find_fact_by_id_when_not_exists_returns_none(self):
        """Test finding a fact by ID when it doesn't exist."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)

        # Act
        result = await repo.find_fact_by_id(created_intent.id, 999)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update_fact_when_exists_returns_updated_fact(self):
        """Test updating an existing fact."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        fact = create_test_fact(id=None, intent_id=created_intent.id, value="Old value")
        created_fact = await repo.add_fact(created_intent.id, fact)

        # Modify the fact
        created_fact.value = "New value"

        # Act
        result = await repo.update_fact(created_intent.id, created_fact.id, created_fact)

        # Assert
        assert result is not None
        assert result.id == created_fact.id
        assert result.value == "New value"

    @pytest.mark.asyncio
    async def test_update_fact_when_not_exists_returns_none(self):
        """Test updating a non-existent fact."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        fact = create_test_fact(id=999, intent_id=created_intent.id, value="Test")

        # Act
        result = await repo.update_fact(created_intent.id, 999, fact)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_remove_fact_when_exists_returns_true(self):
        """Test removing an existing fact."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        fact = create_test_fact(id=None, intent_id=created_intent.id, value="Test fact")
        created_fact = await repo.add_fact(created_intent.id, fact)

        # Act
        result = await repo.remove_fact(created_intent.id, created_fact.id)

        # Assert
        assert result is True
        # Verify fact is actually removed
        found = await repo.find_fact_by_id(created_intent.id, created_fact.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_remove_fact_when_not_exists_returns_false(self):
        """Test removing a non-existent fact."""
        # Arrange
        repo = IntentRepository()
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)

        # Act
        result = await repo.remove_fact(created_intent.id, 999)

        # Assert
        assert result is False

