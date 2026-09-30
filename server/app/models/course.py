"""
Courses & lessons. A course belongs to exactly one level (e.g. courses 1-3 = Beginner).
A lesson belongs to a course and can contain practices across multiple skills.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Identity, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.lookup import ProficiencyLevel


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str | None] = mapped_column(String(50))
    level_id: Mapped[int] = mapped_column(ForeignKey("proficiency_level.id"), nullable=False)
    sort_order: Mapped[int | None] = mapped_column(Integer)

    level: Mapped[ProficiencyLevel] = relationship()
    lessons: Mapped[list[Lesson]] = relationship(back_populates="course", order_by="Lesson.sort_order")


class Lesson(Base):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[str | None] = mapped_column(String(50))
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(50))
    sort_order: Mapped[int | None] = mapped_column(Integer)

    course: Mapped[Course] = relationship(back_populates="lessons")
