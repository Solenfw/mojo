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

DOCS_DIR = ROOT / "docs" / "json"
CHOICE_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TRUE_FALSE_OPTIONS = ("〇", "✕")
TRUE_VALUES = {"〇", "○", "O", "o", "true", "True", "TRUE"}


def _load_jsons(category: str) -> list[tuple[Path, dict]]:
    cat_dir = DOCS_DIR / category
    if not cat_dir.exists():
        return []
    files = sorted(
        cat_dir.glob("lesson_*.json"),
        key=lambda path: int(path.stem.split("_")[-1]),
    )
    sources = []
    for f in files:
        with f.open(encoding="utf-8") as fh:
            sources.append((f, json.load(fh)))
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


async def _create_or_update_exercise(
    db, lesson_id: int, prompt: str, ex_type: str, correct_answer: str, explanation: str, options_data: list[dict]
):
    if not prompt:
        return
    stmt = select(models.Exercises).where(
        models.Exercises.lesson_id == lesson_id,
        models.Exercises.prompt == prompt,
        models.Exercises.exercise_type == ex_type,
    )
    exercise = (await db.execute(stmt)).scalars().first()
    
    if not exercise:
        exercise = models.Exercises(
            lesson_id=lesson_id,
            prompt=prompt,
            exercise_type=ex_type,
        )
        db.add(exercise)
        await db.flush()

    exercise.correct_answer = correct_answer
    exercise.explanation = explanation
    exercise.score_weight = 5.0

    await db.execute(delete(models.ExerciseOptions).where(models.ExerciseOptions.exercise_id == exercise.id))
    for opt in options_data:
        db.add(
            models.ExerciseOptions(
                exercise_id=exercise.id,
                option_text=opt["text"],
                is_correct=opt["is_correct"],
            )
        )


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


async def _upsert_reading_exercises(db, lesson: models.Lessons, source: dict) -> None:
    for exercise_group in source.get("exercises", []):
        exercise_type = _reading_exercise_type(exercise_group.get("type") or "")
        for question in exercise_group.get("questions", []):
            prompt = question.get("question") or question.get("statement") or ""
            if not prompt:
                continue

            answer = str(question.get("answer") or "")
            explanation = question.get("note") or exercise_group.get("title") or ""
            
            options_data = []
            correct_text = answer
            
            if exercise_type == "reading_true_false":
                correct_text = TRUE_FALSE_OPTIONS[0] if answer in TRUE_VALUES else TRUE_FALSE_OPTIONS[1]
                options_data = [
                    {"text": opt, "is_correct": opt == correct_text}
                    for opt in TRUE_FALSE_OPTIONS
                ]
            elif exercise_type == "reading_multiple_choice":
                choices = question.get("choices") or []
                correct_index = _multiple_choice_correct_index(answer, choices)
                if correct_index is not None and correct_index < len(choices):
                    correct_text = choices[correct_index]
                options_data = [
                    {"text": choice, "is_correct": idx == correct_index}
                    for idx, choice in enumerate(choices)
                ]
            else:
                options_data = [{"text": answer, "is_correct": True}]

            await _create_or_update_exercise(db, lesson.id, prompt, exercise_type, correct_text, explanation, options_data)


async def _upsert_kanji_exercises(db, lesson: models.Lessons, source: dict) -> None:
    # 1. Process practice_exercises
    for ex_group in source.get("practice_exercises", []):
        choices = ex_group.get("choices", [])
        for q in ex_group.get("questions", []):
            prompt = q.get("prompt") or q.get("kanji") or q.get("vietnamese") or ""
            if "kanji" in q and "prompt" in q:
                prompt = f"{q.get('kanji')} - {q.get('prompt')}"
                
            if choices:
                ex_type = "kanji_multiple_choice"
                answer_label = q.get("answer", "A")
                ans_idx = ord(answer_label.upper()) - 65 if answer_label else 0
                correct_text = choices[ans_idx].get("vietnamese", "") if ans_idx < len(choices) else ""
                options_data = [
                    {"text": c.get("vietnamese", ""), "is_correct": i == ans_idx} 
                    for i, c in enumerate(choices)
                ]
            else:
                ex_type = "kanji_short_answer"
                correct_text = q.get("full_reading") or q.get("answer") or ""
                options_data = [{"text": correct_text, "is_correct": True}]
                
            await _create_or_update_exercise(db, lesson.id, prompt, ex_type, correct_text, "", options_data)

    # 2. Process generic practice
    practice = source.get("practice", {})
    if practice:
        answers_dict = {a["id"]: a for a in practice.get("answers", [])}
        for q in practice.get("questions", []):
            prompt = q.get("kanji", "")
            ans = answers_dict.get(q.get("id"), {})
            correct_text = ans.get("hiragana", "")
            options_data = [{"text": correct_text, "is_correct": True}]
            await _create_or_update_exercise(db, lesson.id, prompt, "kanji_short_answer", correct_text, "", options_data)


