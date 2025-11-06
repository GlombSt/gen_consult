"""
Database models for items domain.

These models represent the database schema using SQLAlchemy ORM.
Used exclusively by the repository layer.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.shared.database import Base


class ItemDBModel(Base):
    """
    SQLAlchemy ORM model for items table.

    Represents the database schema for items.
    Includes audit fields (created_at, updated_at) but no soft delete.
    Uses hard deletes only.
    """

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
