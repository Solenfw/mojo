from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db import models

router = APIRouter()


@router.get("/league/leaderboard")
async def leaderboard(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # For a weekly leaderboard, you could filter by a `week_xp`
    # field or by `xp_events` timestamped records for the current week.
    # Example: .where(models.User.week_xp != None) or join a weekly XP table.

    result = await db.execute(
        select(models.User)
        .order_by(desc(models.User.xp))
        .limit(50)
    )
    users = result.scalars().all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "xp": user.xp,
            "streak": getattr(user, "streak", 0),
        }
        for user in users
    ]
