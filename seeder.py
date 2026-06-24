# seeder.py
import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import delete, select

# Add server directory to Python path for seamless imports
ROOT = Path(__file__).resolve().parent
SERVER_DIR = ROOT / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.append(str(SERVER_DIR))

from server.app.core.security import get_password_hash
from server.app.db import models
from server.app.db.database import SessionLocal

READING_SOURCE_DIR = ROOT / "docs" / "json" / "reading"
CHOICE_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TRUE_FALSE_OPTIONS = ("〇", "✕")
TRUE_VALUES = {"〇", "○", "O", "o", "true", "True", "TRUE"}


def _reading_lesson_files() -> list[Path]:
    return sorted(
        READING_SOURCE_DIR.glob("lesson_*.json"),
        key=lambda path: int(path.stem.split("_")[-1]),
    )


def _load_reading_sources() -> list[tuple[Path, dict]]:
    sources = []
    for source_file in _reading_lesson_files():
        with source_file.open(encoding="utf-8") as fh:
            sources.append((source_file, json.load(fh)))
    return sources


def _line_from_item(item: dict, field: str) -> str | None:
    value = item.get(field)
    if not value:
        return None
    speaker = item.get("speaker")
    return f"{speaker}: {value}" if speaker else value


def _flatten_reading_passage(passage: dict) -> tuple[str, str]:
    japanese_lines: list[str] = []
    vietnamese_lines: list[str] = []

    for key, value in passage.items():
        if key in {"id", "title", "vietnamese_title"}:
            continue

        if key == "vietnamese" and isinstance(value, list):
            vietnamese_lines.extend(str(line) for line in value if line)
            continue

        if not isinstance(value, list):
            continue

        for item in value:
            if isinstance(item, str):
                japanese_lines.append(item)
            elif isinstance(item, dict):
                japanese = _line_from_item(item, "japanese")
                vietnamese = _line_from_item(item, "vietnamese")
                if japanese:
                    japanese_lines.append(japanese)
                if vietnamese:
                    vietnamese_lines.append(vietnamese)

    return "\n".join(japanese_lines), "\n".join(vietnamese_lines)


def _reading_lesson_content(source: dict) -> str:
    passages = []
    for passage in source.get("reading_passages", []):
        japanese, _ = _flatten_reading_passage(passage)
        if japanese:
            passages.append(japanese)
    return "\n\n".join(passages)


def _normalize_reading_vocab(raw_item: dict, sort_order: int) -> dict:
    word = raw_item.get("hiragana_katakana") or raw_item.get("word") or raw_item.get("kanji")
    kana = raw_item.get("hiragana_katakana") or raw_item.get("kana") or raw_item.get("word")

    return {
        "word": word,
        "kana": kana,
        "kanji": raw_item.get("kanji") or None,
        "romaji": raw_item.get("romaji"),
        "word_type": raw_item.get("type"),
        "meaning": raw_item.get("meaning") or "",
        "level": raw_item.get("level") or "N5",
        "sort_order": sort_order,
    }


def _reading_exercise_type(source_type: str) -> str:
    if source_type == "multiple_choice":
        return "reading_multiple_choice"
    if source_type == "true_false":
        return "reading_true_false"
    return "reading_short_answer"


def _is_true_false_correct(answer: str, option: str) -> bool:
    expected = TRUE_FALSE_OPTIONS[0] if answer in TRUE_VALUES else TRUE_FALSE_OPTIONS[1]
    return option == expected


def _multiple_choice_correct_index(answer: str, choices: list[str]) -> int | None:
    if answer in CHOICE_LABELS:
        index = CHOICE_LABELS.index(answer)
        return index if index < len(choices) else None
    if answer in choices:
        return choices.index(answer)
    return None


