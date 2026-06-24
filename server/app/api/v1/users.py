# server/app/api/v1/users.py
from datetime import datetime, timezone, timedelta
import random

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas import UserRead
from app.db import models
from app.api.deps import get_current_user, get_db
from app.core.security import oauth2_scheme

router = APIRouter(prefix="/users", tags=["users"])

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

class MarkUserOnboardedRequest(BaseModel):
    userId: int = Field(gt=0)
    sessionToken: str | None = Field(default=None, min_length=1)

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.get("/me/dashboard")
async def get_dashboard_data(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Aggregates XP, streak, level, and activity data for the main dashboard."""
    # Fetch learner profile for target level
    profile_stmt = select(models.LearnerProfiles).where(models.LearnerProfiles.user_id == current_user.id)
    profile_res = await db.execute(profile_stmt)
    profile = profile_res.scalars().first()
    
    current_level = profile.current_level if profile and profile.current_level else "N5"

    # For the demo, we generate a visually pleasing activity curve scaled roughly to their actual XP
    base_daily_xp = max(20, int(current_user.xp / 10))
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    activity_data = [
        {"day": day, "xp": base_daily_xp + random.randint(-10, 30)} 
        for day in days
    ]

    # Calculate mock mastery based on level
    mastery_data = [
        {"module": "Hiragana", "score": 100},
        {"module": "Katakana", "score": 95},
        {"module": f"Kanji {current_level}", "score": random.randint(30, 70)},
        {"module": f"Grammar {current_level}", "score": random.randint(40, 80)},
        {"module": "Listening", "score": random.randint(50, 85)},
    ]

    return {
        "user": {
            "name": current_user.full_name or current_user.username,
            "xp": current_user.xp,
            "streak": current_user.streak,
            "level": current_level,
            "avatarUrl": f"https://api.dicebear.com/7.x/avataaars/svg?seed={current_user.username}"
        },
        "activity": activity_data,
        "mastery": mastery_data
    }

@router.get("/me/profile")
async def get_profile_data(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetches detailed profile settings, study goals, and achievements."""
    profile_stmt = select(models.LearnerProfiles).where(models.LearnerProfiles.user_id == current_user.id)
    profile_res = await db.execute(profile_stmt)
    profile = profile_res.scalars().first()

    return {
        "name": current_user.full_name or current_user.username,
        "email": current_user.email,
        "phone": current_user.phone or "Not provided",
        "xp": current_user.xp,
        "streak": current_user.streak,
        "current_level": profile.current_level if profile else "N5",
        "target_level": profile.target_level if profile else "N3",
        "study_goal": profile.study_goal if profile else "Professional Fluency",
        "member_since": current_user.created_at.strftime("%b %Y"),
        "avatarUrl": f"https://api.dicebear.com/7.x/avataaars/svg?seed={current_user.username}"
    }

@router.put("/onboarding/complete")
async def mark_user_onboarded(
    payload: MarkUserOnboardedRequest,
    token: str = Depends(oauth2_scheme),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.userId != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")
    if payload.sessionToken is not None and payload.sessionToken != current_user.session_token and payload.sessionToken != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access.")

    if current_user.is_onboarded:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already onboarded.")

    now = _utcnow()
    current_user.is_onboarded = True
    current_user.onboarded_at = now
    current_user.updated_at = now.replace(tzinfo=None)
    await db.commit()
    await db.refresh(current_user)

    return {
        "success": True,
        "businessCode": "LMS-RESP-SUCCESS",
        "message": "Updated successfully.",
        "data": {
            "userId": current_user.id,
            "isOnboarded": True,
            "updatedAt": _isoformat(current_user.onboarded_at),
        }
    }