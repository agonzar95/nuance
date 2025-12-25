# Discovery Report: Agent Output Contract v0 Implementation

## 1. File Paths Located

### API Entrypoints for Agent Requests
| Component | Path | Description |
|-----------|------|-------------|
| Main App | `backend/app/main.py` | FastAPI application entry point |
| AI Router | `backend/app/routers/ai.py` | Primary agent endpoints (`/api/ai/process`, `/api/ai/chat`, `/api/ai/breakdown`) |
| Actions Router | `backend/app/routers/actions.py` | CRUD for actions |
| Telegram Router | `backend/app/routers/telegram.py` | Telegram integration |

### IntentRouter / RouterResponse Definitions
| Component | Path | Description |
|-----------|------|-------------|
| Python Models | `backend/app/services/intent_router.py:38-57` | `RouterResponse`, `CommandResponse` classes |
| Python Intent Enum | `backend/app/services/intent.py` | `Intent` enum (capture/coaching/command/clarify) |
| TypeScript Types | `frontend/src/types/api.ts:196-201` | `RouterResponse` interface |

### Extraction Pipeline
| Component | Path | Description |
|-----------|------|-------------|
| Orchestrator | `backend/app/services/extraction_orchestrator.py` | Main pipeline coordinator |
| OrchestrationResult | `backend/app/services/extraction_orchestrator.py:62-78` | Pipeline output model |
| EnrichedAction | `backend/app/services/extraction_orchestrator.py:46-59` | Enriched action model |
| Extraction Service | `backend/app/services/extraction.py` | Action extraction from text |
| Avoidance Service | `backend/app/services/avoidance.py` | Emotional resistance scoring |
| Complexity Service | `backend/app/services/complexity.py` | Task complexity classification |
| Confidence Service | `backend/app/services/confidence.py` | Extraction confidence scoring |
| Appraisal Service | `backend/app/services/appraisal.py` | Cognitive load evaluation |
| Scaffolding Service | `backend/app/services/scaffolding.py` | Probe question generation |
| Insight Service | `backend/app/services/insight.py` | Pattern detection |

### Supabase Client Setup + Migrations
| Component | Path | Description |
|-----------|------|-------------|
| Backend Client | `backend/app/clients/supabase.py` | Service role client for RLS bypass |
| Frontend Client | `frontend/src/lib/supabase/client.ts` | Browser client |
| Server Client | `frontend/src/lib/supabase/server.ts` | Server-side client |
| Migrations Folder | `backend/supabase/migrations/` | 5 migration files |

### DB Schema Definitions
| Table | Migration File | Key Fields |
|-------|---------------|------------|
| profiles | `001_initial_schema.sql` | id, timezone, telegram_chat_id, notification_channel |
| actions | `001_initial_schema.sql` | id, user_id, title, status, complexity, avoidance_weight |
| conversations | `001_initial_schema.sql` | id, user_id, type, context_action_id |
| messages | `001_initial_schema.sql` | id, conversation_id, role, content |
| token_usage | `001_initial_schema.sql` | id, user_id, input_tokens, output_tokens |
| intent_log | `003_intent_log.sql` | id, user_id, raw_input, classified_intent, extraction_result (JSONB), prompt_version |

### Prompt Registry / Versioning
| Component | Path | Description |
|-----------|------|-------------|
| Registry | `backend/app/prompts/registry.py` | `PromptVersion`, `PromptRegistry` classes |
| Global Access | `backend/app/prompts/registry.py:387-404` | `get_prompt_registry()`, `get_prompt()` |

**Registered Prompts:**
- `extraction` v1.1.0 - Action extraction
- `avoidance` v1.0.0 - Emotional resistance
- `complexity` v1.1.0 - Task complexity
- `breakdown` v1.0.0 - Micro-step generation
- `intent` v1.1.0 - Intent classification
- `cognitive_appraisal` v1.0.0 - Hidden weight evaluation
- `project_scaffolding` v1.0.0 - Project probe generation
- `insight_analysis` v1.0.0 - Pattern detection
- `coaching` v1.0.0 - Emotional support
- `confidence` v1.0.0 - Extraction confidence

---

## 2. Request Flow Map

