-- TG-0011: Pending Telegram Connections
-- Stores temporary connection tokens for linking Telegram accounts to user profiles

-- Pending telegram connections table
CREATE TABLE pending_telegram_connections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  token TEXT UNIQUE NOT NULL,
  telegram_chat_id TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast token lookups
CREATE INDEX idx_telegram_connections_token ON pending_telegram_connections(token);

-- Index for cleanup queries (expired token deletion)
CREATE INDEX idx_telegram_connections_expires ON pending_telegram_connections(expires_at);

-- No RLS needed - this table is only accessed via service role
-- Tokens are temporary and consumed on use

COMMENT ON TABLE pending_telegram_connections IS 'Temporary tokens for Telegram account linking (15-min expiry)';
COMMENT ON COLUMN pending_telegram_connections.token IS 'URL-safe unique token sent in Telegram /start response';
COMMENT ON COLUMN pending_telegram_connections.telegram_chat_id IS 'Telegram chat ID to link when token is consumed';
COMMENT ON COLUMN pending_telegram_connections.expires_at IS 'Token expiration time (typically now + 15 minutes)';
