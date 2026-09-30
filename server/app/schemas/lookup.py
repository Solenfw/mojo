from __future__ import annotations

from typing import Literal

from app.schemas.base import ApiResponse, CamelModel

SkillCode = Literal["vocab", "reading", "speaking", "writing", "listening"]  # Skill.code values


class ProficiencyLevelRead(CamelModel):
    id: int
    name: str
    sort_order: int


class ProficiencyLevelListResponse(ApiResponse[list[ProficiencyLevelRead]]):
    pass
