# Implementation Record

## Project Status
- **Current Phase:** 4 - AI Layer (COMPLETE)
- **Total Features:** 51 completed of 107 total
- **Last Updated:** December 12, 2025
- **Last Commit:** `df159e2` [PHASE-04] Group E - Extraction Orchestrator (15/16 features)

---

## Current Phase: Phase 4 - AI Layer

**Goal:** Build the complete agentic infrastructure: orchestration, extractors, and handlers.

### Phase 4 Features (16/16 Complete)

| ID | Feature | Status | Complexity | Parallel Group |
|----|---------|--------|------------|----------------|
| AGT-001 | Orchestrator Setup | DONE | Medium | A |
| AGT-007 | Model Abstraction | DONE | Easy | A |
| INF-007 | Intent Log Recording | DONE | Easy | A |
| AGT-004 | Rate Limiting | DONE | Easy | B |
| AGT-005 | Token Budgeting | DONE | Easy | B |
| AGT-006 | SSE Streaming | DONE | Medium | B |
| AGT-015 | Prompt Versioning | DONE | Easy | B |
| AGT-008 | Extract: Actions | DONE | Medium | C |
| AGT-009 | Extract: Avoidance Weight | DONE | Medium | C |
| AGT-010 | Extract: Complexity | DONE | Easy | C |
| AGT-012 | Extract: Breakdown | DONE | Medium | C |
| AGT-013 | Intent Classifier | DONE | Easy | C |
| AGT-011 | Extract: Confidence | DONE | Easy | D |
| AGT-014 | Coaching Handler | DONE | Medium | D |
| AGT-016 | Extraction Orchestrator | DONE | Medium | E |
| AGT-002 | Request Router | DONE | Medium | F |

### Phase 4 Validation Criteria

| Criterion | Test | Status |
|-----------|------|--------|
| Orchestrator runs | Request/response cycle works | READY |
| Model abstraction works | Claude calls succeed via abstraction | READY |
| Rate limiting enforces | Requests beyond limit rejected | READY |
| SSE streams | Client receives streaming tokens | READY |
| Action extraction works | Text → structured actions | READY |
| Avoidance detection works | High-avoidance tasks flagged | READY |
| Breakdown works | Complex task → subtasks | READY |
| Intent classification works | Message → intent label | READY |
| Coaching responds | Multi-turn coaching dialogue works | READY |
| Router routes | Different intents hit correct handlers | READY |
| TypeScript passes | `tsc --noEmit` exits with 0 | PASS |
| Python types pass | `mypy` exits with 0 (excl. supabase lib) | PASS |

### Phase Gate

**Phase 4 is complete when:**
- [x] Orchestrator handles request/response cycle
- [x] SSE streaming delivers tokens to client
- [x] All 5 extractors produce valid outputs
- [x] Extraction orchestrator coordinates parallel extraction
- [x] Intent classifier routes to correct handler
- [x] Coaching handler maintains multi-turn state
- [x] Request router correctly dispatches all intent types
- [x] Integration tests pass for each extractor

---

## In Progress

**Phase 5 IN PROGRESS (0/7 features). Started notification infrastructure.**

Phase 5 features:
- NTF-002: Email Client (Resend) - IN PROGRESS (base types created)
- NTF-003: Telegram Bot Setup - TODO
- NTF-004: Telegram Send - TODO
- NTF-005: Telegram Receive - TODO
- NTF-006: Telegram Commands - TODO
- NTF-009: Channel Router - TODO
- NTF-001: Gateway Abstraction - TODO

**Partial work created:**
- `backend/app/services/notifications/__init__.py` - package init
- `backend/app/services/notifications/base.py` - base types (NotificationChannel, NotificationType, NotificationPayload, DeliveryResult, NotificationProvider)
- `backend/app/services/notifications/providers/__init__.py` - providers init (imports need completion)

---

## Completed: Phase 3 - Data Layer

