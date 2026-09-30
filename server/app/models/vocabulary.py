"""
Vocab practice - flashcards with SRS. Vocabulary is the content (one row per word);
VocabularyReview is per-user SRS state, updated on every review.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Integer, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.course import Lesson
    from app.models.user import User


class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False)
    kanji: Mapped[str | None] = mapped_column(String(100))
    kana: Mapped[str] = mapped_column(String(100), nullable=False)
    romaji: Mapped[str] = mapped_column(String(100), nullable=False)
    meaning: Mapped[str] = mapped_column(String(255), nullable=False)
    example_sentence: Mapped[str | None] = mapped_column(Text)
    example_translation: Mapped[str | None] = mapped_column(Text)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("5"))

    lesson: Mapped[Lesson] = relationship()


class VocabularyReview(Base):
    __tablename__ = "vocabulary_review"
    __table_args__ = (UniqueConstraint("user_id", "vocabulary_id"),)

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    vocabulary_id: Mapped[int] = mapped_column(ForeignKey("vocabulary.id"), nullable=False)

    ease_factor: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, server_default=text("2.5"))
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    repetitions: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_result: Mapped[str | None] = mapped_column(String(20))  # again / hard / good / easy

    user: Mapped[User] = relationship()
    vocabulary: Mapped[Vocabulary] = relationship()
