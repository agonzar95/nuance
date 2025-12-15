# Implementation Record

## Project Status
- **Current Phase:** 7 - Workflow Features (IN PROGRESS)
- **Total Features:** 79 completed of 107 total
- **Last Updated:** December 15, 2025
- **Last Commit:** `425216d` [PHASE-07] Stage 1 - Workflow Foundation Components

---

## Current Phase: Phase 7 - Workflow Features

**Goal:** Build the complete user workflows: Capture, Planning, Execution, Reflection.

### Phase 7 Features (11/26 Complete)

#### Stage 1 - Foundation Components (6/6 Complete)

| ID | Feature | Status | Complexity | Dependencies |
|----|---------|--------|------------|--------------|
| CAP-001 | Chat Message List | DONE | Easy | FE-003 |
| PLN-001 | Inbox View | DONE | Easy | FE-006, FE-007, FE-010 |
| PLN-002 | Today View | DONE | Easy | FE-010 |
| REF-003 | Win Highlights | DONE | Easy | FE-007 |
| REF-005 | Roll/Drop Controls | DONE | Easy | FE-007 |
| REF-006 | Tomorrow Quick Capture | DONE | Easy | CAP-002 |

#### Stage 2 - Execution Core (4/4 Complete)

| ID | Feature | Status | Complexity | Dependencies |
|----|---------|--------|------------|--------------|
| EXE-002 | Focus Task Card | DONE | Easy | FE-007, EXE-003 |
| EXE-001 | Focus Mode Container | DONE | Easy | EXE-002, EXE-004 |
| EXE-005 | Breakdown Prompt | DONE | Easy | EXE-003 |
| EXE-012 | Rest Screen | DONE | Easy | EXE-001 |

#### Stage 3 - Capture Completions (0/5 Pending)

| ID | Feature | Status | Complexity | Dependencies |
|----|---------|--------|------------|--------------|
| CAP-003 | Chat Voice Input | TODO | Medium | INT-003, INT-006 |
| CAP-004 | Ghost Card | TODO | Easy | FE-006, AGT-016 |
| CAP-005 | Confidence Validation | TODO | Easy | AGT-016, CAP-006 |
| CAP-007 | Voice Error Handling | TODO | Easy | CAP-003 |
| CAP-008 | Quick Capture Overlay | TODO | Easy | EXE-001 |

#### Stage 4 - Planning Completions (0/5 Pending)

| ID | Feature | Status | Complexity | Dependencies |
|----|---------|--------|------------|--------------|
| PLN-003 | Drag to Plan | TODO | Easy | PLN-001, PLN-002 |
| PLN-004 | Reorder Tasks | TODO | Easy | PLN-002, FE-002 |
| PLN-005 | Day Commit | TODO | Easy | PLN-002, EXE-001 |
| PLN-007 | Add More Tasks | TODO | Easy | CAP-002, FE-005 |
| PLN-008 | Remove from Today | TODO | Easy | PLN-002, FE-002 |

#### Stage 5 - Execution Completions (1/6 Pending)

| ID | Feature | Status | Complexity | Dependencies |
|----|---------|--------|------------|--------------|
| EXE-004 | Focus Timer | DONE | Easy | FE-008 |
| EXE-006 | First Step Suggestions | TODO | Medium | AGT-012 |
| EXE-009 | Coaching Overlay | TODO | Medium | AGT-014, CAP-001 |
| EXE-008 | Stuck Options | TODO | Easy | EXE-005, EXE-009 |
| EXE-007 | Stuck Button | TODO | Easy | EXE-008 |
| EXE-010 | Complete Task Flow | TODO | Easy | EXE-011, EXE-012 |

### Phase 7 Validation Criteria

