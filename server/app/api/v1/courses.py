"""Curriculum structure: levels, courses and lessons. Practice content is served by each skill's router."""

from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.api.errors import not_found
from app.models import (
    Course,
    Dialogue,
    KanjiPractice,
    Lesson,
    ListeningPractice,
    ProficiencyLevel,
    ReadingPassage,
    Vocabulary,
)
from app.schemas import (
    CourseListResponse,
    CourseRead,
    LessonDetailRead,
    LessonDetailResponse,
    LessonListResponse,
    LessonRead,
    PracticeRef,
    ProficiencyLevelListResponse,
    ProficiencyLevelRead,
)

router = APIRouter(tags=["courses"])


@router.get("/levels", response_model=ProficiencyLevelListResponse)
async def list_levels(db: DbSession, _: CurrentUser) -> ProficiencyLevelListResponse:
    levels = await db.scalars(select(ProficiencyLevel).order_by(ProficiencyLevel.sort_order))
    return ProficiencyLevelListResponse(data=[ProficiencyLevelRead.model_validate(level) for level in levels])


@router.get("/courses", response_model=CourseListResponse)
async def list_courses(
    db: DbSession,
    _: CurrentUser,
    level_id: Annotated[int | None, Query(alias="levelId", gt=0)] = None,
) -> CourseListResponse:
    query = select(Course).order_by(Course.sort_order, Course.id)
    if level_id is not None:
        query = query.where(Course.level_id == level_id)
    courses = await db.scalars(query)
    return CourseListResponse(data=[CourseRead.model_validate(course) for course in courses])


@router.get("/courses/{course_id}/lessons", response_model=LessonListResponse)
async def list_lessons(course_id: int, db: DbSession, _: CurrentUser) -> LessonListResponse:
    if await db.get(Course, course_id) is None:
        raise not_found("Course not found.")
    lessons = await db.scalars(
        select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.sort_order, Lesson.id)
    )
    return LessonListResponse(data=[LessonRead.model_validate(lesson) for lesson in lessons])


@router.get("/lessons/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson(lesson_id: int, db: DbSession, _: CurrentUser) -> LessonDetailResponse:
    """The lesson plus what it contains, so the client knows which practices to offer."""
    lesson = await db.get(Lesson, lesson_id)
    if lesson is None:
        raise not_found("Lesson not found.")

    async def refs(model: type[ReadingPassage | Dialogue | KanjiPractice | ListeningPractice]) -> list[PracticeRef]:
        rows = await db.execute(
            select(model.id, model.title, model.xp_reward).where(model.lesson_id == lesson_id).order_by(model.id)
        )
        return [PracticeRef(id=row.id, title=row.title, xp_reward=row.xp_reward) for row in rows]

    vocabulary_count = await db.scalar(select(func.count()).where(Vocabulary.lesson_id == lesson_id))
    return LessonDetailResponse(
        data=LessonDetailRead(
            **LessonRead.model_validate(lesson).model_dump(),
            vocabulary_count=vocabulary_count or 0,
            reading_passages=await refs(ReadingPassage),
            dialogues=await refs(Dialogue),
            kanji_practices=await refs(KanjiPractice),
            listening_practices=await refs(ListeningPractice),
        )
    )
