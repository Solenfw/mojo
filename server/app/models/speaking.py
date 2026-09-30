"""
Speaking practice - AI conversation. Dialogue is the scripted reference exchange used to seed
the conversation; DialogueAttempt logs a user's actual AI-rated session against it.
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


class Dialogue(Base):
    __tablename__ = "dialogue"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("15"))

    lesson: Mapped[Lesson] = relationship()
    exchanges: Mapped[list[DialogueExchange]] = relationship(
        back_populates="dialogue", order_by="DialogueExchange.order_index"
    )


class DialogueExchange(Base):
    __tablename__ = "dialogue_exchange"
    __table_args__ = (UniqueConstraint("dialogue_id", "order_index"),)

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    dialogue_id: Mapped[int] = mapped_column(ForeignKey("dialogue.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    speaker: Mapped[str] = mapped_column(String(50), nullable=False)  # "A"/"B" or a character name

    ja_text: Mapped[str] = mapped_column(Text, nullable=False)
    ja_romaji: Mapped[str] = mapped_column(Text, nullable=False)
    en_text: Mapped[str] = mapped_column(Text, nullable=False)

    dialogue: Mapped[Dialogue] = relationship(back_populates="exchanges")


class DialogueAttempt(Base):
    __tablename__ = "dialogue_attempt"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    dialogue_id: Mapped[int] = mapped_column(ForeignKey("dialogue.id"), nullable=False)
    ai_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    ai_feedback: Mapped[str | None] = mapped_column(Text)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()
    dialogue: Mapped[Dialogue] = relationship()
