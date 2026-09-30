"""NLP utility (MeCab tokenizer)."""

from __future__ import annotations

from pydantic import Field

from app.schemas.base import CamelModel


class TokenizeRequest(CamelModel):
    text: str = Field(default="", max_length=5000)


class TokenizeItem(CamelModel):
    word: str
    reading: str
    pos: str


class TokenizeResponse(CamelModel):
    tokens: list[TokenizeItem]
