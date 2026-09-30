from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import BCRYPT_MAX_BYTES
from app.schemas.base import ApiResponse, CamelModel


class RegisterRequest(CamelModel):
    username: str = Field(min_length=2, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("password")
    @classmethod
    def _fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError(f"Password must be at most {BCRYPT_MAX_BYTES} bytes.")
        return value


class RegisterData(CamelModel):
    user_id: int
    is_onboarded: bool


class RegisterResponse(ApiResponse[RegisterData]):
    pass


class LoginRequest(CamelModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return value.lower()


class AccessTokenData(CamelModel):
    """The refresh token is never in the body; it is set as an httpOnly cookie."""

    user_id: int
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int  # seconds until the access token expires


class LoginResponse(ApiResponse[AccessTokenData]):
    pass


class RefreshResponse(ApiResponse[AccessTokenData]):
    pass


class Token(BaseModel):
    """OAuth2 password-flow response. Field names are fixed by RFC 6749, so no camelCase."""

    access_token: str
    token_type: str
