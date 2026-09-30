"""XP, streaks and hearts."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ActivityLog, Skill, User

MAX_HEARTS = 5
HEART_REGENERATION_RATE = timedelta(hours=4)  # 1 heart per 4 hours
HEART_REFILL_COST = 10  # gems


class NotEnoughGemsError(Exception):
    pass


class HeartsAlreadyFullError(Exception):
    pass


async def award_xp(db: AsyncSession, user: User, *, skill_code: str, xp: int, now: datetime) -> None:
    """Add XP, extend the streak and log the activity. The caller commits."""
    if xp <= 0:
        return
    user.xp = User.xp + xp  # evaluated in SQL, so concurrent awards don't overwrite each other
    skill_id = await db.scalar(select(Skill.id).where(Skill.code == skill_code))
    db.add(ActivityLog(user_id=user.id, skill_id=skill_id, xp_earned=xp, created_at=now))

    today = now.date()
    if user.last_activity_date == today - timedelta(days=1):
        user.streak += 1
    elif user.last_activity_date != today:
        user.streak = 1
    user.last_activity_date = today


def regenerate_hearts(user: User, now: datetime) -> None:
    """Credit hearts earned since the last update, keeping any partial period."""
    if user.hearts >= MAX_HEARTS or user.hearts_last_updated is None:
        user.hearts_last_updated = now  # the timer starts when a heart is missing
        return
    earned = (now - user.hearts_last_updated) // HEART_REGENERATION_RATE
    if earned:
        user.hearts = min(MAX_HEARTS, user.hearts + earned)
        user.hearts_last_updated += earned * HEART_REGENERATION_RATE


def refill_hearts(user: User, now: datetime) -> None:
    regenerate_hearts(user, now)
    if user.hearts >= MAX_HEARTS:
        raise HeartsAlreadyFullError
    if user.gems < HEART_REFILL_COST:
        raise NotEnoughGemsError
    user.gems -= HEART_REFILL_COST
    user.hearts = MAX_HEARTS
    user.hearts_last_updated = now
