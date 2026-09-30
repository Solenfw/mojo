"""Vocabulary flashcards with spaced repetition (SRS)."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.api.errors import not_found
from app.models import Lesson, Vocabulary
from app.schemas import (
    SRSReviewData,
    SRSReviewRequest,
    SRSReviewResponse,
    VocabQueueResponse,
    VocabularyListResponse,
    VocabularyRead,
)
from app.services import srs

router = APIRouter(prefix="/vocabulary", tags=["vocabulary"])


@router.get("", response_model=VocabularyListResponse)
async def list_lesson_vocabulary(
    db: DbSession,
    _: CurrentUser,
    lesson_id: Annotated[int, Query(alias="lessonId", gt=0)],
) -> VocabularyListResponse:
    if await db.get(Lesson, lesson_id) is None:
        raise not_found("Lesson not found.")
    words = await db.scalars(select(Vocabulary).where(Vocabulary.lesson_id == lesson_id).order_by(Vocabulary.id))
    return VocabularyListResponse(data=[VocabularyRead.model_validate(word) for word in words])


@router.get("/review-queue", response_model=VocabQueueResponse)
async def review_queue(db: DbSession, current_user: CurrentUser) -> VocabQueueResponse:
    """Cards due now. New cards enter the schedule the first time they are reviewed."""
    cards = await srs.due_cards(db, current_user, datetime.now(UTC))
    return VocabQueueResponse(data=[VocabularyRead.model_validate(card) for card in cards])


@router.post("/reviews", response_model=SRSReviewResponse)
async def review(payload: SRSReviewRequest, db: DbSession, current_user: CurrentUser) -> SRSReviewResponse:
    vocabulary = await db.get(Vocabulary, payload.vocab_id)
    if vocabulary is None:
        raise not_found("Vocabulary not found.")

    now = datetime.now(UTC)
    state, xp = await srs.review_card(db, current_user, vocabulary, result=payload.result, now=now)
    data = SRSReviewData(
        repetitions=state.repetitions,
        ease_factor=float(state.ease_factor),
        interval_days=state.interval_days,
        next_review_at=state.next_review_at or now,
        xp_earned=xp,
    )
    await db.commit()
    return SRSReviewResponse(data=data)
