from datetime import date, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    fullName: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(pattern=r"^\d{10,15}$")
    passwordHash: str = Field(min_length=1, max_length=255)


class UserCreateData(BaseModel):
    userId: int
    accountStatus: str
    isLoggedIn: bool


class UserCreateResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: UserCreateData
    timestamp: str


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str | None = None
    full_name: str | None = None
    phone: str | None = None
    is_logged_in: bool | None = None
    last_login_at: datetime | None = None
    is_onboarded: bool | None = None
    onboarded_at: datetime | None = None
    xp: int | None = None
    streak: int | None = None
    gems: int | None = None
    hearts: int | None = None
    hearts_last_updated: datetime | None = None
    last_activity_date: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    emailOrPhone: str = Field(min_length=1, max_length=255)
    passwordHash: str = Field(min_length=1, max_length=255)
    deviceId: str | None = Field(default=None, max_length=255)
    platform: str | None = Field(default="mobile", pattern=r"^(mobile|web)$")

class Token(BaseModel):
    access_token: str
    token_type: str


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


class TokenData(BaseModel):
    id: int | None = None


class TokenizeRequest(BaseModel):
    text: str = Field(default="", max_length=5000)

class TokenizeItem(BaseModel):
    word: str
    reading: str
    pos: str

class TokenizeResponse(BaseModel):
    tokens: list[TokenizeItem]


class CheckUserByEmailOrPhoneRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = Field(default=None, pattern=r"^\d{10,15}$")
    sessionToken: str | None = None

    @model_validator(mode="after")
    def validate_contact(self):
        if not self.email and not self.phone:
            raise ValueError("email or phone is required")
        return self


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


class CheckUserByEmailOrPhoneData(BaseModel):
    existsFlag: bool
    userId: int | None = None


class CheckUserByEmailOrPhoneResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: CheckUserByEmailOrPhoneData
    timestamp: str


class EvaluateSpeakingRequest(BaseModel):
    transcript: str
    expected_text: str
    romaji: Optional[str] = None  # Cho phép truyền romaji hoặc không

class EvaluateSpeakingResponse(BaseModel):
    accuracy_score: int
    fluency_score: int
    score: int                     # Điểm tổng quát (tương đương với 'score' cũ)
    feedback: str                  # Nhận xét bằng tiếng Việt
    tips: List[str] = []           # Lời khuyên cải thiện
    is_correct: bool               # Đạt hay không đạt (score >= 60)

class KaiwaHistoryItem(BaseModel):
    role: str
    content: str

class GenerateKaiwaRequest(BaseModel):
    history: List[KaiwaHistoryItem]

class GenerateKaiwaResponse(BaseModel):
    content: str
    romaji: str
    translation: str

class SaveSpeakingAttemptRequest(BaseModel):
    exercise_id: int
    answer_text: str
    score: float
    feedback: str
    duration_seconds: int

class SaveSpeakingAttemptResponse(BaseModel):
    attempt_id: int
    success: bool

class SpeakingExerciseItem(BaseModel):
    id: int
    prompt: str
    correct_answer: str
    explanation: Optional[str]

class GetExercisesResponse(BaseModel):
    exercises: List[SpeakingExerciseItem]
    
    
class EvaluateWritingRequest(BaseModel):
    image_base64: str
    target_kanji: str

class EvaluateWritingResponse(BaseModel):
    score: int
    feedback: str
    xp_awarded: int
    


class CreateOnboardingSessionRequest(BaseModel):
    userId: int = Field(gt=0)
    sessionToken: str | None = Field(default=None, min_length=1)


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


class SaveOnboardingAnswerRequest(BaseModel):
    sessionId: int = Field(gt=0)
    questionCode: str = Field(min_length=1, max_length=100)
    answerValue: str = Field(min_length=1, max_length=500)


class SaveOnboardingAnswerData(BaseModel):
    answerId: int
    sessionId: int
    questionCode: str
    savedAt: str


class SaveOnboardingAnswerResponse(BaseModel):
    success: bool = True
    businessCode: str
    message: str
    data: SaveOnboardingAnswerData
    timestamp: str


class OnboardingAnswerItem(BaseModel):
    answerId: int
    questionCode: str
    answerValue: str
    updatedAt: str


class LoadOnboardingAnswersData(BaseModel):
    sessionId: int
    answers: list[OnboardingAnswerItem]


class LoadOnboardingAnswersResponse(BaseModel):
    success: bool = True
    businessCode: str
    message: str
    data: LoadOnboardingAnswersData
    timestamp: str


class AnalyzeOnboardingAnswerItem(BaseModel):
    questionCode: str = Field(min_length=1, max_length=100)
    answerValue: str = Field(min_length=1, max_length=500)


class AnalyzePlacementAttemptPayload(BaseModel):
    attemptId: int = Field(gt=0)
    score: float = Field(ge=0, le=100)


class AnalyzeOnboardingDataRequest(BaseModel):
    answerList: list[AnalyzeOnboardingAnswerItem] = Field(min_length=1)
    placementAttempt: AnalyzePlacementAttemptPayload


class AnalyzeOnboardingDataResult(BaseModel):
    currentLevel: str
    recommendedLevel: str
    learningStyle: str
    studyIntensity: str
    analysisVersion: str


class AnalyzeOnboardingDataResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: AnalyzeOnboardingDataResult
    timestamp: str


class FinalizeOnboardingSessionRequest(BaseModel):
    sessionId: int = Field(gt=0)
    sessionToken: str | None = Field(default=None, min_length=1)


class FinalizeOnboardingSessionData(BaseModel):
    sessionId: int
    status: str
    completedAt: str


