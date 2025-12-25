# Agent Output Contract v0

**Version**: 0.1.0
**Status**: Active
**Last Updated**: 2025-01-15

## Purpose

The Agent Output Contract v0 defines a standardized response structure that every agent turn returns, regardless of intent type (capture, coaching, command, or clarify). This contract:

1. **Unifies response formats** across all intent types
2. **Provides rich metadata** (taxonomy, magnitude, state inference)
3. **Enables UI flexibility** with structured rendering hints
4. **Supports debugging** with provenance tracking
5. **Maintains backward compatibility** with existing clients

## Guarantees

Every API response that uses this contract guarantees:

- `contract_version` is present and follows semver
- `request_id` is a valid UUID for tracing
- `timestamp` is an ISO 8601 datetime
- `intent.type` is one of: `capture`, `coaching`, `command`, `clarify`
- `intent.confidence` is between 0.0 and 1.0
- `output.raw_input` contains the original user input
- All array fields (`captures`, `atomic_tasks`, etc.) are never null (empty arrays if none)

## Response Structure

```json
{
  "contract_version": "0.1.0",
  "request_id": "uuid",
  "trace_id": "optional-trace-id",
  "timestamp": "2025-01-15T14:30:00.000Z",
  "intent": {
    "type": "capture|coaching|command|clarify",
    "confidence": 0.95,
    "reasoning": "optional"
  },
  "output": {
    "raw_input": "original user input",
    "captures": [...],
    "atomic_tasks": [...],
    "state_updates": [...],
    "questions": [...],
    "insights": [...],
    "coaching_message": "optional",
    "command_result": {...},
    "user_facing_summary": "Human-readable summary",
    "ui_blocks": [...],
    "overall_confidence": 0.88,
    "cognitive_load": "routine|high_friction",
    "needs_scaffolding": false,
    "scaffolding_question": null
  },
  "provenance": {
    "model_id": "claude-3-5-sonnet-20241022",
    "prompt_versions": {"extraction": "1.1.0", ...},
    "processing_time_ms": 250,
    "token_usage": {"input_tokens": 500, "output_tokens": 300}
  }
}
```

## Field-by-Field Description

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_version` | string | Yes | Semver version of this contract |
| `request_id` | UUID | Yes | Unique identifier for this request |
| `trace_id` | string | No | Distributed tracing ID |
| `timestamp` | datetime | Yes | When this response was generated |
| `intent` | IntentClassification | Yes | Intent classification result |
| `output` | AgentOutput | Yes | The core output payload |
| `provenance` | Provenance | No | Metadata about generation |

### IntentClassification

| Field | Type | Description |
|-------|------|-------------|
| `type` | enum | `capture`, `coaching`, `command`, or `clarify` |
| `confidence` | float | 0.0-1.0 confidence score |
| `reasoning` | string | Optional explanation of classification |

### Captures

Each capture represents an extracted item (task, goal, habit, etc.):

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Temporary ID (e.g., `cap_a1b2c3d4`) |
| `type` | enum | `goal`, `plan`, `habit`, `task`, `reflection`, `blocker`, `metric` |
| `title` | string | Normalized title in imperative form |
| `raw_segment` | string | Original text this was extracted from |
| `estimated_minutes` | int | Time estimate |
| `avoidance_weight` | int | Emotional resistance 1-5 |
| `confidence` | float | Extraction confidence 0.0-1.0 |
| `ambiguities` | string[] | Potential clarifications needed |
| `labels` | TaxonomyLayer | 7-layer taxonomy classification |
| `magnitude` | MagnitudeInference | Scope/complexity inference |
| `state` | StateInference | Current state inference |
| `needs_breakdown` | bool | Should be broken into steps |

### TaxonomyLayer (7-Layer Classification)

| Layer | Options | Description |
|-------|---------|-------------|
| `intent_layer` | capture, clarify, execute, reflect, unknown | What the user intends |
| `survival_function` | maintenance, growth, protection, connection, unknown | Core need |
| `cognitive_load` | routine, high_friction, unknown | Mental effort |
| `time_horizon` | immediate, today, this_week, this_month, long_term, unknown | When needed |
| `agency_level` | autonomous, delegated, blocked, unknown | User's control |
| `psych_source` | intrinsic, extrinsic, avoidance, unknown | Motivation source |
| `system_role` | capture, scaffold, track, remind, coach, unknown | What system should do |

### AtomicTasks

Micro-steps derived from captures:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Task ID (e.g., `task_m3n4o5p6`) |
| `parent_capture_id` | string | Which capture this belongs to |
| `verb` | string | Action verb (e.g., "Open") |
| `object` | string | Object of action (e.g., "laptop") |
| `full_description` | string | Full task description |
| `definition_of_done` | string | Clear completion criteria |
| `estimated_minutes` | int | 1-30 minutes |
| `energy_level` | enum | `low`, `medium`, `high` |
| `prerequisites` | string[] | Task IDs that must complete first |
| `is_first_action` | bool | Recommended first step |
| `is_physical` | bool | Involves physical movement |

### StateUpdates

Track entity changes from this turn:

| Field | Type | Description |
|-------|------|-------------|
| `entity_type` | enum | `action`, `conversation`, `message`, `profile` |
| `entity_id` | UUID | ID after persistence (null before) |
| `temp_id` | string | References capture/task in this turn |
| `operation` | enum | `created`, `updated`, `deleted` |
| `changes` | object | Field changes (for updates) |

### Questions (Clarifications)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Question ID |
| `question` | string | The clarification question |
| `target_capture_id` | string | Which capture this is about |
| `question_type` | enum | `scope`, `timeline`, `priority`, `blocker`, `other` |
| `suggested_answers` | string[] | Optional suggested responses |

### UIBlocks

Structured rendering hints for the frontend:

| Field | Type | Description |
|-------|------|-------------|
| `type` | enum | Block type (see below) |
| `data` | object | Block-specific data |
| `priority` | int | Display priority (0 = highest) |

**Block Types:**
- `capture_list`: List of captured items
- `breakdown_steps`: Micro-step breakdown
- `coaching_message`: Coaching response
- `insight_card`: Pattern insight
- `question_prompt`: Clarification prompt
- `command_result`: Command output

### Provenance

| Field | Type | Description |
|-------|------|-------------|
| `model_id` | string | LLM model used |
| `prompt_versions` | object | Map of prompt name to version |
| `processing_time_ms` | int | Total processing time |
| `token_usage.input_tokens` | int | Input tokens consumed |
| `token_usage.output_tokens` | int | Output tokens generated |

## Examples

### CAPTURE Intent

See [contract_v0_capture.json](../examples/contract_v0_capture.json)

User input: "I need to finally call the insurance company about that claim, ugh. Also buy groceries..."

The contract returns:
- 3 captures (insurance call, groceries, presentation)
- Taxonomy labels for each (cognitive_load, psych_source, etc.)
- Atomic tasks for high-friction items
- State updates for new actions
- UI blocks for rendering
- Scaffolding question for the project

### COACHING Intent

See [contract_v0_coaching.json](../examples/contract_v0_coaching.json)

User input: "I keep staring at this tax folder and I just can't make myself start..."

The contract returns:
- 1 capture (inferred task)
- 5 atomic tasks (tiny steps to start)
- Coaching message with validation and tiny step
- UI blocks for coaching and breakdown

### CLARIFY Intent

See [contract_v0_clarify.json](../examples/contract_v0_clarify.json)

User input: "I should probably deal with that project thing for Sarah..."

The contract returns:
- 2 partial captures (low confidence)
- 4 clarification questions
- UI blocks with question prompts
- Low overall_confidence (0.42)

## API Endpoints

### GET `/api/ai/process?use_contract=true`

Existing endpoint with contract format opt-in:

```bash
curl -X POST /api/ai/process?use_contract=true \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"text": "Buy milk and call mom"}'
```

### POST `/api/ai/process/v2`

New endpoint that always returns the contract:

```bash
curl -X POST /api/ai/process/v2 \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"text": "Buy milk and call mom"}'
```

## Compatibility Notes

### Mapping from RouterResponse

The contract is generated from the existing `RouterResponse` structure:

| RouterResponse Field | Contract Field |
|---------------------|----------------|
| `intent` | `intent.type` |
| `intent_confidence` | `intent.confidence` |
| `extraction.actions[]` | `output.captures[]` |
| `extraction.overall_confidence` | `output.overall_confidence` |
| `extraction.cognitive_load` | `output.cognitive_load` |
| `extraction.needs_scaffolding` | `output.needs_scaffolding` |
| `extraction.scaffolding_question` | `output.scaffolding_question` |
| `insight` | `output.insights[]` |
| `coaching_response` | `output.coaching_message` |
| `command_response` | `output.command_result` |

### Frontend Migration

For TypeScript/React frontends:

```typescript
import { AgentOutputContract, isAgentOutputContract } from '@/types/contracts'

