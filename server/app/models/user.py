"""User & profile."""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Identity, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.lookup import ProficiencyLevel


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    is_onboarded: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    current_level_id: Mapped[int | None] = mapped_column(ForeignKey("proficiency_level.id"))

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    xp: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    streak: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    gems: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    hearts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("5"))
    hearts_last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_activity_date: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    current_level: Mapped[ProficiencyLevel | None] = relationship()
    profile: Mapped[LearnerProfile | None] = relationship(back_populates="user", uselist=False)


class LearnerProfile(Base):
    """Onboarding answers. Current level lives on User; this holds aspirational/contextual data."""

    __tablename__ = "learner_profile"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, unique=True)
    target_level: Mapped[str | None] = mapped_column(String(2))  # JLPT goal: N1 | N2 | N3 | N4
    study_intention: Mapped[str | None] = mapped_column(String(255))  # why they study: travel, work, anime_manga, ...
    daily_study_minutes: Mapped[int | None] = mapped_column(Integer)  # dedicated time

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="profile")
