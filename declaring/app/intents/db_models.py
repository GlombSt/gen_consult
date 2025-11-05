"""
Database models for intents domain.

These models represent the database schema using SQLAlchemy ORM.
Used exclusively by the repository layer.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.shared.database import Base


class IntentDBModel(Base):
    """
    SQLAlchemy ORM model for intents table.

    Represents the database schema for intents.
    Includes audit fields (created_at, updated_at) but no soft delete.
    Uses hard deletes only.
    """

    __tablename__ = "intents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    output_format = Column(String, nullable=False)
    output_structure = Column(String, nullable=True)
    context = Column(String, nullable=True)
    constraints = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to facts (cascade delete)
    facts = relationship("FactDBModel", back_populates="intent", cascade="all, delete-orphan")


class FactDBModel(Base):
    """
    SQLAlchemy ORM model for facts table.

    Represents the database schema for facts.
    Includes audit fields (created_at, updated_at) but no soft delete.
    Uses hard deletes only.
    Has a foreign key relationship to intents with cascade delete.
    """

    __tablename__ = "facts"

    id = Column(Integer, primary_key=True, index=True)
    intent_id = Column(Integer, ForeignKey("intents.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to intent
    intent = relationship("IntentDBModel", back_populates="facts")