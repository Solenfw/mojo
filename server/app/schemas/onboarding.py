"""Onboarding: three questions, answered in one step."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from app.schemas.base import ApiResponse, CamelModel

StudyReason = Literal["travel", "work", "anime_manga", "jlpt", "living_in_japan", "other"]
TargetLevel = Literal["N1", "N2", "N3", "N4"]
DailyStudyMinutes = Literal[10, 20, 30, 60]  # 60 means "60 minutes or more"


class OnboardingRequest(CamelModel):
    study_reason: StudyReason
    target_level: TargetLevel
    daily_study_minutes: DailyStudyMinutes


class OnboardingData(CamelModel):
    user_id: int
    is_onboarded: bool
    study_reason: StudyReason
    target_level: TargetLevel
    daily_study_minutes: DailyStudyMinutes


class OnboardingResponse(ApiResponse[OnboardingData]):
    pass
