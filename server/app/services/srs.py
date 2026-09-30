"""Spaced repetition (SM-2) for vocabulary flashcards."""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Vocabulary, VocabularyReview
from app.services.gamification import award_xp

QUALITY_BY_RESULT = {"again": 1, "hard": 3, "good": 4, "easy": 5}
MIN_EASE_FACTOR = 1.3
DEFAULT_EASE_FACTOR = 2.5
QUEUE_LIMIT = 50


@dataclass(frozen=True)
class Schedule:
    repetitions: int
    ease_factor: float
    interval_days: int


def schedule_next(quality: int, repetitions: int, ease_factor: float, interval_days: int) -> Schedule:
    """
    SM-2. A failed recall (quality < 3) restarts the card at 1 day and lowers its ease;
    the ease factor never drops below 1.3, so hard cards don't get stuck in a loop.
    """
    if quality < 3:
        return Schedule(0, round(max(MIN_EASE_FACTOR, ease_factor - 0.2), 2), 1)

    if repetitions == 0:
        interval = 1
    elif repetitions == 1:
        interval = 6
    else:
        interval = math.ceil(interval_days * ease_factor)
    ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return Schedule(repetitions + 1, round(max(MIN_EASE_FACTOR, ease), 2), interval)


async def due_cards(db: AsyncSession, user: User, now: datetime) -> list[Vocabulary]:
    return list(
        await db.scalars(
            select(Vocabulary)
            .join(VocabularyReview, VocabularyReview.vocabulary_id == Vocabulary.id)
            .where(VocabularyReview.user_id == user.id, VocabularyReview.next_review_at <= now)
            .order_by(VocabularyReview.next_review_at)
            .limit(QUEUE_LIMIT)
        )
    )


async def review_card(
    db: AsyncSession, user: User, vocabulary: Vocabulary, *, result: str, now: datetime
) -> tuple[VocabularyReview, int]:
    """
    Record one review and schedule the next. A card seen for the first time enters the schedule here.
    XP is only earned for a successful review of a new or due card, so reviewing early earns nothing.
    Returns (review state, XP earned). The caller commits.
    """
    review = await db.scalar(
        select(VocabularyReview)
        .where(VocabularyReview.user_id == user.id, VocabularyReview.vocabulary_id == vocabulary.id)
        .with_for_update()
    )
    if review is None:
        review = VocabularyReview(
            user_id=user.id,
            vocabulary_id=vocabulary.id,
            ease_factor=DEFAULT_EASE_FACTOR,
            interval_days=0,
            repetitions=0,
        )
        db.add(review)
    was_due = review.next_review_at is None or review.next_review_at <= now

    quality = QUALITY_BY_RESULT[result]
    schedule = schedule_next(quality, review.repetitions, float(review.ease_factor), review.interval_days)
    review.repetitions = schedule.repetitions
    review.ease_factor = schedule.ease_factor
    review.interval_days = schedule.interval_days
    review.next_review_at = now + timedelta(days=schedule.interval_days)
    review.last_reviewed_at = now
    review.last_result = result

    xp = vocabulary.xp_reward if was_due and quality >= 3 else 0
    await award_xp(db, user, skill_code="vocab", xp=xp, now=now)
    return review, xp