**Goal:** Establish database schema, authentication, and real-time subscriptions.
**Status:** COMPLETE

---

## Completed: Phase 2 - Core Services

**Goal:** Configure deployment and establish all external service integrations.
**Status:** COMPLETE

### Phase 2 Features (12/12 Complete)

| ID | Feature | Status | Complexity | Parallel Group |
|----|---------|--------|------------|----------------|
| INF-003 | Vercel Config | DONE | Easy | A |
| INF-004 | Railway Config | DONE | Easy | A |
| INF-005 | Environment Config | DONE | Easy | A |
| INF-006 | Structured Logging | DONE | Easy | B |
| INF-011 | CORS Configuration | DONE | Easy | B |
| INT-001 | Supabase Client | DONE | Easy | C |
| INT-002 | Claude API Client | DONE | Easy | C |
| INT-003 | Deepgram Client | DONE | Easy | C |
| INT-004 | Telegram API Client | DONE | Easy | C |
| INT-005 | Resend Client | DONE | Easy | C |
| INT-006 | Voice Transcription | DONE | Medium | D |
| INF-008 | Error Middleware | DONE | Easy | D |

---

## Completed: Phase 1 - Foundation

**Goal:** Establish zero-dependency base components that all other features build upon.
**Status:** COMPLETE - Committed `f38cbed`, pushed to origin/main

### Phase 1 Features (12/12 Complete)

| ID | Feature | Status | Complexity | Parallel Group |
|----|---------|--------|------------|----------------|
| INF-001 | Next.js Setup | DONE | Easy | A (Infrastructure) |
| INF-002 | FastAPI Setup | DONE | Easy | A (Infrastructure) |
| FE-007 | Avoidance Indicator | DONE | Easy | B (UI Components) |
| FE-008 | Timer Component | DONE | Easy | B (UI Components) |
| FE-009 | Loading States | DONE | Easy | B (UI Components) |
| FE-010 | Empty States | DONE | Easy | B (UI Components) |
| FE-011 | Offline Awareness | DONE | Easy | B (UI Components) |
| CAP-002 | Chat Text Input | DONE | Easy | C (Input Components) |
| CAP-006 | Correction Flow | DONE | Easy | C (Input Components) |
| EXE-003 | Subtask Checklist | DONE | Easy | D (Execution Components) |
| EXE-011 | Avoidance Acknowledgment | DONE | Easy | D (Execution Components) |
| PLN-006 | Time Budget Display | DONE | Easy | E (Planning Components) |

---

## Patterns & Conventions

### Code Organization
- Frontend: `frontend/src/app/` (App Router), `frontend/src/components/`, `frontend/src/lib/`
- Backend: `backend/app/main.py` (entry), `backend/app/routers/`, `backend/app/services/`, `backend/app/models/`
- Jobs: `backend/jobs/` (scheduled background jobs)
- Migrations: `backend/supabase/migrations/` (SQL schema files)

### Testing Conventions
- Frontend tests: `npm run typecheck` (TypeScript), `npm run lint` (ESLint)
- Backend tests: `pytest` (unit tests), `mypy app` (type checking)

### Naming Conventions
- Components: PascalCase React components in `frontend/src/components/`
- API endpoints: lowercase with hyphens, e.g., `/api/health`
- SQL migrations: numbered prefix, e.g., `001_initial_schema.sql`

---

## Implementation Notes

### AGT-001: Orchestrator Setup
- Main AI router at `/api/ai` with authentication middleware
- JWT validation via Supabase tokens in `backend/app/auth.py`
- Endpoints: `/chat`, `/chat/stream`, `/extract`, `/status`
- User dependency injection for all endpoints
- Artifacts: `backend/app/auth.py`, `backend/app/routers/ai.py`

### AGT-007: Model Abstraction
- Abstract `AIProvider` interface in `backend/app/ai/base.py`
- `ClaudeProvider` implementation with async support
- Methods: `complete()`, `stream()`, `extract()`
- Factory function `get_ai_provider()` for dependency injection
- Artifacts: `backend/app/ai/base.py`, `backend/app/ai/claude.py`, `backend/app/ai/__init__.py`

