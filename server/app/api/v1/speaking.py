"""Speaking practice: scripted dialogues rated by AI, per-line pronunciation feedback, and free conversation."""

from datetime import UTC, datetime

import anyio
from fastapi import APIRouter, status
from sqlalchemy import exists, select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.api.errors import invalid, not_found
from app.clients.audio import AudioClient
from app.models import Dialogue, DialogueAttempt
from app.schemas import (
    DialogueRead,
    DialogueResponse,
    GenerateKaiwaRequest,
    GenerateKaiwaResponse,
    RatePronunciationRequest,
    RatePronunciationResponse,
    SubmitDialogueAttemptData,
    SubmitDialogueAttemptRequest,
    SubmitDialogueAttemptResponse,
)
from app.services.gamification import award_xp
from app.services.practice import PASS_MARK, clamp_score

router = APIRouter(prefix="/speaking", tags=["speaking"])
audio = AudioClient()


async def _load_dialogue(db: DbSession, dialogue_id: int) -> Dialogue:
    dialogue = await db.scalar(
        select(Dialogue).where(Dialogue.id == dialogue_id).options(selectinload(Dialogue.exchanges))
    )
    if dialogue is None:
        raise not_found("Dialogue not found.")
    return dialogue


@router.get("/dialogues/{dialogue_id}", response_model=DialogueResponse)
async def get_dialogue(dialogue_id: int, db: DbSession, _: CurrentUser) -> DialogueResponse:
    dialogue = await _load_dialogue(db, dialogue_id)
    return DialogueResponse(data=DialogueRead.model_validate(dialogue))


@router.post("/attempts", response_model=SubmitDialogueAttemptResponse, status_code=status.HTTP_201_CREATED)
async def submit_attempt(
    payload: SubmitDialogueAttemptRequest, db: DbSession, current_user: CurrentUser
) -> SubmitDialogueAttemptResponse:
    """Rates each transcript against the scripted line; the expected text always comes from the dialogue."""
    dialogue = await _load_dialogue(db, payload.dialogue_id)
    exchanges = {exchange.id: exchange for exchange in dialogue.exchanges}
    if any(turn.exchange_id not in exchanges for turn in payload.turns):
        raise invalid("One or more turns refer to lines outside this dialogue.")

    scores, feedback = [], []
    for turn in payload.turns:
        line = exchanges[turn.exchange_id]
        rating = await anyio.to_thread.run_sync(
            audio.evaluate_pronunciation, turn.transcript, line.ja_text, line.ja_romaji
        )
        scores.append(clamp_score(rating.get("score")))
        feedback.append(f"Line {line.order_index}: {rating.get('feedback', '')}")

    score = round(sum(scores) / len(scores), 2)
    already_passed = await db.scalar(
        select(
            exists().where(
                DialogueAttempt.user_id == current_user.id,
                DialogueAttempt.dialogue_id == dialogue.id,
                DialogueAttempt.xp_earned > 0,
            )
        )
    )
    xp = dialogue.xp_reward if score >= PASS_MARK and not already_passed else 0
    now = datetime.now(UTC)

    attempt = DialogueAttempt(
        user_id=current_user.id,
        dialogue_id=dialogue.id,
        ai_score=score,
        ai_feedback="\n".join(feedback),
        xp_earned=xp,
        completed_at=now,
    )
    db.add(attempt)
    await award_xp(db, current_user, skill_code="speaking", xp=xp, now=now)
    await db.commit()

    return SubmitDialogueAttemptResponse(
        data=SubmitDialogueAttemptData(
            attempt_id=attempt.id, ai_score=score, ai_feedback=attempt.ai_feedback or "", xp_earned=xp, completed_at=now
        )
    )


@router.post("/pronunciation", response_model=RatePronunciationResponse)
async def rate_pronunciation(payload: RatePronunciationRequest, _: CurrentUser) -> RatePronunciationResponse:
    """Per-line feedback while practising; earns no XP."""
    rating = await anyio.to_thread.run_sync(
        audio.evaluate_pronunciation, payload.user_transcript, payload.expected_text, payload.romaji
    )
    return RatePronunciationResponse(
        score=clamp_score(rating.get("score")),
        feedback=str(rating.get("feedback", "")),
        is_correct=bool(rating.get("is_correct", False)),
    )


@router.post("/kaiwa", response_model=GenerateKaiwaResponse)
async def kaiwa_turn(payload: GenerateKaiwaRequest, _: CurrentUser) -> GenerateKaiwaResponse:
    """The next line of a free conversation with the AI partner."""
    history = [{"role": item.role, "content": item.content} for item in payload.history]
    reply = await anyio.to_thread.run_sync(audio.generate_kaiwa_response, history)
    return GenerateKaiwaResponse(
        content=str(reply.get("content", "")),
        romaji=str(reply.get("romaji", "")),
        translation=str(reply.get("translation", "")),
    )
