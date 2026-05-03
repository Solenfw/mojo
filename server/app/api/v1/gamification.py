from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.v1.users import get_current_user
from app.db import models
from app.db.schemas import UserRead
from app.services.gamification_engine import GamificationEngine

router = APIRouter()


@router.get("/gamification/status", response_model=dict)
async def get_gamification_status(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Regenerate hearts before returning status
    await GamificationEngine.regenerate_hearts(current_user, db)
    return {
        "xp": current_user.xp,
        "hearts": current_user.hearts,
        "streak": current_user.streak,
        "gems": current_user.gems,
    }


@router.post("/gamification/hearts/refill")
async def refill_hearts(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    REFILL_COST = 10  # Gems per heart refill
    if current_user.gems < REFILL_COST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough gems to refill hearts.",
        )
    if current_user.hearts >= GamificationEngine.MAX_HEARTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hearts are already full.",
        )
    current_user.gems -= REFILL_COST
    current_user.hearts = GamificationEngine.MAX_HEARTS
    await db.commit()
    return {"message": "Hearts refilled successfully."}
