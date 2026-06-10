from typing import Optional
import datetime
import decimal

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKeyConstraint, Identity, Index, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class BusinessOrgs(Base):
    __tablename__ = 'business_orgs'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='business_orgs_pkey'),
        UniqueConstraint('tax_code', name='business_orgs_tax_code_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    tax_code: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    address: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    business_members: Mapped[list['BusinessMembers']] = relationship('BusinessMembers', back_populates='business_org')
    business_student_assignments: Mapped[list['BusinessStudentAssignments']] = relationship('BusinessStudentAssignments', back_populates='business_org')
    reports: Mapped[list['Reports']] = relationship('Reports', back_populates='business_org')


class ContentCategories(Base):
    __tablename__ = 'content_categories'
    __table_args__ = (
        ForeignKeyConstraint(['parent_id'], ['content_categories.id'], ondelete='SET NULL', name='content_categories_parent_id_fkey'),
        PrimaryKeyConstraint('id', name='content_categories_pkey'),
        UniqueConstraint('slug', name='content_categories_slug_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer)

    parent: Mapped[Optional['ContentCategories']] = relationship('ContentCategories', remote_side=[id], back_populates='parent_reverse')
    parent_reverse: Mapped[list['ContentCategories']] = relationship('ContentCategories', remote_side=[parent_id], back_populates='parent')


class Homework(Base):
    __tablename__ = 'homework'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='homework_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
        UniqueConstraint('code', name='roles_code_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    user: Mapped[list['Users']] = relationship('Users', secondary='user_roles', back_populates='role')


class Tests(Base):
    __tablename__ = 'tests'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tests_pkey'),
        UniqueConstraint('code', name='tests_code_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50))
    test_type: Mapped[Optional[str]] = mapped_column(String(100))
    total_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String(50))

    test_attempts: Mapped[list['TestAttempts']] = relationship('TestAttempts', back_populates='test')
    test_questions: Mapped[list['TestQuestions']] = relationship('TestQuestions', back_populates='test')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        UniqueConstraint('username', name='users_username_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))

    role: Mapped[list['Roles']] = relationship('Roles', secondary='user_roles', back_populates='user')
    admin_actions: Mapped[list['AdminActions']] = relationship('AdminActions', back_populates='admin')
    ai_conversations: Mapped[list['AiConversations']] = relationship('AiConversations', back_populates='user')
    business_members: Mapped[list['BusinessMembers']] = relationship('BusinessMembers', back_populates='user')
    business_student_assignments_assigned_by: Mapped[list['BusinessStudentAssignments']] = relationship('BusinessStudentAssignments', foreign_keys='[BusinessStudentAssignments.assigned_by]', back_populates='users')
    business_student_assignments_user: Mapped[list['BusinessStudentAssignments']] = relationship('BusinessStudentAssignments', foreign_keys='[BusinessStudentAssignments.user_id]', back_populates='user')
    courses: Mapped[list['Courses']] = relationship('Courses', back_populates='users')
    feedbacks: Mapped[list['Feedbacks']] = relationship('Feedbacks', back_populates='user')
    learning_plans: Mapped[list['LearningPlans']] = relationship('LearningPlans', back_populates='user')
    notifications: Mapped[list['Notifications']] = relationship('Notifications', back_populates='user')
    onboarding_sessions: Mapped[list['OnboardingSessions']] = relationship('OnboardingSessions', back_populates='user')
    reports: Mapped[list['Reports']] = relationship('Reports', back_populates='user')
    study_sessions: Mapped[list['StudySessions']] = relationship('StudySessions', back_populates='user')
    test_attempts: Mapped[list['TestAttempts']] = relationship('TestAttempts', back_populates='user')
    tutor_sessions_student: Mapped[list['TutorSessions']] = relationship('TutorSessions', foreign_keys='[TutorSessions.student_id]', back_populates='student')
    tutor_sessions_tutor: Mapped[list['TutorSessions']] = relationship('TutorSessions', foreign_keys='[TutorSessions.tutor_id]', back_populates='tutor')
    user_progress: Mapped[list['UserProgress']] = relationship('UserProgress', back_populates='user')
    user_weaknesses: Mapped[list['UserWeaknesses']] = relationship('UserWeaknesses', back_populates='user')
    exercise_attempts: Mapped[list['ExerciseAttempts']] = relationship('ExerciseAttempts', back_populates='user')


# Alias generated model class for backward compatibility with auth code.
User = Users

class AdminActions(Base):
    __tablename__ = 'admin_actions'
    __table_args__ = (
        ForeignKeyConstraint(['admin_id'], ['users.id'], ondelete='CASCADE', name='admin_actions_admin_id_fkey'),
        PrimaryKeyConstraint('id', name='admin_actions_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    admin_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action_type: Mapped[Optional[str]] = mapped_column(String(100))
    target_type: Mapped[Optional[str]] = mapped_column(String(100))
    target_id: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    admin: Mapped['Users'] = relationship('Users', back_populates='admin_actions')


class AiConversations(Base):
    __tablename__ = 'ai_conversations'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='ai_conversations_user_id_fkey'),
        PrimaryKeyConstraint('id', name='ai_conversations_pkey'),
        Index('idx_ai_conversations_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    context_type: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['Users'] = relationship('Users', back_populates='ai_conversations')
    ai_messages: Mapped[list['AiMessages']] = relationship('AiMessages', back_populates='conversation')


class BusinessMembers(Base):
    __tablename__ = 'business_members'
    __table_args__ = (
        ForeignKeyConstraint(['business_org_id'], ['business_orgs.id'], ondelete='CASCADE', name='business_members_business_org_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='business_members_user_id_fkey'),
        PrimaryKeyConstraint('id', name='business_members_pkey'),
        Index('idx_business_members_org_id', 'business_org_id'),
        Index('idx_business_members_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    business_org_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    member_role: Mapped[Optional[str]] = mapped_column(String(100))
    joined_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    business_org: Mapped['BusinessOrgs'] = relationship('BusinessOrgs', back_populates='business_members')
    user: Mapped['Users'] = relationship('Users', back_populates='business_members')


class BusinessStudentAssignments(Base):
    __tablename__ = 'business_student_assignments'
    __table_args__ = (
        ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='CASCADE', name='business_student_assignments_assigned_by_fkey'),
        ForeignKeyConstraint(['business_org_id'], ['business_orgs.id'], ondelete='CASCADE', name='business_student_assignments_business_org_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='business_student_assignments_user_id_fkey'),
        PrimaryKeyConstraint('id', name='business_student_assignments_pkey'),
        Index('idx_business_assignments_org_id', 'business_org_id'),
        Index('idx_business_assignments_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    business_org_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned_by: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    status: Mapped[Optional[str]] = mapped_column(String(50))

    users: Mapped['Users'] = relationship('Users', foreign_keys=[assigned_by], back_populates='business_student_assignments_assigned_by')
    business_org: Mapped['BusinessOrgs'] = relationship('BusinessOrgs', back_populates='business_student_assignments')
    user: Mapped['Users'] = relationship('Users', foreign_keys=[user_id], back_populates='business_student_assignments_user')


class Courses(Base):
    __tablename__ = 'courses'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL', name='courses_created_by_fkey'),
        PrimaryKeyConstraint('id', name='courses_pkey'),
        UniqueConstraint('code', name='courses_code_key')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    level: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(50))
    created_by: Mapped[Optional[int]] = mapped_column(Integer)

    users: Mapped[Optional['Users']] = relationship('Users', back_populates='courses')
    lessons: Mapped[list['Lessons']] = relationship('Lessons', back_populates='course')


class Feedbacks(Base):
    __tablename__ = 'feedbacks'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='feedbacks_user_id_fkey'),
        PrimaryKeyConstraint('id', name='feedbacks_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    rating: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['Users'] = relationship('Users', back_populates='feedbacks')


class LearnerProfiles(Users):
    __tablename__ = 'learner_profiles'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='learner_profiles_user_id_fkey'),
        PrimaryKeyConstraint('user_id', name='learner_profiles_pkey')
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20))
    dob: Mapped[Optional[datetime.date]] = mapped_column(Date)
    target_language: Mapped[Optional[str]] = mapped_column(String(50))
    current_level: Mapped[Optional[str]] = mapped_column(String(50))
    target_level: Mapped[Optional[str]] = mapped_column(String(50))
    study_goal: Mapped[Optional[str]] = mapped_column(Text)
    study_mode: Mapped[Optional[str]] = mapped_column(String(50))
    commitment_hours_per_week: Mapped[Optional[int]] = mapped_column(Integer)


class LearningPlans(Base):
    __tablename__ = 'learning_plans'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='learning_plans_user_id_fkey'),
        PrimaryKeyConstraint('id', name='learning_plans_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_level: Mapped[Optional[str]] = mapped_column(String(50))
    goal_type: Mapped[Optional[str]] = mapped_column(String(50))
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['Users'] = relationship('Users', back_populates='learning_plans')
    learning_plan_steps: Mapped[list['LearningPlanSteps']] = relationship('LearningPlanSteps', back_populates='plan')


class Notifications(Base):
    __tablename__ = 'notifications'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='notifications_user_id_fkey'),
        PrimaryKeyConstraint('id', name='notifications_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    notification_type: Mapped[Optional[str]] = mapped_column(String(100))
    title: Mapped[Optional[str]] = mapped_column(String(255))
    body: Mapped[Optional[str]] = mapped_column(Text)
    channel: Mapped[Optional[str]] = mapped_column(String(50))
    send_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    status: Mapped[Optional[str]] = mapped_column(String(50))

    user: Mapped['Users'] = relationship('Users', back_populates='notifications')


class OnboardingSessions(Base):
    __tablename__ = 'onboarding_sessions'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='onboarding_sessions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='onboarding_sessions_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    result_level: Mapped[Optional[str]] = mapped_column(String(50))
    result_goal: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Optional[str]] = mapped_column(String(50))

    user: Mapped['Users'] = relationship('Users', back_populates='onboarding_sessions')
    onboarding_answers: Mapped[list['OnboardingAnswers']] = relationship('OnboardingAnswers', back_populates='session')


class Reports(Base):
    __tablename__ = 'reports'
    __table_args__ = (
        ForeignKeyConstraint(['business_org_id'], ['business_orgs.id'], ondelete='SET NULL', name='reports_business_org_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL', name='reports_user_id_fkey'),
        PrimaryKeyConstraint('id', name='reports_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    business_org_id: Mapped[Optional[int]] = mapped_column(Integer)
    report_type: Mapped[Optional[str]] = mapped_column(String(100))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    file_url: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    business_org: Mapped[Optional['BusinessOrgs']] = relationship('BusinessOrgs', back_populates='reports')
    user: Mapped[Optional['Users']] = relationship('Users', back_populates='reports')


class StudySessions(Base):
    __tablename__ = 'study_sessions'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='study_sessions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='study_sessions_pkey'),
        Index('idx_study_sessions_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    study_source: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['Users'] = relationship('Users', back_populates='study_sessions')


class TestAttempts(Base):
    __tablename__ = 'test_attempts'
    __table_args__ = (
        ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE', name='test_attempts_test_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='test_attempts_user_id_fkey'),
        PrimaryKeyConstraint('id', name='test_attempts_pkey'),
        Index('idx_test_attempts_test_id', 'test_id'),
        Index('idx_test_attempts_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    test_id: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    submitted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    level_estimate: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(50))
    ai_reviewed: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('false'))

    test: Mapped['Tests'] = relationship('Tests', back_populates='test_attempts')
    user: Mapped['Users'] = relationship('Users', back_populates='test_attempts')
    test_attempt_answers: Mapped[list['TestAttemptAnswers']] = relationship('TestAttemptAnswers', back_populates='attempt')


class TestQuestions(Base):
    __tablename__ = 'test_questions'
    __table_args__ = (
        ForeignKeyConstraint(['test_id'], ['tests.id'], ondelete='CASCADE', name='test_questions_test_id_fkey'),
        PrimaryKeyConstraint('id', name='test_questions_pkey'),
        Index('idx_test_questions_test_id', 'test_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    test_id: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[Optional[str]] = mapped_column(String(100))
    correct_answer: Mapped[Optional[str]] = mapped_column(Text)
    score_weight: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    sort_order: Mapped[Optional[int]] = mapped_column(Integer)

    test: Mapped['Tests'] = relationship('Tests', back_populates='test_questions')
    test_attempt_answers: Mapped[list['TestAttemptAnswers']] = relationship('TestAttemptAnswers', back_populates='question')
    test_question_options: Mapped[list['TestQuestionOptions']] = relationship('TestQuestionOptions', back_populates='question')


class TutorSessions(Base):
    __tablename__ = 'tutor_sessions'
    __table_args__ = (
        ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE', name='tutor_sessions_student_id_fkey'),
        ForeignKeyConstraint(['tutor_id'], ['users.id'], ondelete='CASCADE', name='tutor_sessions_tutor_id_fkey'),
        PrimaryKeyConstraint('id', name='tutor_sessions_pkey'),
        Index('idx_tutor_sessions_student_id', 'student_id'),
        Index('idx_tutor_sessions_tutor_id', 'tutor_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    student_id: Mapped[int] = mapped_column(Integer, nullable=False)
    tutor_id: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    end_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    meeting_type: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    student: Mapped['Users'] = relationship('Users', foreign_keys=[student_id], back_populates='tutor_sessions_student')
    tutor: Mapped['Users'] = relationship('Users', foreign_keys=[tutor_id], back_populates='tutor_sessions_tutor')
    tutor_session_feedback: Mapped[list['TutorSessionFeedback']] = relationship('TutorSessionFeedback', back_populates='session')


class UserProgress(Base):
    __tablename__ = 'user_progress'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_progress_user_id_fkey'),
        PrimaryKeyConstraint('id', name='user_progress_pkey'),
        Index('idx_user_progress_polymorphic', 'content_type', 'content_id'),
        Index('idx_user_progress_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    content_id: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[Optional[str]] = mapped_column(String(100))
    progress_percent: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    last_accessed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    mastery_level: Mapped[Optional[str]] = mapped_column(String(50))

    user: Mapped['Users'] = relationship('Users', back_populates='user_progress')


t_user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, primary_key=True),
    Column('role_id', Integer, primary_key=True),
    ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE', name='user_roles_role_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_roles_user_id_fkey'),
    PrimaryKeyConstraint('user_id', 'role_id', name='user_roles_pkey'),
    Index('idx_user_roles_role_id', 'role_id')
)


class UserWeaknesses(Base):
    __tablename__ = 'user_weaknesses'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_weaknesses_user_id_fkey'),
        PrimaryKeyConstraint('id', name='user_weaknesses_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_type: Mapped[Optional[str]] = mapped_column(String(100))
    topic_name: Mapped[Optional[str]] = mapped_column(String(255))
    weakness_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['Users'] = relationship('Users', back_populates='user_weaknesses')


class AiMessages(Base):
    __tablename__ = 'ai_messages'
    __table_args__ = (
        ForeignKeyConstraint(['conversation_id'], ['ai_conversations.id'], ondelete='CASCADE', name='ai_messages_conversation_id_fkey'),
        PrimaryKeyConstraint('id', name='ai_messages_pkey'),
        Index('idx_ai_messages_conv_id', 'conversation_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    conversation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    sender_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    conversation: Mapped['AiConversations'] = relationship('AiConversations', back_populates='ai_messages')


class LearningPlanSteps(Base):
    __tablename__ = 'learning_plan_steps'
    __table_args__ = (
        ForeignKeyConstraint(['plan_id'], ['learning_plans.id'], ondelete='CASCADE', name='learning_plan_steps_plan_id_fkey'),
        PrimaryKeyConstraint('id', name='learning_plan_steps_pkey'),
        Index('idx_learning_plan_steps_plan_id', 'plan_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    plan_id: Mapped[int] = mapped_column(Integer, nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    module_type: Mapped[Optional[str]] = mapped_column(String(100))
    content_id: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    is_required: Mapped[Optional[bool]] = mapped_column(Boolean, server_default=text('true'))

    plan: Mapped['LearningPlans'] = relationship('LearningPlans', back_populates='learning_plan_steps')


class Lessons(Base):
    __tablename__ = 'lessons'
    __table_args__ = (
        ForeignKeyConstraint(['course_id'], ['courses.id'], ondelete='CASCADE', name='lessons_course_id_fkey'),
        PrimaryKeyConstraint('id', name='lessons_pkey'),
        Index('idx_lessons_course_id', 'course_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    course_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    lesson_type: Mapped[Optional[str]] = mapped_column(String(100))
    content: Mapped[Optional[str]] = mapped_column(Text)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50))
    estimated_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[Optional[str]] = mapped_column(String(50))

    course: Mapped['Courses'] = relationship('Courses', back_populates='lessons')
    exercises: Mapped[list['Exercises']] = relationship('Exercises', back_populates='lesson')
    lesson_resources: Mapped[list['LessonResources']] = relationship('LessonResources', back_populates='lesson')


class OnboardingAnswers(Base):
    __tablename__ = 'onboarding_answers'
    __table_args__ = (
        ForeignKeyConstraint(['session_id'], ['onboarding_sessions.id'], ondelete='CASCADE', name='onboarding_answers_session_id_fkey'),
        PrimaryKeyConstraint('id', name='onboarding_answers_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, nullable=False)
    question_code: Mapped[Optional[str]] = mapped_column(String(100))
    question_text: Mapped[Optional[str]] = mapped_column(Text)
    answer_text: Mapped[Optional[str]] = mapped_column(Text)
    answer_value: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    session: Mapped['OnboardingSessions'] = relationship('OnboardingSessions', back_populates='onboarding_answers')


class TestAttemptAnswers(Base):
    __tablename__ = 'test_attempt_answers'
    __table_args__ = (
        ForeignKeyConstraint(['attempt_id'], ['test_attempts.id'], ondelete='CASCADE', name='test_attempt_answers_attempt_id_fkey'),
        ForeignKeyConstraint(['question_id'], ['test_questions.id'], ondelete='CASCADE', name='test_attempt_answers_question_id_fkey'),
        PrimaryKeyConstraint('id', name='test_attempt_answers_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    attempt_id: Mapped[int] = mapped_column(Integer, nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, nullable=False)
    answer_text: Mapped[Optional[str]] = mapped_column(Text)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean)
    score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    attempt: Mapped['TestAttempts'] = relationship('TestAttempts', back_populates='test_attempt_answers')
    question: Mapped['TestQuestions'] = relationship('TestQuestions', back_populates='test_attempt_answers')


class TestQuestionOptions(Base):
    __tablename__ = 'test_question_options'
    __table_args__ = (
        ForeignKeyConstraint(['question_id'], ['test_questions.id'], ondelete='CASCADE', name='test_question_options_question_id_fkey'),
        PrimaryKeyConstraint('id', name='test_question_options_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    question: Mapped['TestQuestions'] = relationship('TestQuestions', back_populates='test_question_options')


class TutorSessionFeedback(Base):
    __tablename__ = 'tutor_session_feedback'
    __table_args__ = (
        ForeignKeyConstraint(['session_id'], ['tutor_sessions.id'], ondelete='CASCADE', name='tutor_session_feedback_session_id_fkey'),
        PrimaryKeyConstraint('id', name='tutor_session_feedback_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback_text: Mapped[Optional[str]] = mapped_column(Text)
    pronunciation_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    fluency_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    grammar_score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))

    session: Mapped['TutorSessions'] = relationship('TutorSessions', back_populates='tutor_session_feedback')


class Exercises(Base):
    __tablename__ = 'exercises'
    __table_args__ = (
        ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='SET NULL', name='exercises_lesson_id_fkey'),
        PrimaryKeyConstraint('id', name='exercises_pkey'),
        Index('idx_exercises_lesson_id', 'lesson_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    lesson_id: Mapped[Optional[int]] = mapped_column(Integer)
    exercise_type: Mapped[Optional[str]] = mapped_column(String(100))
    correct_answer: Mapped[Optional[str]] = mapped_column(Text)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    score_weight: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))

    lesson: Mapped[Optional['Lessons']] = relationship('Lessons', back_populates='exercises')
    exercise_attempts: Mapped[list['ExerciseAttempts']] = relationship('ExerciseAttempts', back_populates='exercise')
    exercise_options: Mapped[list['ExerciseOptions']] = relationship('ExerciseOptions', back_populates='exercise')


class LessonResources(Base):
    __tablename__ = 'lesson_resources'
    __table_args__ = (
        ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE', name='lesson_resources_lesson_id_fkey'),
        PrimaryKeyConstraint('id', name='lesson_resources_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(Integer, nullable=False)
    resource_url: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)

    lesson: Mapped['Lessons'] = relationship('Lessons', back_populates='lesson_resources')


class ExerciseAttempts(Base):
    __tablename__ = 'exercise_attempts'
    __table_args__ = (
        ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='CASCADE', name='exercise_attempts_exercise_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='exercise_attempts_user_id_fkey'),
        PrimaryKeyConstraint('id', name='exercise_attempts_pkey'),
        Index('idx_exercise_attempts_exercise_id', 'exercise_id'),
        Index('idx_exercise_attempts_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    exercise_id: Mapped[int] = mapped_column(Integer, nullable=False)
    answer_text: Mapped[Optional[str]] = mapped_column(Text)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean)
    score: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(5, 2))
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text)
    submitted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), server_default=text('CURRENT_TIMESTAMP'))
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)

    exercise: Mapped['Exercises'] = relationship('Exercises', back_populates='exercise_attempts')
    user: Mapped['Users'] = relationship('Users', back_populates='exercise_attempts')


class ExerciseOptions(Base):
    __tablename__ = 'exercise_options'
    __table_args__ = (
        ForeignKeyConstraint(['exercise_id'], ['exercises.id'], ondelete='CASCADE', name='exercise_options_exercise_id_fkey'),
        PrimaryKeyConstraint('id', name='exercise_options_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    exercise_id: Mapped[int] = mapped_column(Integer, nullable=False)
    option_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)

    exercise: Mapped['Exercises'] = relationship('Exercises', back_populates='exercise_options')
