# Knowledge Objects v0 - Derived Knowledge Ledger

## Overview

The Knowledge Objects system provides a flexible persistence layer for "derived knowledge" - information inferred by the AI agent during user interactions. This layer stores taxonomy labels, breakdowns, insights, goals, plans, habits, and other knowledge objects without refactoring existing Action/Conversation schemas.

## Why This Table Exists

1. **Separation of Concerns**: Raw user data (actions, messages) remains in existing tables. Derived knowledge is stored separately for flexibility.

2. **Schema Flexibility**: Knowledge objects use JSONB payloads, allowing new knowledge types without schema migrations.

3. **Provenance Tracking**: Every knowledge object tracks where it came from (source entities, model, prompt version).

4. **Validity Windows**: Built-in TTL/decay support via `valid_from` and `valid_to` columns.

5. **Idempotency**: Natural key constraints prevent duplicate writes from retries or parallel processing.

## Knowledge Object Types

| Type | Description | Typical Source |
|------|-------------|----------------|
| `taxonomy_label` | 7-layer classification for a capture | ExtractionOrchestrator |
| `breakdown` | Atomic task tree from a parent capture | BreakdownService |
| `insight` | Detected psychological pattern | InsightService |
| `checkpoint` | Conversation summary/checkpoint | Future: ConversationService |
| `goal` | User-stated or inferred goal | Agent inference |
| `plan` | Multi-step plan structure | Agent inference |
| `habit` | Recurring behavior pattern | Pattern detection |
| `state_snapshot` | Entity state at a point in time | Every capture |
| `user_pattern` | Inferred user behavior pattern | Analytics |
| `coaching_note` | Observation from coaching interaction | CoachingService |

## Payload Shape Guidelines

### taxonomy_label

```json
{
  "capture_id": "cap_abc123",
  "capture_title": "Call insurance company",
  "intent_layer": "execute",
  "survival_function": "protection",
  "cognitive_load": "high_friction",
  "time_horizon": "today",
  "agency_level": "autonomous",
  "psych_source": "avoidance",
  "system_role": "scaffold"
}
```

### breakdown

```json
{
  "parent_capture_id": "cap_abc123",
  "steps": [
    {
      "id": "task_001",
      "verb": "Open",
      "object": "phone contacts",
      "estimated_minutes": 1,
      "is_first_action": true,
      "is_physical": true
    },
    {
      "id": "task_002",
      "verb": "Search",
      "object": "insurance number",
      "estimated_minutes": 2
    }
  ],
  "total_estimated_minutes": 15,
  "step_count": 5,
  "first_action_id": "task_001"
}
```

### insight

```json
{
  "pattern_name": "morning_avoidance",
  "description": "User tends to avoid high-cognitive tasks before 10 AM",
  "suggested_strategy": "Schedule heavy tasks for afternoon energy peak"
}
```

### goal

```json
{
  "title": "Complete tax filing",
  "description": "File 2024 taxes before April deadline",
  "target_date": "2024-04-15",
  "progress": 25,
  "related_action_ids": ["action_123", "action_456"]
}
```

### plan

```json
{
  "title": "Tax filing plan",
  "goal_id": "ko_goal_123",
  "steps": [
    {"title": "Gather W-2 forms", "status": "done"},
    {"title": "Download tax software", "status": "pending"},
    {"title": "Complete filing", "status": "pending"}
  ],
  "current_step": 1
}
```

### habit

```json
{
  "title": "Morning review",
  "frequency": "daily",
  "streak": 5,
  "last_completed": "2024-01-15",
  "trigger": "After coffee",
  "reward": "Start day with clarity"
}
```

### state_snapshot

```json
{
  "capture_id": "cap_abc123",
  "capture_title": "Call insurance",
  "capture_type": "task",
  "magnitude": {
    "scope": "atomic",
    "complexity": 2,
    "dependencies": 0,
    "uncertainty": 0.1
  },
  "state": {
    "stage": "not_started",
    "bottleneck": null,
    "energy_required": "medium"
  },
  "avoidance_weight": 4,
  "estimated_minutes": 30,
  "needs_breakdown": true
}
```

### coaching_note

```json
{
  "message_summary": "User expressed frustration with overwhelming task list...",
  "full_message_length": 450,
  "cognitive_load": "high_friction",
  "was_high_friction": true
}
```

## Confidence and Importance

