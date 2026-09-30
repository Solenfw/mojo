"""Reading practice - passage with comprehension questions, must pass to earn xp_reward."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Identity, Integer, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.course import Lesson
    from app.models.user import User


class ReadingPassage(Base):
    __tablename__ = "reading_passage"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    content_japanese: Mapped[str] = mapped_column(Text, nullable=False)
    content_vietnamese: Mapped[str | None] = mapped_column(Text)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))

    lesson: Mapped[Lesson] = relationship()
    questions: Mapped[list[ReadingQuestion]] = relationship(
        back_populates="passage", order_by="ReadingQuestion.sort_order"
    )


class ReadingQuestion(Base):
    __tablename__ = "reading_question"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    passage_id: Mapped[int] = mapped_column(ForeignKey("reading_passage.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int | None] = mapped_column(Integer)

    passage: Mapped[ReadingPassage] = relationship(back_populates="questions")
    options: Mapped[list[ReadingQuestionOption]] = relationship(back_populates="question")


class ReadingQuestionOption(Base):
    __tablename__ = "reading_question_option"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("reading_question.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    question: Mapped[ReadingQuestion] = relationship(back_populates="options")


class ReadingAttempt(Base):
    __tablename__ = "reading_attempt"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    passage_id: Mapped[int] = mapped_column(ForeignKey("reading_passage.id"), nullable=False)
    score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()
    passage: Mapped[ReadingPassage] = relationship()


class ReadingAttemptAnswer(Base):
    __tablename__ = "reading_attempt_answer"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("reading_attempt.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("reading_question.id"), nullable=False)
    selected_option_id: Mapped[int | None] = mapped_column(ForeignKey("reading_question_option.id"))
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    attempt: Mapped[ReadingAttempt] = relationship()
