"""
Sign-up, sign-in, token refresh and sign-out.

The access token goes in the response body (clients keep it in memory and send it as a Bearer
header). The refresh token only ever travels in an httpOnly cookie scoped to this router's path.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DbSession
from app.api.errors import (
    AUTH_LOGIN_UNAUTHORIZED,
    AUTH_REGISTER_DUPLICATE,
    AUTH_SESSION_INVALID,
    ApiError,
    unauthorized,
)
from app.api.v1 import API_PREFIX
from app.core.config import settings
from app.schemas import (
    AccessTokenData,
    ErrorDetail,
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    RefreshResponse,
    RegisterData,
    RegisterRequest,
    RegisterResponse,
    Token,
)
from app.services import auth as auth_service
from app.services.auth import (
    DuplicateAccountError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    IssuedTokens,
)

router = APIRouter(prefix="/auth", tags=["auth"])

AUTH_LOGIN_SUCCESS = "LMS-AUTH-LOGIN-SUCCESS"
REFRESH_COOKIE = "mojo_refresh"
REFRESH_COOKIE_PATH = f"{API_PREFIX}/auth"

UNAUTHORIZED_RESPONSE: dict[int | str, dict[str, Any]] = {status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse}}
RefreshCookie = Annotated[str | None, Cookie(alias=REFRESH_COOKIE, include_in_schema=False)]


def _set_refresh_cookie(response: Response, tokens: IssuedTokens) -> None:
    if tokens.refresh_token is None:
        return
    response.set_cookie(
        REFRESH_COOKIE,
        tokens.refresh_token,
        expires=tokens.refresh_expires_at,
        path=REFRESH_COOKIE_PATH,
        secure=settings.refresh_cookie_secure,
        httponly=True,
        samesite=settings.refresh_cookie_samesite,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        REFRESH_COOKIE,
        path=REFRESH_COOKIE_PATH,
        secure=settings.refresh_cookie_secure,
        httponly=True,
        samesite=settings.refresh_cookie_samesite,
    )


def _session_ended() -> ApiError:
    error = unauthorized("Session has ended. Please sign in again.", AUTH_SESSION_INVALID)
    cleared = Response()
    _clear_refresh_cookie(cleared)
    error.headers = {**(error.headers or {}), "set-cookie": cleared.headers["set-cookie"]}
    return error


def _token_data(tokens: IssuedTokens) -> AccessTokenData:
    return AccessTokenData(user_id=tokens.user_id, access_token=tokens.access_token, expires_in=tokens.expires_in)


async def _sign_in(db: DbSession, request: Request, response: Response, *, email: str, password: str) -> IssuedTokens:
    try:
        user = await auth_service.authenticate(db, email=email, password=password)
    except InvalidCredentialsError:
        raise unauthorized("Incorrect email or password.", AUTH_LOGIN_UNAUTHORIZED) from None
    tokens = await auth_service.start_session(db, user, user_agent=request.headers.get("user-agent"))
    _set_refresh_cookie(response, tokens)
    return tokens


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"model": ErrorResponse}},
)
async def register(payload: RegisterRequest, db: DbSession) -> RegisterResponse:
    try:
        user = await auth_service.register_user(
            db,
            username=payload.username,
            full_name=payload.full_name.strip(),
            email=payload.email,
            password=payload.password,
        )
    except DuplicateAccountError as exc:
        raise ApiError(
            status.HTTP_409_CONFLICT,
            AUTH_REGISTER_DUPLICATE,
            "Invalid input data.",
            errors=[ErrorDetail(field=field, message=f"{field.capitalize()} already exists.") for field in exc.fields],
        ) from None
    return RegisterResponse(
        message="Created successfully.",
        data=RegisterData(user_id=user.id, is_onboarded=user.is_onboarded),
    )


@router.post("/login", response_model=LoginResponse, responses=UNAUTHORIZED_RESPONSE)
async def login(payload: LoginRequest, db: DbSession, request: Request, response: Response) -> LoginResponse:
    tokens = await _sign_in(db, request, response, email=payload.email, password=payload.password)
    return LoginResponse(
        business_code=AUTH_LOGIN_SUCCESS,
        message="Login completed successfully.",
        data=_token_data(tokens),
    )


@router.post("/token", response_model=Token, include_in_schema=False)
async def login_oauth2_form(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
    request: Request,
    response: Response,
) -> Token:
    """OAuth2 password flow for Swagger's Authorize button. `username` is the email."""
    tokens = await _sign_in(db, request, response, email=form.username.lower(), password=form.password)
    return Token(access_token=tokens.access_token, token_type="bearer")


@router.post("/refresh", response_model=RefreshResponse, responses=UNAUTHORIZED_RESPONSE)
async def refresh(db: DbSession, response: Response, refresh_token: RefreshCookie = None) -> RefreshResponse:
    if not refresh_token:
        raise _session_ended()
    try:
        tokens = await auth_service.refresh_session(db, refresh_token)
    except InvalidRefreshTokenError:
        raise _session_ended() from None
    _set_refresh_cookie(response, tokens)
    return RefreshResponse(data=_token_data(tokens))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(db: DbSession, refresh_token: RefreshCookie = None) -> Response:
    """Ends this device's session. Idempotent: succeeds even if already signed out."""
    if refresh_token:
        await auth_service.revoke_session(db, refresh_token)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_refresh_cookie(response)
    return response
