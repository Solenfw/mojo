from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.db import models
from app.db.schemas import (
    CourseLessonItem,
    CourseLessonResponse,
    CourseRecommendationItem,
    CourseRecommendationResponse,
    LessonResult,
    QuizSubmitRequest,
    QuizSubmitResponse,
    ReadingLessonResponse,
    SessionTokenPayload,
)
from app.services.gamification_engine import GamificationEngine

router = APIRouter()
courses_router = APIRouter(prefix="/courses", tags=["courses"])
lessons_router = APIRouter(prefix="/lessons", tags=["lessons"])

BUSINESS_SUCCESS = "LMS-RESP-SUCCESS"
BUSINESS_INVALID = "LMS-RESP-INVALID_INPUT"
BUSINESS_NOT_FOUND = "LMS-RESP-NOT_FOUND"
BUSINESS_UNAUTHORIZED = "LMS-RESP-UNAUTHORIZED"

VISIBLE_STATUSES = {"active", "published"}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _isoformat(value: datetime | None) -> str:
    current = value or _utcnow()
    return current.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _response(*, data: list[dict], message: str = "Request completed successfully.") -> dict:
    return {
        "success": True,
        "businessCode": BUSINESS_SUCCESS,
        "message": message,
        "data": data,
        "timestamp": _isoformat(None),
    }


def _raise_error(status_code: int, business_code: str, message: str) -> None:
    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "businessCode": business_code,
            "message": message,
            "timestamp": _isoformat(None),
        },
    )


def _is_visible_status(raw_status: str | None) -> bool:
    return (raw_status or "").strip().lower() in VISIBLE_STATUSES


def _validate_session_token(
    *,
    current_user: models.User,
    session_payload: SessionTokenPayload | None,
) -> None:
    if session_payload is None or session_payload.sessionToken is None:
        return
    if current_user.session_token != session_payload.sessionToken:
        _raise_error(
            status.HTTP_401_UNAUTHORIZED,
            BUSINESS_UNAUTHORIZED,
            "Unauthorized access.",
        )


