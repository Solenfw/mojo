"""Reading practice: a passage with comprehension questions; passing earns the passage's XP once."""

from datetime import UTC, datetime

from fastapi import APIRouter, status
from sqlalchemy import exists, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.api.errors import invalid, not_found
from app.models import ReadingAttempt, ReadingAttemptAnswer, ReadingPassage, ReadingQuestion
from app.schemas import (
    ReadingPassageRead,
    ReadingPassageResponse,
    SubmitReadingAttemptData,
    SubmitReadingAttemptRequest,
    SubmitReadingAttemptResponse,
)
from app.services.gamification import award_xp
from app.services.practice import UnknownQuestionError, grade_choices

router = APIRouter(prefix="/reading", tags=["reading"])


async def _load_passage(db: DbSession, passage_id: int) -> ReadingPassage:
    passage = await db.scalar(
        select(ReadingPassage)
        .where(ReadingPassage.id == passage_id)
        .options(selectinload(ReadingPassage.questions).selectinload(ReadingQuestion.options))
    )
    if passage is None:
        raise not_found("Reading passage not found.")
    return passage


@router.get("/passages/{passage_id}", response_model=ReadingPassageResponse)
async def get_passage(passage_id: int, db: DbSession, _: CurrentUser) -> ReadingPassageResponse:
    passage = await _load_passage(db, passage_id)
    return ReadingPassageResponse(data=ReadingPassageRead.model_validate(passage))


@router.post("/attempts", response_model=SubmitReadingAttemptResponse, status_code=status.HTTP_201_CREATED)
async def submit_attempt(
    payload: SubmitReadingAttemptRequest, db: DbSession, current_user: CurrentUser
) -> SubmitReadingAttemptResponse:
    passage = await _load_passage(db, payload.passage_id)
    try:
        grade = grade_choices(
            passage.questions, {answer.question_id: answer.selected_option_id for answer in payload.answers}
        )
    except UnknownQuestionError:
        raise invalid("One or more answers refer to questions outside this passage.") from None

    already_passed = await db.scalar(
        select(
            exists().where(
                ReadingAttempt.user_id == current_user.id,
                ReadingAttempt.passage_id == passage.id,
                ReadingAttempt.passed.is_(True),
            )
        )
    )
    xp = passage.xp_reward if grade.passed and not already_passed else 0
    now = datetime.now(UTC)

    attempt = ReadingAttempt(
        user_id=current_user.id,
        passage_id=passage.id,
        score=grade.score,
        passed=grade.passed,
        xp_earned=xp,
        completed_at=now,
    )
    db.add(attempt)
    await db.flush()
    db.add_all(
        ReadingAttemptAnswer(
            attempt_id=attempt.id,
            question_id=answer.question_id,
            selected_option_id=answer.selected_option_id,
            is_correct=answer.is_correct,
        )
        for answer in grade.answers
    )
    await award_xp(db, current_user, skill_code="reading", xp=xp, now=now)
    await db.commit()

    return SubmitReadingAttemptResponse(
        data=SubmitReadingAttemptData(
            attempt_id=attempt.id, score=grade.score, passed=grade.passed, xp_earned=xp, completed_at=now
        )
    )
