"""Vocab skill (flashcard + SRS)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.base import ApiResponse, CamelModel

ReviewResult = Literal["again", "hard", "good", "easy"]


class VocabularyRead(CamelModel):
    id: int
    lesson_id: int
    kanji: str | None = None
    kana: str
    romaji: str
    meaning: str
    example_sentence: str | None = None
    example_translation: str | None = None
    xp_reward: int


class VocabularyListResponse(ApiResponse[list[VocabularyRead]]):
    pass


class VocabQueueResponse(ApiResponse[list[VocabularyRead]]):
    """Due cards for today's SRS review session."""


class SRSReviewRequest(CamelModel):
    vocab_id: int = Field(gt=0)
    result: ReviewResult


class SRSReviewData(CamelModel):
    repetitions: int
    ease_factor: float
    interval_days: int
    next_review_at: datetime
    xp_earned: int


class SRSReviewResponse(ApiResponse[SRSReviewData]):
    pass
