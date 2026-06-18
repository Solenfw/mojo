from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
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


@router.put("/onboarding/complete")
async def mark_user_onboarded(
    payload: MarkUserOnboardedRequest,
    token: str = Depends(oauth2_scheme),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access.",
        )
    if payload.sessionToken is not None and current_user.session_token and payload.sessionToken != current_user.session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access.",
        )
    if payload.sessionToken is not None and payload.sessionToken != token and payload.sessionToken != current_user.session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access.",
        )

    result = await db.execute(select(models.User).where(models.User.id == current_user.id))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found.",
        )
    if user.is_onboarded:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invalid input data.",
        )

    now = _utcnow()
    user.is_onboarded = True
    user.onboarded_at = now
    user.updated_at = now.replace(tzinfo=None)
    await db.commit()
    await db.refresh(user)

    return {
        "success": True,
        "businessCode": "LMS-RESP-SUCCESS",
        "message": "Updated successfully.",
        "data": {
            "userId": user.id,
            "isOnboarded": True,
            "updatedAt": _isoformat(user.onboarded_at),
        },
        "timestamp": _isoformat(now),
    }
