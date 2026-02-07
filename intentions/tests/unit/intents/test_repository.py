"""
Unit tests for intents repository layer (V2).

Tests data access and model conversions with database.
"""

from datetime import datetime

import pytest

from app.intents.models import Aspect, Assumption, Choice, Example, Input, Insight, Output, Pitfall, Prompt, Quality
from app.intents.repository import IntentRepository
from tests.fixtures.intents import create_test_intent


@pytest.mark.unit
class TestIntentRepositoryFindById:
    """Test IntentRepository.find_by_id method."""

    @pytest.mark.asyncio
    async def test_find_by_id_when_exists_returns_intent(self, test_db_session):
        """Test finding an intent by ID when it exists."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created = await repo.create(intent)
        await test_db_session.commit()

        result = await repo.find_by_id(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.name == "Test Intent"
        assert hasattr(result, "aspects")
        assert isinstance(result.aspects, list)

    @pytest.mark.asyncio
    async def test_find_by_id_loads_aspects(self, test_db_session):
        """Test that find_by_id loads aspects from the database."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        aspect1 = Aspect(
            id=None,
            intent_id=created_intent.id,
            name="SEO",
        )
        aspect2 = Aspect(
            id=None,
            intent_id=created_intent.id,
            name="Audience",
        )
        await repo.add_aspect(created_intent.id, aspect1)
        await repo.add_aspect(created_intent.id, aspect2)
        await test_db_session.commit()

        result = await repo.find_by_id(created_intent.id)

        assert result is not None
        assert len(result.aspects) == 2
        assert any(a.name == "SEO" for a in result.aspects)
        assert any(a.name == "Audience" for a in result.aspects)

    @pytest.mark.asyncio
    async def test_list_aspects_by_intent_id(self, test_db_session):
        """Test listing aspects by intent_id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        await repo.add_aspect(
            created_intent.id,
            Aspect(id=None, intent_id=created_intent.id, name="A1", description="D1"),
        )
        await test_db_session.commit()

        result = await repo.list_aspects_by_intent_id(created_intent.id)
        assert len(result) == 1
        assert result[0].name == "A1"

    @pytest.mark.asyncio
    async def test_update_aspect_when_exists(self, test_db_session):
        """Test updating an aspect."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        aspect = Aspect(
            id=None,
            intent_id=created_intent.id,
            name="Old",
            description="Old desc",
        )
        added = await repo.add_aspect(created_intent.id, aspect)
        await test_db_session.commit()
        added.name = "New"
        added.description = "New desc"

        updated = await repo.update_aspect(created_intent.id, added.id, added)
        await test_db_session.commit()

        assert updated is not None
        assert updated.name == "New"
        assert updated.description == "New desc"

    @pytest.mark.asyncio
    async def test_delete_aspect_when_exists(self, test_db_session):
        """Test deleting an aspect."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        aspect = Aspect(
            id=None,
            intent_id=created_intent.id,
            name="ToDelete",
            description="Desc",
        )
        added = await repo.add_aspect(created_intent.id, aspect)
        await test_db_session.commit()

        ok = await repo.delete_aspect(created_intent.id, added.id)
        await test_db_session.commit()
        assert ok is True
        listed = await repo.list_aspects_by_intent_id(created_intent.id)
        assert len(listed) == 0

    @pytest.mark.asyncio
    async def test_find_by_id_when_not_exists_returns_none(self, test_db_session):
        """Test finding an intent by ID when it doesn't exist."""
        repo = IntentRepository(test_db_session)
        result = await repo.find_by_id(999)
        assert result is None


