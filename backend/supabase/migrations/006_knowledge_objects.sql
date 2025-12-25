-- MEM-001: Knowledge Objects Table
-- Derived knowledge ledger for persisting agent-inferred knowledge objects
-- Stores taxonomy labels, breakdowns, insights, checkpoints, goals/plans/habits

-- =============================================================================
-- Knowledge Object Type Enum
-- =============================================================================

CREATE TYPE knowledge_object_type AS ENUM (
  'taxonomy_label',    -- 7-layer taxonomy classification
  'breakdown',         -- Atomic task breakdown tree
  'insight',           -- Psychological pattern detection
  'checkpoint',        -- Conversation checkpoint/summary
  'goal',              -- User-stated or inferred goal
  'plan',              -- Multi-step plan structure
  'habit',             -- Recurring behavior pattern
  'state_snapshot',    -- Entity state at a point in time
  'user_pattern',      -- Inferred user behavior pattern
  'coaching_note'      -- Coaching-derived observation
);

-- =============================================================================
-- Knowledge Objects Table
-- =============================================================================

CREATE TABLE knowledge_objects (
  -- Primary key
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- User ownership (required)
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Type classification
  type knowledge_object_type NOT NULL,

  -- Main payload (JSONB for flexibility)
  payload JSONB NOT NULL,

  -- Confidence and importance scores
  confidence NUMERIC(3, 2) CHECK (confidence >= 0 AND confidence <= 1) DEFAULT 0.5,
  importance INT CHECK (importance >= 0 AND importance <= 100) DEFAULT 50,

  -- Source linkage (optional references)
  source_message_id UUID NULL,  -- Would reference messages(id) if populated
  source_conversation_id UUID NULL REFERENCES conversations(id) ON DELETE SET NULL,
  source_action_id UUID NULL REFERENCES actions(id) ON DELETE SET NULL,

  -- Natural key for idempotency (type + source combination)
  natural_key TEXT NULL,

  -- Validity window for TTL/decay support
  valid_from TIMESTAMPTZ DEFAULT NOW(),
  valid_to TIMESTAMPTZ NULL,  -- NULL means no expiry

  -- Provenance tracking
  model_id TEXT NULL,
  prompt_version TEXT NULL,
  request_id UUID NULL,  -- Links to AgentOutputContract request_id

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),

  -- Unique constraint for idempotency
  CONSTRAINT knowledge_objects_natural_key_unique UNIQUE (user_id, type, natural_key)
);

-- =============================================================================
-- Indexes for Performance
-- =============================================================================

-- Primary query pattern: user + type + time
CREATE INDEX idx_knowledge_objects_user_type_created
  ON knowledge_objects(user_id, type, created_at DESC);

-- Query by source action
CREATE INDEX idx_knowledge_objects_source_action
  ON knowledge_objects(user_id, source_action_id)
  WHERE source_action_id IS NOT NULL;

-- Query by source conversation
CREATE INDEX idx_knowledge_objects_source_conversation
  ON knowledge_objects(user_id, source_conversation_id)
  WHERE source_conversation_id IS NOT NULL;

-- Query by request_id for tracing
CREATE INDEX idx_knowledge_objects_request_id
  ON knowledge_objects(request_id)
  WHERE request_id IS NOT NULL;

-- GIN index on payload for JSONB queries
CREATE INDEX idx_knowledge_objects_payload
  ON knowledge_objects USING GIN (payload);

-- Query active objects (not expired) - only indexes NULL valid_to
-- Time comparison (valid_to > NOW()) must be done at query time
CREATE INDEX idx_knowledge_objects_active
  ON knowledge_objects(user_id, type, created_at DESC)
  WHERE valid_to IS NULL;

-- =============================================================================
-- Updated_at Trigger
-- =============================================================================

CREATE TRIGGER update_knowledge_objects_updated_at
  BEFORE UPDATE ON knowledge_objects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Row Level Security
-- =============================================================================

ALTER TABLE knowledge_objects ENABLE ROW LEVEL SECURITY;

-- Users can view their own knowledge objects
CREATE POLICY "Users can view own knowledge objects"
  ON knowledge_objects FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert their own knowledge objects
CREATE POLICY "Users can insert own knowledge objects"
  ON knowledge_objects FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can update their own knowledge objects
CREATE POLICY "Users can update own knowledge objects"
  ON knowledge_objects FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Users can delete their own knowledge objects
CREATE POLICY "Users can delete own knowledge objects"
  ON knowledge_objects FOR DELETE
  USING (auth.uid() = user_id);

-- Note: Service role key bypasses RLS for backend analytics/backfill operations

-- =============================================================================
-- Comments for Documentation
-- =============================================================================

COMMENT ON TABLE knowledge_objects IS 'Derived knowledge ledger storing agent-inferred objects';
COMMENT ON COLUMN knowledge_objects.type IS 'Type of knowledge object (taxonomy_label, breakdown, insight, etc.)';
COMMENT ON COLUMN knowledge_objects.payload IS 'JSONB payload containing type-specific data';
COMMENT ON COLUMN knowledge_objects.confidence IS 'Confidence score 0.0-1.0 from the inference';
COMMENT ON COLUMN knowledge_objects.importance IS 'Importance score 0-100 for prioritization';
COMMENT ON COLUMN knowledge_objects.natural_key IS 'Deterministic key for idempotent upserts';
COMMENT ON COLUMN knowledge_objects.valid_from IS 'When this knowledge became valid';
COMMENT ON COLUMN knowledge_objects.valid_to IS 'When this knowledge expires (NULL = no expiry)';
COMMENT ON COLUMN knowledge_objects.model_id IS 'LLM model that generated this knowledge';
COMMENT ON COLUMN knowledge_objects.prompt_version IS 'Version of prompt used for inference';
COMMENT ON COLUMN knowledge_objects.request_id IS 'Links to AgentOutputContract request_id for tracing';

COMMENT ON POLICY "Users can view own knowledge objects" ON knowledge_objects IS 'RLS: Users see only their own knowledge objects';
COMMENT ON POLICY "Users can insert own knowledge objects" ON knowledge_objects IS 'RLS: Users can create their own knowledge objects';
COMMENT ON POLICY "Users can update own knowledge objects" ON knowledge_objects IS 'RLS: Users can update their own knowledge objects';
COMMENT ON POLICY "Users can delete own knowledge objects" ON knowledge_objects IS 'RLS: Users can delete their own knowledge objects';
