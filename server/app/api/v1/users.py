"""The signed-in user: account, dashboard summary and learning profile."""

from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter
from sqlalchemy import Date, cast, func, select

from app.api.deps import CurrentUser, DbSession
from app.models import ActivityLog, LearnerProfile, ProficiencyLevel, Skill, User
from app.schemas import (
    DailyActivity,
    DashboardData,
    DashboardResponse,
    DashboardUser,
    ProfileData,
    ProfileResponse,
    SkillProgress,
    UserRead,
)

router = APIRouter(prefix="/users", tags=["users"])

ACTIVITY_DAYS = 7


def _avatar_url(user: User) -> str:
    return f"https://api.dicebear.com/7.x/avataaars/svg?seed={user.username}"


async def _level_name(db: DbSession, user: User) -> str | None:
    if user.current_level_id is None:
        return None
    return await db.scalar(select(ProficiencyLevel.name).where(ProficiencyLevel.id == user.current_level_id))


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: CurrentUser) -> User:
    return current_user


@router.get("/me/dashboard", response_model=DashboardResponse)
async def get_dashboard(db: DbSession, current_user: CurrentUser) -> DashboardResponse:
    """XP per day over the last week and XP per skill, both from the activity log."""
    today = datetime.now(UTC).date()
    first_day = today - timedelta(days=ACTIVITY_DAYS - 1)
    day = cast(func.timezone("UTC", ActivityLog.created_at), Date)
    xp_by_day: dict[date, int] = {
        row.day: row.xp
        for row in await db.execute(
            select(day.label("day"), func.sum(ActivityLog.xp_earned).label("xp"))
            .where(ActivityLog.user_id == current_user.id, day >= first_day)
            .group_by(day)
        )
    }
    skills = await db.execute(
        select(Skill.code, func.coalesce(func.sum(ActivityLog.xp_earned), 0).label("xp"))
        .outerjoin(ActivityLog, (ActivityLog.skill_id == Skill.id) & (ActivityLog.user_id == current_user.id))
        .group_by(Skill.id, Skill.code)
        .order_by(Skill.id)
    )

    return DashboardResponse(
        data=DashboardData(
            user=DashboardUser(
                name=current_user.full_name or current_user.username,
                xp=current_user.xp,
                streak=current_user.streak,
                level=await _level_name(db, current_user),
                avatar_url=_avatar_url(current_user),
            ),
            activity=[
                DailyActivity(
                    day=first_day + timedelta(days=offset), xp=xp_by_day.get(first_day + timedelta(days=offset), 0)
                )
                for offset in range(ACTIVITY_DAYS)
            ],
            skills=[SkillProgress(skill=row.code, xp=row.xp) for row in skills],
        )
    )


@router.get("/me/profile", response_model=ProfileResponse)
async def get_profile(db: DbSession, current_user: CurrentUser) -> ProfileResponse:
    profile = await db.scalar(select(LearnerProfile).where(LearnerProfile.user_id == current_user.id))
    return ProfileResponse(
        data=ProfileData(
            name=current_user.full_name or current_user.username,
            username=current_user.username,
            email=current_user.email,
            xp=current_user.xp,
            streak=current_user.streak,
            current_level=await _level_name(db, current_user),
            target_level=profile.target_level if profile else None,
            study_intention=profile.study_intention if profile else None,
            daily_study_minutes=profile.daily_study_minutes if profile else None,
            member_since=current_user.created_at,
            avatar_url=_avatar_url(current_user),
        )
    )