async def _upsert_reading_passages(db, lesson: models.Lessons, source: dict) -> None:
    for sort_order, passage_data in enumerate(source.get("reading_passages", []), start=1):
        source_passage_id = int(passage_data.get("id") or sort_order)
        japanese, vietnamese = _flatten_reading_passage(passage_data)
        stmt = select(models.ReadingPassages).where(
            models.ReadingPassages.lesson_id == lesson.id,
            models.ReadingPassages.source_passage_id == source_passage_id,
        )
        passage = (await db.execute(stmt)).scalars().first()

        if not passage:
            passage = models.ReadingPassages(
                lesson_id=lesson.id,
                source_passage_id=source_passage_id,
            )
            db.add(passage)

        passage.title = passage_data.get("title") or lesson.title
        passage.vietnamese_title = passage_data.get("vietnamese_title")
        passage.content_japanese = japanese
        passage.content_vietnamese = vietnamese or None
        passage.sort_order = sort_order


async def _upsert_reading_vocabulary(db, lesson: models.Lessons, source: dict) -> None:
    seen_words: set[str] = set()
    for sort_order, raw_item in enumerate(source.get("vocabulary", []), start=1):
        vocab_data = _normalize_reading_vocab(raw_item, sort_order)
        word = vocab_data["word"]
        if not word:
            continue
        seen_words.add(word)

        stmt = select(models.ReadingVocabularyItems).where(
            models.ReadingVocabularyItems.lesson_id == lesson.id,
            models.ReadingVocabularyItems.word == word,
        )
        item = (await db.execute(stmt)).scalars().first()

        if not item:
            item = models.ReadingVocabularyItems(lesson_id=lesson.id, word=word)
            db.add(item)

        item.kana = vocab_data["kana"]
        item.kanji = vocab_data["kanji"]
        item.romaji = vocab_data["romaji"]
        item.word_type = vocab_data["word_type"]
        item.meaning = vocab_data["meaning"]
        item.level = vocab_data["level"]
        item.sort_order = vocab_data["sort_order"]

    stale_vocab_stmt = delete(models.ReadingVocabularyItems).where(
        models.ReadingVocabularyItems.lesson_id == lesson.id
    )
    if seen_words:
        stale_vocab_stmt = stale_vocab_stmt.where(
            models.ReadingVocabularyItems.word.notin_(list(seen_words))
        )
    await db.execute(stale_vocab_stmt)


def _exercise_prompt(question: dict) -> str:
    return question.get("question") or question.get("statement") or ""


def _exercise_correct_answer(exercise_type: str, question: dict) -> str:
    answer = str(question.get("answer") or "")
    if exercise_type == "reading_multiple_choice":
        choices = question.get("choices") or []
        correct_index = _multiple_choice_correct_index(answer, choices)
        if correct_index is not None:
            return choices[correct_index]
    if exercise_type == "reading_true_false":
        return TRUE_FALSE_OPTIONS[0] if answer in TRUE_VALUES else TRUE_FALSE_OPTIONS[1]
    return answer


def _exercise_options(exercise_type: str, question: dict) -> list[dict]:
    answer = str(question.get("answer") or "")

    if exercise_type == "reading_true_false":
        return [
            {"text": option, "is_correct": _is_true_false_correct(answer, option)}
            for option in TRUE_FALSE_OPTIONS
        ]

    if exercise_type == "reading_multiple_choice":
        choices = question.get("choices") or []
        correct_index = _multiple_choice_correct_index(answer, choices)
        return [
            {"text": choice, "is_correct": index == correct_index}
            for index, choice in enumerate(choices)
        ]

    return []


async def _upsert_reading_exercises(db, lesson: models.Lessons, source: dict) -> None:
    source_prompts: set[tuple[str, str]] = set()

    for exercise_group in source.get("exercises", []):
        exercise_type = _reading_exercise_type(exercise_group.get("type") or "")
        for question in exercise_group.get("questions", []):
            prompt = _exercise_prompt(question)
            if not prompt:
                continue

            source_prompts.add((exercise_type, prompt))
            stmt = select(models.Exercises).where(
                models.Exercises.lesson_id == lesson.id,
                models.Exercises.exercise_type == exercise_type,
                models.Exercises.prompt == prompt,
            )
            exercise = (await db.execute(stmt)).scalars().first()

            if not exercise:
                exercise = models.Exercises(
                    lesson_id=lesson.id,
                    exercise_type=exercise_type,
                    prompt=prompt,
                )
                db.add(exercise)
                await db.flush()

            exercise.correct_answer = _exercise_correct_answer(exercise_type, question)
            exercise.explanation = question.get("note") or exercise_group.get("title")
            exercise.score_weight = 5.0

            await db.execute(
                delete(models.ExerciseOptions).where(
                    models.ExerciseOptions.exercise_id == exercise.id
                )
            )
            for option in _exercise_options(exercise_type, question):
                db.add(
                    models.ExerciseOptions(
                        exercise_id=exercise.id,
                        option_text=option["text"],
                        is_correct=option["is_correct"],
                    )
                )

    existing_stmt = select(models.Exercises).where(
        models.Exercises.lesson_id == lesson.id,
        models.Exercises.exercise_type.in_(
            ["reading_multiple_choice", "reading_true_false", "reading_short_answer"]
        ),
    )
    existing_exercises = (await db.execute(existing_stmt)).scalars().all()
    for exercise in existing_exercises:
        if (exercise.exercise_type, exercise.prompt) not in source_prompts:
            await db.delete(exercise)


