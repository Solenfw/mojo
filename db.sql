-- ==========================================
-- 1. NHÓM BẢNG ĐỘC LẬP (Tạo đầu tiên)
-- ==========================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    avatar_url TEXT,
    phone VARCHAR(20),
    status VARCHAR(50), -- hoạt động/ngưng/khóa
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL, -- student/business/admin/teacher
    name VARCHAR(100) NOT NULL
);

CREATE TABLE business_orgs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    tax_code VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tests (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE,
    title VARCHAR(255) NOT NULL,
    test_type VARCHAR(100),
    total_score DECIMAL(5,2),
    duration_minutes INT,
    status VARCHAR(50)
);

CREATE TABLE content_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    parent_id INT,
    -- Tự tham chiếu cấp cha con
    FOREIGN KEY (parent_id) REFERENCES content_categories(id) ON DELETE SET NULL
);

-- ==========================================
-- 2. NHÓM BẢNG GẮN VỚI USERS & ORGS
-- ==========================================

CREATE TABLE user_roles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY (user_id, role_id), -- Khóa chính kép
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE learner_profiles (
    user_id INT PRIMARY KEY, -- PK/FK
    gender VARCHAR(20),
    dob DATE,
    target_language VARCHAR(50),
    current_level VARCHAR(50),
    target_level VARCHAR(50),
    study_goal TEXT,
    study_mode VARCHAR(50),
    commitment_hours_per_week INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    level VARCHAR(50),
    status VARCHAR(50),
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE business_members (
    id SERIAL PRIMARY KEY,
    business_org_id INT NOT NULL,
    user_id INT NOT NULL,
    member_role VARCHAR(100),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (business_org_id) REFERENCES business_orgs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE business_student_assignments (
    id SERIAL PRIMARY KEY,
    business_org_id INT NOT NULL,
    user_id INT NOT NULL,
    assigned_by INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    FOREIGN KEY (business_org_id) REFERENCES business_orgs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE CASCADE
);

-- ==========================================
-- 3. HỒ SƠ & ONBOARDING & LỘ TRÌNH
-- ==========================================

CREATE TABLE onboarding_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result_level VARCHAR(50),
    result_goal TEXT,
    status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE onboarding_answers (
    id SERIAL PRIMARY KEY,
    session_id INT NOT NULL,
    question_code VARCHAR(100),
    question_text TEXT,
    answer_text TEXT,
    answer_value VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES onboarding_sessions(id) ON DELETE CASCADE
);

CREATE TABLE learning_plans (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    target_level VARCHAR(50),
    goal_type VARCHAR(50),
    start_date DATE,
    end_date DATE,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE learning_plan_steps (
    id SERIAL PRIMARY KEY,
    plan_id INT NOT NULL,
    step_order INT NOT NULL,
    module_type VARCHAR(100),
    content_id INT, -- Liên kết động, KHÔNG có FOREIGN KEY vật lý
    estimated_minutes INT,
    is_required BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (plan_id) REFERENCES learning_plans(id) ON DELETE CASCADE
);

-- ==========================================
-- 4. BÀI HỌC VÀ BÀI TẬP (EXERCISES)
-- ==========================================

CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    course_id INT NOT NULL,
    lesson_type VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    content TEXT,
    difficulty VARCHAR(50),
    estimated_minutes INT,
    status VARCHAR(50),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE lesson_resources (
    id SERIAL PRIMARY KEY,
    lesson_id INT NOT NULL,
    resource_type VARCHAR(100),
    resource_url TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
);

CREATE TABLE exercises (
    id SERIAL PRIMARY KEY,
    lesson_id INT, -- Có thể rỗng
    exercise_type VARCHAR(100),
    prompt TEXT NOT NULL,
    correct_answer TEXT,
    explanation TEXT,
    score_weight DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL
);

CREATE TABLE exercise_options (
    id SERIAL PRIMARY KEY,
    exercise_id INT NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
);

CREATE TABLE exercise_attempts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    exercise_id INT NOT NULL,
    answer_text TEXT,
    is_correct BOOLEAN,
    score DECIMAL(5,2),
    ai_feedback TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
);

-- ==========================================
-- 5. BÀI KIỂM TRA (TESTS)
-- ==========================================

CREATE TABLE test_questions (
    id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(100),
    correct_answer TEXT,
    score_weight DECIMAL(5,2),
    sort_order INT,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

CREATE TABLE test_question_options (
    id SERIAL PRIMARY KEY,
    question_id INT NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    FOREIGN KEY (question_id) REFERENCES test_questions(id) ON DELETE CASCADE
);

CREATE TABLE test_attempts (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    test_id INT NOT NULL,
    started_at TIMESTAMP,
    submitted_at TIMESTAMP,
    score DECIMAL(5,2),
    level_estimate VARCHAR(50),
    status VARCHAR(50),
    ai_reviewed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
);

CREATE TABLE test_attempt_answers (
    id SERIAL PRIMARY KEY,
    attempt_id INT NOT NULL,
    question_id INT NOT NULL,
    answer_text TEXT,
    is_correct BOOLEAN,
    score DECIMAL(5,2),
    FOREIGN KEY (attempt_id) REFERENCES test_attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES test_questions(id) ON DELETE CASCADE
);

-- ==========================================
-- 6. THEO DÕI & AI & GIAO TIẾP
-- ==========================================

CREATE TABLE study_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration_minutes INT,
    study_source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    content_type VARCHAR(100),
    content_id INT NOT NULL,
    progress_percent DECIMAL(5,2),
    last_accessed_at TIMESTAMP,
    mastery_level VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE user_weaknesses (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    skill_type VARCHAR(100),
    topic_name VARCHAR(255),
    weakness_score DECIMAL(5,2),
    source VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    user_id INT, -- Tùy chọn
    business_org_id INT, -- Tùy chọn
    report_type VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    summary TEXT,
    file_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (business_org_id) REFERENCES business_orgs(id) ON DELETE SET NULL
);

CREATE TABLE ai_conversations (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    context_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE ai_messages (
    id SERIAL PRIMARY KEY,
    conversation_id INT NOT NULL,
    sender_type VARCHAR(50),
    message_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id) ON DELETE CASCADE
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    notification_type VARCHAR(100),
    title VARCHAR(255),
    body TEXT,
    channel VARCHAR(50),
    send_at TIMESTAMP,
    sent_at TIMESTAMP,
    status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE feedbacks (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    category VARCHAR(100),
    content TEXT NOT NULL,
    rating INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==========================================
-- 7. LỚP HỌC WEBRTC & NHẬT KÝ QUẢN TRỊ
-- ==========================================

CREATE TABLE tutor_sessions (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL,
    tutor_id INT NOT NULL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    meeting_type VARCHAR(100),
    status VARCHAR(50),
    notes TEXT,
    -- Chứa 2 FK cùng trỏ về bảng users
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tutor_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE tutor_session_feedback (
    id SERIAL PRIMARY KEY,
    session_id INT NOT NULL,
    feedback_text TEXT,
    pronunciation_score DECIMAL(5,2),
    fluency_score DECIMAL(5,2),
    grammar_score DECIMAL(5,2),
    FOREIGN KEY (session_id) REFERENCES tutor_sessions(id) ON DELETE CASCADE
);

CREATE TABLE admin_actions (
    id SERIAL PRIMARY KEY,
    admin_id INT NOT NULL,
    action_type VARCHAR(100),
    target_type VARCHAR(100),
    target_id INT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);