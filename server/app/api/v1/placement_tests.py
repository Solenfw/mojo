from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.api.deps import get_current_user, get_db
from server.app.db import models
from server.app.db.schemas import (
    CreateTestAttemptData,
    CreateTestAttemptRequest,
    CreateTestAttemptResponse,
    GetQuestionOptionsRequest,
    LatestTestAttemptData,
    LatestTestAttemptResponse,
    PlacementTestItem,
    PlacementTestResponse,
    SaveTestAttemptAnswersData,
    SaveTestAttemptAnswersRequest,
    SaveTestAttemptAnswersResponse,
    TestQuestionItem,
    TestQuestionListResponse,
    TestQuestionOptionItem,
    TestQuestionOptionsResponse,
)

router = APIRouter(tags=["placement-tests"])

BUSINESS_SUCCESS = "LMS-RESP-SUCCESS"
BUSINESS_NOT_FOUND = "LMS-RESP-NOT_FOUND"
BUSINESS_UNAUTHORIZED = "LMS-RESP-UNAUTHORIZED"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _as_float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def _response(*, message: str, data, business_code: str = BUSINESS_SUCCESS) -> dict:
    return {
        "success": True,
        "businessCode": business_code,
        "message": message,
        "data": data,
        "timestamp": _isoformat(_utcnow()),
    }


def _error(status_code: int, *, field: str, message: str, business_code: str) -> None:
    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "businessCode": business_code,
            "message": message,
            "errors": [{"field": field, "message": message}],
            "timestamp": _isoformat(_utcnow()),
        },
    )


def _estimate_level(score_percent: float) -> str:
    if score_percent < 25:
        return "beginner"
    if score_percent < 50:
        return "N5"
    if score_percent < 80:
        return "N4"
    if score_percent < 90:
        return "N3"
    if score_percent < 97:
        return "N2"
    return "N1"


@router.get("/tests/placement", response_model=PlacementTestResponse)
async def get_placement_test_by_type(
    testType: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.Tests)
        .where(models.Tests.test_type == testType)
        .order_by(models.Tests.id.asc())
    )
    test = result.scalars().first()
    if test is None:
        _error(
            status.HTTP_404_NOT_FOUND,
            field="testType",
            message="Placement test does not exist.",
            business_code=BUSINESS_NOT_FOUND,
        )

    return _response(
        message="Loaded successfully.",
        data=PlacementTestItem(
            testId=test.id,
            testCode=test.code,
            title=test.title,
            testType=test.test_type,
            totalScore=_as_float(test.total_score),
            durationMinutes=test.duration_minutes,
            status=test.status,
        ).model_dump(mode="json"),
    )


@router.get("/tests/questions", response_model=TestQuestionListResponse)
async def get_questions_by_test_id(
    testId: int = Query(..., gt=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.TestQuestions)
        .where(models.TestQuestions.test_id == testId)
        .order_by(models.TestQuestions.sort_order.asc(), models.TestQuestions.id.asc())
    )
    questions = result.scalars().all()
    if not questions:
        _error(
            status.HTTP_404_NOT_FOUND,
            field="testId",
            message="Questions do not exist.",
            business_code=BUSINESS_NOT_FOUND,
        )

    return _response(
        message="Loaded successfully.",
        data=[
            TestQuestionItem(
                questionId=question.id,
                questionText=question.question_text,
                questionType=question.question_type,
                scoreWeight=_as_float(question.score_weight),
                sortOrder=question.sort_order,
            ).model_dump(mode="json")
            for question in questions
        ],
    )


@router.post("/questions/options", response_model=TestQuestionOptionsResponse)
async def get_options_by_question_ids(
    payload: GetQuestionOptionsRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.TestQuestionOptions)
        .where(models.TestQuestionOptions.question_id.in_(payload.questionIds))
        .order_by(models.TestQuestionOptions.question_id.asc(), models.TestQuestionOptions.id.asc())
    )
    options = result.scalars().all()
    if not options:
        _error(
            status.HTTP_404_NOT_FOUND,
            field="questionIds",
            message="Options do not exist.",
            business_code=BUSINESS_NOT_FOUND,
        )

    return _response(
        message="Loaded successfully.",
        data=[
            TestQuestionOptionItem(
                optionId=option.id,
                questionId=option.question_id,
                optionText=option.option_text,
            ).model_dump(mode="json")
            for option in options
        ],
    )


