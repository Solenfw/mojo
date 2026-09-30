"""Onboarding: the learner's study reason, JLPT target and daily study time, submitted in one step."""

from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy.dialects.postgresql import insert

from app.api.deps import CurrentUser, DbSession
from app.models import LearnerProfile
from app.schemas import OnboardingData, OnboardingRequest, OnboardingResponse

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("", response_model=OnboardingResponse)
async def submit_onboarding(payload: OnboardingRequest, current_user: CurrentUser, db: DbSession) -> OnboardingResponse:
    """Saves the answers and marks the user onboarded. Submitting again updates the answers."""
    now = datetime.now(UTC)
    answers = {
        "study_intention": payload.study_reason,
        "target_level": payload.target_level,
        "daily_study_minutes": payload.daily_study_minutes,
        "updated_at": now,
    }
    # Upsert: a repeated or concurrent submit updates the one profile row instead of violating user_id's uniqueness.
    await db.execute(
        insert(LearnerProfile)
        .values(user_id=current_user.id, **answers)
        .on_conflict_do_update(index_elements=[LearnerProfile.user_id], set_=answers)
    )
    if not current_user.is_onboarded:
        current_user.is_onboarded = True
    await db.commit()

    return OnboardingResponse(
        message="Saved successfully.",
        data=OnboardingData(
            user_id=current_user.id,
            is_onboarded=True,
            study_reason=payload.study_reason,
            target_level=payload.target_level,
            daily_study_minutes=payload.daily_study_minutes
        ),
    )
