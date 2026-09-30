"""
ORM models, one module per domain. Importing this package registers every table on
Base.metadata (Alembic and the relationship resolver rely on that), so import models from here:

    from app.models import User, AuthSession
"""

from app.models.activity import ActivityLog
from app.models.auth import AuthSession
from app.models.course import Course, Lesson
from app.models.listening import ListeningAttempt, ListeningPractice, ListeningQuestion, ListeningQuestionOption
from app.models.lookup import ProficiencyLevel, Skill
from app.models.reading import (
    ReadingAttempt,
    ReadingAttemptAnswer,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionOption,
)
from app.models.speaking import Dialogue, DialogueAttempt, DialogueExchange
from app.models.user import LearnerProfile, User
from app.models.vocabulary import Vocabulary, VocabularyReview
from app.models.writing import KanjiPractice, KanjiPracticeAttempt

__all__ = [
    "ActivityLog",
    "AuthSession",
    "Course",
    "Dialogue",
    "DialogueAttempt",
    "DialogueExchange",
    "KanjiPractice",
    "KanjiPracticeAttempt",
    "LearnerProfile",
    "Lesson",
    "ListeningAttempt",
    "ListeningPractice",
    "ListeningQuestion",
    "ListeningQuestionOption",
    "ProficiencyLevel",
    "ReadingAttempt",
    "ReadingAttemptAnswer",
    "ReadingPassage",
    "ReadingQuestion",
    "ReadingQuestionOption",
    "Skill",
    "User",
    "Vocabulary",
    "VocabularyReview",
]
