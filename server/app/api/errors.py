from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.schemas import ErrorDetail, ErrorResponse

BUSINESS_INVALID = "LMS-RESP-INVALID_INPUT"
BUSINESS_UNAUTHORIZED = "LMS-RESP-UNAUTHORIZED"
BUSINESS_NOT_FOUND = "LMS-RESP-NOT_FOUND"
BUSINESS_UNAVAILABLE = "LMS-RESP-UNAVAILABLE"
AUTH_REGISTER_DUPLICATE = "LMS-AUTH-REGISTER-INVALID_INPUT"
AUTH_LOGIN_UNAUTHORIZED = "LMS-AUTH-LOGIN-UNAUTHORIZED"
AUTH_SESSION_INVALID = "LMS-AUTH-SESSION-INVALID"


class ApiError(Exception):
    """Raise from routes or services; rendered as an ErrorResponse body."""

    def __init__(
        self,
        status_code: int,
        business_code: str,
        message: str,
        *,
        errors: list[ErrorDetail] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.business_code = business_code
        self.message = message
        self.errors = errors or []
        self.headers = headers


def unauthorized(message: str = "Unauthorized access.", business_code: str = BUSINESS_UNAUTHORIZED) -> ApiError:
    return ApiError(
        status.HTTP_401_UNAUTHORIZED,
        business_code,
        message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def not_found(message: str = "Resource not found.") -> ApiError:
    return ApiError(status.HTTP_404_NOT_FOUND, BUSINESS_NOT_FOUND, message)


def invalid(message: str, errors: list[ErrorDetail] | None = None) -> ApiError:
    return ApiError(status.HTTP_400_BAD_REQUEST, BUSINESS_INVALID, message, errors=errors)


def unavailable(message: str) -> ApiError:
    return ApiError(status.HTTP_503_SERVICE_UNAVAILABLE, BUSINESS_UNAVAILABLE, message)


async def _handle_api_error(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ApiError)
    body = ErrorResponse(business_code=exc.business_code, message=exc.message, errors=exc.errors)
    return JSONResponse(body.model_dump(mode="json"), status_code=exc.status_code, headers=exc.headers)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, _handle_api_error)
