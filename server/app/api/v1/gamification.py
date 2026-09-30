"""XP, streak, hearts and gems."""

from datetime import UTC, datetime

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.api.errors import invalid
from app.models import User
from app.schemas import GamificationStatusData, GamificationStatusResponse
from app.services import gamification
from app.services.gamification import HeartsAlreadyFullError, NotEnoughGemsError

router = APIRouter(prefix="/gamification", tags=["gamification"])


def _status(user: User) -> GamificationStatusResponse:
    return GamificationStatusResponse(
        data=GamificationStatusData(xp=user.xp, hearts=user.hearts, streak=user.streak, gems=user.gems)
    )


@router.get("/status", response_model=GamificationStatusResponse)
async def get_status(db: DbSession, current_user: CurrentUser) -> GamificationStatusResponse:
    gamification.regenerate_hearts(current_user, datetime.now(UTC))
    await db.commit()
    return _status(current_user)


@router.post("/hearts/refill", response_model=GamificationStatusResponse)
async def refill_hearts(db: DbSession, current_user: CurrentUser) -> GamificationStatusResponse:
    try:
        gamification.refill_hearts(current_user, datetime.now(UTC))
    except HeartsAlreadyFullError:
        raise invalid("Hearts are already full.") from None
    except NotEnoughGemsError:
        raise invalid(f"Refilling hearts costs {gamification.HEART_REFILL_COST} gems.") from None
    await db.commit()
    return _status(current_user)
