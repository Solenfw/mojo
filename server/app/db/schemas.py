from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ─────────────────────────────────────────────────────────────
# Lookup
# ─────────────────────────────────────────────────────────────

class ProficiencyLevelRead(BaseModel):
    id: int
    name: str
    sort_order: int
    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────────────────────
# Auth & User
# ─────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    fullName: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)


class RegisterData(BaseModel):
    userId: int
    isOnboarded: bool


class RegisterResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: RegisterData
    timestamp: str


class UserRead(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None = None
    is_logged_in: bool
    is_onboarded: bool
    current_level_id: int | None = None
    last_login_at: datetime | None = None
    onboarded_at: datetime | None = None
    xp: int
    streak: int
    gems: int
    hearts: int
    hearts_last_updated: datetime | None = None
    last_activity_date: date | None = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=255)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None


class LoginData(BaseModel):
    userId: int
    accessToken: str
    refreshToken: str


class LoginResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: LoginData
    timestamp: str


class CheckLoginStateRequest(BaseModel):
    sessionToken: str = Field(min_length=1)


class CheckLoginStateData(BaseModel):
    loginState: bool
    userId: int | None = None
    redirectScreen: str


class CheckLoginStateResponse(BaseModel):
    businessCode: str
    message: str
    timestamp: str
    data: CheckLoginStateData


class MarkUserLoggedInRequest(BaseModel):
    userId: int = Field(gt=0)
    isLoggedIn: bool = True
    lastLoginAt: datetime | None = None


class MarkUserLoggedInData(BaseModel):
    userId: int
    isLoggedIn: bool
    lastLoginAt: str
    redirectScreen: str


class MarkUserLoggedInResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: MarkUserLoggedInData
    timestamp: str


# ─────────────────────────────────────────────────────────────
# Onboarding
# ─────────────────────────────────────────────────────────────

class CreateOnboardingSessionRequest(BaseModel):
    userId: int = Field(gt=0)


class CreateOnboardingSessionData(BaseModel):
    sessionId: int
    status: str
    startedAt: str


class CreateOnboardingSessionResponse(BaseModel):
    success: bool = True
    businessCode: str
    message: str
    data: CreateOnboardingSessionData
    timestamp: str


class SaveOnboardingDetailsRequest(BaseModel):
    """
    Captures the three structured onboarding inputs.
    Called after the user picks level, intention, and daily time.
    If chosenLevelId > beginner, backend should then prompt a placement test.
    """
    sessionId: int = Field(gt=0)
    chosenLevelId: int = Field(gt=0)
    studyIntention: str = Field(min_length=1, max_length=255)
    dailyStudyMinutes: int = Field(gt=0)


class SaveOnboardingDetailsData(BaseModel):
    sessionId: int
    chosenLevelId: int
    requiresPlacementTest: bool  # backend sets this based on chosen level


class SaveOnboardingDetailsResponse(BaseModel):
    success: bool = True
    businessCode: str
    message: str
    data: SaveOnboardingDetailsData
    timestamp: str


class FinalizeOnboardingRequest(BaseModel):
    """
    Called after the optional placement test is done (or skipped for Beginner).
    resultLevelId is the final assigned level: either chosen level (if passed/Beginner)
    or Beginner (if failed).
    """
    sessionId: int = Field(gt=0)
    resultLevelId: int = Field(gt=0)
    testAttemptId: int | None = None  # null if Beginner, no test taken


class FinalizeOnboardingData(BaseModel):
    sessionId: int
    status: str
    resultLevelId: int
    completedAt: str


class FinalizeOnboardingResponse(BaseModel):
    success: bool = True
    businessCode: str
    message: str
    data: FinalizeOnboardingData
    timestamp: str


class MarkUserOnboardedRequest(BaseModel):
    userId: int = Field(gt=0)


class MarkUserOnboardedData(BaseModel):
    userId: int
    isOnboarded: bool
    currentLevelId: int
    updatedAt: str


class MarkUserOnboardedResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: MarkUserOnboardedData
    timestamp: str


class LearnerProfileRead(BaseModel):
    id: int
    user_id: int
    target_level_id: int | None = None
    study_intention: str | None = None
    daily_study_minutes: int | None = None
    experience: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class UpsertLearnerProfileRequest(BaseModel):
    userId: int = Field(gt=0)
    targetLevelId: int = Field(gt=0)
    studyIntention: str = Field(min_length=1, max_length=255)
    dailyStudyMinutes: int = Field(gt=0)
    experience: str = Field(min_length=1, max_length=50)


class UpsertLearnerProfileData(BaseModel):
    profileId: int
    userId: int
    targetLevelId: int
    updatedAt: str


class UpsertLearnerProfileResponse(BaseModel):
    success: bool = True
    businessCode: str
    message: str
    data: UpsertLearnerProfileData
    timestamp: str


