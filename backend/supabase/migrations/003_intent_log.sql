-- INF-007: Intent Log Recording
-- Records all user intents and AI responses for analytics and prompt improvement

-- Intent log table
CREATE TABLE intent_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users ON DELETE CASCADE NOT NULL,
  raw_input TEXT NOT NULL,
  classified_intent TEXT,  -- 'capture', 'coaching', 'command'
  extraction_result JSONB,
  ai_response TEXT,
  prompt_version TEXT,  -- Version of prompt used (AGT-015)
  input_tokens INT,
  output_tokens INT,
  processing_time_ms INT,  -- Time taken to process
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for querying user history and analytics
CREATE INDEX idx_intent_log_user_date ON intent_log(user_id, created_at DESC);
CREATE INDEX idx_intent_log_intent ON intent_log(classified_intent);
CREATE INDEX idx_intent_log_prompt_version ON intent_log(prompt_version);

-- Enable RLS
ALTER TABLE intent_log ENABLE ROW LEVEL SECURITY;

-- Policy: Users cannot read their own logs (privacy/analytics-only data)
-- Admin access via service role bypasses RLS
-- No user-facing policies - this is internal analytics data

COMMENT ON TABLE intent_log IS 'Records all AI interactions for analytics and prompt improvement';
COMMENT ON COLUMN intent_log.classified_intent IS 'Intent type: capture/coaching/command';
COMMENT ON COLUMN intent_log.extraction_result IS 'Structured data extracted from input';
COMMENT ON COLUMN intent_log.prompt_version IS 'Version ID of the prompt used for this call';