async def _seed_reading_sources(db, n5_course: models.Courses) -> dict[str, models.Lessons]:
    seeded_lessons = {}
    for source_file, source in _load_reading_sources():
        title = source.get("title") or source.get("lesson") or source_file.stem
        content = _reading_lesson_content(source)
        stmt = select(models.Lessons).where(
            models.Lessons.course_id == n5_course.id,
            models.Lessons.title == title,
        )
        lesson = (await db.execute(stmt)).scalars().first()

        if not lesson:
            lesson = models.Lessons(
                course_id=n5_course.id,
                title=title,
                lesson_type="reading",
                difficulty="N5",
                estimated_minutes=20,
                status="active",
            )
            db.add(lesson)
            await db.flush()
            print(f"Created reading lesson from {source_file.name}: {title}")
        else:
            print(f"Reading lesson already exists for {source_file.name}: {title}")

        lesson.content = content
        lesson.lesson_type = "reading"
        lesson.difficulty = lesson.difficulty or "N5"
        lesson.status = lesson.status or "active"

        await _upsert_reading_passages(db, lesson, source)
        await _upsert_reading_vocabulary(db, lesson, source)
        await _upsert_reading_exercises(db, lesson, source)
        seeded_lessons[title] = lesson

    return seeded_lessons


async def seed_data():
    async with SessionLocal() as db:
        print("Starting database seeding...")

        roles_to_seed = [
            {"code": "admin", "name": "Administrator"},
            {"code": "student", "name": "Student"},
            {"code": "B2B", "name": "Business Member"},
        ]

        seeded_roles = {}
        for role_data in roles_to_seed:
            stmt = select(models.Roles).where(models.Roles.code == role_data["code"])
            role = (await db.execute(stmt)).scalars().first()
            if not role:
                role = models.Roles(code=role_data["code"], name=role_data["name"])
                db.add(role)
                await db.flush()
                print(f"Created role: {role_data['code']}")
            seeded_roles[role_data["code"]] = role

        users_to_seed = [
            {
                "username": "admin",
                "email": "admin@linguasphere.io",
                "full_name": "Global Administrator",
                "password": "adminpassword123",
                "role_code": "admin",
            },
            {
                "username": "alex",
                "email": "alex@linguasphere.io",
                "full_name": "Alex Johnson",
                "password": "password123",
                "role_code": "student",
                "phone": "0988888888",
            },
        ]

        for user_data in users_to_seed:
            stmt = select(models.Users).where(models.Users.email == user_data["email"])
            user = (await db.execute(stmt)).scalars().first()
            if not user:
                user = models.Users(
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    hashed_password=get_password_hash(user_data["password"]),
                    phone=user_data.get("phone"),
                    is_onboarded=user_data["role_code"] == "student",
                )
                db.add(user)
                await db.flush()
                user.role.append(seeded_roles[user_data["role_code"]])
                print(f"Created user: {user_data['email']} with role {user_data['role_code']}")
            else:
                print(f"User {user_data['email']} already exists.")

        courses_to_seed = [
            {
                "title": "JLPT N5 Foundation",
                "code": "N5-FOUNDATION",
                "description": "Essential Japanese grammar, vocabulary, and hiragana/katakana basics.",
                "level": "N5",
                "status": "active",
            },
            {
                "title": "JLPT N4 Elementary",
                "code": "N4-ELEMENTARY",
                "description": "Mid-beginner Japanese grammar, reading comprehension, and everyday scenarios.",
                "level": "N4",
                "status": "active",
            },
        ]

        seeded_courses = {}
        for course_data in courses_to_seed:
            stmt = select(models.Courses).where(models.Courses.code == course_data["code"])
            course = (await db.execute(stmt)).scalars().first()
            if not course:
                course = models.Courses(**course_data)
                db.add(course)
                await db.flush()
                print(f"Created course: {course_data['code']}")
            seeded_courses[course_data["code"]] = course

        lessons_to_seed = [
            {
                "course_code": "N5-FOUNDATION",
                "title": "Self-Introduction",
                "lesson_type": "vocabulary",
                "content": "Learn how to introduce yourself and others in Japanese professionally.",
                "difficulty": "beginner",
                "estimated_minutes": 15,
                "status": "active",
            },
            {
                "course_code": "N5-FOUNDATION",
                "title": "Ordering at a Cafe",
                "lesson_type": "speaking",
                "content": "Practice ordering coffees, teas, and food in natural Japanese using conversational patterns.",
                "difficulty": "beginner",
                "estimated_minutes": 20,
                "status": "active",
            },
        ]

        seeded_lessons = {}
        for lesson_data in lessons_to_seed:
            course = seeded_courses[lesson_data["course_code"]]
            stmt = select(models.Lessons).where(
                models.Lessons.course_id == course.id,
                models.Lessons.title == lesson_data["title"],
            )
            lesson = (await db.execute(stmt)).scalars().first()
            if not lesson:
                lesson = models.Lessons(
                    course_id=course.id,
                    title=lesson_data["title"],
                    lesson_type=lesson_data["lesson_type"],
                    content=lesson_data["content"],
                    difficulty=lesson_data["difficulty"],
                    estimated_minutes=lesson_data["estimated_minutes"],
                    status=lesson_data["status"],
                )
                db.add(lesson)
                await db.flush()
                print(f"Created lesson: {lesson_data['title']} (Type: {lesson_data['lesson_type']})")
            seeded_lessons[lesson_data["title"]] = lesson

        exercises_to_seed = [
            {
                "lesson_title": "Ordering at a Cafe",
                "prompt": "Practice speaking the phrase: 'すいません、ホットコーヒーを一つお願いします。' (Excuse me, one hot coffee please.)",
                "exercise_type": "speaking",
                "correct_answer": "すいません、ホットコーヒーを一つお願いします。",
                "explanation": "Focus on the natural rhythm of 'one please' (hitotsu onegai shimasu).",
                "score_weight": 10.0,
                "options": [],
            },
        ]

        for ex_data in exercises_to_seed:
            lesson = seeded_lessons[ex_data["lesson_title"]]
            stmt = select(models.Exercises).where(
                models.Exercises.lesson_id == lesson.id,
                models.Exercises.prompt == ex_data["prompt"],
            )
            exercise = (await db.execute(stmt)).scalars().first()
            if not exercise:
                exercise = models.Exercises(
                    lesson_id=lesson.id,
                    prompt=ex_data["prompt"],
                    exercise_type=ex_data["exercise_type"],
                    correct_answer=ex_data["correct_answer"],
                    explanation=ex_data["explanation"],
                    score_weight=ex_data["score_weight"],
                )
                db.add(exercise)
                await db.flush()
                print(f"Created exercise: {ex_data['prompt'][:30]}...")

            for opt in ex_data["options"]:
                option_stmt = select(models.ExerciseOptions).where(
                    models.ExerciseOptions.exercise_id == exercise.id,
                    models.ExerciseOptions.option_text == opt["text"],
                )
                option = (await db.execute(option_stmt)).scalars().first()
                if not option:
                    db.add(
                        models.ExerciseOptions(
                            exercise_id=exercise.id,
                            option_text=opt["text"],
                            is_correct=opt["is_correct"],
                        )
                    )

        reading_lessons = await _seed_reading_sources(db, seeded_courses["N5-FOUNDATION"])
        seeded_lessons.update(reading_lessons)

        await db.commit()
        print("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())
