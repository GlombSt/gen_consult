"""
Repository layer for intents domain (V2).

Handles data access and conversion between DB models and domain models using SQLAlchemy.
"""

from typing import List, Optional

from sqlalchemy import inspect, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .db_models import (
    AssumptionDBModel,
    AspectDBModel,
    ChoiceDBModel,
    ExampleDBModel,
    InsightDBModel,
    InputDBModel,
    IntentDBModel,
    OutputDBModel,
    PitfallDBModel,
    PromptDBModel,
    QualityDBModel,
)
from .models import (
    Assumption,
    Aspect,
    Choice,
    Example,
    Insight,
    Input,
    Intent,
    Output,
    Pitfall,
    Prompt,
    Quality,
)


def _safe_relation_list(db_obj, rel_name: str) -> list:
    """Return loaded relationship list or empty list if not loaded."""
    try:
        state = inspect(db_obj)
        if hasattr(state, "unloaded") and rel_name in state.unloaded:
            return []
        rel = getattr(db_obj, rel_name, None)
        return list(rel) if rel is not None else []
    except AttributeError:
        return []
    except KeyError:
        return []


class IntentRepository:
    """Repository for intent and V2 entity data access."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_id(self, intent_id: int) -> Optional[Intent]:
        result = await self.db.execute(
            select(IntentDBModel)
            .options(
                selectinload(IntentDBModel.aspects),
                selectinload(IntentDBModel.inputs),
                selectinload(IntentDBModel.choices),
                selectinload(IntentDBModel.pitfalls),
                selectinload(IntentDBModel.assumptions),
                selectinload(IntentDBModel.qualities),
                selectinload(IntentDBModel.examples),
                selectinload(IntentDBModel.prompts),
                selectinload(IntentDBModel.insights),
            )
            .where(IntentDBModel.id == intent_id)
        )
        db_intent = result.scalar_one_or_none()
        if db_intent:
            return self._to_intent_domain_model(db_intent)
        return None

    async def list_all(self) -> List[Intent]:
        """List all intents with full composition (aspects, inputs, etc.)."""
        result = await self.db.execute(
            select(IntentDBModel)
            .options(
                selectinload(IntentDBModel.aspects),
                selectinload(IntentDBModel.inputs),
                selectinload(IntentDBModel.choices),
                selectinload(IntentDBModel.pitfalls),
                selectinload(IntentDBModel.assumptions),
                selectinload(IntentDBModel.qualities),
                selectinload(IntentDBModel.examples),
                selectinload(IntentDBModel.prompts),
                selectinload(IntentDBModel.insights),
            )
            .order_by(IntentDBModel.id)
        )
        rows = result.scalars().all()
        return [self._to_intent_domain_model(db_intent) for db_intent in rows]

    async def create(self, intent: Intent) -> Intent:
        db_intent = self._to_intent_db_model(intent)
        self.db.add(db_intent)
        await self.db.flush()
        await self.db.refresh(db_intent)
        return self._to_intent_domain_model(db_intent)

    async def update(self, intent_id: int, intent: Intent) -> Optional[Intent]:
        result = await self.db.execute(
            select(IntentDBModel)
            .options(
                selectinload(IntentDBModel.aspects),
                selectinload(IntentDBModel.inputs),
                selectinload(IntentDBModel.choices),
                selectinload(IntentDBModel.pitfalls),
                selectinload(IntentDBModel.assumptions),
                selectinload(IntentDBModel.qualities),
                selectinload(IntentDBModel.examples),
                selectinload(IntentDBModel.prompts),
                selectinload(IntentDBModel.insights),
            )
            .where(IntentDBModel.id == intent_id)
        )
        db_intent = result.scalar_one_or_none()
        if not db_intent:
            return None
        db_intent.name = intent.name
        db_intent.description = intent.description
        await self.db.flush()
        await self.db.refresh(db_intent)
        return self._to_intent_domain_model(db_intent)

    async def delete(self, intent_id: int) -> bool:
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(
            sql_delete(IntentDBModel).where(IntentDBModel.id == intent_id)
        )
        await self.db.flush()
        return bool(result.rowcount and result.rowcount > 0)

    def _to_intent_domain_model(self, db_intent: IntentDBModel) -> Intent:
        aspects = _safe_relation_list(db_intent, "aspects")
        inputs = _safe_relation_list(db_intent, "inputs")
        choices = _safe_relation_list(db_intent, "choices")
        pitfalls = _safe_relation_list(db_intent, "pitfalls")
        assumptions = _safe_relation_list(db_intent, "assumptions")
        qualities = _safe_relation_list(db_intent, "qualities")
        examples = _safe_relation_list(db_intent, "examples")
        prompts = _safe_relation_list(db_intent, "prompts")
        insights = _safe_relation_list(db_intent, "insights")
        return Intent(
            id=db_intent.id,
            name=db_intent.name,
            description=db_intent.description,
            created_at=db_intent.created_at,
            updated_at=db_intent.updated_at,
            aspects=[self._to_aspect_domain_model(a) for a in aspects],
            inputs=[self._to_input_domain_model(i) for i in inputs],
            choices=[self._to_choice_domain_model(c) for c in choices],
            pitfalls=[self._to_pitfall_domain_model(p) for p in pitfalls],
            assumptions=[self._to_assumption_domain_model(a) for a in assumptions],
            qualities=[self._to_quality_domain_model(q) for q in qualities],
            examples=[self._to_example_domain_model(e) for e in examples],
            prompts=[self._to_prompt_domain_model(p) for p in prompts],
            insights=[self._to_insight_domain_model(i) for i in insights],
        )

    def _to_intent_db_model(self, intent: Intent) -> IntentDBModel:
        return IntentDBModel(
            id=intent.id,
            name=intent.name,
            description=intent.description,
            created_at=intent.created_at,
            updated_at=intent.updated_at,
        )

    # --- Aspect ---
    async def add_aspect(self, intent_id: int, aspect: Aspect) -> Aspect:
        await self._ensure_intent_exists(intent_id)
        db = self._to_aspect_db_model(aspect)
        db.intent_id = intent_id
        self.db.add(db)
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_aspect_domain_model(db)

    async def find_aspect_by_id(
        self, intent_id: int, aspect_id: int
    ) -> Optional[Aspect]:
        result = await self.db.execute(
            select(AspectDBModel).where(
                AspectDBModel.id == aspect_id,
                AspectDBModel.intent_id == intent_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_aspect_domain_model(row) if row else None

    async def list_aspects_by_intent_id(self, intent_id: int) -> List[Aspect]:
        result = await self.db.execute(
            select(AspectDBModel).where(AspectDBModel.intent_id == intent_id)
        )
        return [self._to_aspect_domain_model(r) for r in result.scalars().all()]

    async def update_aspect(
        self, intent_id: int, aspect_id: int, aspect: Aspect
    ) -> Optional[Aspect]:
        result = await self.db.execute(
            select(AspectDBModel).where(
                AspectDBModel.id == aspect_id,
                AspectDBModel.intent_id == intent_id,
            )
        )
        db = result.scalar_one_or_none()
        if not db:
            return None
        db.name = aspect.name
        db.description = aspect.description
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_aspect_domain_model(db)

    async def delete_aspect(self, intent_id: int, aspect_id: int) -> bool:
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(
            sql_delete(AspectDBModel).where(
                AspectDBModel.id == aspect_id,
                AspectDBModel.intent_id == intent_id,
            )
        )
        await self.db.flush()
        return bool(result.rowcount and result.rowcount > 0)

    def _to_aspect_domain_model(self, db: AspectDBModel) -> Aspect:
        return Aspect(
            id=db.id,
            intent_id=db.intent_id,
            name=db.name,
            description=db.description,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    def _to_aspect_db_model(self, a: Aspect) -> AspectDBModel:
        return AspectDBModel(
            id=a.id,
            intent_id=a.intent_id,
            name=a.name,
            description=a.description,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )

    # --- Input ---
    async def add_input(self, intent_id: int, entity: Input) -> Input:
        await self._ensure_intent_exists(intent_id)
        db = self._to_input_db_model(entity)
        db.intent_id = intent_id
        self.db.add(db)
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_input_domain_model(db)

    async def find_input_by_id(
        self, intent_id: int, input_id: int
    ) -> Optional[Input]:
        result = await self.db.execute(
            select(InputDBModel).where(
                InputDBModel.id == input_id,
                InputDBModel.intent_id == intent_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_input_domain_model(row) if row else None

    async def list_inputs_by_intent_id(self, intent_id: int) -> List[Input]:
        result = await self.db.execute(
            select(InputDBModel).where(InputDBModel.intent_id == intent_id)
        )
        return [self._to_input_domain_model(r) for r in result.scalars().all()]

    async def update_input(
        self, intent_id: int, input_id: int, entity: Input
    ) -> Optional[Input]:
        result = await self.db.execute(
            select(InputDBModel).where(
                InputDBModel.id == input_id,
                InputDBModel.intent_id == intent_id,
            )
        )
        db = result.scalar_one_or_none()
        if not db:
            return None
        db.name = entity.name
        db.description = entity.description
        db.aspect_id = entity.aspect_id
        db.format = entity.format
        db.required = entity.required
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_input_domain_model(db)

    async def delete_input(self, intent_id: int, input_id: int) -> bool:
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(
            sql_delete(InputDBModel).where(
                InputDBModel.id == input_id,
                InputDBModel.intent_id == intent_id,
            )
        )
        await self.db.flush()
        return bool(result.rowcount and result.rowcount > 0)

    def _to_input_domain_model(self, db: InputDBModel) -> Input:
        return Input(
            id=db.id,
            intent_id=db.intent_id,
            aspect_id=db.aspect_id,
            name=db.name,
            description=db.description,
            format=db.format,
            required=db.required,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    def _to_input_db_model(self, e: Input) -> InputDBModel:
        return InputDBModel(
            id=e.id,
            intent_id=e.intent_id,
            aspect_id=e.aspect_id,
            name=e.name,
            description=e.description,
            format=e.format,
            required=e.required,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    # --- Choice ---
    async def add_choice(self, intent_id: int, entity: Choice) -> Choice:
        await self._ensure_intent_exists(intent_id)
        db = self._to_choice_db_model(entity)
        db.intent_id = intent_id
        self.db.add(db)
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_choice_domain_model(db)

    async def find_choice_by_id(
        self, intent_id: int, choice_id: int
    ) -> Optional[Choice]:
        result = await self.db.execute(
            select(ChoiceDBModel).where(
                ChoiceDBModel.id == choice_id,
                ChoiceDBModel.intent_id == intent_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_choice_domain_model(row) if row else None

    async def list_choices_by_intent_id(self, intent_id: int) -> List[Choice]:
        result = await self.db.execute(
            select(ChoiceDBModel).where(ChoiceDBModel.intent_id == intent_id)
        )
        return [self._to_choice_domain_model(r) for r in result.scalars().all()]

    async def update_choice(
        self, intent_id: int, choice_id: int, entity: Choice
    ) -> Optional[Choice]:
        result = await self.db.execute(
            select(ChoiceDBModel).where(
                ChoiceDBModel.id == choice_id,
                ChoiceDBModel.intent_id == intent_id,
            )
        )
        db = result.scalar_one_or_none()
        if not db:
            return None
        db.name = entity.name
        db.description = entity.description
        db.aspect_id = entity.aspect_id
        db.options = entity.options
        db.selected_option = entity.selected_option
        db.rationale = entity.rationale
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_choice_domain_model(db)

    async def delete_choice(self, intent_id: int, choice_id: int) -> bool:
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(
            sql_delete(ChoiceDBModel).where(
                ChoiceDBModel.id == choice_id,
                ChoiceDBModel.intent_id == intent_id,
            )
        )
        await self.db.flush()
        return bool(result.rowcount and result.rowcount > 0)

    def _to_choice_domain_model(self, db: ChoiceDBModel) -> Choice:
        return Choice(
            id=db.id,
            intent_id=db.intent_id,
            aspect_id=db.aspect_id,
            name=db.name,
            description=db.description,
            options=db.options,
            selected_option=db.selected_option,
            rationale=db.rationale,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    def _to_choice_db_model(self, e: Choice) -> ChoiceDBModel:
        return ChoiceDBModel(
            id=e.id,
            intent_id=e.intent_id,
            aspect_id=e.aspect_id,
            name=e.name,
            description=e.description,
            options=e.options,
            selected_option=e.selected_option,
            rationale=e.rationale,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    # --- Pitfall ---
    async def add_pitfall(self, intent_id: int, entity: Pitfall) -> Pitfall:
        await self._ensure_intent_exists(intent_id)
        db = self._to_pitfall_db_model(entity)
        db.intent_id = intent_id
        self.db.add(db)
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_pitfall_domain_model(db)

    async def find_pitfall_by_id(
        self, intent_id: int, pitfall_id: int
    ) -> Optional[Pitfall]:
        result = await self.db.execute(
            select(PitfallDBModel).where(
                PitfallDBModel.id == pitfall_id,
                PitfallDBModel.intent_id == intent_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_pitfall_domain_model(row) if row else None

    async def list_pitfalls_by_intent_id(self, intent_id: int) -> List[Pitfall]:
        result = await self.db.execute(
            select(PitfallDBModel).where(PitfallDBModel.intent_id == intent_id)
        )
        return [self._to_pitfall_domain_model(r) for r in result.scalars().all()]

    async def update_pitfall(
        self, intent_id: int, pitfall_id: int, entity: Pitfall
    ) -> Optional[Pitfall]:
        result = await self.db.execute(
            select(PitfallDBModel).where(
                PitfallDBModel.id == pitfall_id,
                PitfallDBModel.intent_id == intent_id,
            )
        )
        db = result.scalar_one_or_none()
        if not db:
            return None
        db.description = entity.description
        db.aspect_id = entity.aspect_id
        db.mitigation = entity.mitigation
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_pitfall_domain_model(db)

    async def delete_pitfall(self, intent_id: int, pitfall_id: int) -> bool:
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(
            sql_delete(PitfallDBModel).where(
                PitfallDBModel.id == pitfall_id,
                PitfallDBModel.intent_id == intent_id,
            )
        )
        await self.db.flush()
        return bool(result.rowcount and result.rowcount > 0)

    def _to_pitfall_domain_model(self, db: PitfallDBModel) -> Pitfall:
        return Pitfall(
            id=db.id,
            intent_id=db.intent_id,
            aspect_id=db.aspect_id,
            description=db.description,
            mitigation=db.mitigation,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    def _to_pitfall_db_model(self, e: Pitfall) -> PitfallDBModel:
        return PitfallDBModel(
            id=e.id,
            intent_id=e.intent_id,
            aspect_id=e.aspect_id,
            description=e.description,
            mitigation=e.mitigation,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    # --- Assumption ---
    async def add_assumption(
        self, intent_id: int, entity: Assumption
    ) -> Assumption:
        await self._ensure_intent_exists(intent_id)
        db = self._to_assumption_db_model(entity)
        db.intent_id = intent_id
        self.db.add(db)
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_assumption_domain_model(db)

    async def find_assumption_by_id(
        self, intent_id: int, assumption_id: int
    ) -> Optional[Assumption]:
        result = await self.db.execute(
            select(AssumptionDBModel).where(
                AssumptionDBModel.id == assumption_id,
                AssumptionDBModel.intent_id == intent_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_assumption_domain_model(row) if row else None

    async def list_assumptions_by_intent_id(
        self, intent_id: int
    ) -> List[Assumption]:
        result = await self.db.execute(
            select(AssumptionDBModel).where(
                AssumptionDBModel.intent_id == intent_id
            )
        )
        return [
            self._to_assumption_domain_model(r) for r in result.scalars().all()
        ]

    async def update_assumption(
        self, intent_id: int, assumption_id: int, entity: Assumption
    ) -> Optional[Assumption]:
        result = await self.db.execute(
            select(AssumptionDBModel).where(
                AssumptionDBModel.id == assumption_id,
                AssumptionDBModel.intent_id == intent_id,
            )
        )
        db = result.scalar_one_or_none()
        if not db:
            return None
        db.description = entity.description
        db.aspect_id = entity.aspect_id
        db.confidence = entity.confidence
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_assumption_domain_model(db)

    async def delete_assumption(
        self, intent_id: int, assumption_id: int
    ) -> bool:
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(
            sql_delete(AssumptionDBModel).where(
                AssumptionDBModel.id == assumption_id,
                AssumptionDBModel.intent_id == intent_id,
            )
        )
        await self.db.flush()
        return bool(result.rowcount and result.rowcount > 0)

    def _to_assumption_domain_model(
        self, db: AssumptionDBModel
    ) -> Assumption:
        return Assumption(
            id=db.id,
            intent_id=db.intent_id,
            aspect_id=db.aspect_id,
            description=db.description,
            confidence=db.confidence,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    def _to_assumption_db_model(self, e: Assumption) -> AssumptionDBModel:
        return AssumptionDBModel(
            id=e.id,
            intent_id=e.intent_id,
            aspect_id=e.aspect_id,
            description=e.description,
            confidence=e.confidence,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    # --- Quality ---
    async def add_quality(self, intent_id: int, entity: Quality) -> Quality:
        await self._ensure_intent_exists(intent_id)
        db = self._to_quality_db_model(entity)
        db.intent_id = intent_id
        self.db.add(db)
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_quality_domain_model(db)

    async def find_quality_by_id(
        self, intent_id: int, quality_id: int
    ) -> Optional[Quality]:
        result = await self.db.execute(
            select(QualityDBModel).where(
                QualityDBModel.id == quality_id,
                QualityDBModel.intent_id == intent_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_quality_domain_model(row) if row else None

    async def list_qualities_by_intent_id(self, intent_id: int) -> List[Quality]:
        result = await self.db.execute(
            select(QualityDBModel).where(QualityDBModel.intent_id == intent_id)
        )
        return [self._to_quality_domain_model(r) for r in result.scalars().all()]

    async def update_quality(
        self, intent_id: int, quality_id: int, entity: Quality
    ) -> Optional[Quality]:
        result = await self.db.execute(
            select(QualityDBModel).where(
                QualityDBModel.id == quality_id,
                QualityDBModel.intent_id == intent_id,
            )
        )
        db = result.scalar_one_or_none()
        if not db:
            return None
        db.criterion = entity.criterion
        db.aspect_id = entity.aspect_id
        db.measurement = entity.measurement
        db.priority = entity.priority
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_quality_domain_model(db)

    async def delete_quality(self, intent_id: int, quality_id: int) -> bool:
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(
            sql_delete(QualityDBModel).where(
                QualityDBModel.id == quality_id,
                QualityDBModel.intent_id == intent_id,
            )
        )
        await self.db.flush()
        return bool(result.rowcount and result.rowcount > 0)

    def _to_quality_domain_model(self, db: QualityDBModel) -> Quality:
        return Quality(
            id=db.id,
            intent_id=db.intent_id,
            aspect_id=db.aspect_id,
            criterion=db.criterion,
            measurement=db.measurement,
            priority=db.priority,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    def _to_quality_db_model(self, e: Quality) -> QualityDBModel:
        return QualityDBModel(
            id=e.id,
            intent_id=e.intent_id,
            aspect_id=e.aspect_id,
            criterion=e.criterion,
            measurement=e.measurement,
            priority=e.priority,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    # --- Example ---
    async def add_example(self, intent_id: int, entity: Example) -> Example:
        await self._ensure_intent_exists(intent_id)
        db = self._to_example_db_model(entity)
        db.intent_id = intent_id
        self.db.add(db)
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_example_domain_model(db)

    async def find_example_by_id(
        self, intent_id: int, example_id: int
    ) -> Optional[Example]:
        result = await self.db.execute(
            select(ExampleDBModel).where(
                ExampleDBModel.id == example_id,
                ExampleDBModel.intent_id == intent_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_example_domain_model(row) if row else None

    async def list_examples_by_intent_id(self, intent_id: int) -> List[Example]:
        result = await self.db.execute(
            select(ExampleDBModel).where(ExampleDBModel.intent_id == intent_id)
        )
        return [self._to_example_domain_model(r) for r in result.scalars().all()]

    async def update_example(
        self, intent_id: int, example_id: int, entity: Example
    ) -> Optional[Example]:
        result = await self.db.execute(
            select(ExampleDBModel).where(
                ExampleDBModel.id == example_id,
                ExampleDBModel.intent_id == intent_id,
            )
        )
        db = result.scalar_one_or_none()
        if not db:
            return None
        db.sample = entity.sample
        db.aspect_id = entity.aspect_id
        db.explanation = entity.explanation
        db.source = entity.source
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_example_domain_model(db)

    async def delete_example(self, intent_id: int, example_id: int) -> bool:
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(
            sql_delete(ExampleDBModel).where(
                ExampleDBModel.id == example_id,
                ExampleDBModel.intent_id == intent_id,
            )
        )
        await self.db.flush()
        return bool(result.rowcount and result.rowcount > 0)

    def _to_example_domain_model(self, db: ExampleDBModel) -> Example:
        return Example(
            id=db.id,
            intent_id=db.intent_id,
            aspect_id=db.aspect_id,
            sample=db.sample,
            explanation=db.explanation,
            source=db.source,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    def _to_example_db_model(self, e: Example) -> ExampleDBModel:
        return ExampleDBModel(
            id=e.id,
            intent_id=e.intent_id,
            aspect_id=e.aspect_id,
            sample=e.sample,
            explanation=e.explanation,
            source=e.source,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    # --- Prompt ---
    async def add_prompt(self, intent_id: int, entity: Prompt) -> Prompt:
        await self._ensure_intent_exists(intent_id)
        db = self._to_prompt_db_model(entity)
        db.intent_id = intent_id
        self.db.add(db)
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_prompt_domain_model(db)

    async def get_next_prompt_version(self, intent_id: int) -> int:
        from sqlalchemy import func

        result = await self.db.execute(
            select(func.coalesce(func.max(PromptDBModel.version), 0)).where(
                PromptDBModel.intent_id == intent_id
            )
        )
        row = result.scalar_one_or_none()
        return (row or 0) + 1

    async def find_prompt_by_id(
        self, intent_id: int, prompt_id: int
    ) -> Optional[Prompt]:
        result = await self.db.execute(
            select(PromptDBModel).where(
                PromptDBModel.id == prompt_id,
                PromptDBModel.intent_id == intent_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_prompt_domain_model(row) if row else None

    async def list_prompts_by_intent_id(self, intent_id: int) -> List[Prompt]:
        result = await self.db.execute(
            select(PromptDBModel).where(PromptDBModel.intent_id == intent_id)
        )
        return [self._to_prompt_domain_model(r) for r in result.scalars().all()]

    def _to_prompt_domain_model(self, db: PromptDBModel) -> Prompt:
        return Prompt(
            id=db.id,
            intent_id=db.intent_id,
            content=db.content,
            version=db.version,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    def _to_prompt_db_model(self, e: Prompt) -> PromptDBModel:
        return PromptDBModel(
            id=e.id,
            intent_id=e.intent_id,
            content=e.content,
            version=e.version,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    # --- Output ---
    async def add_output(self, prompt_id: int, entity: Output) -> Output:
        await self._ensure_prompt_exists(prompt_id)
        db = self._to_output_db_model(entity)
        db.prompt_id = prompt_id
        self.db.add(db)
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_output_domain_model(db)

    async def find_output_by_id(
        self, prompt_id: int, output_id: int
    ) -> Optional[Output]:
        result = await self.db.execute(
            select(OutputDBModel).where(
                OutputDBModel.id == output_id,
                OutputDBModel.prompt_id == prompt_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_output_domain_model(row) if row else None

    async def list_outputs_by_prompt_id(self, prompt_id: int) -> List[Output]:
        result = await self.db.execute(
            select(OutputDBModel).where(OutputDBModel.prompt_id == prompt_id)
        )
        return [self._to_output_domain_model(r) for r in result.scalars().all()]

    def _to_output_domain_model(self, db: OutputDBModel) -> Output:
        return Output(
            id=db.id,
            prompt_id=db.prompt_id,
            content=db.content,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    def _to_output_db_model(self, e: Output) -> OutputDBModel:
        return OutputDBModel(
            id=e.id,
            prompt_id=e.prompt_id,
            content=e.content,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    # --- Insight ---
    async def add_insight(self, intent_id: int, entity: Insight) -> Insight:
        await self._ensure_intent_exists(intent_id)
        db = self._to_insight_db_model(entity)
        db.intent_id = intent_id
        self.db.add(db)
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_insight_domain_model(db)

    async def find_insight_by_id(
        self, intent_id: int, insight_id: int
    ) -> Optional[Insight]:
        result = await self.db.execute(
            select(InsightDBModel).where(
                InsightDBModel.id == insight_id,
                InsightDBModel.intent_id == intent_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_insight_domain_model(row) if row else None

    async def list_insights_by_intent_id(self, intent_id: int) -> List[Insight]:
        result = await self.db.execute(
            select(InsightDBModel).where(InsightDBModel.intent_id == intent_id)
        )
        return [
            self._to_insight_domain_model(r) for r in result.scalars().all()
        ]

    async def update_insight(
        self, intent_id: int, insight_id: int, entity: Insight
    ) -> Optional[Insight]:
        result = await self.db.execute(
            select(InsightDBModel).where(
                InsightDBModel.id == insight_id,
                InsightDBModel.intent_id == intent_id,
            )
        )
        db = result.scalar_one_or_none()
        if not db:
            return None
        db.content = entity.content
        db.source_type = entity.source_type
        db.source_output_id = entity.source_output_id
        db.source_prompt_id = entity.source_prompt_id
        db.source_assumption_id = entity.source_assumption_id
        db.status = entity.status
        await self.db.flush()
        await self.db.refresh(db)
        return self._to_insight_domain_model(db)

    async def delete_insight(self, intent_id: int, insight_id: int) -> bool:
        from sqlalchemy import delete as sql_delete

        result = await self.db.execute(
            sql_delete(InsightDBModel).where(
                InsightDBModel.id == insight_id,
                InsightDBModel.intent_id == intent_id,
            )
        )
        await self.db.flush()
        return bool(result.rowcount and result.rowcount > 0)

    def _to_insight_domain_model(self, db: InsightDBModel) -> Insight:
        return Insight(
            id=db.id,
            intent_id=db.intent_id,
            content=db.content,
            source_type=db.source_type,
            source_output_id=db.source_output_id,
            source_prompt_id=db.source_prompt_id,
            source_assumption_id=db.source_assumption_id,
            status=db.status,
            created_at=db.created_at,
            updated_at=db.updated_at,
        )

    def _to_insight_db_model(self, e: Insight) -> InsightDBModel:
        return InsightDBModel(
            id=e.id,
            intent_id=e.intent_id,
            content=e.content,
            source_type=e.source_type,
            source_output_id=e.source_output_id,
            source_prompt_id=e.source_prompt_id,
            source_assumption_id=e.source_assumption_id,
            status=e.status,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )

    async def _ensure_intent_exists(self, intent_id: int) -> None:
        result = await self.db.execute(
            select(IntentDBModel).where(IntentDBModel.id == intent_id)
        )
        if result.scalar_one_or_none() is None:
            raise ValueError(f"Intent with id {intent_id} not found")

    async def _ensure_prompt_exists(self, prompt_id: int) -> None:
        result = await self.db.execute(
            select(PromptDBModel).where(PromptDBModel.id == prompt_id)
        )
        if result.scalar_one_or_none() is None:
            raise ValueError(f"Prompt with id {prompt_id} not found")