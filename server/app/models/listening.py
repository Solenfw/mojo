"""
Listening practice - audio from a conversation, song, or set of sentences, with comprehension
questions (same pass/question/option shape as reading).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Identity, Integer, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.course import Lesson
    from app.models.user import User


class ListeningPractice(Base):
    __tablename__ = "listening_practice"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'dialogue' | 'song' | 'sentences'
    audio_url: Mapped[str | None] = mapped_column(String(500))
    transcript_japanese: Mapped[str | None] = mapped_column(Text)
    transcript_vietnamese: Mapped[str | None] = mapped_column(Text)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))

    lesson: Mapped[Lesson] = relationship()
    questions: Mapped[list[ListeningQuestion]] = relationship(back_populates="practice")


class ListeningQuestion(Base):
    __tablename__ = "listening_question"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    practice_id: Mapped[int] = mapped_column(ForeignKey("listening_practice.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int | None] = mapped_column(Integer)

    practice: Mapped[ListeningPractice] = relationship(back_populates="questions")
    options: Mapped[list[ListeningQuestionOption]] = relationship(back_populates="question")


class ListeningQuestionOption(Base):
    __tablename__ = "listening_question_option"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("listening_question.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    question: Mapped[ListeningQuestion] = relationship(back_populates="options")


class ListeningAttempt(Base):
    __tablename__ = "listening_attempt"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    practice_id: Mapped[int] = mapped_column(ForeignKey("listening_practice.id"), nullable=False)
    score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()
    practice: Mapped[ListeningPractice] = relationship()