- **confidence** (0.0 - 1.0): How certain the AI is about this knowledge
  - 0.9+: High confidence, directly observed
  - 0.7-0.9: Good confidence, inferred with supporting evidence
  - 0.5-0.7: Moderate confidence, educated guess
  - <0.5: Low confidence, speculative

- **importance** (0 - 100): How valuable this knowledge is for the user
  - 80+: Critical for user success
  - 60-80: Important for planning/execution
  - 40-60: Useful context
  - <40: Nice to have

## Retention Strategy

### Valid From / Valid To

- `valid_from`: When this knowledge became valid (defaults to creation time)
- `valid_to`: When this knowledge expires (NULL = no expiry)

### Expiry Patterns

1. **Insights**: Consider 30-day expiry for behavioral patterns that may change
2. **State Snapshots**: Consider 7-day expiry as state changes frequently
3. **Goals/Plans**: No expiry - user explicitly manages these
4. **Taxonomy Labels**: No expiry - persist for historical analysis
5. **Breakdowns**: No expiry - reuse for similar tasks

### Pruning Strategy

Run periodic cleanup to remove expired objects:

```sql
-- Delete expired objects older than 90 days
DELETE FROM knowledge_objects
WHERE valid_to IS NOT NULL
  AND valid_to < NOW() - INTERVAL '90 days';
```

## Query Examples

### SQL Queries

```sql
-- Get all active goals for a user
SELECT * FROM knowledge_objects
WHERE user_id = 'user-123'
  AND type = 'goal'
  AND (valid_to IS NULL OR valid_to > NOW())
ORDER BY created_at DESC;

-- Get taxonomy labels for an action
SELECT payload FROM knowledge_objects
WHERE user_id = 'user-123'
  AND type = 'taxonomy_label'
  AND source_action_id = 'action-456';

-- Find insights mentioning "procrastination"
SELECT * FROM knowledge_objects
WHERE user_id = 'user-123'
  AND type = 'insight'
  AND payload::text ILIKE '%procrastination%';

-- Get recent high-friction coaching notes
SELECT * FROM knowledge_objects
WHERE user_id = 'user-123'
  AND type = 'coaching_note'
  AND payload->>'was_high_friction' = 'true'
ORDER BY created_at DESC
LIMIT 10;
```

### API Queries

```bash
# List knowledge objects by type
GET /api/knowledge?type=goal&type=plan&limit=20

# Get knowledge for a specific action
GET /api/knowledge/by-action/action-123

# Search knowledge objects
GET /api/knowledge/search?q=insurance

# Get latest derived state
GET /api/knowledge/latest-state

# Get single object
GET /api/knowledge/{object-id}
```

## Integration with Agent Flow

The knowledge writeback happens automatically after each `/api/ai/process/v2` call:

```
User Input
    │
    ▼
IntentRouter.route()
    │
    ▼
AgentOutputContract
    │
    ├──► log_intent()
    │
    └──► KnowledgeWritebackService.process_agent_output()
              │
              ├── For each capture with labels:
              │   └── Upsert taxonomy_label
              │
              ├── For each capture with magnitude/state:
              │   └── Upsert state_snapshot
              │
              ├── For atomic_tasks:
              │   └── Upsert breakdown
              │
              ├── For each insight:
              │   └── Upsert insight
              │
              └── For coaching_message:
                  └── Upsert coaching_note
```

## Idempotency

All writes use `upsert` with a `natural_key` to prevent duplicates:

- **taxonomy_label**: `taxonomy:{capture_id}`
- **state_snapshot**: `snapshot:{capture_id}:{request_id}`
- **breakdown**: `breakdown:{parent_capture_id}:{request_id}`
- **insight**: `insight:{pattern_name}:{conversation_id}:{request_id}`
- **coaching_note**: `coaching:{request_id}`

The natural key ensures that:
1. Same capture always updates the same taxonomy label
2. Retries don't create duplicate objects
3. Parallel processing is safe

## Security (RLS)

Row Level Security ensures users only access their own knowledge:

```sql
-- Users can only see their own objects
CREATE POLICY "Users can view own knowledge objects"
  ON knowledge_objects FOR SELECT
  USING (auth.uid() = user_id);

-- Service role bypasses RLS for backend operations
```

## Future Considerations

1. **Vector Search**: Add embeddings column for semantic search
2. **Full-Text Search**: Add tsvector column for better text search
3. **Analytics Views**: Materialized views for dashboard queries
4. **Archival**: Move old objects to cold storage
5. **Compression**: Compress large payloads after N days
