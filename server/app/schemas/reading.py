from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.schemas.base import ApiResponse, CamelModel


class ReadingOptionRead(CamelModel):
    id: int
    option_text: str


class ReadingQuestionRead(CamelModel):
    id: int
    question_text: str
    sort_order: int | None = None
    options: list[ReadingOptionRead] = []


class ReadingPassageRead(CamelModel):
    id: int
    title: str | None = None
    content_japanese: str
    content_vietnamese: str | None = None
    xp_reward: int
    questions: list[ReadingQuestionRead] = []


class ReadingPassageResponse(ApiResponse[ReadingPassageRead]):
    pass


class ReadingAnswerSubmission(CamelModel):
    question_id: int = Field(gt=0)
    selected_option_id: int = Field(gt=0)


class SubmitReadingAttemptRequest(CamelModel):
    passage_id: int = Field(gt=0)
    answers: list[ReadingAnswerSubmission] = Field(min_length=1)


class SubmitReadingAttemptData(CamelModel):
    attempt_id: int
    score: float
    passed: bool
    xp_earned: int
    completed_at: datetime


class SubmitReadingAttemptResponse(ApiResponse[SubmitReadingAttemptData]):
    pass
