from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.security import oauth2_scheme
from app.db import models
from server.app.db.schemas import (
    CreateOnboardingSessionRequest,
    CreateOnboardingSessionResponse,
    CreateOnboardingSessionData,
    SaveOnboardingAnswerRequest,
    SaveOnboardingAnswerResponse,
    SaveOnboardingAnswerData,
    LoadOnboardingAnswersResponse,
    LoadOnboardingAnswersData,
    OnboardingAnswerItem,
    FinalizeOnboardingSessionRequest,
    FinalizeOnboardingSessionResponse,
    FinalizeOnboardingSessionData,
    SubmitOnboardingRequest,
    SubmitOnboardingResponse,
    SubmitOnboardingData,
    UpsertLearnerProfileRequest,
    UpsertLearnerProfileResponse,
    UpsertLearnerProfileData,
    ConfirmCommitmentRequest,
    ConfirmCommitmentResponse,
    ConfirmCommitmentData,
)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

BUSINESS_SUCCESS = "LMS-RESP-SUCCESS"
BUSINESS_INVALID = "LMS-RESP-INVALID_INPUT"
BUSINESS_NOT_FOUND = "LMS-RESP-NOT_FOUND"
BUSINESS_UNAUTHORIZED = "LMS-RESP-UNAUTHORIZED"
BUSINESS_FAILED = "LMS-RESP-FAILED"