@pytest.mark.unit
class TestIntentRepositoryCreate:
    """Test IntentRepository.create method."""

    @pytest.mark.asyncio
    async def test_create_intent_assigns_id_and_returns_intent(self, test_db_session):
        """Test creating an intent assigns ID and returns domain model."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(
            id=None,
            name="New Intent",
            description="New description",
        )

        result = await repo.create(intent)
        await test_db_session.commit()

        assert result.id is not None
        assert result.id == 1
        assert result.name == "New Intent"
        assert result.description == "New description"

    @pytest.mark.asyncio
    async def test_create_multiple_intents_increments_id(self, test_db_session):
        """Test creating multiple intents increments ID counter."""
        repo = IntentRepository(test_db_session)
        intent1 = create_test_intent(id=None, name="Intent 1")
        intent2 = create_test_intent(id=None, name="Intent 2")

        result1 = await repo.create(intent1)
        await test_db_session.commit()
        result2 = await repo.create(intent2)
        await test_db_session.commit()

        assert result1.id == 1
        assert result2.id == 2


@pytest.mark.unit
class TestIntentRepositoryUpdate:
    """Test IntentRepository.update method."""

    @pytest.mark.asyncio
    async def test_update_intent_when_exists_returns_updated_intent(self, test_db_session):
        """Test updating an existing intent."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Old Name", description="Old description")
        created = await repo.create(intent)
        await test_db_session.commit()

        created.name = "New Name"
        created.description = "New description"

        result = await repo.update(created.id, created)
        await test_db_session.commit()

        assert result is not None
        assert result.id == created.id
        assert result.name == "New Name"
        assert result.description == "New description"

    @pytest.mark.asyncio
    async def test_update_intent_when_not_exists_returns_none(self, test_db_session):
        """Test updating a non-existent intent."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=999, name="Test", description="Test description")

        result = await repo.update(999, intent)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_intent_preserves_created_at(self, test_db_session):
        """Test updating an intent preserves created_at timestamp."""
        repo = IntentRepository(test_db_session)
        original_date = datetime(2025, 1, 1, 12, 0, 0)
        intent = create_test_intent(
            id=None,
            name="Test",
            description="Test description",
            created_at=original_date,
        )
        created = await repo.create(intent)
        await test_db_session.commit()

        created.name = "Updated"

        result = await repo.update(created.id, created)
        await test_db_session.commit()

        assert result.created_at == original_date


@pytest.mark.unit
class TestIntentRepositoryDelete:
    """Test IntentRepository.delete method."""

    @pytest.mark.asyncio
    async def test_delete_intent_when_exists_returns_true(self, test_db_session):
        """Test deleting an existing intent."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created = await repo.create(intent)
        await test_db_session.commit()

        result = await repo.delete(created.id)
        await test_db_session.commit()

        assert result is True
        found = await repo.find_by_id(created.id)
        assert found is None

    @pytest.mark.asyncio
    async def test_delete_intent_when_not_exists_returns_false(self, test_db_session):
        """Test deleting a non-existent intent."""
        repo = IntentRepository(test_db_session)
        result = await repo.delete(999)
        assert result is False


@pytest.mark.unit
class TestIntentRepositoryListAll:
    """Test IntentRepository.list_all method."""

    @pytest.mark.asyncio
    async def test_list_all_returns_all_intents_with_composition(self, test_db_session):
        """Test that list_all returns all intents with full composition."""
        repo = IntentRepository(test_db_session)
        intent1 = create_test_intent(id=None, name="First")
        intent2 = create_test_intent(id=None, name="Second")
        created1 = await repo.create(intent1)
        created2 = await repo.create(intent2)
        await test_db_session.commit()

        result = await repo.list_all()

        assert len(result) >= 2
        ids = [r.id for r in result]
        assert created1.id in ids
        assert created2.id in ids
        for r in result:
            assert hasattr(r, "aspects")
            assert hasattr(r, "inputs")
            assert hasattr(r, "prompts")
            assert hasattr(r, "insights")