```
User Input
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  POST /api/ai/process  (backend/app/routers/ai.py:343)      │
│  - Auth check via CurrentUser                               │
│  - Rate limit check                                         │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  IntentRouter.route() (intent_router.py:196)                │
│  - Classifies intent via IntentClassifier.classify()        │
│  - Dispatches to handler based on intent                    │
└─────────────────────────────────────────────────────────────┘
    │
    ├──────────────────┬──────────────────┬───────────────────┐
    ▼ CAPTURE          ▼ COACHING         ▼ COMMAND           ▼ CLARIFY
┌───────────┐     ┌───────────┐      ┌───────────┐       ┌───────────┐
│_handle_   │     │_handle_   │      │_handle_   │       │ → CAPTURE │
│ capture() │     │ coaching()│      │ command() │       └───────────┘
└───────────┘     └───────────┘      └───────────┘
    │                  │                  │
    ▼                  ▼                  ▼
ExtractionOrch.    CoachingService   CommandHandler
    │                  │                  │
    ├─ Appraisal       │                  │
    ├─ Extract         │                  │
    ├─ Enrich (║)      │                  │
    │  ├─ Avoidance    │                  │
    │  ├─ Complexity   │                  │
    │  └─ Confidence   │                  │
    ├─ Scaffolding?    │                  │
    └─ Insight?        │                  │
    │                  │                  │
    ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│  RouterResponse (intent_router.py:38-57)                    │
│  - intent, intent_confidence, response_type                 │
│  - extraction?, insight?, coaching_response?, command_resp? │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  log_intent() (services/intent_logger.py)                   │
│  → INSERT intent_log (extraction_result as JSONB)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. LLM Call Locations

| Service | File | Method | Prompt Used |
|---------|------|--------|-------------|
| IntentClassifier | `intent.py` | `classify()` | `intent` |
| AppraisalService | `appraisal.py` | `appraise()` | `cognitive_appraisal` |
| ExtractionService | `extraction.py` | `extract()` | `extraction` |
| AvoidanceService | `avoidance.py` | `detect()` | `avoidance` |
| ComplexityService | `complexity.py` | `classify()` | `complexity` |
| ConfidenceService | `confidence.py` | `score()` | `confidence` |
| ScaffoldingService | `scaffolding.py` | `generate_probe()` | `project_scaffolding` |
| InsightService | `insight.py` | `analyze_history()` | `insight_analysis` |
| CoachingService | `coaching.py` | `process()` | `coaching` |
| BreakdownService | `breakdown.py` | `breakdown()` | `breakdown` |

---

## 4. DB Write Locations

| Table | Write Location | Trigger |
|-------|----------------|---------|
| intent_log | `services/intent_logger.py:log_intent()` | Every `/api/ai/process` call |
| token_usage | `services/token_budget.py:record_usage()` | Every `/api/ai/chat` call |
| actions | `routers/actions.py` | POST/PATCH `/api/actions` |
| conversations | Not directly written (future) | - |
| messages | Not directly written (future) | - |

---

## 5. Current Response Structures

### Python `RouterResponse` (intent_router.py:38-57)
```python
class RouterResponse(BaseModel):
    intent: Intent                          # capture|coaching|command|clarify
    intent_confidence: float                # 0.0-1.0
    response_type: str                      # "capture"|"coaching"|"command"
    extraction: OrchestrationResult | None  # For CAPTURE
    insight: Any | None                     # PsychologicalInsight (optional)
    coaching_response: str | None           # For COACHING
    command_response: CommandResponse | None # For COMMAND
```

### Python `OrchestrationResult` (extraction_orchestrator.py:62-78)
```python
class OrchestrationResult(BaseModel):
    actions: list[EnrichedAction]
    raw_input: str
    overall_confidence: float               # 0.0-1.0
    needs_validation: bool
    cognitive_load: str                     # "ROUTINE"|"HIGH_FRICTION"
    needs_scaffolding: bool
    scaffolding_question: str | None
```

### Python `EnrichedAction` (extraction_orchestrator.py:46-59)
```python
class EnrichedAction(BaseModel):
    title: str
    estimated_minutes: int
    raw_segment: str
    avoidance_weight: int                   # 1-5
    complexity: ActionComplexity            # atomic|composite|project
    needs_breakdown: bool
    confidence: float                       # 0.0-1.0
    ambiguities: list[str]
    cognitive_load: str                     # "ROUTINE"|"HIGH_FRICTION"
```

### TypeScript `RouterResponse` (api.ts:196-201)
```typescript
interface RouterResponse {
  intent: Intent
  extraction?: CaptureResult
  insight?: PsychologicalInsight
  coaching_response?: string
}
```

---

## 6. Integration Points for AgentOutputContract v0

### Where to Add Contract
1. **Definition**: New file `backend/app/contracts/agent_output_v0.py`
2. **TS Types**: Extend `frontend/src/types/api.ts`
3. **JSON Schema**: `shared/contracts/agent_output/v0/schema.json`

### Mapping Sources
| Contract Field | Source |
|---------------|--------|
| `captures[]` | `OrchestrationResult.actions` → transform to capture format |
| `labels[]` | New taxonomy layer (extend EnrichedAction) |
| `atomic_tasks[]` | From BreakdownService or inline if needs_breakdown |
| `state_updates[]` | Track created/updated entities per turn |
| `questions[]` | From `scaffolding_question` or new clarification flow |
| `user_facing_summary` | Generate from extraction/coaching response |

### Backward Compatibility Strategy
- Return both `RouterResponse` fields AND new `output: AgentOutputContractV0`
- Frontend checks for `contract_version` presence
- Gradual migration with feature flag if needed

---

## 7. Items Not Found / Proposed Locations

| Missing | Proposed Location |
|---------|-------------------|
| 7-layer taxonomy labels | Extend `EnrichedAction` or new `TaxonomyLabel` model |
| Magnitude/state inference | New service or extend ExtractionOrchestrator |
| Atomic tasks with DoD | Extend BreakdownService output |
| State updates tracking | New utility in intent_router |
| Trace ID / request ID | Add to middleware context |

---

## 8. Next Steps

1. Create JSON Schema for AgentOutputContract v0
2. Create Pydantic models (Python) and TS types
3. Implement mapping from OrchestrationResult → contract
4. Update `/api/ai/process` to return contract wrapper
5. Update IntentLog to store contract v0 payload
6. Create 3 example payloads
7. Add schema validation to CI
8. Document in `/docs/contracts/agent_output_v0.md`
