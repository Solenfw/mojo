from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt.exceptions as JWTError
from app.core.security import decode_access_token
from app.db import models
from app.db.database import async_session
from app.db.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")
   

def get_db() -> AsyncGenerator[AsyncSession, None]: # type: ignore
   with async_session() as session:
      yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=int(user_id))
    except (JWTError, ValueError):
        raise credentials_exception

    result = await db.execute(select(models.User).where(models.User.id == token_data.id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not getattr(current_user, "is_active", True) or not getattr(current_user, "is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have enough privileges",
        )
    return current_user