| Criterion | Test | Status |
|-----------|------|--------|
| Chat displays | Messages render in scrollable list | READY |
| Inbox shows actions | All inbox actions displayed | READY |
| Today view works | Today's planned actions display | READY |
| Win highlights | High-avoidance completions celebrated | READY |
| Roll/drop works | Remaining tasks roll or drop | READY |
| Tomorrow capture | Quick capture for tomorrow | READY |
| Focus task card | Task displays with title, avoidance, subtasks | READY |
| Focus mode container | Full-screen with timer and exit confirm | READY |
| Breakdown prompt | Prompts for first step on complex tasks | READY |
| Rest screen | Calming break screen with countdown | READY |
| TypeScript passes | `npm run typecheck` exits with 0 | PASS |

---

## Completed: Phase 6 - Frontend Layer

**Goal:** Build frontend infrastructure: API client, real-time handling, and PWA.
**Status:** COMPLETE

---

## Completed: Phase 5 - Notifications

**Goal:** Build notification infrastructure for email and Telegram delivery.
**Status:** COMPLETE

---

## Completed: Phase 4 - AI Layer

**Goal:** Build the complete agentic infrastructure: orchestration, extractors, and handlers.
**Status:** COMPLETE

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

### NTF-002: Email Client (Resend)
- `EmailProvider` implements `NotificationProvider` interface
- Wraps existing `ResendClient` from INT-005
- Exponential backoff retry (3 retries, 2^attempt seconds)
- HTML email formatting with type-specific templates (morning plan, EOD summary)
- Gets user email via Supabase admin API
- Artifacts: `backend/app/services/notifications/providers/email.py`

### NTF-003: Telegram Bot Setup
- `TelegramBotSetup` class for webhook configuration
- `TelegramBotConfig` dataclass with bot_token, webhook_url, webhook_secret
- Methods: verify_bot(), setup_webhook(), get_webhook_info(), delete_webhook()
- Added `app_url` and `telegram_webhook_secret` to config settings
- Artifacts: `backend/app/services/notifications/telegram/setup.py`, updated `backend/app/config.py`

### NTF-004: Telegram Send Provider
- `TelegramNotificationProvider` implements `NotificationProvider`
- Wraps existing `TelegramClient` from INT-004
- Markdown message formatting with type-specific templates
- Gets chat_id from profiles table
- Artifacts: `backend/app/services/notifications/providers/telegram.py`

### NTF-005: Telegram Receive Handler
- `TelegramHandler` processes incoming updates from webhook
- `TelegramUpdate` dataclass parses message, chat_id, voice_file_id
- Routes commands to `TelegramCommandHandler`
- Looks up user by chat_id, processes capture via ExtractionOrchestrator
- Supports voice transcription via INT-006
- Saves extracted actions to database
- Artifacts: `backend/app/services/notifications/telegram/handler.py`

### NTF-006: Telegram Commands
- `TelegramCommandHandler` handles /start, /help, /today, /status
- /start: Welcome message, generates connection token for new users
- /help: Shows available commands and usage examples
- /today: Displays today's planned actions with completion status
- /status: Shows progress stats (completed, time tracked, inbox count)
- Artifacts: `backend/app/services/notifications/telegram/commands.py`

### NTF-009: Channel Router
- `ChannelRouter` determines which channel to use for notifications
- `NotificationPreferences` and `UserChannelConfig` dataclasses
- Reads preferences from profiles table (notification_channel, notification_enabled)
- Falls back to available channel if preferred unavailable
- get_available_channels() returns list of configured channels
- Artifacts: `backend/app/services/notifications/router.py`

### NTF-001: Gateway Abstraction
- `NotificationGateway` provides unified interface
- Methods: send(), send_to_channel(), send_to_all()
- Routes via ChannelRouter based on user preferences
- Registers providers at initialization
- Factory function handles provider availability gracefully
- Artifacts: `backend/app/services/notifications/gateway.py`

### Telegram Router
- FastAPI router at `/telegram` prefix
- Webhook endpoint `POST /telegram/webhook` with secret token verification
- Management endpoints: `/webhook/info`, `/webhook/setup`, `/bot/verify`
- DELETE `/webhook` for removing webhook
- Artifacts: `backend/app/routers/telegram.py`

