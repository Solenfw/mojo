from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.db.database import Base


"""
    Lookup tables.
"""


class ProficiencyLevel(Base):
    __tablename__ = "proficiency_level"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)  # "Beginner", "Intermediate", ...
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)  # used to resolve "next level"


class Skill(Base):
    __tablename__ = "skill"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)  # vocab/reading/speaking/writing/listening
    name: Mapped[str] = mapped_column(String(100), nullable=False)


"""
    User & profile.
"""


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    session_token: Mapped[str | None] = mapped_column(String(255))

    is_logged_in: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_onboarded: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    current_level_id: Mapped[int | None] = mapped_column(ForeignKey("proficiency_level.id"))

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    onboarded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    xp: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    streak: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    gems: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    hearts: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("5"))
    hearts_last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_activity_date: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    current_level: Mapped[ProficiencyLevel | None] = relationship()
    profile: Mapped["LearnerProfile | None"] = relationship(back_populates="user", uselist=False)


class LearnerProfile(Base):
    """Onboarding-captured preferences. Current level lives on User; this holds aspirational/contextual data."""

    __tablename__ = "learner_profile"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, unique=True)
    target_level_id: Mapped[int | None] = mapped_column(ForeignKey("proficiency_level.id"))
    study_intention: Mapped[str | None] = mapped_column(String(255))  # why they study
    daily_study_minutes: Mapped[int | None] = mapped_column(Integer)  # dedicated time
    experience: Mapped[str | None] = mapped_column(String(50))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="profile")
    target_level: Mapped[ProficiencyLevel | None] = relationship()


"""
    Onboarding process.
    Three known inputs (chosen level, intention, study time) -> structured columns instead of a
    generic question/answer pattern. If the level chosen is above Beginner, an onboarding session
    links to the placement Test taken; result_level is the level the user actually got placed into.
"""


class OnboardingSession(Base):
    __tablename__ = "onboarding_session"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    chosen_level_id: Mapped[int | None] = mapped_column(ForeignKey("proficiency_level.id"))  # self-assessed pick
    study_intention: Mapped[str | None] = mapped_column(String(255))
    daily_study_minutes: Mapped[int | None] = mapped_column(Integer)

    test_attempt_id: Mapped[int | None] = mapped_column(ForeignKey("test_attempt.id"))  # null if Beginner, no test taken
    result_level_id: Mapped[int | None] = mapped_column(ForeignKey("proficiency_level.id"))  # final placement

    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'in_progress'"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()
    chosen_level: Mapped[ProficiencyLevel | None] = relationship(foreign_keys=[chosen_level_id])
    result_level: Mapped[ProficiencyLevel | None] = relationship(foreign_keys=[result_level_id])
    test_attempt: Mapped["TestAttempt | None"] = relationship()


"""
    Tests. Shared between onboarding placement and in-app level-up requests - a Test is just
    "the gate into target_level_id", reused for both purposes (see Test.test_type).
    The "2 attempts / 24h" rule is enforced in the application layer by counting TestAttempt rows
    for (user_id, test_id) with started_at >= now() - 24h; index that pair for the lookup.
"""


class Test(Base):
    __tablename__ = "test"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    code: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    test_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'placement' | 'level_up'
    target_level_id: Mapped[int] = mapped_column(ForeignKey("proficiency_level.id"), nullable=False)
    total_score: Mapped[float | None] = mapped_column(Numeric(10, 2))
    passing_score: Mapped[float | None] = mapped_column(Numeric(10, 2))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(50))

    target_level: Mapped[ProficiencyLevel] = relationship()
    questions: Mapped[list["TestQuestion"]] = relationship(back_populates="test", order_by="TestQuestion.sort_order")


