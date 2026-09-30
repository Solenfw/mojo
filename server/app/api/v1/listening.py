"""Listening practice: audio with comprehension questions; passing earns the practice's XP once."""

from datetime import UTC, datetime

from fastapi import APIRouter, status
from sqlalchemy import exists, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.api.errors import invalid, not_found
from app.models import ListeningAttempt, ListeningPractice, ListeningQuestion
from app.schemas import (
    ListeningPracticeRead,
    ListeningPracticeResponse,
    SubmitListeningAttemptData,
    SubmitListeningAttemptRequest,
    SubmitListeningAttemptResponse,
)
from app.services.gamification import award_xp
from app.services.practice import UnknownQuestionError, grade_choices

router = APIRouter(prefix="/listening", tags=["listening"])


async def _load_practice(db: DbSession, practice_id: int) -> ListeningPractice:
    practice = await db.scalar(
        select(ListeningPractice)
        .where(ListeningPractice.id == practice_id)
        .options(selectinload(ListeningPractice.questions).selectinload(ListeningQuestion.options))
    )
    if practice is None:
        raise not_found("Listening practice not found.")
    return practice


@router.get("/practices/{practice_id}", response_model=ListeningPracticeResponse)
async def get_practice(practice_id: int, db: DbSession, _: CurrentUser) -> ListeningPracticeResponse:
    practice = await _load_practice(db, practice_id)
    return ListeningPracticeResponse(data=ListeningPracticeRead.model_validate(practice))


@router.post("/attempts", response_model=SubmitListeningAttemptResponse, status_code=status.HTTP_201_CREATED)
async def submit_attempt(
    payload: SubmitListeningAttemptRequest, db: DbSession, current_user: CurrentUser
) -> SubmitListeningAttemptResponse:
    practice = await _load_practice(db, payload.practice_id)
    try:
        grade = grade_choices(
            practice.questions, {answer.question_id: answer.selected_option_id for answer in payload.answers}
        )
    except UnknownQuestionError:
        raise invalid("One or more answers refer to questions outside this practice.") from None

    already_passed = await db.scalar(
        select(
            exists().where(
                ListeningAttempt.user_id == current_user.id,
                ListeningAttempt.practice_id == practice.id,
                ListeningAttempt.passed.is_(True),
            )
        )
    )
    xp = practice.xp_reward if grade.passed and not already_passed else 0
    now = datetime.now(UTC)

    attempt = ListeningAttempt(
        user_id=current_user.id,
        practice_id=practice.id,
        score=grade.score,
        passed=grade.passed,
        xp_earned=xp,
        completed_at=now,
    )
    db.add(attempt)
    await award_xp(db, current_user, skill_code="listening", xp=xp, now=now)
    await db.commit()

    return SubmitListeningAttemptResponse(
        data=SubmitListeningAttemptData(
            attempt_id=attempt.id, score=grade.score, passed=grade.passed, xp_earned=xp, completed_at=now
        )
    )
