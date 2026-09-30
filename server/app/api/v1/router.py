"""Every v1 router, mounted under API_PREFIX by app.main.create_app()."""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    courses,
    gamification,
    listening,
    nlp,
    onboarding,
    reading,
    speaking,
    users,
    vocabulary,
    writing,
)

api_router = APIRouter()
for module in (auth, users, onboarding, courses, vocabulary, reading, listening, speaking, writing, gamification, nlp):
    api_router.include_router(module.router)
