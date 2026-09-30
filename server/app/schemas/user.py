from __future__ import annotations

from datetime import date, datetime

from app.schemas.base import ApiResponse, CamelModel
from app.schemas.lookup import SkillCode


class UserRead(CamelModel):
    id: int
    username: str
    email: str
    full_name: str | None = None
    is_onboarded: bool
    current_level_id: int | None = None
    last_login_at: datetime | None = None
    xp: int
    streak: int
    gems: int
    hearts: int
    hearts_last_updated: datetime | None = None
    last_activity_date: date | None = None


class DashboardUser(CamelModel):
    name: str
    xp: int
    streak: int
    level: str | None = None  # ProficiencyLevel.name; null until onboarded
    avatar_url: str


class DailyActivity(CamelModel):
    day: date
    xp: int


class SkillProgress(CamelModel):
    skill: SkillCode
    xp: int


class DashboardData(CamelModel):
    user: DashboardUser
    activity: list[DailyActivity]  # last 7 days, oldest first
    skills: list[SkillProgress]


class DashboardResponse(ApiResponse[DashboardData]):
    pass


class ProfileData(CamelModel):
    name: str
    username: str
    email: str
    xp: int
    streak: int
    current_level: str | None = None
    target_level: str | None = None
    study_intention: str | None = None
    daily_study_minutes: int | None = None
    member_since: datetime
    avatar_url: str


class ProfileResponse(ApiResponse[ProfileData]):
    pass
