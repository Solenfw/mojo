# from fastapi import APIRouter, Depends
# from pydantic import BaseModel

# from app.api.v1.users import get_current_user
# from app.db import models
# from app.services.mecab_service import MeCabService
# from app.services.gpt_service import GPTService

# router = APIRouter()

# mecab_service = MeCabService()
# gpt_service = GPTService()


# class TokenizeRequest(BaseModel):
#     text: str


# class ExplainRequest(BaseModel):
#     sentence: str
#     context: str


# @router.post("/nlp/tokenize")
# async def tokenize_text(
#     request: TokenizeRequest,
#     current_user: models.User = Depends(get_current_user),
# ):
#     tokens = mecab_service.tokenize_japanese_sentence(request.text)
#     return {"tokens": tokens}


# @router.post("/nlp/ai-explain")
# async def explain_grammar(
#     request: ExplainRequest,
#     current_user: models.User = Depends(get_current_user),
# ):
#     explanation = await gpt_service.explain_grammar(request.sentence, request.context)
#     return {"explanation": explanation}
