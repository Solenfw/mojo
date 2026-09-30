"""Japanese text utilities (MeCab tokenizer)."""

import anyio
from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.api.errors import unavailable
from app.clients.mecab import MeCabTokenizer
from app.schemas import TokenizeItem, TokenizeRequest, TokenizeResponse

router = APIRouter(prefix="/nlp", tags=["nlp"])
tokenizer = MeCabTokenizer()


@router.post("/tokenize", response_model=TokenizeResponse)
async def tokenize_text(payload: TokenizeRequest, _: CurrentUser) -> TokenizeResponse:
    try:
        tokens = await anyio.to_thread.run_sync(tokenizer.tokenize_japanese_sentence, payload.text)
    except RuntimeError as exc:
        raise unavailable(str(exc)) from None
    return TokenizeResponse(tokens=[TokenizeItem(**token) for token in tokens])