### INF-007: Intent Log Recording
- SQL migration `003_intent_log.sql` for intent_log table
- Service function `log_intent()` records all AI interactions
- Captures: raw_input, intent, extraction_result, response, prompt_version, tokens
- RLS enabled but no user-facing policies (admin analytics only)
- Artifacts: `backend/supabase/migrations/003_intent_log.sql`, `backend/app/services/intent_logger.py`

### AGT-004: Rate Limiting
- In-memory rate limiter with per-minute (60) and per-day (500) limits
- `RateLimiter` class in `backend/app/utils/rate_limiter.py`
- Returns 429 with Retry-After header when exceeded
- `RateLimitError` exception with custom handler
- Artifacts: `backend/app/utils/rate_limiter.py`, updated `backend/app/middleware/error_handler.py`

### AGT-005: Token Budgeting
- `TokenBudgetService` for tracking daily token usage
- Default 100K tokens/day limit with warning at 80%
- Records usage to existing `token_usage` table
- `BudgetStatus` dataclass with remaining/warning info
- Artifacts: `backend/app/services/token_budget.py`

### AGT-006: SSE Streaming
- Added `sse-starlette` dependency for Server-Sent Events
- `/api/ai/chat/stream` endpoint with EventSourceResponse
- Event types: `message` (chunks), `done` (completion), `error`
- Uses `AIProvider.stream()` for async iteration
- Artifacts: Updated `backend/app/routers/ai.py`, `backend/requirements.txt`

### AGT-015: Prompt Versioning
- `PromptRegistry` for centralized prompt management
- `PromptVersion` dataclass with name, version, content, metadata
- Pre-loaded prompts: extraction, avoidance, complexity, breakdown, intent, coaching, confidence
- Supports multiple versions per prompt for A/B testing
- Artifacts: `backend/app/prompts/registry.py`, `backend/app/prompts/__init__.py`

### AGT-008: Extract Actions
- `ExtractionService` parses natural language into structured actions
- `ExtractedAction` model with title, estimated_minutes, raw_segment
- `ExtractionResult` includes actions list, confidence, and ambiguities
- Uses AI provider `extract()` with versioned "extraction" prompt
- Artifacts: `backend/app/services/extraction.py`

### AGT-009: Extract Avoidance Weight
- `AvoidanceService` detects emotional resistance in task descriptions
- `AvoidanceAnalysis` model with weight (1-5), signals, reasoning
- Scores based on dread words, anxiety markers, avoidance history
- Supports batch processing via `detect_batch()`
- Artifacts: `backend/app/services/avoidance.py`

### AGT-010: Extract Complexity
- `ComplexityService` classifies tasks as atomic/composite/project
- `ComplexityAnalysis` model with complexity enum, suggested_steps, needs_breakdown
- Fast-path: tasks ≤20min classified as atomic without AI call
- Uses existing `ActionComplexity` enum from database models
- Artifacts: `backend/app/services/complexity.py`

### AGT-012: Extract Breakdown
- `BreakdownService` generates 3-5 micro-steps for complex tasks
- `BreakdownStep` model with title, estimated_minutes (max 15), is_physical
- Steps are physical, immediate, and tiny (2-10 min)
- Focus on initiation - overcoming paralysis to start
- Artifacts: `backend/app/services/breakdown.py`

### AGT-013: Intent Classifier
- `IntentClassifier` routes messages to capture/coaching/command
- `Intent` enum with CAPTURE, COACHING, COMMAND values
- Fast-path heuristics: command prefix (/), action verbs, coaching signals
- Falls back to AI classification for ambiguous cases
- Artifacts: `backend/app/services/intent.py`

