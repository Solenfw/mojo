from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db import models
from app.services.audio_service import AudioService
from server.app.db.schemas import GetExercisesResponse, SpeakingExerciseItem, EvaluateSpeakingRequest, EvaluateSpeakingResponse, GenerateKaiwaRequest, GenerateKaiwaResponse, SaveSpeakingAttemptRequest, SaveSpeakingAttemptResponse  

router = APIRouter(prefix="/speaking", tags=["speaking"])
audio_service = AudioService()

@router.get("/exercises/{lesson_id}", response_model=GetExercisesResponse)
async def get_speaking_exercises(
    lesson_id: int,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve speech exercises linked to a specific lesson."""
    del current_user
    stmt = select(models.Exercises).where(
        models.Exercises.lesson_id == lesson_id,
        models.Exercises.exercise_type == "speaking"
    )
    res = await db.execute(stmt)
    exercises = res.scalars().all()
    
    return {
        "exercises": [
            SpeakingExerciseItem(
                id=ex.id,
                prompt=ex.prompt,
                correct_answer=ex.correct_answer or "",
                explanation=ex.explanation
            ) for ex in exercises
        ]
    }


@router.post("/evaluate", response_model=EvaluateSpeakingResponse)
async def evaluate_speaking_submission(
    payload: EvaluateSpeakingRequest,
    current_user: models.User = Depends(get_current_user)
):
    """Pass user transcript to AI speech analyzer for scoring."""
    del current_user
    evaluation = audio_service.evaluate_pronunciation(payload.transcript, payload.expected_text)
    return EvaluateSpeakingResponse(
        accuracy_score=evaluation.get("accuracy_score", 80),
        fluency_score=evaluation.get("fluency_score", 80),
        feedback=evaluation.get("feedback", ""),
        tips=evaluation.get("tips", [])
    )


@router.post("/chat", response_model=GenerateKaiwaResponse)
async def generate_kaiwa_turn(
    payload: GenerateKaiwaRequest,
    current_user: models.User = Depends(get_current_user)
):
    """Submit dialogue history to receive the next conversational turn."""
    del current_user
    # Convert Pydantic objects to native dictionary
    history_list = [{"role": m.role, "content": m.content} for m in payload.history]
    reply = audio_service.generate_kaiwa_response(history_list)
    return GenerateKaiwaResponse(
        content=reply.get("content", ""),
        romaji=reply.get("romaji", ""),
        translation=reply.get("translation", "")
    )


@router.post("/attempt", response_model=SaveSpeakingAttemptResponse, status_code=status.HTTP_201_CREATED)
async def save_speaking_attempt(
    payload: SaveSpeakingAttemptRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Commit the speak score and performance feedback to the student progress database."""
    attempt = models.ExerciseAttempts(
        user_id=current_user.id,
        exercise_id=payload.exercise_id,
        answer_text=payload.answer_text,
        is_correct=payload.score >= 70,  # considered correct if above 70%
        score=payload.score,
        ai_feedback=payload.feedback,
        duration_seconds=payload.duration_seconds
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    
    return SaveSpeakingAttemptResponse(attempt_id=attempt.id, success=True)