# ─────────────────────────────────────────────────────────────
# Tests  (shared: placement + level-up)
# ─────────────────────────────────────────────────────────────

class TestRead(BaseModel):
    id: int
    code: str | None = None
    title: str
    test_type: str
    target_level_id: int
    total_score: float | None = None
    passing_score: float | None = None
    duration_minutes: int | None = None
    status: str | None = None
    model_config = ConfigDict(from_attributes=True)


class TestResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: TestRead
    timestamp: str


class TestQuestionRead(BaseModel):
    id: int
    test_id: int
    question_text: str
    question_type: str | None = None
    score_weight: float | None = None
    sort_order: int | None = None
    model_config = ConfigDict(from_attributes=True)


class TestQuestionListResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: list[TestQuestionRead]
    timestamp: str


class GetQuestionOptionsRequest(BaseModel):
    questionIds: list[int] = Field(min_length=1)


class TestQuestionOptionRead(BaseModel):
    id: int
    question_id: int
    option_text: str
    model_config = ConfigDict(from_attributes=True)


class TestQuestionOptionsResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: list[TestQuestionOptionRead]
    timestamp: str


class CreateTestAttemptRequest(BaseModel):
    testId: int = Field(gt=0)
    userId: int = Field(gt=0)


class CreateTestAttemptData(BaseModel):
    attemptId: int
    testId: int
    userId: int
    status: str
    startedAt: str


class CreateTestAttemptResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: CreateTestAttemptData
    timestamp: str


class TestAnswerSubmission(BaseModel):
    questionId: int = Field(gt=0)
    answerText: str = Field(min_length=1)


class SubmitTestAttemptRequest(BaseModel):
    attemptId: int = Field(gt=0)
    answers: list[TestAnswerSubmission] = Field(min_length=1)


class SubmitTestAttemptData(BaseModel):
    attemptId: int
    score: float
    passed: bool
    submittedAt: str


class SubmitTestAttemptResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: SubmitTestAttemptData
    timestamp: str


class TestAttemptRead(BaseModel):
    id: int
    test_id: int
    user_id: int
    score: float | None = None
    passed: bool | None = None
    status: str | None = None
    started_at: datetime | None = None
    submitted_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class TestAttemptResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: TestAttemptRead
    timestamp: str


# ─────────────────────────────────────────────────────────────
# Courses & Lessons
# ─────────────────────────────────────────────────────────────

class CourseRead(BaseModel):
    id: int
    title: str
    status: str | None = None
    level_id: int
    sort_order: int | None = None
    model_config = ConfigDict(from_attributes=True)


class CourseListResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: list[CourseRead]
    timestamp: str


class LessonRead(BaseModel):
    id: int
    course_id: int
    title: str
    content: str | None = None
    difficulty: str | None = None
    estimated_minutes: int | None = None
    status: str | None = None
    sort_order: int | None = None
    model_config = ConfigDict(from_attributes=True)


class LessonListResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: list[LessonRead]
    timestamp: str


# ─────────────────────────────────────────────────────────────
# Vocab skill  (flashcard + SRS)
# ─────────────────────────────────────────────────────────────

class VocabularyRead(BaseModel):
    id: int
    lesson_id: int
    kanji: str | None = None
    kana: str
    romaji: str
    meaning: str
    example_sentence: str | None = None
    example_translation: str | None = None
    xp_reward: int
    model_config = ConfigDict(from_attributes=True)


class VocabularyListResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: list[VocabularyRead]
    timestamp: str


class VocabQueueResponse(BaseModel):
    """Due cards for today's SRS review session."""
    success: bool
    businessCode: str
    message: str
    data: list[VocabularyRead]
    timestamp: str


class SRSReviewRequest(BaseModel):
    vocabId: int = Field(gt=0)
    result: str = Field(pattern=r"^(again|hard|good|easy)$")


class SRSReviewData(BaseModel):
    repetitions: int
    easeFactor: float
    intervalDays: int
    nextReviewAt: datetime
    xpEarned: int


class SRSReviewResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: SRSReviewData
    timestamp: str


# ─────────────────────────────────────────────────────────────
# Reading skill
# ─────────────────────────────────────────────────────────────

class ReadingOptionRead(BaseModel):
    id: int
    option_text: str
    model_config = ConfigDict(from_attributes=True)


class ReadingQuestionRead(BaseModel):
    id: int
    question_text: str
    sort_order: int | None = None
    options: list[ReadingOptionRead] = []
    model_config = ConfigDict(from_attributes=True)


class ReadingPassageRead(BaseModel):
    id: int
    title: str | None = None
    content_japanese: str
    content_vietnamese: str | None = None
    xp_reward: int
    questions: list[ReadingQuestionRead] = []
    model_config = ConfigDict(from_attributes=True)


class ReadingPassageResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: ReadingPassageRead
    timestamp: str


