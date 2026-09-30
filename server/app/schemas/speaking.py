"""Speaking skill (scripted dialogue + free Kaiwa + pronunciation)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.base import ApiResponse, CamelModel


class DialogueExchangeRead(CamelModel):
    id: int
    order_index: int
    speaker: str
    ja_text: str
    ja_romaji: str
    en_text: str


class DialogueRead(CamelModel):
    id: int
    title: str
    description: str | None = None
    xp_reward: int
    exchanges: list[DialogueExchangeRead] = []


class DialogueResponse(ApiResponse[DialogueRead]):
    pass


class DialogueTurnSubmission(CamelModel):
    exchange_id: int = Field(gt=0)
    transcript: str = Field(max_length=1000)


class SubmitDialogueAttemptRequest(CamelModel):
    """The learner's transcripts per exchange; the server rates them and awards XP."""

    dialogue_id: int = Field(gt=0)
    turns: list[DialogueTurnSubmission] = Field(min_length=1)


class SubmitDialogueAttemptData(CamelModel):
    attempt_id: int
    ai_score: float
    ai_feedback: str
    xp_earned: int
    completed_at: datetime


class SubmitDialogueAttemptResponse(ApiResponse[SubmitDialogueAttemptData]):
    pass


# Free AI conversation (Kaiwa)
class KaiwaHistoryItem(CamelModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=1000)


class GenerateKaiwaRequest(CamelModel):
    history: list[KaiwaHistoryItem]


class GenerateKaiwaResponse(CamelModel):
    content: str
    romaji: str
    translation: str


# Pronunciation rating (per-line feedback only; awards no XP)
class RatePronunciationRequest(CamelModel):
    expected_text: str = Field(max_length=500)
    user_transcript: str = Field(max_length=500)
    romaji: str = Field(default="", max_length=500)


class RatePronunciationResponse(CamelModel):
    score: int
    feedback: str
    is_correct: bool
