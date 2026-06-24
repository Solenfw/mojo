from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None
    full_name: str | None = None
    phone: str | None = None


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str | None = None
    full_name: str | None = None
    phone: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


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


class EvaluateSpeakingRequest(BaseModel):
    transcript: str
    expected_text: str

class EvaluateSpeakingResponse(BaseModel):
    accuracy_score: int
    fluency_score: int
    feedback: str
    tips: List[str]

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
