-- Secure RLS Policies for StudyGapAI with Supabase Auth
-- Run this SQL in Supabase SQL Editor after enabling Google OAuth

-- Step 1: Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE diagnostic_quizzes ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_diagnostics ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;

-- Step 2: Drop old permissive policies (if they exist)
DROP POLICY IF EXISTS "Users can read own profile" ON users;
DROP POLICY IF EXISTS "Users can insert own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Topics are publicly readable" ON topics;
DROP POLICY IF EXISTS "Questions are publicly readable" ON questions;
DROP POLICY IF EXISTS "Users can read own quizzes" ON diagnostic_quizzes;
DROP POLICY IF EXISTS "Users can create own quizzes" ON diagnostic_quizzes;
DROP POLICY IF EXISTS "Users can update own quizzes" ON diagnostic_quizzes;
DROP POLICY IF EXISTS "Users can read own quiz responses" ON quiz_responses;
DROP POLICY IF EXISTS "Users can insert own quiz responses" ON quiz_responses;
DROP POLICY IF EXISTS "Users can read own diagnostics" ON ai_diagnostics;
DROP POLICY IF EXISTS "Users can create own diagnostics" ON ai_diagnostics;
DROP POLICY IF EXISTS "Users can read own study plans" ON study_plans;
DROP POLICY IF EXISTS "Users can create own study plans" ON study_plans;
DROP POLICY IF EXISTS "Users can update own study plans" ON study_plans;
DROP POLICY IF EXISTS "Users can read own progress" ON progress_tracking;
DROP POLICY IF EXISTS "Users can manage own progress" ON progress_tracking;
DROP POLICY IF EXISTS "Resources are publicly readable" ON resources;

-- Step 3: Create secure policies using auth.uid()

-- PUBLIC TABLES (Read-only for everyone)
-- Topics: Public read access
CREATE POLICY "topics_public_read"
ON topics FOR SELECT
USING (true);

-- Questions: Public read access
CREATE POLICY "questions_public_read"
ON questions FOR SELECT
USING (true);

-- Resources: Public read access
CREATE POLICY "resources_public_read"
ON resources FOR SELECT
USING (true);

-- USER-SPECIFIC TABLES (Secure with auth.uid())
-- Users: Can only access own profile
CREATE POLICY "users_read_own"
ON users FOR SELECT
USING (id = auth.uid());

CREATE POLICY "users_insert_own"
ON users FOR INSERT
WITH CHECK (id = auth.uid());

CREATE POLICY "users_update_own"
ON users FOR UPDATE
USING (id = auth.uid())
WITH CHECK (id = auth.uid());

-- Diagnostic Quizzes: Can only access own quizzes
CREATE POLICY "quizzes_read_own"
ON diagnostic_quizzes FOR SELECT
USING (user_id = auth.uid());

CREATE POLICY "quizzes_insert_own"
ON diagnostic_quizzes FOR INSERT
WITH CHECK (user_id = auth.uid());

CREATE POLICY "quizzes_update_own"
ON diagnostic_quizzes FOR UPDATE
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());

-- Quiz Responses: Can only access responses for own quizzes
CREATE POLICY "responses_read_own"
ON quiz_responses FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM diagnostic_quizzes dq
    WHERE dq.id = quiz_responses.quiz_id
      AND dq.user_id = auth.uid()
  )
);

CREATE POLICY "responses_insert_own"
ON quiz_responses FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM diagnostic_quizzes dq
    WHERE dq.id = quiz_responses.quiz_id
      AND dq.user_id = auth.uid()
  )
);

-- AI Diagnostics: Can only access diagnostics for own quizzes
CREATE POLICY "diagnostics_read_own"
ON ai_diagnostics FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM diagnostic_quizzes dq
    WHERE dq.id = ai_diagnostics.quiz_id
      AND dq.user_id = auth.uid()
  )
);

CREATE POLICY "diagnostics_insert_own"
ON ai_diagnostics FOR INSERT
WITH CHECK (
  EXISTS (
    SELECT 1 FROM diagnostic_quizzes dq
    WHERE dq.id = ai_diagnostics.quiz_id
      AND dq.user_id = auth.uid()
  )
);

-- Study Plans: Can only access own study plans
CREATE POLICY "plans_read_own"
ON study_plans FOR SELECT
USING (user_id = auth.uid());

CREATE POLICY "plans_insert_own"
ON study_plans FOR INSERT
WITH CHECK (user_id = auth.uid());

CREATE POLICY "plans_update_own"
ON study_plans FOR UPDATE
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());

-- Progress Tracking: Can only access own progress
CREATE POLICY "progress_read_own"
ON progress_tracking FOR SELECT
USING (user_id = auth.uid());

CREATE POLICY "progress_insert_own"
ON progress_tracking FOR INSERT
WITH CHECK (user_id = auth.uid());

CREATE POLICY "progress_update_own"
ON progress_tracking FOR UPDATE
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());

-- Step 4: Create function to sync auth.users to public.users
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, name, created_at)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'name', NEW.email),
    NOW()
  )
  ON CONFLICT (id) DO UPDATE
  SET
    email = EXCLUDED.email,
    last_active = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 5: Create trigger to sync users on auth signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT OR UPDATE ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Verification: Check policies are created
SELECT schemaname, tablename, policyname, cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

