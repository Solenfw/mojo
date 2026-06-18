from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import authenticate_user, get_current_user, get_db
from app.core.security import oauth2_scheme
from app.core.security import create_access_token, get_password_hash
from app.db import models
from app.db.schemas import CheckUserByEmailOrPhoneRequest, LoginRequest, Token, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30
BUSINESS_SUCCESS = "LMS-RESP-SUCCESS"
BUSINESS_INVALID = "LMS-RESP-INVALID_INPUT"
BUSINESS_NOT_FOUND = "LMS-RESP-NOT_FOUND"
BUSINESS_UNAUTHORIZED = "LMS-RESP-UNAUTHORIZED"
AUTH_LOGIN_SUCCESS = "LMS-AUTH-LOGIN-SUCCESS"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _token_for_user(user: models.User) -> dict[str, str]:
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def _mark_user_logged_in(
    db: AsyncSession,
    user: models.User,
    *,
    token: str,
) -> None:
    now = _utcnow()
    user.session_token = token
    user.is_logged_in = True
    user.last_login_at = now
    user.updated_at = now.replace(tzinfo=None)
    await db.commit()
    await db.refresh(user)


def _standard_response(*, business_code: str, message: str, data: dict) -> dict:
    return {
        "businessCode": business_code,
        "message": message,
        "timestamp": _isoformat(_utcnow()),
        "data": data,
    }


class CheckLoginStateRequest(BaseModel):
    sessionToken: str = Field(min_length=1)


class MarkUserLoggedInRequest(BaseModel):
    userId: int = Field(gt=0)
    isLoggedIn: bool = True
    lastLoginAt: datetime | None = None


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.User).where(models.User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    if user_in.phone:
        phone_result = await db.execute(select(models.User).where(models.User.phone == user_in.phone))
        existing_phone = phone_result.scalars().first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this phone number already exists.",
            )

    username = user_in.username or (user_in.full_name or "").strip() or user_in.email.split("@")[0]
    new_user = models.User(
        email=user_in.email,
        username=username,
        full_name=user_in.full_name,
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    token = _token_for_user(new_user)
    await _mark_user_logged_in(db, new_user, token=token["access_token"])
    return token


@router.post("/login", response_model=Token)
async def login(
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
    token = _token_for_user(user)
    await _mark_user_logged_in(db, user, token=token["access_token"])
    return token


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, form_data.username, form_data.password) # Note: form_data.username is actually the email in this case
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = _token_for_user(user)
    await _mark_user_logged_in(db, user, token=token["access_token"])
    return token


@router.post("/token", response_model=Token)
async def login_for_access_token(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await login(payload, db)


@router.post("/check-login-state")
async def check_login_state(
    payload: CheckLoginStateRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if payload.sessionToken != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_standard_response(
                business_code=BUSINESS_UNAUTHORIZED,
                message="Unauthorized access.",
                data={"loginState": False, "userId": None, "redirectScreen": "AUTH"},
            ),
        )
    result = await db.execute(
        select(models.User).where(models.User.session_token == payload.sessionToken)
    )
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_standard_response(
                business_code=BUSINESS_NOT_FOUND,
                message="Resource not found.",
                data={"loginState": False, "userId": None, "redirectScreen": "AUTH"},
            ),
        )
    if not user.is_logged_in:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_standard_response(
                business_code=BUSINESS_UNAUTHORIZED,
                message="Unauthorized access.",
                data={"loginState": False, "userId": None, "redirectScreen": "AUTH"},
            ),
        )

    return _standard_response(
        business_code=BUSINESS_SUCCESS,
        message="Request completed successfully.",
        data={"loginState": True, "userId": user.id, "redirectScreen": "HOME"},
    )


@router.post("/mark-user-logged-in")
async def mark_user_logged_in(
    payload: MarkUserLoggedInRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access.",
        )
    result = await db.execute(select(models.User).where(models.User.id == payload.userId))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found.",
        )

    now = payload.lastLoginAt or _utcnow()
    user.is_logged_in = payload.isLoggedIn
    user.last_login_at = now
    user.updated_at = now.replace(tzinfo=None)
    await db.commit()
    await db.refresh(user)

    return {
        "success": True,
        "businessCode": AUTH_LOGIN_SUCCESS,
        "message": "Login completed successfully.",
        "data": {
            "userId": user.id,
            "isLoggedIn": bool(user.is_logged_in),
            "lastLoginAt": _isoformat(user.last_login_at),
            "redirectScreen": "HOME" if user.is_logged_in else "AUTH",
        },
    }


@router.post("/check-user-by-email-or-phone")
async def check_user_by_email_or_phone(
    payload: CheckUserByEmailOrPhoneRequest,
    db: AsyncSession = Depends(get_db),
):
    clauses = []
    if payload.email:
        clauses.append(models.User.email == payload.email)
    if payload.phone:
        clauses.append(models.User.phone == payload.phone)

    result = await db.execute(select(models.User).where(or_(*clauses)))
    user = result.scalars().first()
    if user is None:
        return {
            "success": True,
            "businessCode": BUSINESS_SUCCESS,
            "message": "Request completed successfully.",
            "data": {"existsFlag": False, "userId": None},
            "timestamp": _isoformat(_utcnow()),
        }

    field = "email" if payload.email and user.email == payload.email else "phone"
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "success": False,
            "businessCode": "LMS-AUTH-REGISTER-INVALID_INPUT",
            "message": "Invalid input data.",
            "errors": [
                {
                    "field": field,
                    "message": f"{field.capitalize()} already exists.",
                }
            ],
            "timestamp": _isoformat(_utcnow()),
        },
    )
