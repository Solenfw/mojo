"""Writing skill (kanji canvas + AI rating)."""

from __future__ import annotations

from pydantic import Field

from app.schemas.base import ApiResponse, CamelModel


class KanjiPracticeRead(CamelModel):
    id: int
    title: str
    kanji: str
    difficulty: str | None = None
    xp_reward: int


class KanjiPracticeResponse(ApiResponse[KanjiPracticeRead]):
    pass


class EvaluateWritingRequest(CamelModel):
    """The target kanji is loaded from the KanjiPractice row, not taken from the client."""

    kanji_practice_id: int = Field(gt=0)
    image_base64: str


class EvaluateWritingData(CamelModel):
    attempt_id: int
    score: int
    feedback: str
    xp_earned: int


class EvaluateWritingResponse(ApiResponse[EvaluateWritingData]):
    pass
