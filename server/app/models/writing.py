"""Writing practice - kanji stroke practice on an HTML canvas, AI-rated."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Integer, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.course import Lesson
    from app.models.user import User


class KanjiPractice(Base):
    __tablename__ = "kanji_practice"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kanji: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[str | None] = mapped_column(String(50))
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))

    lesson: Mapped[Lesson] = relationship()


class KanjiPracticeAttempt(Base):
    __tablename__ = "kanji_practice_attempt"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    kanji_practice_id: Mapped[int] = mapped_column(ForeignKey("kanji_practice.id"), nullable=False)
    canvas_image_url: Mapped[str | None] = mapped_column(String(500))
    ai_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    ai_feedback: Mapped[str | None] = mapped_column(Text)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()
    kanji_practice: Mapped[KanjiPractice] = relationship()
