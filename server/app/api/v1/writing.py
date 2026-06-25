# server/app/api/v1/writing.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db import models
from app.services.vision_service import VisionService
from app.services.gamification_engine import GamificationEngine
from server.app.db.schemas import EvaluateWritingRequest, EvaluateWritingResponse

router = APIRouter(prefix="/writing", tags=["writing"])
vision_service = VisionService()

@router.post("/evaluate", response_model=EvaluateWritingResponse)
async def evaluate_writing(
    payload: EvaluateWritingRequest,
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Evaluates base64 canvas drawing and awards XP for practice."""
    # Strip the data URL prefix if sent from frontend canvas
    b64_data = payload.image_base64
    if "," in b64_data:
        b64_data = b64_data.split(",")[1]

    # Call Gemini Vision
    evaluation = vision_service.evaluate_kanji(b64_data, payload.target_kanji)
    
    score = evaluation.get("score", 70)
    feedback = evaluation.get("feedback", "Good effort.")
    
    # Award Gamification XP
    xp_awarded = 0
    if score >= 60:
        xp_awarded = 15  # Base reward
        if score >= 90:
            xp_awarded += 10  # Bonus for high accuracy
            
        await GamificationEngine.add_xp(current_user, xp_awarded, db)
        await GamificationEngine.update_streak(current_user, db)

    return EvaluateWritingResponse(
        score=score,
        feedback=feedback,
        xp_awarded=xp_awarded
    )