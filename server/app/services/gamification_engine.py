from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models


class GamificationEngine:
    MAX_HEARTS = 5
    HEART_REGENERATION_RATE = timedelta(hours=4)  # 1 heart per 4 hours

    @staticmethod
    async def add_xp(user: models.User, amount: int, db: AsyncSession):
        user.xp += amount
        await db.commit()

    @staticmethod
    async def update_streak(user: models.User, db: AsyncSession):
        today = datetime.utcnow().date()
        if user.last_activity_date:
            if user.last_activity_date == today - timedelta(days=1):
                user.streak += 1
            elif user.last_activity_date < today - timedelta(days=1):
                user.streak = 1
        else:
            user.streak = 1
        user.last_activity_date = today
        await db.commit()

    @staticmethod
    async def deduct_heart(user: models.User, db: AsyncSession) -> bool:
        if user.role == "B2B":  # Unlimited hearts
            return True
        if user.hearts > 0:
            user.hearts -= 1
            await db.commit()
            return True
        return False

    @staticmethod
    async def regenerate_hearts(user: models.User, db: AsyncSession):
        if user.role == "B2B":
            user.hearts = GamificationEngine.MAX_HEARTS
        else:
            now = datetime.utcnow()
            if user.hearts_last_updated:
                elapsed = now - user.hearts_last_updated
                hearts_to_add = elapsed // GamificationEngine.HEART_REGENERATION_RATE
                if hearts_to_add > 0:
                    user.hearts = min(user.hearts + hearts_to_add, GamificationEngine.MAX_HEARTS)
                    user.hearts_last_updated = now
                    await db.commit()
            else:
                user.hearts_last_updated = now
                await db.commit()
