-- SUB-001: Database Schema
-- Initial schema for Nuance - Executive Function Prosthetic
-- Run this migration in Supabase SQL editor or via CLI

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom enums
CREATE TYPE action_status AS ENUM (
  'inbox',      -- Captured but not reviewed
  'candidate',  -- Suggested for today (morning plan)
  'planned',    -- Committed to today's plan
  'active',     -- Currently being worked on
  'done',       -- Completed
  'dropped',    -- User decided not to do
  'rolled'      -- Rolled over from previous day
);

CREATE TYPE action_complexity AS ENUM (
  'atomic',     -- Single focused action (<30 min)
  'composite',  -- Multi-step but manageable (30-120 min)
  'project'     -- Needs breakdown (>2 hours)
);

-- Profiles table (extends auth.users)
CREATE TABLE profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  timezone TEXT DEFAULT 'UTC',
  telegram_chat_id TEXT UNIQUE,
  notification_channel TEXT DEFAULT 'email' CHECK (notification_channel IN ('email', 'telegram', 'both')),
  notification_enabled BOOLEAN DEFAULT true,
  onboarding_completed BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Actions table (tasks/to-dos)
CREATE TABLE actions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  parent_id UUID REFERENCES actions(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  raw_input TEXT,
  status action_status DEFAULT 'inbox',
  complexity action_complexity DEFAULT 'atomic',
  avoidance_weight INT CHECK (avoidance_weight BETWEEN 1 AND 5) DEFAULT 1,
  estimated_minutes INT DEFAULT 15,
  actual_minutes INT,
  planned_date DATE,
  completed_at TIMESTAMPTZ,
  position INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversations table (chat sessions)
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  type TEXT DEFAULT 'capture' CHECK (type IN ('capture', 'coaching', 'onboarding')),
  context_action_id UUID REFERENCES actions(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages table (conversation content)
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Token usage tracking (for AGT-005: Token Budgeting)
CREATE TABLE token_usage (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  input_tokens INT NOT NULL,
  output_tokens INT NOT NULL,
  endpoint TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_actions_user_status ON actions(user_id, status);
CREATE INDEX idx_actions_planned_date ON actions(user_id, planned_date);
CREATE INDEX idx_actions_parent ON actions(parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_token_usage_user_date ON token_usage(user_id, created_at);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_actions_updated_at
  BEFORE UPDATE ON actions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at
  BEFORE UPDATE ON conversations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable REPLICA IDENTITY for real-time (SUB-013)
ALTER TABLE actions REPLICA IDENTITY FULL;
ALTER TABLE profiles REPLICA IDENTITY FULL;

-- Profile creation trigger (creates profile when user signs up)
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id)
  VALUES (NEW.id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Comments for documentation
COMMENT ON TABLE profiles IS 'User profiles extending Supabase auth.users';
COMMENT ON TABLE actions IS 'Tasks/to-dos with ADHD-aware metadata';
COMMENT ON TABLE conversations IS 'Chat sessions for capture and coaching';
COMMENT ON TABLE messages IS 'Individual messages within conversations';
COMMENT ON TABLE token_usage IS 'AI token usage tracking for budgeting';

COMMENT ON COLUMN actions.avoidance_weight IS 'Emotional resistance score 1-5 (5=high avoidance)';
COMMENT ON COLUMN actions.complexity IS 'Task complexity: atomic/composite/project';
COMMENT ON COLUMN profiles.notification_channel IS 'Preferred notification: email/telegram/both';