QUESTION_TEXT_BY_CODE = {
    "starting_level": "Starting level",
    "goal": "Study goal",
    "time": "Daily commitment time",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _response(
    *,
    message: str,
    data: BaseModel | dict | None = None,
    success: bool = True,
    business_code: str = BUSINESS_SUCCESS,
) -> dict:
    payload: dict[str, object] = {
        "success": success,
        "businessCode": business_code,
        "message": message,
        "timestamp": _isoformat(_utcnow()),
    }
    if data is not None:
        payload["data"] = data.model_dump(mode="json") if isinstance(data, BaseModel) else data
    return payload


def _raise_error(status_code: int, *, message: str, business_code: str) -> None:
    raise HTTPException(
        status_code=status_code,
        detail=_response(message=message, success=False, business_code=business_code),
    )



def _calculate_current_level(score: float) -> str:
    if score < 25:
        return "beginner"
    if score < 50:
        return "N5"
    if score < 80:
        return "N4"
    if score < 90:
        return "N3"
    if score < 97:
        return "N2"
    return "N1"


async def _load_session_for_user(
    db: AsyncSession,
    *,
    session_id: int,
    user_id: int,
) -> models.OnboardingSessions:
    result = await db.execute(
        select(models.OnboardingSessions).where(models.OnboardingSessions.id == session_id)
    )
    session = result.scalars().first()
    if session is None:
        _raise_error(
            status.HTTP_404_NOT_FOUND,
            message="Resource not found.",
            business_code=BUSINESS_NOT_FOUND,
        )
    if session.user_id != user_id:
        _raise_error(
            status.HTTP_401_UNAUTHORIZED,
            message="Unauthorized access.",
            business_code=BUSINESS_UNAUTHORIZED,
        )
    return session


async def _find_active_session(
    db: AsyncSession,
    *,
    user_id: int,
) -> models.OnboardingSessions | None:
    result = await db.execute(
        select(models.OnboardingSessions)
        .where(models.OnboardingSessions.user_id == user_id)
        .where(models.OnboardingSessions.status == "in_progress")
        .order_by(models.OnboardingSessions.id.desc())
    )
    return result.scalars().first()


async def _create_session(
    db: AsyncSession,
    *,
    current_user: models.User,
) -> models.OnboardingSessions:
    existing_session = await _find_active_session(db, user_id=current_user.id)
    if existing_session is not None:
        _raise_error(
            status.HTTP_409_CONFLICT,
            message="Invalid input data.",
            business_code=BUSINESS_FAILED,
        )

    session = models.OnboardingSessions(
        user_id=current_user.id,
        started_at=_utcnow(),
        status="in_progress",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def _upsert_answer(
    db: AsyncSession,
    *,
    session: models.OnboardingSessions,
    question_code: str,
    answer_value: str,
) -> models.OnboardingAnswers:
    result = await db.execute(
        select(models.OnboardingAnswers)
        .where(models.OnboardingAnswers.session_id == session.id)
        .where(models.OnboardingAnswers.question_code == question_code)
    )
    answer = result.scalars().first()
    question_text = QUESTION_TEXT_BY_CODE.get(question_code, question_code.replace("_", " ").title())

    if answer is None:
        answer = models.OnboardingAnswers(
            session_id=session.id,
            question_code=question_code,
            question_text=question_text,
            answer_text=answer_value,
            answer_value=answer_value,
        )
        db.add(answer)
    else:
        answer.question_text = question_text
        answer.answer_text = answer_value
        answer.answer_value = answer_value

    await db.commit()
    await db.refresh(answer)
    return answer


async def _finalize_session(
    db: AsyncSession,
    *,
    session: models.OnboardingSessions,
) -> models.OnboardingSessions:
    if session.status == "completed":
        _raise_error(
            status.HTTP_409_CONFLICT,
            message="Invalid input data.",
            business_code=BUSINESS_FAILED,
        )

    result = await db.execute(
        select(models.OnboardingAnswers).where(models.OnboardingAnswers.session_id == session.id)
    )
    answers = result.scalars().all()
    answer_map = {item.question_code: item.answer_value for item in answers if item.question_code}

    session.result_level = answer_map.get("starting_level")
    session.result_goal = answer_map.get("goal")
    session.status = "completed"
    session.completed_at = _utcnow()

    await db.commit()
    await db.refresh(session)
    return session


async def _mark_user_onboarded(
    db: AsyncSession,
    *,
    user: models.User,
) -> None:
    if user.is_onboarded:
        return

    now = _utcnow()
    user.is_onboarded = True
    user.onboarded_at = now
    user.updated_at = now.replace(tzinfo=None)
    await db.commit()
    await db.refresh(user)


async def _load_user_by_id(db: AsyncSession, user_id: int) -> models.User:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if user is None:
        _raise_error(
            status.HTTP_404_NOT_FOUND,
            message="Resource not found.",
            business_code=BUSINESS_NOT_FOUND,
        )
    return user


@router.post("/session", response_model=CreateOnboardingSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_onboarding_session(
    payload: CreateOnboardingSessionRequest,
    token: str = Depends(oauth2_scheme),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.userId != current_user.id:
        _raise_error(
            status.HTTP_401_UNAUTHORIZED,
            message="Unauthorized access.",
            business_code=BUSINESS_UNAUTHORIZED,
        )
    if payload.sessionToken is not None and payload.sessionToken != token:
        _raise_error(
            status.HTTP_401_UNAUTHORIZED,
            message="Unauthorized access.",
            business_code=BUSINESS_UNAUTHORIZED,
        )

    session = await _create_session(db, current_user=current_user)
    return _response(
        message="Created successfully.",
        data=CreateOnboardingSessionData(
            sessionId=session.id,
            status=session.status or "in_progress",
            startedAt=_isoformat(session.started_at) or _isoformat(_utcnow()) or "",
        ),
    )


@router.post("/answers", response_model=SaveOnboardingAnswerResponse)
async def save_onboarding_answer(
    payload: SaveOnboardingAnswerRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await _load_session_for_user(db, session_id=payload.sessionId, user_id=current_user.id)
    if session.status == "completed":
        _raise_error(
            status.HTTP_409_CONFLICT,
            message="Invalid input data.",
            business_code=BUSINESS_FAILED,
        )

    answer = await _upsert_answer(
        db,
        session=session,
        question_code=payload.questionCode,
        answer_value=payload.answerValue,
    )
    return _response(
        message="Saved successfully.",
        data=SaveOnboardingAnswerData(
            answerId=answer.id,
            sessionId=session.id,
            questionCode=answer.question_code or payload.questionCode,
            savedAt=_isoformat(answer.created_at) or _isoformat(_utcnow()) or "",
        ),
    )


@router.get("/answers", response_model=LoadOnboardingAnswersResponse)
async def load_onboarding_answers(
    sessionId: int = Query(..., gt=0),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await _load_session_for_user(db, session_id=sessionId, user_id=current_user.id)
    result = await db.execute(
        select(models.OnboardingAnswers)
        .where(models.OnboardingAnswers.session_id == session.id)
        .order_by(models.OnboardingAnswers.id.desc())
    )
    answers = result.scalars().all()
    if not answers:
        _raise_error(
            status.HTTP_404_NOT_FOUND,
            message="Resource not found.",
            business_code=BUSINESS_NOT_FOUND,
        )

    return _response(
        message="Loaded successfully.",
        data=LoadOnboardingAnswersData(
            sessionId=session.id,
            answers=[
                OnboardingAnswerItem(
                    answerId=answer.id,
                    questionCode=answer.question_code or "",
                    answerValue=answer.answer_value or "",
                    updatedAt=_isoformat(answer.created_at) or _isoformat(_utcnow()) or "",
                )
                for answer in answers
            ],
        ),
    )


@router.put("/session/finalize", response_model=FinalizeOnboardingSessionResponse)
async def finalize_onboarding_session(
    payload: FinalizeOnboardingSessionRequest,
    token: str = Depends(oauth2_scheme),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.sessionToken is not None and payload.sessionToken != token:
        _raise_error(
            status.HTTP_401_UNAUTHORIZED,
            message="Unauthorized access.",
            business_code=BUSINESS_UNAUTHORIZED,
        )

    session = await _load_session_for_user(db, session_id=payload.sessionId, user_id=current_user.id)
    session = await _finalize_session(db, session=session)
    return _response(
        message="Updated successfully.",
        data=FinalizeOnboardingSessionData(
            sessionId=session.id,
            status=session.status or "completed",
            completedAt=_isoformat(session.completed_at) or _isoformat(_utcnow()) or "",
        ),
    )


@router.post("/submit", response_model=SubmitOnboardingResponse, status_code=status.HTTP_201_CREATED)
async def submit_onboarding(
    payload: SubmitOnboardingRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    session = await _find_active_session(db, user_id=current_user.id)
    if session is None:
        session = await _create_session(db, current_user=current_user)

    for question_code, answer_value in (
        ("starting_level", payload.level),
        ("goal", payload.goal),
        ("time", payload.time),
    ):
        await _upsert_answer(
            db,
            session=session,
            question_code=question_code,
            answer_value=answer_value,
        )

    session = await _finalize_session(db, session=session)
    await _mark_user_onboarded(db, user=current_user)
    return _response(
        message="Created successfully.",
        data=SubmitOnboardingData(
            sessionId=session.id,
            status=session.status or "completed",
            level=payload.level,
            goal=payload.goal,
            time=payload.time,
            completedAt=_isoformat(session.completed_at) or _isoformat(_utcnow()) or "",
        ),
    )


profile_router = APIRouter(prefix="/learner-profile", tags=["onboarding"])


@profile_router.post("/upsert", response_model=UpsertLearnerProfileResponse)
async def upsert_learner_profile(
    payload: UpsertLearnerProfileRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.userId != current_user.id:
        _raise_error(
            status.HTTP_401_UNAUTHORIZED,
            message="Unauthorized access.",
            business_code=BUSINESS_UNAUTHORIZED,
        )

    if payload.experience not in {"beginner", "intermediate", "advanced"}:
        _raise_error(
            status.HTTP_400_BAD_REQUEST,
            message="Validation failed.",
            business_code=BUSINESS_INVALID,
        )

    await _load_user_by_id(db, payload.userId)

    result = await db.execute(
        select(models.LearnerProfiles).where(models.LearnerProfiles.user_id == payload.userId)
    )
    profile = result.scalars().first()
    current_level = _calculate_current_level(payload.testResult)

    if profile is None:
        profile = models.LearnerProfiles(
            user_id=payload.userId,
            target_language="ja",
            current_level=current_level,
            target_level=payload.targetLevel,
            study_goal=payload.targetGoal,
            study_mode=payload.experience,
        )
        db.add(profile)
    else:
        profile.current_level = current_level
        profile.target_level = payload.targetLevel
        profile.study_goal = payload.targetGoal
        profile.study_mode = payload.experience
        if not profile.target_language:
            profile.target_language = "ja"

    await db.commit()
    await db.refresh(profile)

    return _response(
        message="Saved successfully.",
        data=UpsertLearnerProfileData(
            profileId=profile.user_id,
            userId=profile.user_id,
            currentLevel=profile.current_level or current_level,
            targetLevel=profile.target_level or payload.targetLevel,
            updatedAt=_isoformat(_utcnow()) or "",
        ),
    )


@router.post("/confirm-commitment", response_model=ConfirmCommitmentResponse)
async def confirm_commitment(
    payload: ConfirmCommitmentRequest,
    token: str = Depends(oauth2_scheme),
    current_user: models.User = Depends(get_current_user),
):
    if payload.sessionToken != token:
        _raise_error(
            status.HTTP_401_UNAUTHORIZED,
            message="Unauthorized access.",
            business_code=BUSINESS_UNAUTHORIZED,
        )

    return {
        "businessCode": BUSINESS_SUCCESS,
        "message": "Request completed successfully.",
        "timestamp": _isoformat(_utcnow()),
        "data": ConfirmCommitmentData(
            loginState=True,
            userId=current_user.id,
            redirectScreen="HOME",
        ).model_dump(mode="json"),
    }


router.include_router(profile_router)
