from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_superuser
from app.db import models

router = APIRouter()


@router.get("/admin/users")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    current_user: models.User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * page_size
    result = await db.execute(
        select(models.User).order_by(models.User.id).offset(offset).limit(page_size)
    )
    users = result.scalars().all()
    return {
        "page": page,
        "page_size": page_size,
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": getattr(user, "is_active", True),
                "is_superuser": getattr(user, "is_superuser", False),
            }
            for user in users
        ],
    }


@router.put("/admin/users/{user_id}/status")
async def toggle_user_status(
    user_id: int,
    current_user: models.User = Depends(get_current_active_superuser),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_active = not getattr(user, "is_active", True)
    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
    }
