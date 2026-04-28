from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models


class LessonGenerator:
    @staticmethod
    async def get_lesson_structure(user: models.User, db: AsyncSession) -> dict:
        """
        Fetches lesson structure based on user's JLPT goal.
        Returns a dict with lesson details for the level.
        """
        # Assume Lesson model has level (e.g., 'N5'), and structure as JSON or fields
        result = await db.execute(
            select(models.Lesson).where(models.Lesson.level == user.jlpt_goal)
        )
        lessons = result.scalars().all()
        return {
            "level": user.jlpt_goal,
            "lessons": [{"id": l.id, "title": l.title, "content": l.content} for l in lessons]
        }
