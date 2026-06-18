from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.db import models
from app.services.mecab_service import MeCabService

router = APIRouter(prefix="/nlp", tags=["nlp"])

mecab_service = MeCabService()


class TokenizeRequest(BaseModel):
    text: str = Field(default="", max_length=5000)


class TokenizeItem(BaseModel):
    word: str
    reading: str
    pos: str


class TokenizeResponse(BaseModel):
    tokens: list[TokenizeItem]


@router.post("/tokenize", response_model=TokenizeResponse)
async def tokenize_text(
    request: TokenizeRequest,
    current_user: models.User = Depends(get_current_user),
):
    del current_user
    try:
        tokens = mecab_service.tokenize_japanese_sentence(request.text)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return {"tokens": tokens}
