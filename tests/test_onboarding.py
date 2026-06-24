import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from server.app.api.v1 import onboarding, users
from server.app.db.schemas import (
    AnalyzeOnboardingDataRequest,
    ConfirmCommitmentRequest,
    CreateOnboardingSessionRequest,
    FinalizeOnboardingSessionRequest,
    MarkUserOnboardedRequest,
    SaveOnboardingAnswerRequest,
)


class DummyResult:
    def __init__(self, value=None, values=None):
        self._value = value
        self._values = values if values is not None else ([] if value is None else [value])

    def scalars(self):
        return self

    def first(self):
        return self._value

    def all(self):
        return self._values


class DummyDB:
    def __init__(self, responses):
        self._responses = list(responses)
        self.added = []
        self.commits = 0
        self.refreshes = 0

    async def execute(self, query):
        return self._responses.pop(0)

    def add(self, value):
        self.added.append(value)

    async def commit(self):
        self.commits += 1

    async def refresh(self, value):
        self.refreshes += 1
        if getattr(value, "id", None) is None:
            value.id = 501 + self.refreshes


def test_create_onboarding_session_returns_dd_payload():
    current_user = SimpleNamespace(id=1001)
    db = DummyDB([DummyResult()])

    response = asyncio.run(
        onboarding.create_onboarding_session(
            CreateOnboardingSessionRequest(userId=1001, sessionToken="session-123"),
            token="session-123",
            current_user=current_user,
            db=db,
        )
    )

    assert response["success"] is True
    assert response["businessCode"] == "LMS-RESP-SUCCESS"
    assert response["message"] == "Created successfully."
    assert response["data"]["sessionId"] >= 502
    assert response["data"]["status"] == "in_progress"


def test_analyze_onboarding_data_returns_dd_payload():
    current_user = SimpleNamespace(id=1001)
    attempt = SimpleNamespace(
        id=5001,
        user_id=1001,
        score=72.5,
        status="submitted",
    )
    db = DummyDB([DummyResult(attempt)])

    response = asyncio.run(
        onboarding.analyze_onboarding_data(
            AnalyzeOnboardingDataRequest(
                answerList=[
                    {"questionCode": "learning_goal", "answerValue": "JLPT N3"},
                    {"questionCode": "time", "answerValue": "30m"},
                ],
                placementAttempt={"attemptId": 5001, "score": 72.5},
            ),
            current_user=current_user,
            db=db,
        )
    )

    assert response["success"] is True
    assert response["businessCode"] == "LMS-RESP-SUCCESS"
    assert response["message"] == "Request completed successfully."
    assert response["data"]["currentLevel"] == "N4"
    assert response["data"]["recommendedLevel"] == "N3"
    assert response["data"]["learningStyle"] == "structured_learning"
    assert response["data"]["studyIntensity"] == "medium"
    assert response["data"]["analysisVersion"] == "v1.0.0"


def test_save_and_load_onboarding_answers_return_dd_payloads():
    current_user = SimpleNamespace(id=1001)
    session = SimpleNamespace(id=2001, user_id=1001, status="in_progress")
    answer = SimpleNamespace(
        id=3001,
        question_code="goal",
        answer_value="business",
        created_at=datetime(2026, 6, 24, tzinfo=timezone.utc),
        updated_at=datetime(2026, 6, 24, 1, tzinfo=timezone.utc),
    )
    save_db = DummyDB([
        DummyResult(session),
        DummyResult(),
    ])
    load_db = DummyDB([
        DummyResult(session),
        DummyResult(values=[answer]),
    ])

    save_response = asyncio.run(
        onboarding.save_onboarding_answer(
            SaveOnboardingAnswerRequest(
                sessionId=2001,
                questionCode="goal",
                answerValue="business",
            ),
            current_user=current_user,
            db=save_db,
        )
    )
    load_response = asyncio.run(
        onboarding.load_onboarding_answers(
            sessionId=2001,
            current_user=current_user,
            db=load_db,
        )
    )

    assert save_response["success"] is True
    assert save_response["data"]["answerId"] >= 502
    assert save_response["data"]["questionCode"] == "goal"
    assert load_response["success"] is True
    assert load_response["data"]["sessionId"] == 2001
    assert load_response["data"]["answers"][0]["questionCode"] == "goal"
    assert load_response["data"]["answers"][0]["answerValue"] == "business"


def test_finalize_and_confirm_commitment_return_dd_payloads():
    current_user = SimpleNamespace(id=1001)
    session = SimpleNamespace(
        id=2001,
        user_id=1001,
        status="in_progress",
        completed_at=None,
        result_level=None,
        result_goal=None,
    )
    answers = [
        SimpleNamespace(question_code="starting_level", answer_value="N5"),
        SimpleNamespace(question_code="goal", answer_value="travel"),
    ]
    db = DummyDB([
        DummyResult(session),
        DummyResult(values=answers),
    ])

    finalize_response = asyncio.run(
        onboarding.finalize_onboarding_session(
            FinalizeOnboardingSessionRequest(sessionId=2001, sessionToken="session-123"),
            token="session-123",
            current_user=current_user,
            db=db,
        )
    )
    confirm_response = asyncio.run(
        onboarding.confirm_commitment(
            ConfirmCommitmentRequest(sessionToken="session-123"),
            token="session-123",
            current_user=current_user,
        )
    )

    assert finalize_response["success"] is True
    assert finalize_response["data"]["sessionId"] == 2001
    assert finalize_response["data"]["status"] == "completed"
    assert confirm_response["businessCode"] == "LMS-RESP-SUCCESS"
    assert confirm_response["data"]["loginState"] is True
    assert confirm_response["data"]["redirectScreen"] == "HOME"


def test_mark_user_onboarded_returns_dd_payload():
    current_user = SimpleNamespace(
        id=1001,
        session_token="session-123",
        is_onboarded=False,
        onboarded_at=None,
        updated_at=None,
    )
    db = DummyDB([])

    response = asyncio.run(
        users.mark_user_onboarded(
            MarkUserOnboardedRequest(userId=1001, sessionToken="session-123"),
            token="session-123",
            current_user=current_user,
            db=db,
        )
    )

    assert response["success"] is True
    assert response["businessCode"] == "LMS-RESP-SUCCESS"
    assert response["data"]["userId"] == 1001
    assert response["data"]["isOnboarded"] is True
    assert response["timestamp"]
    assert db.commits == 1