// Check if response uses new contract
if (isAgentOutputContract(response)) {
  // Use new contract structure
  const captures = response.output.captures
  const summary = response.output.user_facing_summary
} else {
  // Fall back to old RouterResponse
  const actions = response.extraction?.actions
}
```

## Versioning Policy

This contract follows **Semantic Versioning**:

- **MAJOR** (1.0.0): Breaking changes to required fields or structure
- **MINOR** (0.2.0): New optional fields, backward-compatible additions
- **PATCH** (0.1.1): Bug fixes, documentation updates

### How to Bump

1. Update `CONTRACT_VERSION` in `backend/app/contracts/agent_output_v0.py`
2. Update `CONTRACT_VERSION` in `frontend/src/types/contracts.ts`
3. Update `$id` in `shared/contracts/agent_output/v0/schema.json`
4. Add migration notes to this document

### Migration Guidance

When upgrading from 0.1.x to 0.2.x:
- Check for new optional fields you may want to use
- Existing code should continue to work

When upgrading to 1.0.0:
- Review all changes in the changelog
- Update client code to handle new structure
- Use the compatibility layer during transition

## File Locations

| File | Purpose |
|------|---------|
| `shared/contracts/agent_output/v0/schema.json` | JSON Schema (source of truth) |
| `backend/app/contracts/agent_output_v0.py` | Python Pydantic models |
| `backend/app/contracts/mapper.py` | RouterResponse → Contract mapping |
| `frontend/src/types/contracts.ts` | TypeScript types |
| `docs/examples/contract_v0_*.json` | Example payloads |
| `backend/tests/test_contract_v0.py` | Contract tests |

## FAQ

**Q: Can I use the old RouterResponse format?**
A: Yes, the existing `/api/ai/process` endpoint continues to return `RouterResponse` by default. Add `?use_contract=true` to opt-in to the new format.

**Q: Are atomic_tasks always populated?**
A: No, they are generated on-demand when a capture has `needs_breakdown=true`. Use the `/api/ai/breakdown` endpoint to generate steps for a specific task.

**Q: What if I only need some fields?**
A: The contract is designed to be easily filtered. You can ignore fields you don't need. UI blocks provide hints but are optional.

**Q: How do I track which prompt versions were used?**
A: Check `provenance.prompt_versions` for a map of prompt names to their versions.

**Q: Is the contract stored in the database?**
A: Yes, when using `/api/ai/process/v2`, the full contract is stored in `intent_log.extraction_result` as JSONB.
