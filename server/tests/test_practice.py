from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.api.v1 import speaking, writing
from app.models import (
    Course,
    Dialogue,
    DialogueExchange,
    KanjiPractice,
    Lesson,
    ProficiencyLevel,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionOption,
    User,
    Vocabulary,
    VocabularyReview,
)
from app.services.srs import schedule_next

pytestmark = pytest.mark.anyio


@pytest.fixture
async def headers(api) -> dict[str, str]:
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


@pytest.fixture
async def lesson(session_factory) -> dict[str, int]:
    """One lesson with a two-question reading passage, a word, a dialogue and a kanji practice."""
    async with session_factory() as db:
        level = ProficiencyLevel(name="Beginner", sort_order=1)
        course = Course(title="Basics", level=level, sort_order=1)
        lesson = Lesson(course=course, title="Greetings", sort_order=1)
        passage = ReadingPassage(lesson=lesson, title="At the station", content_japanese="駅です。", xp_reward=10)
        q1 = ReadingQuestion(passage=passage, question_text="Where?", sort_order=1)
        q2 = ReadingQuestion(passage=passage, question_text="When?", sort_order=2)
        q1_right = ReadingQuestionOption(question=q1, option_text="Station", is_correct=True)
        q1_wrong = ReadingQuestionOption(question=q1, option_text="School", is_correct=False)
        q2_right = ReadingQuestionOption(question=q2, option_text="Morning", is_correct=True)
        word = Vocabulary(lesson=lesson, kana="えき", romaji="eki", meaning="station", xp_reward=5)
        dialogue = Dialogue(lesson=lesson, title="Buying a ticket", xp_reward=15)
        line = DialogueExchange(
            dialogue=dialogue, order_index=1, speaker="A", ja_text="きっぷ", ja_romaji="kippu", en_text="ticket"
        )
        kanji = KanjiPractice(lesson=lesson, title="Station", kanji="駅", xp_reward=10)
        db.add_all([level, course, lesson, passage, q1, q2, q1_right, q1_wrong, q2_right, word, dialogue, line, kanji])
        await db.commit()
        return {
            "level": level.id,
            "course": course.id,
            "lesson": lesson.id,
            "passage": passage.id,
            "q1": q1.id,
            "q2": q2.id,
            "q1_right": q1_right.id,
            "q1_wrong": q1_wrong.id,
            "q2_right": q2_right.id,
            "word": word.id,
            "dialogue": dialogue.id,
            "line": line.id,
            "kanji": kanji.id,
        }


async def current_xp(session_factory) -> int:
    async with session_factory() as db:
        return (await db.scalar(select(User))).xp


# Curriculum


async def test_lesson_detail_lists_its_practices(api, headers, lesson):
    courses = (await api.get("/api/v1/courses", params={"levelId": lesson["level"]}, headers=headers)).json()["data"]
    lessons = (await api.get(f"/api/v1/courses/{lesson['course']}/lessons", headers=headers)).json()["data"]
    detail = (await api.get(f"/api/v1/lessons/{lesson['lesson']}", headers=headers)).json()["data"]

    assert [course["title"] for course in courses] == ["Basics"]
    assert [item["title"] for item in lessons] == ["Greetings"]
    assert detail["vocabularyCount"] == 1
    assert [ref["id"] for ref in detail["readingPassages"]] == [lesson["passage"]]
    assert [ref["id"] for ref in detail["dialogues"]] == [lesson["dialogue"]]
    assert [ref["id"] for ref in detail["kanjiPractices"]] == [lesson["kanji"]]


async def test_missing_lesson_is_404(api, headers):
    response = await api.get("/api/v1/lessons/999", headers=headers)

    assert response.status_code == 404
    assert response.json()["businessCode"] == "LMS-RESP-NOT_FOUND"


# Reading


async def test_passage_never_reveals_correct_answers(api, headers, lesson):
    passage = (await api.get(f"/api/v1/reading/passages/{lesson['passage']}", headers=headers)).json()["data"]

    options = [option for question in passage["questions"] for option in question["options"]]
    assert options and all(set(option) == {"id", "optionText"} for option in options)


async def test_passing_a_passage_awards_xp_only_once(api, headers, lesson, session_factory):
    answers = [
        {"questionId": lesson["q1"], "selectedOptionId": lesson["q1_right"]},
        {"questionId": lesson["q2"], "selectedOptionId": lesson["q2_right"]},
    ]

    first = (
        await api.post(
            "/api/v1/reading/attempts", json={"passageId": lesson["passage"], "answers": answers}, headers=headers
        )
    ).json()["data"]
    second = (
        await api.post(
            "/api/v1/reading/attempts", json={"passageId": lesson["passage"], "answers": answers}, headers=headers
        )
    ).json()["data"]

    assert (first["score"], first["passed"], first["xpEarned"]) == (100.0, True, 10)
    assert (second["passed"], second["xpEarned"]) == (True, 0)
    assert await current_xp(session_factory) == 10


async def test_unanswered_and_foreign_options_count_as_wrong(api, headers, lesson):
    # Answer q2 with q1's correct option and skip q1 entirely.
    answers = [{"questionId": lesson["q2"], "selectedOptionId": lesson["q1_right"]}]

    result = (
        await api.post(
            "/api/v1/reading/attempts", json={"passageId": lesson["passage"], "answers": answers}, headers=headers
        )
    ).json()["data"]

    assert (result["score"], result["passed"], result["xpEarned"]) == (0.0, False, 0)