class ReadingAnswerSubmission(BaseModel):
    questionId: int = Field(gt=0)
    selectedOptionId: int = Field(gt=0)


class SubmitReadingAttemptRequest(BaseModel):
    passageId: int = Field(gt=0)
    userId: int = Field(gt=0)
    answers: list[ReadingAnswerSubmission] = Field(min_length=1)


class SubmitReadingAttemptData(BaseModel):
    attemptId: int
    score: float
    passed: bool
    xpEarned: int
    completedAt: str


class SubmitReadingAttemptResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: SubmitReadingAttemptData
    timestamp: str


# ─────────────────────────────────────────────────────────────
# Speaking skill  (scripted dialogue + free Kaiwa + pronunciation)
# ─────────────────────────────────────────────────────────────

class DialogueExchangeRead(BaseModel):
    id: int
    order_index: int
    speaker: str
    ja_text: str
    ja_romaji: str
    vi_text: str
    model_config = ConfigDict(from_attributes=True)


class DialogueRead(BaseModel):
    id: int
    title: str
    description: str | None = None
    xp_reward: int
    exchanges: list[DialogueExchangeRead] = []
    model_config = ConfigDict(from_attributes=True)


class DialogueResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: DialogueRead
    timestamp: str


class SubmitDialogueAttemptRequest(BaseModel):
    userId: int = Field(gt=0)
    dialogueId: int = Field(gt=0)
    aiScore: float = Field(ge=0, le=100)
    aiFeedback: str


class SubmitDialogueAttemptData(BaseModel):
    attemptId: int
    xpEarned: int
    completedAt: str


class SubmitDialogueAttemptResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: SubmitDialogueAttemptData
    timestamp: str


# Free AI conversation (Kaiwa)
class KaiwaHistoryItem(BaseModel):
    role: str
    content: str


class GenerateKaiwaRequest(BaseModel):
    history: list[KaiwaHistoryItem]


class GenerateKaiwaResponse(BaseModel):
    content: str
    romaji: str
    translation: str


# Pronunciation rating
class RatePronunciationRequest(BaseModel):
    expectedText: str
    userTranscript: str
    romaji: str = ""


class RatePronunciationResponse(BaseModel):
    score: int
    feedback: str
    isCorrect: bool


# ─────────────────────────────────────────────────────────────
# Writing skill  (kanji canvas + AI rating)
# ─────────────────────────────────────────────────────────────

class KanjiPracticeRead(BaseModel):
    id: int
    title: str
    kanji: str
    difficulty: str | None = None
    xp_reward: int
    model_config = ConfigDict(from_attributes=True)


class KanjiPracticeResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: KanjiPracticeRead
    timestamp: str


class EvaluateWritingRequest(BaseModel):
    kanjiPracticeId: int = Field(gt=0)
    userId: int = Field(gt=0)
    imageBase64: str
    targetKanji: str


class EvaluateWritingData(BaseModel):
    attemptId: int
    score: int
    feedback: str
    xpEarned: int


class EvaluateWritingResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: EvaluateWritingData
    timestamp: str


# ─────────────────────────────────────────────────────────────
# Listening skill
# ─────────────────────────────────────────────────────────────

class ListeningOptionRead(BaseModel):
    id: int
    option_text: str
    model_config = ConfigDict(from_attributes=True)


class ListeningQuestionRead(BaseModel):
    id: int
    question_text: str
    sort_order: int | None = None
    options: list[ListeningOptionRead] = []
    model_config = ConfigDict(from_attributes=True)


class ListeningPracticeRead(BaseModel):
    id: int
    title: str
    source_type: str  # dialogue | song | sentences
    audio_url: str | None = None
    transcript_japanese: str | None = None
    transcript_vietnamese: str | None = None
    xp_reward: int
    questions: list[ListeningQuestionRead] = []
    model_config = ConfigDict(from_attributes=True)


class ListeningPracticeResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: ListeningPracticeRead
    timestamp: str


class ListeningAnswerSubmission(BaseModel):
    questionId: int = Field(gt=0)
    selectedOptionId: int = Field(gt=0)


class SubmitListeningAttemptRequest(BaseModel):
    practiceId: int = Field(gt=0)
    userId: int = Field(gt=0)
    answers: list[ListeningAnswerSubmission] = Field(min_length=1)


class SubmitListeningAttemptData(BaseModel):
    attemptId: int
    score: float
    passed: bool
    xpEarned: int
    completedAt: str


class SubmitListeningAttemptResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: SubmitListeningAttemptData
    timestamp: str


# ─────────────────────────────────────────────────────────────
# NLP utility  (MeCab tokenizer)
# ─────────────────────────────────────────────────────────────

class TokenizeRequest(BaseModel):
    text: str = Field(default="", max_length=5000)


class TokenizeItem(BaseModel):
    word: str
    reading: str
    pos: str


class TokenizeResponse(BaseModel):
    tokens: list[TokenizeItem]