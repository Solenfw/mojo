from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db import models
from app.services.srs_engine import calculate_next_review

router = APIRouter()


class ReviewRequest(BaseModel):
    vocab_id: int
    quality_score: int


@router.get("/srs/due")
async def get_due_reviews(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = datetime.utcnow().date()
    result = await db.execute(
        select(models.UserVocabulary).where(
            models.UserVocabulary.user_id == current_user.id,
            models.UserVocabulary.next_review_date <= today,
        )
    )
    due_items = result.scalars().all()
    return [
        {
            "vocab_id": item.vocab_id,
            "next_review_date": item.next_review_date,
            "ease_factor": item.ease_factor,
            "interval": item.interval,
            "repetitions": item.repetitions,
        }
        for item in due_items
    ]


@router.post("/srs/review")
async def review_vocab(
    review: ReviewRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(models.UserVocabulary).where(
            models.UserVocabulary.user_id == current_user.id,
            models.UserVocabulary.vocab_id == review.vocab_id,
        )
    )
    user_vocab = result.scalars().first()
    if not user_vocab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary item not found for this user.",
        )

    # Calculate new values
    updates = calculate_next_review(
        review.quality_score,
        user_vocab.repetitions,
        user_vocab.ease_factor,
        user_vocab.interval,
    )

    # Update the record
    await db.execute(
        update(models.UserVocabulary)
        .where(
            models.UserVocabulary.user_id == current_user.id,
            models.UserVocabulary.vocab_id == review.vocab_id,
        )
        .values(**updates)
    )
    await db.commit()

    return {"next_review_date": updates["next_review_date"]}