---

## Phase 6 Implementation Notes

### FE-001: API Client
- Typed `ApiClient` class with automatic auth header injection
- Methods for actions (CRUD), AI (chat, process), profile, conversations
- `ApiError` class with status helpers (isAuthError, isRateLimited, etc.)
- React Query integration with `queryKeys` factory
- Artifacts: `frontend/src/lib/api.ts`, `frontend/src/types/api.ts`, `frontend/src/lib/query.ts`

### FE-002: Optimistic Updates
- `useOptimisticMutation` hook for generic optimistic patterns
- Pre-built hooks: `useOptimisticCompleteAction`, `useOptimisticUpdateAction`, `useOptimisticDeleteAction`, `useOptimisticReorderActions`
- Automatic rollback on error, cache invalidation on settle
- Artifacts: `frontend/src/hooks/useOptimisticMutation.ts`

### FE-003: SSE Handler
- `useSSE` hook for basic EventSource connections
- `useProcessStream` for AI process endpoint with POST streaming
- `useChatStream` for AI chat endpoint streaming
- Handles message/done/error events, content accumulation
- Artifacts: `frontend/src/hooks/useSSE.ts`

### FE-004: Real-time Handler
- `useRealtimeSync` integrates Supabase real-time with React Query
- Handles INSERT/UPDATE/DELETE events for actions table
- Specialized hooks: `useRealtimeTodayActions`, `useRealtimeInboxActions`
- Automatic cache updates without full refetch
- Artifacts: `frontend/src/hooks/useRealtimeSync.ts`

### FE-006: Action Card Component
- `ActionCard` displays action with title, avoidance indicator, time estimate
- Variants: default, compact, focus
- Status-based styling with colored left border
- Supports draggable and selected states
- Artifacts: `frontend/src/components/actions/ActionCard.tsx`

### FE-005: Action List Component
- `ActionList` renders actions with empty/loading states
- Pre-configured variants: `InboxActionList`, `TodayActionList`, `CompactActionList`
- `GroupedActionList` for displaying actions by category
- Artifacts: `frontend/src/components/actions/ActionList.tsx`

### FE-012: PWA Manifest
- Complete manifest.json with name, icons, shortcuts
- App metadata in layout.tsx (viewport, theme-color, apple-web-app)
- SVG icon as placeholder (real icons needed for production)
- Artifacts: `frontend/public/manifest.json`, updated `frontend/src/app/layout.tsx`

### FE-013: Service Worker
- Custom service worker with cache strategies
- Static assets: Cache-first
- API requests: Network-first with cache fallback
- Navigation: Network-first with offline fallback page
- `ServiceWorkerProvider` component for registration and updates
- Artifacts: `frontend/public/sw.js`, `frontend/src/app/offline/page.tsx`, `frontend/src/components/providers/ServiceWorkerProvider.tsx`

### FE-014: Responsive Layout
- `AppLayout` with side navbar (desktop) and bottom tabs (mobile)
- `SplitLayout` for planning page (inbox + today)
- `FocusLayout` for minimal focus mode chrome
- `PageContainer` for standard page wrapper with title
- Artifacts: `frontend/src/components/layout/AppLayout.tsx`

### FE-015: Navigation Component
- `Navbar` for desktop with logo, nav items, quick add button
- `BottomTabs` for mobile with floating action button
- Active route highlighting via usePathname
- Routes: /capture, /plan, /focus, /reflect
- Artifacts: `frontend/src/components/layout/Navbar.tsx`, `frontend/src/components/layout/BottomTabs.tsx`

---

## Phase 7 Implementation Notes

### CAP-001: Chat Message List
- `ChatMessageList` component with scrollable message history
- `ChatBubble` subcomponent with role-based styling (user on right, AI on left)
- Support for `streamingContent` prop for real-time AI responses
- `TypingIndicator` component with animated dots
- Auto-scroll to newest message via ref
- Artifacts: `frontend/src/components/chat/ChatMessageList.tsx`

