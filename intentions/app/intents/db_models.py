"""
Database models for intents domain.

These models represent the database schema using SQLAlchemy ORM.
Used exclusively by the repository layer.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.shared.database import Base


# Enum values stored as strings (DB-agnostic)
ASSUMPTION_CONFIDENCE_VALUES = ("verified", "likely", "uncertain")
QUALITY_PRIORITY_VALUES = ("must_have", "should_have", "nice_to_have")
EXAMPLE_SOURCE_VALUES = ("user_provided", "llm_generated", "from_output")
INSIGHT_SOURCE_TYPE_VALUES = ("sharpening", "output", "prompt", "assumption")
INSIGHT_STATUS_VALUES = ("pending", "incorporated", "dismissed")


class IntentDBModel(Base):
    """
    SQLAlchemy ORM model for intents table (V2).
    """

    __tablename__ = "intents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    aspects = relationship("AspectDBModel", back_populates="intent", cascade="all, delete-orphan")
    inputs = relationship("InputDBModel", back_populates="intent", cascade="all, delete-orphan")
    choices = relationship("ChoiceDBModel", back_populates="intent", cascade="all, delete-orphan")
    pitfalls = relationship("PitfallDBModel", back_populates="intent", cascade="all, delete-orphan")
    assumptions = relationship("AssumptionDBModel", back_populates="intent", cascade="all, delete-orphan")
    qualities = relationship("QualityDBModel", back_populates="intent", cascade="all, delete-orphan")
    examples = relationship("ExampleDBModel", back_populates="intent", cascade="all, delete-orphan")
    prompts = relationship("PromptDBModel", back_populates="intent", cascade="all, delete-orphan")
    insights = relationship("InsightDBModel", back_populates="intent", cascade="all, delete-orphan")


class AspectDBModel(Base):
    """Aspect: domain/area of consideration for an intent."""

    __tablename__ = "aspects"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    intent = relationship("IntentDBModel", back_populates="aspects")


class InputDBModel(Base):
    """Input: what the user provides for execution."""

    __tablename__ = "inputs"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect_id = Column(Integer, ForeignKey("aspects.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    format = Column(String, nullable=True)
    required = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    intent = relationship("IntentDBModel", back_populates="inputs")


class ChoiceDBModel(Base):
    """Choice: decision point with options and selected approach."""

    __tablename__ = "choices"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect_id = Column(Integer, ForeignKey("aspects.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    options = Column(Text, nullable=True)
    selected_option = Column(String, nullable=True)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    intent = relationship("IntentDBModel", back_populates="choices")


class PitfallDBModel(Base):
    """Pitfall: failure mode or anti-pattern to avoid."""

    __tablename__ = "pitfalls"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect_id = Column(Integer, ForeignKey("aspects.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(Text, nullable=False)
    mitigation = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    intent = relationship("IntentDBModel", back_populates="pitfalls")


class AssumptionDBModel(Base):
    """Assumption: implicit belief made explicit."""

    __tablename__ = "assumptions"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect_id = Column(Integer, ForeignKey("aspects.id", ondelete="SET NULL"), nullable=True, index=True)
    description = Column(Text, nullable=False)
    confidence = Column(String(50), nullable=True)  # verified, likely, uncertain
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    intent = relationship("IntentDBModel", back_populates="assumptions")


class QualityDBModel(Base):
    """Quality: success criterion or output standard."""

    __tablename__ = "qualities"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect_id = Column(Integer, ForeignKey("aspects.id", ondelete="SET NULL"), nullable=True, index=True)
    criterion = Column(Text, nullable=False)
    measurement = Column(Text, nullable=True)
    priority = Column(String(50), nullable=True)  # must_have, should_have, nice_to_have
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    intent = relationship("IntentDBModel", back_populates="qualities")


class ExampleDBModel(Base):
    """Example: concrete input→output demonstration."""

    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.id", ondelete="CASCADE"), nullable=False, index=True)
    aspect_id = Column(Integer, ForeignKey("aspects.id", ondelete="SET NULL"), nullable=True, index=True)
    sample = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    source = Column(String(50), nullable=True)  # user_provided, llm_generated, from_output
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    intent = relationship("IntentDBModel", back_populates="examples")


class PromptDBModel(Base):
    """Prompt: generated, versioned instruction for the AI."""

    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    intent = relationship("IntentDBModel", back_populates="prompts")
    outputs = relationship("OutputDBModel", back_populates="prompt", cascade="all, delete-orphan")


class OutputDBModel(Base):
    """Output: AI response to a prompt."""

    __tablename__ = "outputs"

    id = Column(Integer, primary_key=True, index=True)
    prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    prompt = relationship("PromptDBModel", back_populates="outputs")


class InsightDBModel(Base):
    """Insight: discovery that feeds back to the intent."""

    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=True)  # sharpening, output, prompt, assumption
    source_output_id = Column(Integer, ForeignKey("outputs.id", ondelete="SET NULL"), nullable=True, index=True)
    source_prompt_id = Column(Integer, ForeignKey("prompts.id", ondelete="SET NULL"), nullable=True, index=True)
    source_assumption_id = Column(Integer, ForeignKey("assumptions.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(50), nullable=True)  # pending, incorporated, dismissed
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    intent = relationship("IntentDBModel", back_populates="insights")