class TestQuestion(Base):
    __tablename__ = "test_question"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("test.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str | None] = mapped_column(String(50))
    score_weight: Mapped[float | None] = mapped_column(Numeric(10, 2))
    sort_order: Mapped[int | None] = mapped_column(Integer)
    correct_answer: Mapped[str | None] = mapped_column(Text)

    test: Mapped[Test] = relationship(back_populates="questions")
    options: Mapped[list["TestQuestionOption"]] = relationship(back_populates="question")


class TestQuestionOption(Base):
    __tablename__ = "test_question_option"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("test_question.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    sort_order: Mapped[int | None] = mapped_column(Integer)

    question: Mapped[TestQuestion] = relationship(back_populates="options")


class TestAttempt(Base):
    __tablename__ = "test_attempt"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("test.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    score: Mapped[float | None] = mapped_column(Numeric(10, 2))
    passed: Mapped[bool | None] = mapped_column(Boolean)
    status: Mapped[str | None] = mapped_column(String(50))

    test: Mapped[Test] = relationship()
    user: Mapped[User] = relationship()


class TestAttemptAnswer(Base):
    __tablename__ = "test_attempt_answer"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("test_attempt.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("test_question.id"), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    score: Mapped[float | None] = mapped_column(Numeric(10, 2))

    attempt: Mapped[TestAttempt] = relationship()


"""
    Courses & lessons. A course belongs to exactly one level (e.g. courses 1-3 = Beginner).
    A lesson belongs to a course and can contain practices across multiple skills.
"""


class Course(Base):
    __tablename__ = "course"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str | None] = mapped_column(String(50))
    level_id: Mapped[int] = mapped_column(ForeignKey("proficiency_level.id"), nullable=False)
    sort_order: Mapped[int | None] = mapped_column(Integer)

    level: Mapped[ProficiencyLevel] = relationship()
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="course", order_by="Lesson.sort_order")


class Lesson(Base):
    __tablename__ = "lesson"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    difficulty: Mapped[str | None] = mapped_column(String(50))
    estimated_minutes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str | None] = mapped_column(String(50))
    sort_order: Mapped[int | None] = mapped_column(Integer)

    course: Mapped[Course] = relationship(back_populates="lessons")


"""
    Vocab practice - flashcards with SRS. Vocabulary is the content (one row per word);
    VocabularyReview is per-user SRS state, updated on every review.
"""


class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False)
    kanji: Mapped[str | None] = mapped_column(String(100))
    kana: Mapped[str] = mapped_column(String(100), nullable=False)
    romaji: Mapped[str] = mapped_column(String(100), nullable=False)
    meaning: Mapped[str] = mapped_column(String(255), nullable=False)
    example_sentence: Mapped[str | None] = mapped_column(Text)
    example_translation: Mapped[str | None] = mapped_column(Text)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("5"))

    lesson: Mapped[Lesson] = relationship()


class VocabularyReview(Base):
    __tablename__ = "vocabulary_review"
    __table_args__ = (UniqueConstraint("user_id", "vocabulary_id"),)

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    vocabulary_id: Mapped[int] = mapped_column(ForeignKey("vocabulary.id"), nullable=False)

    ease_factor: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, server_default=text("2.5"))
    interval_days: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    repetitions: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_result: Mapped[str | None] = mapped_column(String(20))  # again / hard / good / easy

    user: Mapped[User] = relationship()
    vocabulary: Mapped[Vocabulary] = relationship()


"""
    Reading practice - passage with comprehension questions, must pass to earn xp_reward.
"""


class ReadingPassage(Base):
    __tablename__ = "reading_passage"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    content_japanese: Mapped[str] = mapped_column(Text, nullable=False)
    content_vietnamese: Mapped[str | None] = mapped_column(Text)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))

    lesson: Mapped[Lesson] = relationship()
    questions: Mapped[list["ReadingQuestion"]] = relationship(
        back_populates="passage", order_by="ReadingQuestion.sort_order"
    )


