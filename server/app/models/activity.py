"""
Activity log (optional) - a unified, append-only feed of completed practices across all five
skills. Write one row here alongside each *Attempt/*Review insert. Makes streaks, "xp earned
today", and the level-up-unlock check (SUM xp_earned since current_level was reached) a single
query instead of five UNIONs across the skill-specific attempt tables.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Identity, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.lookup import Skill
    from app.models.user import User


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill.id"), nullable=False)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    user: Mapped[User] = relationship()
    skill: Mapped[Skill] = relationship()