async def _upsert_listening_exercises(db, lesson: models.Lessons, source: dict) -> None:
    for passage in source.get("listening_passages", []):
        for q in passage.get("questions", []):
            prompt = q.get("question", "")
            opts = q.get("options", [])
            answer_label = q.get("answer", "A")
            ans_idx = ord(answer_label.upper()) - 65 if answer_label else 0
            correct_text = opts[ans_idx] if ans_idx < len(opts) else ""
            options_data = [{"text": o, "is_correct": i == ans_idx} for i, o in enumerate(opts)]
            
            await _create_or_update_exercise(db, lesson.id, prompt, "listening_multiple_choice", correct_text, "", options_data)


async def _seed_global_vocabularies(db) -> None:
    seen = set()
    for _, source in _load_jsons("vocabulary"):
        for item in source.get("items", []):
            vocab = item.get("vocab", "")
            kanji = item.get("Kanji")
            if not kanji or kanji == "null":
                kanji = vocab
            
            kana = item.get("kana") or vocab
            romaji = item.get("romaji") or item.get("Romaji") or ""
            meaning = item.get("meaning", "")
            example = item.get("example") or ""
            example_meaning = item.get("example_meaning") or ""
            
            key = (kanji, kana)
            if key in seen:
                continue
            seen.add(key)
            
            stmt = select(models.Vocabularies).where(
                models.Vocabularies.kanji == kanji,
                models.Vocabularies.kana == kana
            )
            db_item = (await db.execute(stmt)).scalars().first()
            if not db_item:
                db_item = models.Vocabularies(
                    kanji=kanji,
                    kana=kana,
                    romaji=romaji,
                    meaning=meaning,
                    example_sentence=example,
                    example_english=example_meaning,
                    level="N5"
                )
                db.add(db_item)
            else:
                db_item.romaji = romaji
                db_item.meaning = meaning
                db_item.example_sentence = example
                db_item.example_english = example_meaning
    await db.flush()
    print("Seed global vocabularies completed.")


async def _seed_all_lessons(db, course: models.Courses) -> None:
    categories = ["grammar", "kanji", "listening", "reading", "speaking", "vocabulary"]
    for category in categories:
        for source_file, source in _load_jsons(category):
            title = source.get("title") or source.get("lesson_title") or source.get("lesson") or f"{category.title()} - {source_file.stem}"
            stmt = select(models.Lessons).where(
                models.Lessons.course_id == course.id,
                models.Lessons.title == title,
            )
            lesson = (await db.execute(stmt)).scalars().first()

            if not lesson:
                lesson = models.Lessons(
                    course_id=course.id,
                    title=title,
                    lesson_type=category,
                    difficulty="N5",
                    estimated_minutes=20,
                    status="active",
                )
                db.add(lesson)
                await db.flush()
                print(f"Created {category} lesson: {title}")
            else:
                lesson.lesson_type = category

            # Store the raw JSON content so the frontend can parse UI elements (dialogues, grammar_points, etc.)
            lesson.content = json.dumps(source, ensure_ascii=False)

            # Extra processing for interactive exercise elements
            if category == "reading":
                await _upsert_reading_passages(db, lesson, source)
                await _upsert_reading_vocabulary(db, lesson, source)
                await _upsert_reading_exercises(db, lesson, source)
            elif category == "kanji":
                await _upsert_kanji_exercises(db, lesson, source)
            elif category == "listening":
                await _upsert_listening_exercises(db, lesson, source)
                
    print("All lessons seeded and attached to course successfully.")