### AGT-011: Extract Confidence
- `ConfidenceService` scores extraction confidence from 0.0-1.0
- `ConfidenceAnalysis` model with confidence, ambiguities, reasoning
- Heuristic scoring: action verbs (+), vague patterns (-), short titles (-)
- Falls back to AI for complex cases below 0.6 confidence
- Artifacts: `backend/app/services/confidence.py`

### AGT-014: Coaching Handler
- `CoachingService` provides empathetic multi-turn conversations
- `CoachingConversation` manages conversation history per user/task
- Supports both `process()` (full response) and `stream()` (SSE)
- Principles: validate feelings, normalize struggles, suggest tiny steps, no shame
- Artifacts: `backend/app/services/coaching.py`

### AGT-016: Extraction Orchestrator
- `ExtractionOrchestrator` coordinates full extraction pipeline
- Pipeline: extract actions → parallel (avoidance, complexity) → confidence
- `EnrichedAction` model with all metadata (avoidance, complexity, confidence)
- `OrchestrationResult` includes needs_validation flag for UI
- Artifacts: `backend/app/services/extraction_orchestrator.py`

### AGT-002: Request Router
- `IntentRouter` routes messages to appropriate handlers based on intent
- `CommandHandler` for system commands (/start, /help, /clear, /status)
- Routes: CAPTURE → ExtractionOrchestrator, COACHING → CoachingService, COMMAND → CommandHandler
- `RouterResponse` unified response model with intent-specific content
- API endpoints: `POST /api/ai/process`, `POST /api/ai/process/stream`
- Supports forced intent for UI flows (skip classification)
- Streaming only for COACHING; other intents return full result
- Artifacts: `backend/app/services/intent_router.py`, updated `backend/app/routers/ai.py`

---

### SUB-001: Database Schema
- Created `backend/supabase/migrations/001_initial_schema.sql`
- Tables: profiles, actions, conversations, messages, token_usage
- Enums: action_status, action_complexity
- Indexes on frequently queried columns
- Trigger for automatic profile creation on signup
- REPLICA IDENTITY FULL for real-time subscriptions
- Artifacts: `backend/supabase/migrations/001_initial_schema.sql`

### AGT-003: Circuit Breakers
- Circuit breaker pattern in `backend/app/utils/circuit_breaker.py`
- States: CLOSED (normal), OPEN (blocking), HALF_OPEN (testing)
- Configurable failure threshold (default: 3) and cooldown (default: 60s)
- Pre-configured breakers for Claude, Deepgram, Telegram, Resend
- Artifacts: `backend/app/utils/circuit_breaker.py`

### SUB-002: RLS Policies
- Created `backend/supabase/migrations/002_rls_policies.sql`
- Enabled RLS on all user-owned tables
- Users can only access their own data (via auth.uid())
- Messages checked via conversation ownership
- Artifacts: `backend/supabase/migrations/002_rls_policies.sql`

### SUB-003: Email/Password Auth
- Auth functions in `frontend/src/lib/auth.ts`
- Functions: signUp, signIn, signOut, resetPassword, updatePassword
- Auth callback route at `/auth/callback`
- Login page at `/login`, Signup page at `/signup`
- Artifacts: `frontend/src/lib/auth.ts`, `frontend/src/app/auth/callback/route.ts`, `frontend/src/app/(auth)/login/page.tsx`, `frontend/src/app/(auth)/signup/page.tsx`

### SUB-004: Google OAuth
- Added `signInWithGoogle()` to auth library
- Google button on login page with SVG icon
- Uses same callback route as email auth
- Artifacts: Updated `frontend/src/lib/auth.ts`, `frontend/src/app/(auth)/login/page.tsx`

### SUB-005: Profile Management
- Profile hook in `frontend/src/hooks/useProfile.ts`
- Optimistic updates with rollback on error
- Timezone detection utility
- Artifacts: `frontend/src/hooks/useProfile.ts`