### PLN-001: Inbox View
- `InboxView` component displays AI-curated suggestions (max 12)
- `InboxCard` subcomponent with selection checkbox and AI reasoning
- `Suggestion` type includes action, reasoning, and priorityScore
- Uses `ActionCardSkeleton` for loading state
- Artifacts: `frontend/src/components/planning/InboxView.tsx`

### PLN-002: Today View
- `TodayView` component displays committed plan with date header
- `TodayActionCard` subcomponent with drag handle and remove button
- Shows total planned time, supports reordering
- "Start Day" button triggers focus mode
- Installed `date-fns` and `@hello-pangea/dnd` dependencies
- Artifacts: `frontend/src/components/planning/TodayView.tsx`

### REF-003: Win Highlights
- `WinHighlights` component celebrates high-avoidance completions (weight >= 4)
- Gradient background with decorative star
- `WinCard` subcomponent with avoidance indicator
- `filterHighAvoidanceWins` utility function
- Artifacts: `frontend/src/components/reflection/WinHighlights.tsx`

### REF-005: Roll/Drop Controls
- `RemainingTaskCard` component with roll and drop buttons
- Roll moves task to tomorrow, drop removes with confirmation
- `DropConfirmDialog` inline confirmation overlay
- `BatchRollDropControls` for handling all remaining tasks
- Artifacts: `frontend/src/components/reflection/RemainingTaskCard.tsx`

### REF-006: Tomorrow Quick Capture
- `TomorrowQuickCapture` component for EOD quick thoughts
- Simple text input with captured items list
- Shows "Added for tomorrow" confirmation
- "Finish" or "Skip for now" buttons
- Keyboard support (Escape to skip)
- Artifacts: `frontend/src/components/reflection/TomorrowQuickCapture.tsx`

### EXE-002: Focus Task Card
- `FocusTaskCard` component displays current task prominently
- Large centered title with avoidance indicator
- Shows subtasks via `SubtaskChecklist` integration
- Displays estimated time
- Artifacts: `frontend/src/components/execution/FocusTaskCard.tsx`

### EXE-004: Focus Timer
- `FocusTimer` component displays elapsed time subtly
- Format: MM:SS or H:MM:SS for longer sessions
- `useFocusTimer` hook for timer state management
- Supports pause, resume, reset controls
- Resets when action changes
- Artifacts: `frontend/src/components/execution/FocusTimer.tsx`

### EXE-005: Breakdown Prompt
- `BreakdownPrompt` component for complex task decomposition
- Asks "What's the smallest first step you can take?"
- Text input for user-defined step
- Skip option for clear tasks
- Loading state during save
- Artifacts: `frontend/src/components/execution/BreakdownPrompt.tsx`

### EXE-001: Focus Mode Container
- `FocusModeContainer` provides full-screen focus experience
- Adds `focus-mode` class to body for navbar hiding
- Shows elapsed time via `FocusTimer`
- Action bar with "I'm stuck" and "Done" buttons
- `ExitConfirmDialog` with Escape key trigger
- Artifacts: `frontend/src/components/execution/FocusModeContainer.tsx`

### EXE-012: Rest Screen
- `RestScreen` for calming breaks between focus blocks
- Gradient background with coffee icon
- Countdown timer from suggested minutes (default 5)
- "I'm ready to continue" and "Skip break" options
- Non-pressuring, guilt-free messaging
- Artifacts: `frontend/src/components/execution/RestScreen.tsx`

---

*Last session ended: December 15, 2025*
*Next session should: Continue Phase 7 - Stage 3 Capture Completions (CAP-003, CAP-004, CAP-005, CAP-007, CAP-008)*

**Session Notes:**
- Stage 2 complete (4/4 features + EXE-004): EXE-002, EXE-004, EXE-005, EXE-001, EXE-012
- TypeScript passes
- Ready to start CAP-003 (Chat Voice Input) - depends on INT-003, INT-006 (both done)