async def seed_data():
    async with SessionLocal() as db:
        print("Starting database seeding...")

        # 1. Setup Base Roles
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

        # 2. Setup Base Users
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

        # 3. Setup Base Courses
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

        # 4. Seed Global Vocabularies
        await _seed_global_vocabularies(db)

        # 5. Parse dynamic docs/json files and attach as lessons to N5 course
        n5_course = seeded_courses["N5-FOUNDATION"]
        await _seed_all_lessons(db, n5_course)

        await db.commit()
        print("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())# seeder.py
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

DOCS_DIR = ROOT / "docs" / "json"
CHOICE_LABELS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
TRUE_FALSE_OPTIONS = ("〇", "✕")
TRUE_VALUES = {"〇", "○", "O", "o", "true", "True", "TRUE"}


def _load_jsons(category: str) -> list[tuple[Path, dict]]:
    cat_dir = DOCS_DIR / category
    if not cat_dir.exists():
        return []
    files = sorted(
        cat_dir.glob("lesson_*.json"),
        key=lambda path: int(path.stem.split("_")[-1]),
    )
    sources = []
    for f in files:
        with f.open(encoding="utf-8") as fh:
            sources.append((f, json.load(fh)))
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


async def _create_or_update_exercise(
    db, lesson_id: int, prompt: str, ex_type: str, correct_answer: str, explanation: str, options_data: list[dict]
):
    if not prompt:
        return
    stmt = select(models.Exercises).where(
        models.Exercises.lesson_id == lesson_id,
        models.Exercises.prompt == prompt,
        models.Exercises.exercise_type == ex_type,
    )
    exercise = (await db.execute(stmt)).scalars().first()
    
    if not exercise:
        exercise = models.Exercises(
            lesson_id=lesson_id,
            prompt=prompt,
            exercise_type=ex_type,
        )
        db.add(exercise)
        await db.flush()

    exercise.correct_answer = correct_answer
    exercise.explanation = explanation
    exercise.score_weight = 5.0

    await db.execute(delete(models.ExerciseOptions).where(models.ExerciseOptions.exercise_id == exercise.id))
    for opt in options_data:
        db.add(
            models.ExerciseOptions(
                exercise_id=exercise.id,
                option_text=opt["text"],
                is_correct=opt["is_correct"],
            )
        )


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


async def _upsert_reading_exercises(db, lesson: models.Lessons, source: dict) -> None:
    for exercise_group in source.get("exercises", []):
        exercise_type = _reading_exercise_type(exercise_group.get("type") or "")
        for question in exercise_group.get("questions", []):
            prompt = question.get("question") or question.get("statement") or ""
            if not prompt:
                continue

            answer = str(question.get("answer") or "")
            explanation = question.get("note") or exercise_group.get("title") or ""
            
            options_data = []
            correct_text = answer
            
            if exercise_type == "reading_true_false":
                correct_text = TRUE_FALSE_OPTIONS[0] if answer in TRUE_VALUES else TRUE_FALSE_OPTIONS[1]
                options_data = [
                    {"text": opt, "is_correct": opt == correct_text}
                    for opt in TRUE_FALSE_OPTIONS
                ]
            elif exercise_type == "reading_multiple_choice":
                choices = question.get("choices") or []
                correct_index = _multiple_choice_correct_index(answer, choices)
                if correct_index is not None and correct_index < len(choices):
                    correct_text = choices[correct_index]
                options_data = [
                    {"text": choice, "is_correct": idx == correct_index}
                    for idx, choice in enumerate(choices)
                ]
            else:
                options_data = [{"text": answer, "is_correct": True}]

            await _create_or_update_exercise(db, lesson.id, prompt, exercise_type, correct_text, explanation, options_data)


async def _upsert_kanji_exercises(db, lesson: models.Lessons, source: dict) -> None:
    # 1. Process practice_exercises
    for ex_group in source.get("practice_exercises", []):
        choices = ex_group.get("choices", [])
        for q in ex_group.get("questions", []):
            prompt = q.get("prompt") or q.get("kanji") or q.get("vietnamese") or ""
            if "kanji" in q and "prompt" in q:
                prompt = f"{q.get('kanji')} - {q.get('prompt')}"
                
            if choices:
                ex_type = "kanji_multiple_choice"
                answer_label = q.get("answer", "A")
                ans_idx = ord(answer_label.upper()) - 65 if answer_label else 0
                correct_text = choices[ans_idx].get("vietnamese", "") if ans_idx < len(choices) else ""
                options_data = [
                    {"text": c.get("vietnamese", ""), "is_correct": i == ans_idx} 
                    for i, c in enumerate(choices)
                ]
            else:
                ex_type = "kanji_short_answer"
                correct_text = q.get("full_reading") or q.get("answer") or ""
                options_data = [{"text": correct_text, "is_correct": True}]
                
            await _create_or_update_exercise(db, lesson.id, prompt, ex_type, correct_text, "", options_data)

    # 2. Process generic practice
    practice = source.get("practice", {})
    if practice:
        answers_dict = {a["id"]: a for a in practice.get("answers", [])}
        for q in practice.get("questions", []):
            prompt = q.get("kanji", "")
            ans = answers_dict.get(q.get("id"), {})
            correct_text = ans.get("hiragana", "")
            options_data = [{"text": correct_text, "is_correct": True}]
            await _create_or_update_exercise(db, lesson.id, prompt, "kanji_short_answer", correct_text, "", options_data)


async def _upsert_listening_exercises(db, lesson: models.Lessons, source: dict) -> None:
    for passage in source.get("listening_passages", []):
        for q in passage.get("questions", []):
            prompt = q.get("question", "")
            opts = q.get("options", [])
            answer_label = q.get("answer", "A")
            ans_idx = ord(answer_label.upper()) - 65 if answer_label else 0
            correct_text = opts[ans_idx] if ans_idx < len(opts) else ""
            options_data = [{"text": o, "is_correct": i == ans_idx} for i, o in enumerate(opts)]
            
            await _create_or_update_exercise(db, lesson.id, prompt, "listening_multiple_choice", correct_text, "", options_data)


async def _seed_global_vocabularies(db) -> None:
    seen = set()
    for _, source in _load_jsons("vocabulary"):
        for item in source.get("items", []):
            vocab = item.get("vocab", "")
            kanji = item.get("Kanji")
            if not kanji or kanji == "null":
                kanji = vocab
            
            kana = item.get("kana") or vocab
            romaji = item.get("romaji") or item.get("Romaji") or ""
            meaning = item.get("meaning", "")
            example = item.get("example") or ""
            example_meaning = item.get("example_meaning") or ""
            
            key = (kanji, kana)
            if key in seen:
                continue
            seen.add(key)
            
            stmt = select(models.Vocabularies).where(
                models.Vocabularies.kanji == kanji,
                models.Vocabularies.kana == kana
            )
            db_item = (await db.execute(stmt)).scalars().first()
            if not db_item:
                db_item = models.Vocabularies(
                    kanji=kanji,
                    kana=kana,
                    romaji=romaji,
                    meaning=meaning,
                    example_sentence=example,
                    example_english=example_meaning,
                    level="N5"
                )
                db.add(db_item)
            else:
                db_item.romaji = romaji
                db_item.meaning = meaning
                db_item.example_sentence = example
                db_item.example_english = example_meaning
    await db.flush()
    print("Seed global vocabularies completed.")


async def _seed_all_lessons(db, course: models.Courses) -> None:
    categories = ["grammar", "kanji", "listening", "reading", "speaking", "vocabulary"]
    for category in categories:
        for source_file, source in _load_jsons(category):
            title = source.get("title") or source.get("lesson_title") or source.get("lesson") or f"{category.title()} - {source_file.stem}"
            stmt = select(models.Lessons).where(
                models.Lessons.course_id == course.id,
                models.Lessons.title == title,
            )
            lesson = (await db.execute(stmt)).scalars().first()

            if not lesson:
                lesson = models.Lessons(
                    course_id=course.id,
                    title=title,
                    lesson_type=category,
                    difficulty="N5",
                    estimated_minutes=20,
                    status="active",
                )
                db.add(lesson)
                await db.flush()
                print(f"Created {category} lesson: {title}")
            else:
                lesson.lesson_type = category

            # Store the raw JSON content so the frontend can parse UI elements (dialogues, grammar_points, etc.)
            lesson.content = json.dumps(source, ensure_ascii=False)

            # Extra processing for interactive exercise elements
            if category == "reading":
                await _upsert_reading_passages(db, lesson, source)
                await _upsert_reading_vocabulary(db, lesson, source)
                await _upsert_reading_exercises(db, lesson, source)
            elif category == "kanji":
                await _upsert_kanji_exercises(db, lesson, source)
            elif category == "listening":
                await _upsert_listening_exercises(db, lesson, source)
                
    print("All lessons seeded and attached to course successfully.")


async def seed_data():
    async with SessionLocal() as db:
        print("Starting database seeding...")

        # 1. Setup Base Roles
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

        # 2. Setup Base Users
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

        # 3. Setup Base Courses
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

        # 4. Seed Global Vocabularies
        await _seed_global_vocabularies(db)

        # 5. Parse dynamic docs/json files and attach as lessons to N5 course
        n5_course = seeded_courses["N5-FOUNDATION"]
        await _seed_all_lessons(db, n5_course)

        await db.commit()
        print("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())