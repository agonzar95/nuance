-- SUB-002: Row Level Security Policies
-- Enables RLS on all user-owned tables and creates policies for data isolation
-- Run after 001_initial_schema.sql

-- =============================================================================
-- Enable Row Level Security
-- =============================================================================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE token_usage ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- Profiles Policies
-- Users can only access their own profile (id matches auth.uid())
-- =============================================================================

CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id)
  WITH CHECK (auth.uid() = id);

-- Note: INSERT is handled by trigger (handle_new_user)
-- Note: DELETE not allowed - profiles persist with auth.users

-- =============================================================================
-- Actions Policies
-- Users can only access their own actions (user_id matches auth.uid())
-- =============================================================================

CREATE POLICY "Users can view own actions"
  ON actions FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own actions"
  ON actions FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own actions"
  ON actions FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own actions"
  ON actions FOR DELETE
  USING (auth.uid() = user_id);

-- =============================================================================
-- Conversations Policies
-- Users can only access their own conversations
-- =============================================================================

CREATE POLICY "Users can view own conversations"
  ON conversations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own conversations"
  ON conversations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own conversations"
  ON conversations FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own conversations"
  ON conversations FOR DELETE
  USING (auth.uid() = user_id);

-- =============================================================================
-- Messages Policies
-- Users can access messages in conversations they own
-- (Check via conversation ownership rather than direct user_id)
-- =============================================================================

CREATE POLICY "Users can view messages in own conversations"
  ON messages FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM conversations
      WHERE conversations.id = messages.conversation_id
      AND conversations.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can insert messages in own conversations"
  ON messages FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM conversations
      WHERE conversations.id = messages.conversation_id
      AND conversations.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can update messages in own conversations"
  ON messages FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM conversations
      WHERE conversations.id = messages.conversation_id
      AND conversations.user_id = auth.uid()
    )
  )
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM conversations
      WHERE conversations.id = messages.conversation_id
      AND conversations.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can delete messages in own conversations"
  ON messages FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM conversations
      WHERE conversations.id = messages.conversation_id
      AND conversations.user_id = auth.uid()
    )
  );

-- =============================================================================
-- Token Usage Policies
-- Users can view their own token usage (read-only from client perspective)
-- Insert is done by backend with service role key
-- =============================================================================

CREATE POLICY "Users can view own token usage"
  ON token_usage FOR SELECT
  USING (auth.uid() = user_id);

-- Note: INSERT/UPDATE/DELETE for token_usage is done by backend
-- with service role key (bypasses RLS)

-- =============================================================================
-- Service Role Bypass
-- The backend uses service role key which bypasses RLS
-- This is by design for admin operations and background jobs
-- =============================================================================

COMMENT ON POLICY "Users can view own profile" ON profiles IS 'RLS: Users see only their own profile';
COMMENT ON POLICY "Users can view own actions" ON actions IS 'RLS: Users see only their own actions';
COMMENT ON POLICY "Users can view own conversations" ON conversations IS 'RLS: Users see only their own conversations';
COMMENT ON POLICY "Users can view messages in own conversations" ON messages IS 'RLS: Users see messages in conversations they own';
COMMENT ON POLICY "Users can view own token usage" ON token_usage IS 'RLS: Users can view their AI usage stats';
