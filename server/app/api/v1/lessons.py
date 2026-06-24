# server/app/api/v1/lessons.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.v1.users import get_current_user
from app.db import models
from app.services.gamification_engine import GamificationEngine
from app.db.schemas import (
    ReadingLessonResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    LessonResult
)

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{lesson_id}/reading", response_model=ReadingLessonResponse)
async def get_reading_lesson(
    lesson_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve reading text, multiple choice questions, and highlightable vocabulary."""
    lesson = await db.scalar(select(models.Lessons).where(models.Lessons.id == lesson_id))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    passage_stmt = (
        select(models.ReadingPassages)
        .where(models.ReadingPassages.lesson_id == lesson_id)
        .order_by(models.ReadingPassages.sort_order, models.ReadingPassages.id)
    )
    passages = (await db.scalars(passage_stmt)).all()

    ex_stmt = select(models.Exercises).where(
        models.Exercises.lesson_id == lesson_id,
        models.Exercises.exercise_type.in_([
            "reading_comprehension",
            "reading_multiple_choice",
            "reading_true_false",
        ])
    ).order_by(models.Exercises.id)
    exercises = (await db.scalars(ex_stmt)).all()

    questions = []
    for ex in exercises:
        opt_stmt = (
            select(models.ExerciseOptions)
            .where(models.ExerciseOptions.exercise_id == ex.id)
            .order_by(models.ExerciseOptions.id)
        )
        options = (await db.scalars(opt_stmt)).all()
        if not options:
            continue
        questions.append({
            "id": ex.id,
            "prompt": ex.prompt,
            "options": [{"id": o.id, "text": o.option_text} for o in options]
        })

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

    content = "\n\n".join(p.content_japanese for p in passages) if passages else lesson.content

    return {
        "id": lesson.id,
        "title": lesson.title,
        "content": content or "",
        "difficulty": lesson.difficulty or "N5",
        "passages": [
            {
                "id": p.id,
                "title": p.title,
                "japanese": p.content_japanese,
                "vietnamese": p.content_vietnamese,
            }
            for p in passages
        ],
        "questions": questions,
        "words": words
    }

@router.post("/{lesson_id}/reading/submit", response_model=QuizSubmitResponse)
async def submit_reading_quiz(
    lesson_id: int,
    payload: QuizSubmitRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Grade reading comprehension quiz, save attempts, and award Gamification XP."""
    total_score = 0
    max_score = 0

    async with db.begin():
        for exercise_id, selected_option_id in payload.answers.items():
            ex = await db.scalar(select(models.Exercises).where(models.Exercises.id == exercise_id))
            if not ex:
                continue
            
            opt = await db.scalar(select(models.ExerciseOptions).where(models.ExerciseOptions.id == selected_option_id))
            is_correct = opt.is_correct if opt else False
            
            weight = int(ex.score_weight or 10)
            max_score += weight
            if is_correct:
                total_score += weight

            # Save the attempt
            attempt = models.ExerciseAttempts(
                user_id=current_user.id,
                exercise_id=exercise_id,
                answer_text=opt.option_text if opt else "",
                is_correct=is_correct,
                score=weight if is_correct else 0
            )
            db.add(attempt)

        # Calculate pass/fail and award XP
        is_passed = total_score >= (max_score * 0.7) if max_score > 0 else True
        xp_gained = total_score * 2  # 2 XP per point
        
        if xp_gained > 0:
            await GamificationEngine.add_xp(current_user, xp_gained, db)
            await GamificationEngine.update_streak(current_user, db)

    return {
        "score": total_score,
        "max_score": max_score,
        "xp_gained": xp_gained,
        "is_passed": is_passed
    }

# Keep original lesson complete endpoint
@router.post("/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: int,
    result: LessonResult,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        await GamificationEngine.add_xp(current_user, result.xp_gained, db)
        await GamificationEngine.update_streak(current_user, db)
        
        for vocab_id in result.vocab_learned:
            existing = await db.scalar(
                select(models.UserVocabulary).where(
                    models.UserVocabulary.user_id == current_user.id,
                    models.UserVocabulary.vocab_id == vocab_id,
                )
            )
            if not existing:
                new_uv = models.UserVocabulary(
                    user_id=current_user.id,
                    vocab_id=vocab_id,
                    ease_factor=2.5,
                    interval=1,
                    repetitions=0,
                    next_review_date=None,
                )
                db.add(new_uv)
                
    return {
        "xp_gained": result.xp_gained,
        "streak": getattr(current_user, "streak", 0)
    }
