from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.api.deps import authenticate_user, get_current_user, get_db
from server.app.core.security import oauth2_scheme
from server.app.core.security import create_access_token, get_password_hash
from server.app.db import models
from server.app.db.schemas import (
    CheckLoginStateRequest,
    CheckLoginStateResponse,
    CheckUserByEmailOrPhoneRequest,
    CheckUserByEmailOrPhoneResponse,
    LoginData,
    LoginRequest,
    LoginResponse,
    MarkUserLoggedInRequest,
    MarkUserLoggedInResponse,
    Token,
    UserCreate,
    UserCreateData,
    UserCreateResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30
BUSINESS_SUCCESS = "LMS-RESP-SUCCESS"
BUSINESS_INVALID = "LMS-RESP-INVALID_INPUT"
BUSINESS_NOT_FOUND = "LMS-RESP-NOT_FOUND"
BUSINESS_UNAUTHORIZED = "LMS-RESP-UNAUTHORIZED"
AUTH_LOGIN_SUCCESS = "LMS-AUTH-LOGIN-SUCCESS"
AUTH_REGISTER_DUPLICATE = "LMS-AUTH-REGISTER-INVALID_INPUT"
AUTH_LOGIN_UNAUTHORIZED = "LMS-AUTH-LOGIN-UNAUTHORIZED"
AUTH_LOGIN_SOFT_DELETE = "LMS-AUTH-LOGIN-SOFT_DELETE"


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


def _refresh_token_for_user(user: models.User) -> str:
    return create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=30),
    )


def _looks_like_password_hash(value: str) -> bool:
    prefixes = ("$2a$", "$2b$", "$2y$", "$argon2")
    return value.startswith(prefixes)


def _normalize_secret_for_storage(value: str) -> str:
    return value if _looks_like_password_hash(value) else get_password_hash(value)


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


def _error_response(*, business_code: str, message: str, errors: list[dict] | None = None) -> dict:
    payload = {
        "success": False,
        "businessCode": business_code,
        "message": message,
        "timestamp": _isoformat(_utcnow()),
    }
    if errors:
        payload["errors"] = errors
    return payload


@router.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.User).where(models.User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_error_response(
                business_code=AUTH_REGISTER_DUPLICATE,
                message="Invalid input data.",
                errors=[{"field": "email", "message": "Email already exists."}],
            ),
        )
    phone_result = await db.execute(select(models.User).where(models.User.phone == user_in.phone))
    existing_phone = phone_result.scalars().first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_error_response(
                business_code=AUTH_REGISTER_DUPLICATE,
                message="Invalid input data.",
                errors=[{"field": "phone", "message": "Phone already exists."}],
            ),
        )

    full_name = user_in.fullName.strip()
    username = full_name or user_in.email.split("@")[0]
    new_user = models.User(
        email=user_in.email,
        username=username,
        full_name=full_name,
        phone=user_in.phone,
        hashed_password=_normalize_secret_for_storage(user_in.passwordHash),
        is_logged_in=False,
        is_onboarded=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "success": True,
        "businessCode": BUSINESS_SUCCESS,
        "message": "Created successfully.",
        "data": UserCreateData(
            userId=new_user.id,
            accountStatus="pending_verification",
            isLoggedIn=False,
        ).model_dump(mode="json"),
        "timestamp": _isoformat(_utcnow()),
    }


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user_lookup = await db.execute(
        select(models.User).where(
            or_(
                models.User.email == payload.emailOrPhone,
                models.User.phone == payload.emailOrPhone,
            )
        )
    )
    existing_user = user_lookup.scalars().first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_response(
                business_code=BUSINESS_NOT_FOUND,
                message="Resource not found.",
                errors=[{"field": "emailOrPhone", "message": "User does not exist."}],
            ),
        )

    user = await authenticate_user(db, payload.emailOrPhone, payload.passwordHash)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_error_response(
                business_code=AUTH_LOGIN_UNAUTHORIZED,
                message="Unauthorized access.",
                errors=[{"field": "passwordHash", "message": "Password does not match."}],
            ),
        )
    token = _token_for_user(user)["access_token"]
    refresh_token = _refresh_token_for_user(user)
    await _mark_user_logged_in(db, user, token=token)
    return {
        "success": True,
        "businessCode": AUTH_LOGIN_SUCCESS,
        "message": "Login completed successfully.",
        "data": LoginData(
            userId=user.id,
            accessToken=token,
            refreshToken=refresh_token,
        ).model_dump(mode="json"),
        "timestamp": _isoformat(_utcnow()),
    }


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
    response = await login(payload, db)
    login_data = response["data"]
    return {
        "access_token": login_data["accessToken"],
        "token_type": "bearer",
    }


@router.post("/check-login-state", response_model=CheckLoginStateResponse)
async def check_login_state(
    payload: CheckLoginStateRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if payload.sessionToken != token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_error_response(
                business_code=BUSINESS_UNAUTHORIZED,
                message="Unauthorized access.",
                errors=[{"field": "sessionToken", "message": "Session token is invalid."}],
            ),
        )
    result = await db.execute(
        select(models.User).where(models.User.session_token == payload.sessionToken)
    )
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_error_response(
                business_code=BUSINESS_UNAUTHORIZED,
                message="Unauthorized access.",
                errors=[{"field": "sessionToken", "message": "Session token is expired or missing."}],
            ),
        )
    if not user.is_logged_in:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_error_response(
                business_code=BUSINESS_UNAUTHORIZED,
                message="Unauthorized access.",
                errors=[{"field": "sessionToken", "message": "User is not logged in."}],
            ),
        )

    return _standard_response(
        business_code=BUSINESS_SUCCESS,
        message="Request completed successfully.",
        data={"loginState": True, "userId": user.id, "redirectScreen": "HOME"},
    )


@router.post("/mark-user-logged-in", response_model=MarkUserLoggedInResponse)
async def mark_user_logged_in(
    payload: MarkUserLoggedInRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if payload.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_error_response(
                business_code=BUSINESS_UNAUTHORIZED,
                message="Unauthorized access.",
                errors=[{"field": "userId", "message": "User does not match access token."}],
            ),
        )
    result = await db.execute(select(models.User).where(models.User.id == payload.userId))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_error_response(
                business_code=BUSINESS_NOT_FOUND,
                message="Resource not found.",
                errors=[{"field": "userId", "message": "User does not exist."}],
            ),
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
        "timestamp": _isoformat(_utcnow()),
    }


@router.post("/check-user-by-email-or-phone", response_model=CheckUserByEmailOrPhoneResponse)
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
