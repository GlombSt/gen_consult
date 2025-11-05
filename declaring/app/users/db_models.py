"""
Database models for users domain.

These models represent the database schema using SQLAlchemy ORM.
Used exclusively by the repository layer.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.shared.database import Base


class UserDBModel(Base):
    """
    SQLAlchemy ORM model for users table.

    Represents the database schema for users.
    Includes audit fields (created_at, updated_at) but no soft delete.
    Uses hard deletes only.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
