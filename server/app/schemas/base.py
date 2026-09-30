"""
Shared building blocks of the API contract.

Conventions:
- Python fields are snake_case; JSON on the wire is camelCase (see CamelModel).
- The acting user always comes from the access token, never from the request body.
- Scores, XP and levels are computed by the server, never accepted from the client.
- Enveloped responses subclass ApiResponse[<Data>] so each gets its own schema name.
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

BUSINESS_SUCCESS = "LMS-RESP-SUCCESS"


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        serialize_by_alias=True,
        from_attributes=True,
        # Responses always emit defaulted fields, so the generated client types mark them non-optional.
        json_schema_serialization_defaults_required=True,
    )


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ApiResponse[DataT](CamelModel):
    success: bool = True
    business_code: str = BUSINESS_SUCCESS
    message: str = "Request completed successfully."
    data: DataT
    timestamp: datetime = Field(default_factory=_utcnow)


class ErrorDetail(CamelModel):
    field: str
    message: str


class ErrorResponse(CamelModel):
    success: bool = False
    business_code: str
    message: str
    errors: list[ErrorDetail] = []
    timestamp: datetime = Field(default_factory=_utcnow)
