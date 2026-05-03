from app.api.deps import get_db, authenticate_user
from app.core.security import create_access_token
from app.db.schemas import Token, LoginRequest

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30),  # Token expires in 30 minutes
    )
    return {"access_token": access_token, "token_type": "bearer"}