@pytest.mark.unit
class TestInputRepository:
    """Test Input repository operations (V2)."""

    @pytest.mark.asyncio
    async def test_add_input_to_intent_assigns_id(self, test_db_session):
        """Test adding an input to an intent."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Input(
            id=None,
            intent_id=created_intent.id,
            name="Source document",
            description="The document to summarize",
        )
        result = await repo.add_input(created_intent.id, entity)
        await test_db_session.commit()

        assert result.id is not None
        assert result.name == "Source document"
        assert result.intent_id == created_intent.id

    @pytest.mark.asyncio
    async def test_list_inputs_by_intent_id(self, test_db_session):
        """Test listing inputs by intent_id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Input(
            id=None,
            intent_id=created_intent.id,
            name="Input 1",
            description="First input",
        )
        await repo.add_input(created_intent.id, entity)
        await test_db_session.commit()

        result = await repo.list_inputs_by_intent_id(created_intent.id)
        assert len(result) == 1
        assert result[0].name == "Input 1"

    @pytest.mark.asyncio
    async def test_update_input_when_exists(self, test_db_session):
        """Test updating an input."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        entity = Input(
            id=None,
            intent_id=created_intent.id,
            name="OldName",
            description="Old desc",
        )
        added = await repo.add_input(created_intent.id, entity)
        await test_db_session.commit()
        added.name = "NewName"
        added.description = "New desc"

        updated = await repo.update_input(created_intent.id, added.id, added)
        await test_db_session.commit()
        assert updated is not None
        assert updated.name == "NewName"

    @pytest.mark.asyncio
    async def test_delete_input_when_exists(self, test_db_session):
        """Test deleting an input."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        entity = Input(
            id=None,
            intent_id=created_intent.id,
            name="ToDelete",
            description="Desc",
        )
        added = await repo.add_input(created_intent.id, entity)
        await test_db_session.commit()

        ok = await repo.delete_input(created_intent.id, added.id)
        await test_db_session.commit()
        assert ok is True
        listed = await repo.list_inputs_by_intent_id(created_intent.id)
        assert len(listed) == 0


@pytest.mark.unit
class TestPromptRepository:
    """Test Prompt repository operations (V2)."""

    @pytest.mark.asyncio
    async def test_add_prompt_and_get_next_version(self, test_db_session):
        """Test adding a prompt and get_next_prompt_version."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        version = await repo.get_next_prompt_version(created_intent.id)
        assert version == 1

        entity = Prompt(
            id=None,
            intent_id=created_intent.id,
            content="Do the task.",
            version=version,
        )
        result = await repo.add_prompt(created_intent.id, entity)
        await test_db_session.commit()

        assert result.id is not None
        assert result.version == 1

        version2 = await repo.get_next_prompt_version(created_intent.id)
        assert version2 == 2

    @pytest.mark.asyncio
    async def test_list_prompts_by_intent_id(self, test_db_session):
        """Test listing prompts by intent_id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        p1 = Prompt(
            id=None,
            intent_id=created_intent.id,
            content="First prompt",
            version=1,
        )
        await repo.add_prompt(created_intent.id, p1)
        await test_db_session.commit()

        result = await repo.list_prompts_by_intent_id(created_intent.id)
        assert len(result) == 1
        assert result[0].content == "First prompt"


