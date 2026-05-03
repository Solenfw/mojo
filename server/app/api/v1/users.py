from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.schemas import UserCreate, UserRead
from app.db import models
from app.api.deps import get_db, get_current_user

router = APIRouter()

@router.post("/user", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    username = user_in.username or user_in.email.split("@")[0]
    new_user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        username=username,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
