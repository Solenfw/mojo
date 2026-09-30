"""Grading for multiple-choice practices (reading and listening share the question/option shape)."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Protocol

PASS_MARK = 70.0  # percent


class _Option(Protocol):
    id: int
    is_correct: bool


class _Question(Protocol):
    id: int

    @property
    def options(self) -> Iterable[_Option]: ...


class UnknownQuestionError(Exception):
    """An answer refers to a question that isn't part of the practice."""


@dataclass(frozen=True)
class GradedAnswer:
    question_id: int
    selected_option_id: int | None
    is_correct: bool


@dataclass(frozen=True)
class Grade:
    answers: list[GradedAnswer]
    score: float  # percent of all questions, unanswered ones count as wrong
    passed: bool


def clamp_score(value: object) -> int:
    """An AI-reported 0-100 score; anything malformed counts as 0 so it can never earn XP."""
    try:
        return max(0, min(100, round(float(value))))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def grade_choices(questions: Iterable[_Question], selected: Mapping[int, int]) -> Grade:
    """`selected` maps question id -> chosen option id. An option from another question counts as wrong."""
    questions = list(questions)
    if unknown := set(selected) - {question.id for question in questions}:
        raise UnknownQuestionError(sorted(unknown))

    answers = []
    for question in questions:
        option_id = selected.get(question.id)
        correct_ids = {option.id for option in question.options if option.is_correct}
        answers.append(GradedAnswer(question.id, option_id, option_id in correct_ids))

    score = round(100 * sum(answer.is_correct for answer in answers) / len(answers), 2) if answers else 0.0
    return Grade(answers, score, bool(answers) and score >= PASS_MARK)
