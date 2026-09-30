from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.base import ApiResponse, CamelModel


class ListeningOptionRead(CamelModel):
    id: int
    option_text: str


class ListeningQuestionRead(CamelModel):
    id: int
    question_text: str
    sort_order: int | None = None
    options: list[ListeningOptionRead] = []


class ListeningPracticeRead(CamelModel):
    id: int
    title: str
    source_type: Literal["dialogue", "song", "sentences"]
    audio_url: str | None = None
    transcript_japanese: str | None = None
    transcript_vietnamese: str | None = None
    xp_reward: int
    questions: list[ListeningQuestionRead] = []


class ListeningPracticeResponse(ApiResponse[ListeningPracticeRead]):
    pass


class ListeningAnswerSubmission(CamelModel):
    question_id: int = Field(gt=0)
    selected_option_id: int = Field(gt=0)


class SubmitListeningAttemptRequest(CamelModel):
    practice_id: int = Field(gt=0)
    answers: list[ListeningAnswerSubmission] = Field(min_length=1)


class SubmitListeningAttemptData(CamelModel):
    attempt_id: int
    score: float
    passed: bool
    xp_earned: int
    completed_at: datetime


class SubmitListeningAttemptResponse(ApiResponse[SubmitListeningAttemptData]):
    pass
