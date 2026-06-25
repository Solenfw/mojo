from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.api.deps import get_current_user, get_db
from server.app.db import models
from server.app.db.schemas import ReviewRequest
from server.app.services.srs_engine import process_srs_review

router = APIRouter(prefix="/srs", tags=["srs"])


@router.get("/due")
async def get_due_reviews(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve due vocabulary items with complete metadata for card rendering."""
    today = datetime.utcnow().date()
    
    # Query due user cards and join with vocabulary dictionary
    stmt = (
        select(models.UserVocabulary, models.Vocabularies)
        .join(models.Vocabularies, models.UserVocabulary.vocab_id == models.Vocabularies.id)
        .where(
            models.UserVocabulary.user_id == current_user.id,
            models.UserVocabulary.next_review_date <= today
        )
    )
    result = await db.execute(stmt)
    due_items = result.all()
    
    # If no items are due, fetch up to 5 general items for study session fallback
    if not due_items:
        fallback_stmt = (
            select(models.UserVocabulary, models.Vocabularies)
            .join(models.Vocabularies, models.UserVocabulary.vocab_id == models.Vocabularies.id)
            .where(models.UserVocabulary.user_id == current_user.id)
            .limit(5)
        )
        res = await db.execute(fallback_stmt)
        due_items = res.all()

    return [
        {
            "vocab_id": item.Vocabularies.id,
            "kanji": item.Vocabularies.kanji,
            "furigana": item.Vocabularies.kana,
            "romaji": item.Vocabularies.romaji,
            "meaning": item.Vocabularies.meaning,
            "example": item.Vocabularies.example_sentence or "",
            "exampleEnglish": item.Vocabularies.example_english or "",
            "level": item.Vocabularies.level,
            "next_review_date": str(item.UserVocabulary.next_review_date),
            "ease_factor": float(item.UserVocabulary.ease_factor),
            "interval": item.UserVocabulary.interval,
            "repetitions": item.UserVocabulary.repetitions,
        }
        for item in due_items
    ]


@router.post("/review")
async def review_vocab(
    review: ReviewRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Process an individual card SM-2 revision and schedule the next study date."""
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
            detail="Vocabulary item not found in your study plan.",
        )

    # Invoke SM-2 scheduler algorithm
    updates = process_srs_review(
        review.quality_score,
        user_vocab.repetitions,
        float(user_vocab.ease_factor),
        user_vocab.interval,
    )

    # Fixed: Update attributes using object properties instead of dictionaries
    user_vocab.ease_factor = updates.easiness_factor
    user_vocab.interval = updates.interval_days
    user_vocab.repetitions = updates.repetitions
    user_vocab.next_review_date = updates.next_review.date()

    await db.commit()

    return {"next_review_date": str(user_vocab.next_review_date)}