@courses_router.get("/by-level", response_model=CourseRecommendationResponse)
async def get_courses_by_level(
    targetLevel: str = Query(..., min_length=1),
    session_payload: SessionTokenPayload | None = Body(default=None),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _validate_session_token(current_user=current_user, session_payload=session_payload)

    normalized_level = targetLevel.strip().upper()
    if normalized_level not in {"N5", "N4", "N3", "N2", "N1", "BEGINNER", "INTERMEDIATE", "ADVANCED"}:
        _raise_error(
            status.HTTP_400_BAD_REQUEST,
            BUSINESS_INVALID,
            "Validation failed.",
        )

    lessons_subquery = (
        select(
            models.Lessons.course_id.label("course_id"),
            func.coalesce(func.sum(models.Lessons.estimated_minutes), 0).label("total_minutes"),
        )
        .where(func.lower(func.coalesce(models.Lessons.status, "")).in_(VISIBLE_STATUSES))
        .group_by(models.Lessons.course_id)
        .subquery()
    )

    stmt = (
        select(models.Courses, lessons_subquery.c.total_minutes)
        .outerjoin(lessons_subquery, lessons_subquery.c.course_id == models.Courses.id)
        .where(models.Courses.level == normalized_level)
        .where(func.lower(func.coalesce(models.Courses.status, "")).in_(VISIBLE_STATUSES))
        .order_by(models.Courses.id.asc())
    )
    rows = (await db.execute(stmt)).all()
    if not rows:
        _raise_error(
            status.HTTP_404_NOT_FOUND,
            BUSINESS_NOT_FOUND,
            "Resource not found.",
        )

    items = [
        CourseRecommendationItem(
            courseId=course.id,
            courseName=course.title,
            targetLevel=course.level or normalized_level,
            thumbnailUrl=None,
            estimatedDuration=max(1, int((total_minutes or 0) / 60)) if (total_minutes or 0) > 0 else 1,
        ).model_dump(mode="json")
        for course, total_minutes in rows
    ]
    return _response(data=items)


@courses_router.get("/lessons", response_model=CourseLessonResponse)
async def get_lessons_by_course_id(
    recommendedCourseId: int = Query(..., gt=0),
    session_payload: SessionTokenPayload | None = Body(default=None),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _validate_session_token(current_user=current_user, session_payload=session_payload)

    course = await db.scalar(select(models.Courses).where(models.Courses.id == recommendedCourseId))
    if course is None or not _is_visible_status(course.status):
        _raise_error(
            status.HTTP_404_NOT_FOUND,
            BUSINESS_NOT_FOUND,
            "Resource not found.",
        )

    lessons = (
        await db.scalars(
            select(models.Lessons)
            .options(
                selectinload(models.Lessons.lesson_resources),
                selectinload(models.Lessons.reading_passages),
            )
            .where(models.Lessons.course_id == recommendedCourseId)
            .where(func.lower(func.coalesce(models.Lessons.status, "")).in_(VISIBLE_STATUSES))
            .order_by(models.Lessons.id.asc())
        )
    ).all()
    if not lessons:
        _raise_error(
            status.HTTP_404_NOT_FOUND,
            BUSINESS_NOT_FOUND,
            "Resource not found.",
        )

    items = []
    for index, lesson in enumerate(lessons, start=1):
        has_preview = bool(lesson.content) or bool(lesson.lesson_resources) or bool(lesson.reading_passages)
        items.append(
            CourseLessonItem(
                lessonId=lesson.id,
                lessonTitle=lesson.title,
                lessonOrder=index,
                estimatedDuration=lesson.estimated_minutes or 0,
                isPreviewAvailable=has_preview,
                lessonType=lesson.lesson_type,
            ).model_dump(mode="json")
        )
    return _response(data=items)


@lessons_router.get("/{lesson_id}/reading", response_model=ReadingLessonResponse)
async def get_reading_lesson(
    lesson_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson = await db.scalar(select(models.Lessons).where(models.Lessons.id == lesson_id))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    passage_stmt = (
        select(models.ReadingPassages)
        .where(models.ReadingPassages.lesson_id == lesson_id)
        .order_by(models.ReadingPassages.sort_order, models.ReadingPassages.id)
    )
    passages = (await db.scalars(passage_stmt)).all()

    ex_stmt = (
        select(models.Exercises)
        .where(
            models.Exercises.lesson_id == lesson_id,
            models.Exercises.exercise_type.in_(
                [
                    "reading_multiple_choice",
                    "reading_true_false",
                    "reading_short_answer",
                ]
            ),
        )
        .order_by(models.Exercises.id)
    )
    exercises = (await db.scalars(ex_stmt)).all()

    questions = []
    for exercise in exercises:
        opt_stmt = (
            select(models.ExerciseOptions)
            .where(models.ExerciseOptions.exercise_id == exercise.id)
            .order_by(models.ExerciseOptions.id)
        )
        options = (await db.scalars(opt_stmt)).all()
        if not options:
            continue
        questions.append(
            {
                "id": exercise.id,
                "prompt": exercise.prompt,
                "options": [{"id": option.id, "text": option.option_text} for option in options],
            }
        )

    vocab_stmt = (
        select(models.ReadingVocabularyItems)
        .where(models.ReadingVocabularyItems.lesson_id == lesson_id)
        .order_by(models.ReadingVocabularyItems.sort_order, models.ReadingVocabularyItems.id)
    )
    vocabulary = (await db.scalars(vocab_stmt)).all()
    words = {
        item.word: {
            "kana": item.kana or item.word,
            "meaning": item.meaning,
            "level": item.level or lesson.difficulty or "N5",
            "kanji": item.kanji or "",
            "romaji": item.romaji or "",
            "type": item.word_type or "",
        }
        for item in vocabulary
    }

    content = "\n\n".join(passage.content_japanese for passage in passages) if passages else lesson.content

    return {
        "id": lesson.id,
        "title": lesson.title,
        "content": content or "",
        "difficulty": lesson.difficulty or "N5",
        "passages": [
            {
                "id": passage.id,
                "title": passage.title,
                "japanese": passage.content_japanese,
                "vietnamese": passage.content_vietnamese,
            }
            for passage in passages
        ],
        "questions": questions,
        "words": words,
    }


@lessons_router.post("/{lesson_id}/reading/submit", response_model=QuizSubmitResponse)
async def submit_reading_quiz(
    lesson_id: int,
    payload: QuizSubmitRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_score = 0
    max_score = 0

    for exercise_id, selected_option_id in payload.answers.items():
        exercise = await db.scalar(select(models.Exercises).where(models.Exercises.id == exercise_id))
        if not exercise or exercise.lesson_id != lesson_id:
            continue

        option = await db.scalar(select(models.ExerciseOptions).where(models.ExerciseOptions.id == selected_option_id))
        is_correct = option.is_correct if option else False

        weight = int(exercise.score_weight or 10)
        max_score += weight
        if is_correct:
            total_score += weight

        attempt = models.ExerciseAttempts(
            user_id=current_user.id,
            exercise_id=exercise_id,
            answer_text=option.option_text if option else "",
            is_correct=is_correct,
            score=weight if is_correct else 0,
        )
        db.add(attempt)

    xp_gained = total_score * 2
    is_passed = total_score >= (max_score * 0.7) if max_score > 0 else True

    if xp_gained > 0:
        await GamificationEngine.add_xp(current_user, xp_gained, db)
        await GamificationEngine.update_streak(current_user, db)
    else:
        await db.commit()

    return {
        "score": total_score,
        "max_score": max_score,
        "xp_gained": xp_gained,
        "is_passed": is_passed,
    }


@lessons_router.post("/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: int,
    result: LessonResult,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    lesson = await db.scalar(select(models.Lessons).where(models.Lessons.id == lesson_id))
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    await GamificationEngine.add_xp(current_user, result.xp_gained, db)
    await GamificationEngine.update_streak(current_user, db)

    for vocab_id in result.vocab_learned:
        existing = await db.scalar(
            select(models.UserVocabulary).where(
                models.UserVocabulary.user_id == current_user.id,
                models.UserVocabulary.vocab_id == vocab_id,
            )
        )
        if existing:
            continue
        db.add(
            models.UserVocabulary(
                user_id=current_user.id,
                vocab_id=vocab_id,
                ease_factor=2.5,
                interval=1,
                repetitions=0,
                next_review_date=None,
            )
        )

    await db.commit()
    await db.refresh(current_user)

    return {
        "xp_gained": result.xp_gained,
        "streak": getattr(current_user, "streak", 0),
    }


router.include_router(courses_router)
router.include_router(lessons_router)