class ReadingQuestion(Base):
    __tablename__ = "reading_question"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    passage_id: Mapped[int] = mapped_column(ForeignKey("reading_passage.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int | None] = mapped_column(Integer)

    passage: Mapped[ReadingPassage] = relationship(back_populates="questions")
    options: Mapped[list["ReadingQuestionOption"]] = relationship(back_populates="question")


class ReadingQuestionOption(Base):
    __tablename__ = "reading_question_option"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("reading_question.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    question: Mapped[ReadingQuestion] = relationship(back_populates="options")


class ReadingAttempt(Base):
    __tablename__ = "reading_attempt"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    passage_id: Mapped[int] = mapped_column(ForeignKey("reading_passage.id"), nullable=False)
    score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()
    passage: Mapped[ReadingPassage] = relationship()


class ReadingAttemptAnswer(Base):
    __tablename__ = "reading_attempt_answer"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("reading_attempt.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("reading_question.id"), nullable=False)
    selected_option_id: Mapped[int | None] = mapped_column(ForeignKey("reading_question_option.id"))
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    attempt: Mapped[ReadingAttempt] = relationship()


"""
    Speaking practice - AI conversation. Dialogue is the scripted reference exchange used to seed
    the conversation; DialogueAttempt logs a user's actual AI-rated session against it.
"""


class Dialogue(Base):
    __tablename__ = "dialogue"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("15"))

    lesson: Mapped[Lesson] = relationship()
    exchanges: Mapped[list["DialogueExchange"]] = relationship(
        back_populates="dialogue", order_by="DialogueExchange.order_index"
    )


class DialogueExchange(Base):
    __tablename__ = "dialogue_exchange"
    __table_args__ = (UniqueConstraint("dialogue_id", "order_index"),)

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    dialogue_id: Mapped[int] = mapped_column(ForeignKey("dialogue.id"), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    speaker: Mapped[str] = mapped_column(String(50), nullable=False)  # "A"/"B" or a character name

    ja_text: Mapped[str] = mapped_column(Text, nullable=False)
    ja_romaji: Mapped[str] = mapped_column(Text, nullable=False)
    en_text: Mapped[str] = mapped_column(Text, nullable=False)

    dialogue: Mapped[Dialogue] = relationship(back_populates="exchanges")


class DialogueAttempt(Base):
    __tablename__ = "dialogue_attempt"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    dialogue_id: Mapped[int] = mapped_column(ForeignKey("dialogue.id"), nullable=False)
    ai_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    ai_feedback: Mapped[str | None] = mapped_column(Text)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()
    dialogue: Mapped[Dialogue] = relationship()


"""
    Writing practice - kanji stroke practice on an HTML canvas, AI-rated.
"""


class KanjiPractice(Base):
    __tablename__ = "kanji_practice"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kanji: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[str | None] = mapped_column(String(50))
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))

    lesson: Mapped[Lesson] = relationship()


class KanjiPracticeAttempt(Base):
    __tablename__ = "kanji_practice_attempt"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    kanji_practice_id: Mapped[int] = mapped_column(ForeignKey("kanji_practice.id"), nullable=False)
    canvas_image_url: Mapped[str | None] = mapped_column(String(500))
    ai_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    ai_feedback: Mapped[str | None] = mapped_column(Text)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()
    kanji_practice: Mapped[KanjiPractice] = relationship()


"""
    Listening practice - audio from a conversation, song, or set of sentences, with comprehension
    questions (same pass/question/option shape as reading).
"""


class ListeningPractice(Base):
    __tablename__ = "listening_practice"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'dialogue' | 'song' | 'sentences'
    audio_url: Mapped[str | None] = mapped_column(String(500))
    transcript_japanese: Mapped[str | None] = mapped_column(Text)
    transcript_vietnamese: Mapped[str | None] = mapped_column(Text)
    xp_reward: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))

    lesson: Mapped[Lesson] = relationship()
    questions: Mapped[list["ListeningQuestion"]] = relationship(back_populates="practice")


class ListeningQuestion(Base):
    __tablename__ = "listening_question"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    practice_id: Mapped[int] = mapped_column(ForeignKey("listening_practice.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int | None] = mapped_column(Integer)

    practice: Mapped[ListeningPractice] = relationship(back_populates="questions")
    options: Mapped[list["ListeningQuestionOption"]] = relationship(back_populates="question")


class ListeningQuestionOption(Base):
    __tablename__ = "listening_question_option"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("listening_question.id"), nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    question: Mapped[ListeningQuestion] = relationship(back_populates="options")


class ListeningAttempt(Base):
    __tablename__ = "listening_attempt"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    practice_id: Mapped[int] = mapped_column(ForeignKey("listening_practice.id"), nullable=False)
    score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()
    practice: Mapped[ListeningPractice] = relationship()


"""
    Activity log (optional) - a unified, append-only feed of completed practices across all five
    skills. Write one row here alongside each *Attempt/*Review insert. Makes streaks, "xp earned
    today", and the level-up-unlock check (SUM xp_earned since current_level was reached) a single
    query instead of five UNIONs across the skill-specific attempt tables.
"""


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill.id"), nullable=False)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    user: Mapped[User] = relationship()
    skill: Mapped[Skill] = relationship()