@pytest.mark.unit
class TestChoiceRepository:
    """Test Choice repository operations (V2)."""

    @pytest.mark.asyncio
    async def test_add_choice_to_intent_assigns_id(self, test_db_session):
        """Test adding a choice to an intent."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Choice(
            id=None,
            intent_id=created_intent.id,
            name="Format",
            description="Output format",
            options='["markdown", "plain"]',
        )
        result = await repo.add_choice(created_intent.id, entity)
        await test_db_session.commit()

        assert result.id is not None
        assert result.name == "Format"
        assert result.intent_id == created_intent.id

    @pytest.mark.asyncio
    async def test_list_choices_by_intent_id(self, test_db_session):
        """Test listing choices by intent_id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Choice(
            id=None,
            intent_id=created_intent.id,
            name="Choice 1",
            description="First choice",
        )
        await repo.add_choice(created_intent.id, entity)
        await test_db_session.commit()

        result = await repo.list_choices_by_intent_id(created_intent.id)
        assert len(result) == 1
        assert result[0].name == "Choice 1"

    @pytest.mark.asyncio
    async def test_find_choice_by_id_when_exists(self, test_db_session):
        """Test finding a choice by id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        entity = Choice(
            id=None,
            intent_id=created_intent.id,
            name="FindMe",
            description="Choice to find",
        )
        added = await repo.add_choice(created_intent.id, entity)
        await test_db_session.commit()

        found = await repo.find_choice_by_id(created_intent.id, added.id)
        assert found is not None
        assert found.name == "FindMe"


@pytest.mark.unit
class TestPitfallRepository:
    """Test Pitfall repository operations (V2)."""

    @pytest.mark.asyncio
    async def test_add_pitfall_to_intent_assigns_id(self, test_db_session):
        """Test adding a pitfall to an intent."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Pitfall(
            id=None,
            intent_id=created_intent.id,
            description="Output may be too verbose",
            mitigation="Add max length constraint",
        )
        result = await repo.add_pitfall(created_intent.id, entity)
        await test_db_session.commit()

        assert result.id is not None
        assert "verbose" in result.description
        assert result.intent_id == created_intent.id

    @pytest.mark.asyncio
    async def test_list_pitfalls_by_intent_id(self, test_db_session):
        """Test listing pitfalls by intent_id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Pitfall(
            id=None,
            intent_id=created_intent.id,
            description="Pitfall one",
        )
        await repo.add_pitfall(created_intent.id, entity)
        await test_db_session.commit()

        result = await repo.list_pitfalls_by_intent_id(created_intent.id)
        assert len(result) == 1
        assert result[0].description == "Pitfall one"

    @pytest.mark.asyncio
    async def test_find_pitfall_by_id_when_exists(self, test_db_session):
        """Test finding a pitfall by id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        entity = Pitfall(
            id=None,
            intent_id=created_intent.id,
            description="FindMe pitfall",
        )
        added = await repo.add_pitfall(created_intent.id, entity)
        await test_db_session.commit()

        found = await repo.find_pitfall_by_id(created_intent.id, added.id)
        assert found is not None
        assert "FindMe" in found.description


@pytest.mark.unit
class TestAssumptionRepository:
    """Test Assumption repository operations (V2)."""

    @pytest.mark.asyncio
    async def test_add_assumption_to_intent_assigns_id(self, test_db_session):
        """Test adding an assumption to an intent."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Assumption(
            id=None,
            intent_id=created_intent.id,
            description="User has basic domain knowledge",
            confidence="likely",
        )
        result = await repo.add_assumption(created_intent.id, entity)
        await test_db_session.commit()

        assert result.id is not None
        assert "domain knowledge" in result.description
        assert result.intent_id == created_intent.id

    @pytest.mark.asyncio
    async def test_list_assumptions_by_intent_id(self, test_db_session):
        """Test listing assumptions by intent_id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Assumption(
            id=None,
            intent_id=created_intent.id,
            description="Assumption one",
        )
        await repo.add_assumption(created_intent.id, entity)
        await test_db_session.commit()

        result = await repo.list_assumptions_by_intent_id(created_intent.id)
        assert len(result) == 1
        assert result[0].description == "Assumption one"


@pytest.mark.unit
class TestQualityRepository:
    """Test Quality repository operations (V2)."""

    @pytest.mark.asyncio
    async def test_add_quality_to_intent_assigns_id(self, test_db_session):
        """Test adding a quality to an intent."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Quality(
            id=None,
            intent_id=created_intent.id,
            criterion="Output is under 500 words",
            priority="must_have",
        )
        result = await repo.add_quality(created_intent.id, entity)
        await test_db_session.commit()

        assert result.id is not None
        assert "500 words" in result.criterion
        assert result.intent_id == created_intent.id

    @pytest.mark.asyncio
    async def test_list_qualities_by_intent_id(self, test_db_session):
        """Test listing qualities by intent_id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Quality(
            id=None,
            intent_id=created_intent.id,
            criterion="Quality one",
        )
        await repo.add_quality(created_intent.id, entity)
        await test_db_session.commit()

        result = await repo.list_qualities_by_intent_id(created_intent.id)
        assert len(result) == 1
        assert result[0].criterion == "Quality one"