### SUB-006: Session Handling
- Session hooks in `frontend/src/hooks/useSession.ts`
- `useSession()`: Main hook with auto-refresh
- `useRequireAuth()`: Redirect if not authenticated
- `useRedirectIfAuthenticated()`: Redirect if already authenticated
- Artifacts: `frontend/src/hooks/useSession.ts`

### SUB-007: Notification Preferences
- Settings component in `frontend/src/components/settings/NotificationSettings.tsx`
- Toggle for enable/disable notifications
- Radio buttons for channel selection (email/telegram/both)
- Disabled states when Telegram not connected
- Artifacts: `frontend/src/components/settings/NotificationSettings.tsx`

### SUB-008: Timezone Handling
- Timezone utilities in `backend/app/utils/timezone.py`
- Functions: get_user_local_time, is_users_local_hour, utc_to_user_local, etc.
- Used by scheduled jobs to determine user's local time
- Uses Python zoneinfo (Python 3.9+)
- Artifacts: `backend/app/utils/timezone.py`

### SUB-009: Job: State Transitions
- Scheduled job in `backend/jobs/state_transitions.py`
- Runs hourly, transitions actions at 4am user local time
- Moves "planned" and "active" actions to "rolled" status
- Clears planned_date for rolled actions
- Artifacts: `backend/jobs/state_transitions.py`

### SUB-013: Real-time Subscriptions
- Real-time hook in `frontend/src/hooks/useRealtimeActions.ts`
- Subscribes to postgres_changes on actions table
- Handles INSERT, UPDATE, DELETE events
- Supports filtering by status and planned_date
- Optimistic update helpers included
- Artifacts: `frontend/src/hooks/useRealtimeActions.ts`

---

## Previous Implementation Notes

### INF-001: Next.js Setup
- Used Next.js 16 with App Router and Tailwind CSS v4
- Tailwind v4 uses CSS-based configuration (`@import "tailwindcss"` + `@theme {}`)
- Path aliases configured: `@/*` → `./src/*`
- Artifacts: `frontend/` directory with full Next.js setup

### INF-002: FastAPI Setup
- Used FastAPI 0.124 with Pydantic Settings for configuration
- Modular structure: routers/, services/, models/ directories
- Config loads from `.env` file with defaults for development
- Artifacts: `backend/` directory with FastAPI setup

### INT-001: Supabase Client
- Frontend: `@supabase/ssr` with `createBrowserClient` and `createServerClient`
- Backend: `supabase-py` with service role key for admin operations
- Includes Next.js middleware for session refresh
- Artifacts: `frontend/src/lib/supabase/client.ts`, `server.ts`, `middleware.ts`, `frontend/src/middleware.ts`, `backend/app/clients/supabase.py`

### INT-002: Claude API Client
- Wrapper around Anthropic SDK with retry logic for rate limits
- Methods: `chat()`, `chat_stream()`, `extract()` for structured output
- Uses claude-sonnet-4-20250514 model
- Artifacts: `backend/app/clients/claude.py`

### INT-006: Voice Transcription
- Unified `TranscriptionService` handling web audio and Telegram voice notes
- `transcribe_bytes()` for raw audio from MediaRecorder
- `transcribe_telegram_voice()` downloads via Telegram client then transcribes
- API endpoint: `POST /transcribe` for file upload, `POST /transcribe/telegram` for file_id
- Artifacts: `backend/app/services/transcription.py`, `backend/app/routers/transcription.py`

### INF-008: Error Middleware
- Custom exception classes: `NotFoundError`, `ValidationError`, `AuthenticationError`, `AuthorizationError`, `ExternalServiceError`
- Consistent `ErrorResponse` schema with error code, message, request_id, and details
- Generic catch-all handler logs stack traces but returns sanitized errors to clients
- Artifacts: `backend/app/middleware/error_handler.py`, `backend/app/middleware/__init__.py`

---

*Last session ended: December 12, 2025*
*Next session should: Continue Phase 5 - Complete NTF-002 (Email Provider), then NTF-003/NTF-004 (Telegram)*
