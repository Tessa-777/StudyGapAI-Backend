-- StudyGapAI schema baseline (aligns with brief)
-- Note: gen_random_uuid() is built into PostgreSQL 13+, no extension needed

-- 1. USERS TABLE
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  email varchar(255) not null,
  name varchar(255) not null,
  phone varchar(20),
  target_score int,
  created_at timestamp with time zone default now(),
  last_active timestamp with time zone default now()
);

create unique index if not exists idx_users_email on users(email);

-- 2. TOPICS TABLE
create table if not exists topics (
  id uuid primary key default gen_random_uuid(),
  name varchar(100) not null,
  description text,
  prerequisite_topic_ids uuid[],
  jamb_weight float
);

-- 3. QUESTIONS TABLE
create table if not exists questions (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid references topics(id) on delete set null,
  question_text text not null,
  option_a text not null,
  option_b text not null,
  option_c text not null,
  option_d text not null,
  correct_answer varchar(1) not null check (correct_answer in ('A', 'B', 'C', 'D')),
  difficulty varchar(20) check (difficulty in ('easy', 'medium', 'hard')),
  subtopic varchar(100)
);

-- 4. DIAGNOSTIC_QUIZZES TABLE
create table if not exists diagnostic_quizzes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  started_at timestamp with time zone default now(),
  completed_at timestamp with time zone,
  total_questions int default 30,
  correct_answers int default 0,
  score_percentage float default 0.0
);

-- 5. QUIZ_RESPONSES TABLE
create table if not exists quiz_responses (
  id uuid primary key default gen_random_uuid(),
  quiz_id uuid references diagnostic_quizzes(id) on delete cascade,
  question_id uuid references questions(id) on delete set null,
  student_answer varchar(1) check (student_answer in ('A', 'B', 'C', 'D')),
  correct_answer varchar(1) check (correct_answer in ('A', 'B', 'C', 'D')),
  is_correct boolean,
  explanation_text text,
  time_spent_seconds int
);

-- 6. AI_DIAGNOSTICS TABLE
create table if not exists ai_diagnostics (
  id uuid primary key default gen_random_uuid(),
  quiz_id uuid references diagnostic_quizzes(id) on delete cascade,
  weak_topics jsonb,
  strong_topics jsonb,
  analysis_summary text,
  projected_score int,
  foundational_gaps jsonb,
  generated_at timestamp with time zone default now()
);

-- 7. STUDY_PLANS TABLE
create table if not exists study_plans (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  diagnostic_id uuid references ai_diagnostics(id) on delete cascade,
  plan_data jsonb,
  created_at timestamp with time zone default now(),
  updated_at timestamp with time zone default now()
);

-- 8. PROGRESS_TRACKING TABLE
create table if not exists progress_tracking (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  topic_id uuid references topics(id) on delete set null,
  status varchar(20) check (status in ('not_started', 'in_progress', 'completed')),
  resources_viewed int default 0,
  practice_problems_completed int default 0,
  last_updated timestamp with time zone default now()
);

-- 9. RESOURCES TABLE
create table if not exists resources (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid references topics(id) on delete set null,
  type varchar(20) check (type in ('video', 'practice_set')),
  title varchar(255) not null,
  url text not null,
  source varchar(100),
  duration_minutes int,
  difficulty varchar(20) check (difficulty in ('easy', 'medium', 'hard')),
  upvotes int default 0
);

-- Create indexes for better query performance
create index if not exists idx_questions_topic_id on questions(topic_id);
create index if not exists idx_quiz_responses_quiz_id on quiz_responses(quiz_id);
create index if not exists idx_diagnostic_quizzes_user_id on diagnostic_quizzes(user_id);
create index if not exists idx_ai_diagnostics_quiz_id on ai_diagnostics(quiz_id);
create index if not exists idx_study_plans_user_id on study_plans(user_id);
create index if not exists idx_progress_tracking_user_id on progress_tracking(user_id);
create index if not exists idx_resources_topic_id on resources(topic_id);


