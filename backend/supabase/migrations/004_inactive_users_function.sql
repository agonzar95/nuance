-- JOB-003: Inactive Users Function
-- SQL function to find users who haven't been active in 3+ days

-- Function to get inactive users
-- Returns profiles of users with no activity in the specified time period
CREATE OR REPLACE FUNCTION get_inactive_users(since TIMESTAMPTZ)
RETURNS SETOF profiles AS $$
  SELECT p.* FROM profiles p
  WHERE p.notification_enabled = true
  AND NOT EXISTS (
    -- No actions created since
    SELECT 1 FROM actions a
    WHERE a.user_id = p.id AND a.created_at > since
  )
  AND NOT EXISTS (
    -- No user messages sent since
    SELECT 1 FROM messages m
    JOIN conversations c ON c.id = m.conversation_id
    WHERE c.user_id = p.id AND m.created_at > since AND m.role = 'user'
  )
  AND NOT EXISTS (
    -- No actions updated since (includes completions)
    SELECT 1 FROM actions a
    WHERE a.user_id = p.id AND a.updated_at > since
  )
$$ LANGUAGE sql;

-- Add comment for documentation
COMMENT ON FUNCTION get_inactive_users(TIMESTAMPTZ) IS
  'Returns profiles of users with no activity (actions created/updated, messages sent) since the specified timestamp. Used by JOB-003 idle nudge job.';
