"""Writing practice: a kanji drawn on a canvas, rated by AI; a passing score earns the practice's XP once."""

from datetime import UTC, datetime

import anyio
from fastapi import APIRouter, status
from sqlalchemy import exists, select

from app.api.deps import CurrentUser, DbSession
from app.api.errors import not_found, unavailable
from app.clients.vision import VisionClient
from app.models import KanjiPractice, KanjiPracticeAttempt
from app.schemas import (
    EvaluateWritingData,
    EvaluateWritingRequest,
    EvaluateWritingResponse,
    KanjiPracticeRead,
    KanjiPracticeResponse,
)
from app.services.gamification import award_xp
from app.services.practice import clamp_score

router = APIRouter(prefix="/writing", tags=["writing"])
vision = VisionClient()

WRITING_PASS_SCORE = 60


@router.get("/kanji/{practice_id}", response_model=KanjiPracticeResponse)
async def get_kanji_practice(practice_id: int, db: DbSession, _: CurrentUser) -> KanjiPracticeResponse:
    practice = await db.get(KanjiPractice, practice_id)
    if practice is None:
        raise not_found("Kanji practice not found.")
    return KanjiPracticeResponse(data=KanjiPracticeRead.model_validate(practice))


@router.post("/evaluations", response_model=EvaluateWritingResponse, status_code=status.HTTP_201_CREATED)
async def evaluate(
    payload: EvaluateWritingRequest, db: DbSession, current_user: CurrentUser
) -> EvaluateWritingResponse:
    """Rates the drawing against the practice's kanji (taken from the database, never from the client)."""
    practice = await db.get(KanjiPractice, payload.kanji_practice_id)
    if practice is None:
        raise not_found("Kanji practice not found.")

    image = payload.image_base64.split(",", 1)[-1]  # accept a data URL straight from the canvas
    try:
        rating = await anyio.to_thread.run_sync(vision.evaluate_kanji, image, practice.kanji)
    except RuntimeError:
        raise unavailable("Handwriting evaluation is unavailable right now. Please try again.") from None
    score = clamp_score(rating.get("score"))
    feedback = str(rating.get("feedback", ""))

    already_passed = await db.scalar(
        select(
            exists().where(
                KanjiPracticeAttempt.user_id == current_user.id,
                KanjiPracticeAttempt.kanji_practice_id == practice.id,
                KanjiPracticeAttempt.xp_earned > 0,
            )
        )
    )
    xp = practice.xp_reward if score >= WRITING_PASS_SCORE and not already_passed else 0
    now = datetime.now(UTC)

    attempt = KanjiPracticeAttempt(
        user_id=current_user.id,
        kanji_practice_id=practice.id,
        ai_score=score,
        ai_feedback=feedback,
        xp_earned=xp,
        completed_at=now,
    )
    db.add(attempt)
    await award_xp(db, current_user, skill_code="writing", xp=xp, now=now)
    await db.commit()

    return EvaluateWritingResponse(
        data=EvaluateWritingData(attempt_id=attempt.id, score=score, feedback=feedback, xp_earned=xp)
    )