async def test_answers_to_other_passages_questions_are_rejected(api, headers, lesson):
    answers = [{"questionId": 999, "selectedOptionId": lesson["q1_right"]}]

    response = await api.post(
        "/api/v1/reading/attempts", json={"passageId": lesson["passage"], "answers": answers}, headers=headers
    )

    assert response.status_code == 400


# Vocabulary (SRS)


async def test_reviewing_a_new_card_schedules_it_and_early_reviews_earn_nothing(api, headers, lesson, session_factory):
    first = (
        await api.post(
            "/api/v1/vocabulary/reviews", json={"vocabId": lesson["word"], "result": "good"}, headers=headers
        )
    ).json()["data"]
    early = (
        await api.post(
            "/api/v1/vocabulary/reviews", json={"vocabId": lesson["word"], "result": "good"}, headers=headers
        )
    ).json()["data"]
    queue = (await api.get("/api/v1/vocabulary/review-queue", headers=headers)).json()["data"]

    assert (first["repetitions"], first["intervalDays"], first["xpEarned"]) == (1, 1, 5)
    assert early["xpEarned"] == 0
    assert queue == []  # nothing is due until tomorrow

    async with session_factory() as db:
        review = await db.scalar(select(VocabularyReview))
        review.next_review_at = datetime.now(UTC) - timedelta(minutes=1)
        await db.commit()
    queue = (await api.get("/api/v1/vocabulary/review-queue", headers=headers)).json()["data"]
    assert [card["id"] for card in queue] == [lesson["word"]]


def test_sm2_schedule():
    assert schedule_next(4, 0, 2.5, 0).interval_days == 1
    assert schedule_next(4, 1, 2.5, 1).interval_days == 6
    assert schedule_next(4, 2, 2.5, 6).interval_days == 15
    failed = schedule_next(1, 5, 1.4, 30)
    assert (failed.repetitions, failed.interval_days, failed.ease_factor) == (0, 1, 1.3)


# Speaking and writing (AI stubbed)


async def test_dialogue_is_rated_against_the_scripted_line(api, headers, lesson, monkeypatch):
    seen = []

    def fake_rating(transcript, expected_text, romaji=""):
        seen.append(expected_text)
        return {"score": 90, "feedback": "Clear."}

    monkeypatch.setattr(speaking.audio, "evaluate_pronunciation", fake_rating)
    body = {"dialogueId": lesson["dialogue"], "turns": [{"exchangeId": lesson["line"], "transcript": "きっぷ"}]}

    result = (await api.post("/api/v1/speaking/attempts", json=body, headers=headers)).json()["data"]

    assert seen == ["きっぷ"]
    assert (result["aiScore"], result["xpEarned"]) == (90.0, 15)


async def test_writing_takes_the_target_kanji_from_the_practice(api, headers, lesson, monkeypatch):
    seen = []
    monkeypatch.setattr(
        writing.vision,
        "evaluate_kanji",
        lambda image, kanji: seen.append((image, kanji)) or {"score": "72", "feedback": "Good."},
    )
    body = {"kanjiPracticeId": lesson["kanji"], "imageBase64": "data:image/png;base64,AAAA"}

    result = (await api.post("/api/v1/writing/evaluations", json=body, headers=headers)).json()["data"]

    assert seen == [("AAAA", "駅")]
    assert (result["score"], result["xpEarned"]) == (72, 10)


async def test_writing_reports_an_unavailable_ai(api, headers, lesson, monkeypatch):
    def broken(image, kanji):
        raise RuntimeError("Vision API Call failed: 500")

    monkeypatch.setattr(writing.vision, "evaluate_kanji", broken)
    body = {"kanjiPracticeId": lesson["kanji"], "imageBase64": "AAAA"}

    response = await api.post("/api/v1/writing/evaluations", json=body, headers=headers)

    assert response.status_code == 503
    assert "500" not in response.text  # upstream error details are not leaked


# Dashboard, profile and gamification


async def test_dashboard_reports_logged_xp_by_day_and_skill(api, headers, lesson):
    answers = [
        {"questionId": lesson["q1"], "selectedOptionId": lesson["q1_right"]},
        {"questionId": lesson["q2"], "selectedOptionId": lesson["q2_right"]},
    ]
    await api.post(
        "/api/v1/reading/attempts", json={"passageId": lesson["passage"], "answers": answers}, headers=headers
    )

    data = (await api.get("/api/v1/users/me/dashboard", headers=headers)).json()["data"]

    assert data["user"]["xp"] == 10
    assert data["user"]["streak"] == 1
    assert len(data["activity"]) == 7 and data["activity"][-1]["xp"] == 10
    assert {skill["skill"]: skill["xp"] for skill in data["skills"]} == {
        "vocab": 0,
        "reading": 10,
        "speaking": 0,
        "writing": 0,
        "listening": 0,
    }


async def test_profile_shows_onboarding_answers(api, headers):
    await api.post(
        "/api/v1/onboarding",
        json={"studyReason": "work", "targetLevel": "N2", "dailyStudyMinutes": 30},
        headers=headers,
    )

    profile = (await api.get("/api/v1/users/me/profile", headers=headers)).json()["data"]

    assert (profile["studyIntention"], profile["targetLevel"], profile["dailyStudyMinutes"]) == ("work", "N2", 30)


async def test_gamification_status_is_stable_across_calls(api, headers):
    first = await api.get("/api/v1/gamification/status", headers=headers)
    second = await api.get("/api/v1/gamification/status", headers=headers)  # the old code crashed here

    assert first.status_code == second.status_code == 200
    assert second.json()["data"]["hearts"] == 5


async def test_refilling_full_hearts_is_rejected(api, headers):
    response = await api.post("/api/v1/gamification/hearts/refill", headers=headers)

    assert response.status_code == 400