class FinalizeOnboardingSessionResponse(BaseModel):
    success: bool = True
    businessCode: str
    message: str
    data: FinalizeOnboardingSessionData
    timestamp: str


class SubmitOnboardingRequest(BaseModel):
    level: str = Field(min_length=1, max_length=50)
    goal: str = Field(min_length=1, max_length=255)
    time: str = Field(min_length=1, max_length=50)


class SubmitOnboardingData(BaseModel):
    sessionId: int
    status: str
    level: str
    goal: str
    time: str
    completedAt: str


class SubmitOnboardingResponse(BaseModel):
    success: bool = True
    businessCode: str
    message: str
    data: SubmitOnboardingData
    timestamp: str


class UpsertLearnerProfileRequest(BaseModel):
    userId: int = Field(gt=0)
    targetLevel: str = Field(min_length=1, max_length=50)
    targetGoal: str = Field(min_length=1, max_length=255)
    experience: str = Field(min_length=1, max_length=50)
    testResult: float = Field(ge=0, le=100)


class UpsertLearnerProfileData(BaseModel):
    profileId: int
    userId: int
    currentLevel: str
    targetLevel: str
    updatedAt: str


class UpsertLearnerProfileResponse(BaseModel):
    success: bool = True
    businessCode: str
    message: str
    data: UpsertLearnerProfileData
    timestamp: str


class ConfirmCommitmentRequest(BaseModel):
    sessionToken: str = Field(min_length=1)


class ConfirmCommitmentData(BaseModel):
    loginState: bool
    userId: int | None = None
    redirectScreen: str


class ConfirmCommitmentResponse(BaseModel):
    businessCode: str
    message: str
    timestamp: str
    data: ConfirmCommitmentData


class MarkUserOnboardedRequest(BaseModel):
    userId: int = Field(gt=0)
    sessionToken: str | None = Field(default=None, min_length=1)


class MarkUserOnboardedData(BaseModel):
    userId: int
    isOnboarded: bool
    updatedAt: str


class MarkUserOnboardedResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: MarkUserOnboardedData
    timestamp: str


class PlacementTestItem(BaseModel):
    testId: int
    testCode: str | None = None
    title: str
    testType: str | None = None
    totalScore: float | None = None
    durationMinutes: int | None = None
    status: str | None = None


class PlacementTestResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: PlacementTestItem
    timestamp: str


class TestQuestionItem(BaseModel):
    questionId: int
    questionText: str
    questionType: str | None = None
    scoreWeight: float | None = None
    sortOrder: int | None = None


class TestQuestionListResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: list[TestQuestionItem]
    timestamp: str


class GetQuestionOptionsRequest(BaseModel):
    questionIds: list[int] = Field(min_length=1)


class TestQuestionOptionItem(BaseModel):
    optionId: int
    questionId: int
    optionText: str


class TestQuestionOptionsResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: list[TestQuestionOptionItem]
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


class TestAttemptAnswerSubmission(BaseModel):
    questionId: int = Field(gt=0)
    answerText: str = Field(min_length=1)


class SaveTestAttemptAnswersRequest(BaseModel):
    attemptId: int = Field(gt=0)
    answers: list[TestAttemptAnswerSubmission] = Field(min_length=1)


class SaveTestAttemptAnswersData(BaseModel):
    attemptId: int
    status: str
    submittedAt: str
    score: float
    levelEstimate: str


class SaveTestAttemptAnswersResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: SaveTestAttemptAnswersData
    timestamp: str


class LatestTestAttemptData(BaseModel):
    attemptId: int
    testId: int
    userId: int
    status: str | None = None
    startedAt: str | None = None
    submittedAt: str | None = None
    score: float | None = None
    levelEstimate: str | None = None


class LatestTestAttemptResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: LatestTestAttemptData
    timestamp: str


class SessionTokenPayload(BaseModel):
    sessionToken: str | None = Field(default=None, min_length=1)


class CourseRecommendationItem(BaseModel):
    courseId: int
    courseName: str
    targetLevel: str
    thumbnailUrl: str | None = None
    estimatedDuration: int


class CourseRecommendationResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: list[CourseRecommendationItem]
    timestamp: str


class CourseLessonItem(BaseModel):
    lessonId: int
    lessonTitle: str
    lessonOrder: int
    estimatedDuration: int
    isPreviewAvailable: bool
    lessonType: str | None = None


class CourseLessonResponse(BaseModel):
    success: bool
    businessCode: str
    message: str
    data: list[CourseLessonItem]
    timestamp: str


class ReviewRequest(BaseModel):
    vocab_id: int
    quality_score: int



class LessonResult(BaseModel):
    xp_gained: int
    vocab_learned: list[int]

class OptionResponse(BaseModel):
    id: int
    text: str

class QuestionResponse(BaseModel):
    id: int
    prompt: str
    options: List[OptionResponse]

class ReadingPassageResponse(BaseModel):
    id: int
    title: str
    japanese: str
    vietnamese: Optional[str] = None

class ReadingLessonResponse(BaseModel):
    id: int
    title: str
    content: str
    difficulty: str
    passages: List[ReadingPassageResponse] = Field(default_factory=list)
    questions: List[QuestionResponse]
    words: Dict[str, Dict[str, str]]

class QuizSubmitRequest(BaseModel):
    answers: Dict[int, int]  # exercise_id -> option_id

class QuizSubmitResponse(BaseModel):
    score: int
    max_score: int
    xp_gained: int
    is_passed: bool

class RatePronunciationRequest(BaseModel):
    expected_text: str      # câu Japanese gốc
    user_transcript: str    # STT output từ browser
    romaji: str = ""

class RatePronunciationResponse(BaseModel):
    score: int
    feedback: str
    is_correct: bool