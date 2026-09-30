import pytest
from sqlalchemy import func, select

from app.models import LearnerProfile, User

pytestmark = pytest.mark.anyio

ONBOARDING = "/api/v1/onboarding"
ME = "/api/v1/users/me"

ANSWERS = {"studyReason": "anime_manga", "targetLevel": "N3", "dailyStudyMinutes": 20}


async def signed_in(api) -> dict[str, str]:
    await api.post(
        "/api/v1/auth/register",
        json={
            "username": "alexj",
            "fullName": "Alex Johnson",
            "email": "alex@example.com",
            "password": "correct-horse",
        },
    )
    login = await api.post("/api/v1/auth/login", json={"email": "alex@example.com", "password": "correct-horse"})
    return {"Authorization": f"Bearer {login.json()['data']['accessToken']}"}


async def test_onboarding_requires_a_signed_in_user(api):
    response = await api.post(ONBOARDING, json=ANSWERS)

    assert response.status_code == 401


async def test_onboarding_saves_answers_and_marks_user_onboarded(api, session_factory):
    headers = await signed_in(api)

    response = await api.post(ONBOARDING, json=ANSWERS, headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert {key: data[key] for key in ANSWERS} == ANSWERS
    assert data["isOnboarded"] is True
    assert data["onboardedAt"] is not None
    me = (await api.get(ME, headers=headers)).json()
    assert me["isOnboarded"] is True
    async with session_factory() as db:
        profile = await db.scalar(select(LearnerProfile))
    assert (profile.study_intention, profile.target_level, profile.daily_study_minutes) == ("anime_manga", "N3", 20)


@pytest.mark.parametrize(
    "overrides",
    [
        {"studyReason": "gaming"},
        {"targetLevel": "N5"},
        {"dailyStudyMinutes": 45},
        {"dailyStudyMinutes": None},
    ],
)
async def test_onboarding_rejects_answers_outside_the_choices(api, overrides):
    headers = await signed_in(api)

    response = await api.post(ONBOARDING, json={**ANSWERS, **overrides}, headers=headers)

    assert response.status_code == 422
