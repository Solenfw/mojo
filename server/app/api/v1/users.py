from fastapi import APIRouter, Depends

from app.db.schemas import UserRead
from app.db import models
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
