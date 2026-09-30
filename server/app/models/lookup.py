"""Lookup tables."""

from __future__ import annotations

from sqlalchemy import Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ProficiencyLevel(Base):
    __tablename__ = "proficiency_level"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)  # "Beginner", "Intermediate", ...
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)  # used to resolve "next level"


class Skill(Base):
    __tablename__ = "skill"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    code: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True
    )  # vocab/reading/speaking/writing/listening
    name: Mapped[str] = mapped_column(String(100), nullable=False)
