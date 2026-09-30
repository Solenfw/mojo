from __future__ import annotations

from app.schemas.base import ApiResponse, CamelModel


class GamificationStatusData(CamelModel):
    xp: int
    hearts: int
    streak: int
    gems: int


class GamificationStatusResponse(ApiResponse[GamificationStatusData]):
    pass