@pytest.mark.unit
class TestExampleRepository:
    """Test Example repository operations (V2)."""

    @pytest.mark.asyncio
    async def test_add_example_to_intent_assigns_id(self, test_db_session):
        """Test adding an example to an intent."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Example(
            id=None,
            intent_id=created_intent.id,
            sample="Input: doc.pdf -> Output: summary",
            source="user_provided",
        )
        result = await repo.add_example(created_intent.id, entity)
        await test_db_session.commit()

        assert result.id is not None
        assert "doc.pdf" in result.sample
        assert result.intent_id == created_intent.id

    @pytest.mark.asyncio
    async def test_list_examples_by_intent_id(self, test_db_session):
        """Test listing examples by intent_id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Example(
            id=None,
            intent_id=created_intent.id,
            sample="Example one",
        )
        await repo.add_example(created_intent.id, entity)
        await test_db_session.commit()

        result = await repo.list_examples_by_intent_id(created_intent.id)
        assert len(result) == 1
        assert result[0].sample == "Example one"


@pytest.mark.unit
class TestOutputRepository:
    """Test Output repository operations (V2)."""

    @pytest.mark.asyncio
    async def test_add_output_to_prompt_assigns_id(self, test_db_session):
        """Test adding an output to a prompt."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        prompt = Prompt(
            id=None,
            intent_id=created_intent.id,
            content="Summarize the doc.",
            version=1,
        )
        created_prompt = await repo.add_prompt(created_intent.id, prompt)
        await test_db_session.commit()

        entity = Output(
            id=None,
            prompt_id=created_prompt.id,
            content="This is the summary.",
        )
        result = await repo.add_output(created_prompt.id, entity)
        await test_db_session.commit()

        assert result.id is not None
        assert "summary" in result.content
        assert result.prompt_id == created_prompt.id

    @pytest.mark.asyncio
    async def test_list_outputs_by_prompt_id(self, test_db_session):
        """Test listing outputs by prompt_id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()
        prompt = Prompt(
            id=None,
            intent_id=created_intent.id,
            content="Prompt.",
            version=1,
        )
        created_prompt = await repo.add_prompt(created_intent.id, prompt)
        await test_db_session.commit()
        entity = Output(
            id=None,
            prompt_id=created_prompt.id,
            content="Output one",
        )
        await repo.add_output(created_prompt.id, entity)
        await test_db_session.commit()

        result = await repo.list_outputs_by_prompt_id(created_prompt.id)
        assert len(result) == 1
        assert result[0].content == "Output one"


@pytest.mark.unit
class TestInsightRepository:
    """Test Insight repository operations (V2)."""

    @pytest.mark.asyncio
    async def test_add_insight_to_intent_assigns_id(self, test_db_session):
        """Test adding an insight to an intent."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Insight(
            id=None,
            intent_id=created_intent.id,
            content="Clarify scope with stakeholder",
            status="pending",
        )
        result = await repo.add_insight(created_intent.id, entity)
        await test_db_session.commit()

        assert result.id is not None
        assert "stakeholder" in result.content
        assert result.intent_id == created_intent.id

    @pytest.mark.asyncio
    async def test_list_insights_by_intent_id(self, test_db_session):
        """Test listing insights by intent_id."""
        repo = IntentRepository(test_db_session)
        intent = create_test_intent(id=None, name="Test Intent")
        created_intent = await repo.create(intent)
        await test_db_session.commit()

        entity = Insight(
            id=None,
            intent_id=created_intent.id,
            content="Insight one",
        )
        await repo.add_insight(created_intent.id, entity)
        await test_db_session.commit()

        result = await repo.list_insights_by_intent_id(created_intent.id)
        assert len(result) == 1
        assert result[0].content == "Insight one"
