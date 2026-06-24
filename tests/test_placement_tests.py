import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from server.app.api.v1 import placement_tests
from server.app.db import schemas as db_schemas
from server.app.db.schemas import (
    CreateTestAttemptRequest,
    GetQuestionOptionsRequest,
    SaveTestAttemptAnswersRequest,
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
            value.id = 700 + self.refreshes


def test_get_placement_test_by_type_returns_dd_payload():
    test = SimpleNamespace(
        id=11,
        code="PLACEMENT-N5",
        title="Placement Test N5",
        test_type="placement",
        total_score=Decimal("100"),
        duration_minutes=30,
        status="active",
    )
    db = DummyDB([DummyResult(test)])

    response = asyncio.run(
        placement_tests.get_placement_test_by_type(
            testType="placement",
            db=db,
        )
    )

    assert response["success"] is True
    assert response["businessCode"] == "LMS-RESP-SUCCESS"
    assert response["data"]["testId"] == 11
    assert response["data"]["testType"] == "placement"


def test_get_questions_and_options_return_dd_payloads():
    questions = [
        SimpleNamespace(
            id=101,
            question_text="Kana for a",
            question_type="multiple_choice",
            score_weight=Decimal("2"),
            sort_order=1,
        )
    ]
    options = [
        SimpleNamespace(id=201, question_id=101, option_text="あ"),
        SimpleNamespace(id=202, question_id=101, option_text="い"),
    ]
    question_db = DummyDB([DummyResult(values=questions)])
    option_db = DummyDB([DummyResult(values=options)])

    question_response = asyncio.run(
        placement_tests.get_questions_by_test_id(
            testId=11,
            db=question_db,
        )
    )
    option_response = asyncio.run(
        placement_tests.get_options_by_question_ids(
            GetQuestionOptionsRequest(questionIds=[101]),
            db=option_db,
        )
    )

    assert question_response["success"] is True
    assert question_response["data"][0]["questionId"] == 101
    assert option_response["success"] is True
    assert len(option_response["data"]) == 2
    assert option_response["data"][0]["questionId"] == 101


def test_create_test_attempt_returns_dd_payload():
    current_user = SimpleNamespace(id=1001)
    test = SimpleNamespace(id=11)
    db = DummyDB([DummyResult(test)])

    response = asyncio.run(
        placement_tests.create_test_attempt(
            CreateTestAttemptRequest(testId=11, userId=1001),
            current_user=current_user,
            db=db,
        )
    )

    assert response["success"] is True
    assert response["data"]["attemptId"] >= 701
    assert response["data"]["status"] == "in_progress"
    assert db.commits == 1


def test_save_answers_and_load_latest_attempt_return_dd_payloads():
    current_user = SimpleNamespace(id=1001)
    attempt = SimpleNamespace(
        id=301,
        user_id=1001,
        test_id=11,
        submitted_at=None,
        started_at=datetime(2026, 6, 24, tzinfo=timezone.utc),
        score=None,
        level_estimate=None,
        status="in_progress",
    )
    questions = [
        SimpleNamespace(id=101, correct_answer="あ", score_weight=Decimal("2")),
        SimpleNamespace(id=102, correct_answer="い", score_weight=Decimal("2")),
    ]
    save_db = DummyDB([
        DummyResult(attempt),
        DummyResult(values=questions),
    ])
    latest_db = DummyDB([DummyResult(attempt)])

    save_response = asyncio.run(
        placement_tests.save_test_attempt_answers(
            SaveTestAttemptAnswersRequest(
                attemptId=301,
                answers=[
                    db_schemas.TestAttemptAnswerSubmission(questionId=101, answerText="あ"),
                    db_schemas.TestAttemptAnswerSubmission(questionId=102, answerText="う"),
                ],
            ),
            current_user=current_user,
            db=save_db,
        )
    )
    latest_response = asyncio.run(
        placement_tests.load_latest_test_attempt_by_user_id(
            current_user=current_user,
            db=latest_db,
        )
    )

    assert save_response["success"] is True
    assert save_response["data"]["attemptId"] == 301
    assert save_response["data"]["status"] == "submitted"
    assert save_response["data"]["score"] == 50.0
    assert save_response["data"]["levelEstimate"] == "N4"
    assert len(save_db.added) == 2
    assert latest_response["success"] is True
    assert latest_response["data"]["attemptId"] == 301
    assert latest_response["data"]["score"] == 50.0