@router.post("/tests/attempts", response_model=CreateTestAttemptResponse, status_code=status.HTTP_201_CREATED)
async def create_test_attempt(
    payload: CreateTestAttemptRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.userId != current_user.id:
        _error(
            status.HTTP_401_UNAUTHORIZED,
            field="userId",
            message="Unauthorized access.",
            business_code=BUSINESS_UNAUTHORIZED,
        )

    test_result = await db.execute(select(models.Tests).where(models.Tests.id == payload.testId))
    test = test_result.scalars().first()
    if test is None:
        _error(
            status.HTTP_404_NOT_FOUND,
            field="testId",
            message="Placement test does not exist.",
            business_code=BUSINESS_NOT_FOUND,
        )

    attempt = models.TestAttempts(
        user_id=current_user.id,
        test_id=payload.testId,
        started_at=_utcnow(),
        status="in_progress",
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    return _response(
        message="Created successfully.",
        data=CreateTestAttemptData(
            attemptId=attempt.id,
            testId=attempt.test_id,
            userId=attempt.user_id,
            status=attempt.status or "in_progress",
            startedAt=_isoformat(attempt.started_at) or "",
        ).model_dump(mode="json"),
    )


@router.post("/tests/attempts/answers", response_model=SaveTestAttemptAnswersResponse)
async def save_test_attempt_answers(
    payload: SaveTestAttemptAnswersRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    attempt_result = await db.execute(select(models.TestAttempts).where(models.TestAttempts.id == payload.attemptId))
    attempt = attempt_result.scalars().first()
    if attempt is None:
        _error(
            status.HTTP_404_NOT_FOUND,
            field="attemptId",
            message="Test attempt does not exist.",
            business_code=BUSINESS_NOT_FOUND,
        )
    if attempt.user_id != current_user.id:
        _error(
            status.HTTP_401_UNAUTHORIZED,
            field="attemptId",
            message="Unauthorized access.",
            business_code=BUSINESS_UNAUTHORIZED,
        )

    question_ids = [item.questionId for item in payload.answers]
    questions_result = await db.execute(
        select(models.TestQuestions).where(models.TestQuestions.id.in_(question_ids))
    )
    questions = questions_result.scalars().all()
    question_map = {question.id: question for question in questions}
    if len(question_map) != len(set(question_ids)):
        _error(
            status.HTTP_404_NOT_FOUND,
            field="answers",
            message="One or more questions do not exist.",
            business_code=BUSINESS_NOT_FOUND,
        )

    total_possible = 0.0
    total_score = 0.0
    for item in payload.answers:
        question = question_map[item.questionId]
        weight = _as_float(question.score_weight) or 1.0
        total_possible += weight
        is_correct = (question.correct_answer or "").strip() == item.answerText.strip()
        awarded_score = weight if is_correct else 0.0

        db.add(
            models.TestAttemptAnswers(
                attempt_id=attempt.id,
                question_id=question.id,
                answer_text=item.answerText,
                is_correct=is_correct,
                score=Decimal(str(awarded_score)),
            )
        )
        total_score += awarded_score

    submitted_at = _utcnow()
    score_percent = (total_score / total_possible * 100.0) if total_possible else 0.0
    attempt.submitted_at = submitted_at
    attempt.score = Decimal(str(round(score_percent, 2)))
    attempt.level_estimate = _estimate_level(score_percent)
    attempt.status = "submitted"
    await db.commit()
    await db.refresh(attempt)

    return _response(
        message="Saved successfully.",
        data=SaveTestAttemptAnswersData(
            attemptId=attempt.id,
            status=attempt.status or "submitted",
            submittedAt=_isoformat(attempt.submitted_at) or "",
            score=_as_float(attempt.score) or 0.0,
            levelEstimate=attempt.level_estimate or _estimate_level(score_percent),
        ).model_dump(mode="json"),
    )


@router.get("/tests/attempts/latest", response_model=LatestTestAttemptResponse)
async def load_latest_test_attempt_by_user_id(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.TestAttempts)
        .where(models.TestAttempts.user_id == current_user.id)
        .order_by(models.TestAttempts.id.desc())
    )
    attempt = result.scalars().first()
    if attempt is None:
        _error(
            status.HTTP_404_NOT_FOUND,
            field="userId",
            message="Test attempt does not exist.",
            business_code=BUSINESS_NOT_FOUND,
        )

    return _response(
        message="Loaded successfully.",
        data=LatestTestAttemptData(
            attemptId=attempt.id,
            testId=attempt.test_id,
            userId=attempt.user_id,
            status=attempt.status,
            startedAt=_isoformat(attempt.started_at),
            submittedAt=_isoformat(attempt.submitted_at),
            score=_as_float(attempt.score),
            levelEstimate=attempt.level_estimate,
        ).model_dump(mode="json"),
    )
