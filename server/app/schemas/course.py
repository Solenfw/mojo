from __future__ import annotations

from app.schemas.base import ApiResponse, CamelModel


class CourseRead(CamelModel):
    id: int
    title: str
    status: str | None = None
    level_id: int
    sort_order: int | None = None


class CourseListResponse(ApiResponse[list[CourseRead]]):
    pass


class LessonRead(CamelModel):
    id: int
    course_id: int
    title: str
    content: str | None = None
    difficulty: str | None = None
    estimated_minutes: int | None = None
    status: str | None = None
    sort_order: int | None = None


class LessonListResponse(ApiResponse[list[LessonRead]]):
    pass


class PracticeRef(CamelModel):
    """A practice item inside a lesson; fetch its content from the skill's own endpoint."""

    id: int
    title: str | None = None
    xp_reward: int


class LessonDetailRead(LessonRead):
    vocabulary_count: int
    reading_passages: list[PracticeRef] = []
    dialogues: list[PracticeRef] = []
    kanji_practices: list[PracticeRef] = []
    listening_practices: list[PracticeRef] = []


class LessonDetailResponse(ApiResponse[LessonDetailRead]):
    pass
