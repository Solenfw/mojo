from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.v1.users import get_current_user
from app.db import models
from app.services.gamification_engine import GamificationEngine

router = APIRouter()


class LessonResult(BaseModel):
    xp_gained: int
    vocab_learned: list[int]  # List of vocab_ids


@router.get("/lessons/path")
async def get_learning_path(
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Assume PathNode model or something; for now, return based on progress
    # Mock: return nodes up to current_progress
    nodes = [
        {"id": 1, "title": "Hiragana", "unlocked": current_user.current_progress >= 1},
        {"id": 2, "title": "Katakana", "unlocked": current_user.current_progress >= 2},
        # etc.
    ]
    return {"path": nodes}


@router.post("/lessons/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: int,
    result: LessonResult,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Use transaction for rollback
    async with db.begin():
        # a) Add XP and update streak
        await GamificationEngine.add_xp(current_user, result.xp_gained, db)
        await GamificationEngine.update_streak(current_user, db)

        # b) Add vocab to SRS
        for vocab_id in result.vocab_learned:
            # Check if already exists
            existing = await db.execute(
                select(models.UserVocabulary).where(
                    models.UserVocabulary.user_id == current_user.id,
                    models.UserVocabulary.vocab_id == vocab_id,
                )
            )
            if not existing.scalars().first():
                new_uv = models.UserVocabulary(
                    user_id=current_user.id,
                    vocab_id=vocab_id,
                    ease_factor=2.5,
                    interval=1,
                    repetitions=0,
                    next_review_date=None,  # Will be set on first review
                )
                db.add(new_uv)

        # c) Update progress
        current_user.current_progress += 1
        await db.commit()

    # Get updated streak
    streak = current_user.streak
    unlocked_nodes = current_user.current_progress  # Or calculate properly

    return {
        "xp_gained": result.xp_gained,
        "streak": streak,
        "unlocked_nodes": unlocked_nodes,
    }
