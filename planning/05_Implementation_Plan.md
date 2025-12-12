# Implementation Plan

**Step 5 of Planning Phase**
**Date:** December 11, 2025 (Updated)
**Total Features:** 107 features across 8 phases

---

## Overview

This document transforms the validated dependency matrix into a comprehensive, phase-organized implementation roadmap. Each phase contains features that can be safely built once all previous phases are complete.

**Principle Applied:** "Schedule Implementation by Dependencies" (Principle 7)

---

## Critical Path

The longest dependency chain determines the minimum implementation timeline:

```
INF-001/INF-002 → INF-005 → INT-001 → SUB-001 → SUB-003 → SUB-005 → SUB-007 → NTF-001 → SUB-010 → NTF-007
```

**Critical Path Length:** 10 features

Features on this path must be prioritized—any delay cascades through the entire project.

---

## Phase Summary

| Phase | Name | Features | Focus |
|-------|------|----------|-------|
| 1 | Foundation | 12 | Zero-dependency base components |
| 2 | Core Services | 12 | Deployment configs and integrations |
| 3 | Data Layer | 11 | Database, auth, and subscriptions |
| 4 | AI Layer | 16 | Orchestration, extractors, orchestrator, handlers |
| 5 | Notification Layer | 7 | Email, Telegram, routing |
| 6 | Frontend Layer | 10 | API client, components, PWA |
| 7 | Workflow Features | 26 | Capture, Planning, Execution, Reflection |
| 8 | Jobs & Polish | 13 | Page orchestrators, background jobs, onboarding |

---

## Phase 1: Foundation

**Goal:** Establish zero-dependency base components that all other features build upon.

### Features (12)

| ID | Feature | Complexity | Parallel Group |
|----|---------|------------|----------------|
| INF-001 | Next.js Setup | Easy | A (Infrastructure) |
| INF-002 | FastAPI Setup | Easy | A (Infrastructure) |
| FE-007 | Avoidance Indicator | Easy | B (UI Components) |
| FE-008 | Timer Component | Easy | B (UI Components) |
| FE-009 | Loading States | Easy | B (UI Components) |
| FE-010 | Empty States | Easy | B (UI Components) |
| FE-011 | Offline Awareness | Easy | B (UI Components) |
| CAP-002 | Chat Text Input | Easy | C (Input Components) |
| CAP-006 | Correction Flow | Easy | C (Input Components) |
| EXE-003 | Subtask Checklist | Easy | D (Execution Components) |
| EXE-011 | Avoidance Acknowledgment | Easy | D (Execution Components) |
| PLN-006 | Time Budget Display | Easy | E (Planning Components) |

### Parallel Work Opportunities

All 12 features have no dependencies and can be built simultaneously:
- **Group A:** INF-001 + INF-002 (infrastructure setup, different repos)
- **Group B:** FE-007 through FE-011 (pure React components)
- **Group C:** CAP-002 + CAP-006 (capture UI components)
- **Group D:** EXE-003 + EXE-011 (execution UI components)
- **Group E:** PLN-006 (planning UI component)

### Validation Criteria

| Criterion | Test |
|-----------|------|
| Next.js runs | `npm run dev` starts on port 3000 |
| FastAPI runs | `uvicorn main:app` starts on port 8000 |
| Components render | Storybook/test harness shows all components |
| No console errors | Browser console clean during component render |
| TypeScript passes | `tsc --noEmit` exits with 0 |
| Python types pass | `mypy` exits with 0 |

### Phase Gate

**Phase 1 is complete when:**
- [ ] Next.js dev server starts successfully
- [ ] FastAPI dev server starts successfully
- [ ] All 10 UI components render in isolation
- [ ] Unit tests pass for all components
- [ ] No TypeScript/Python type errors

---

## Phase 2: Core Services

**Goal:** Configure deployment and establish all external service integrations.

**Depends on:** Phase 1 (INF-001, INF-002)

### Features (12)

| ID | Feature | Complexity | Dependencies | Parallel Group |
|----|---------|------------|--------------|----------------|
| INF-003 | Vercel Config | Easy | INF-001 | A |
| INF-004 | Railway Config | Easy | INF-002 | A |
| INF-005 | Environment Config | Easy | INF-001, INF-002 | A |
| INF-006 | Structured Logging | Easy | INF-002 | B |
| INF-011 | CORS Configuration | Easy | INF-002 | B |
| INT-001 | Supabase Client | Easy | INF-005 | C |
| INT-002 | Claude API Client | Easy | INF-005 | C |
| INT-003 | Deepgram Client | Easy | INF-005 | C |
| INT-004 | Telegram API Client | Easy | INF-005 | C |
| INT-005 | Resend Client | Easy | INF-005 | C |
| INT-006 | Voice Transcription | Medium | INT-003 | D |
| INF-008 | Error Middleware | Easy | INF-002, INF-006 | D |

### Parallel Work Opportunities

**After INF-005 is complete, INT-001 through INT-005 can be built in parallel.**

Sequence within phase:
1. INF-003 + INF-004 + INF-005 (can start immediately)
2. INF-006 + INF-011 (after INF-002, so immediately)
3. INT-001..INT-005 (after INF-005)
4. INT-006 + INF-008 (after their dependencies)

### Validation Criteria

| Criterion | Test |
|-----------|------|
| Vercel deploys | Preview deployment succeeds |
| Railway deploys | API container runs successfully |
| Env vars load | All clients initialize without error |
| Supabase connects | `supabase.auth.getSession()` returns |
| Claude responds | Simple prompt returns valid response |
| Deepgram connects | Audio byte stream accepted |
| Telegram connects | Bot receives test message |
| Resend sends | Test email delivered |
| Logging works | Structured logs appear in output |
| CORS works | Frontend can call backend |

### Phase Gate

**Phase 2 is complete when:**
- [ ] All 5 external service clients initialize successfully
- [ ] Deployment pipelines work (Vercel + Railway)
- [ ] Environment variables properly loaded
- [ ] Voice transcription produces text from audio
- [ ] Error middleware catches and logs exceptions
- [ ] Integration tests pass for each client

---

## Phase 3: Data Layer

**Goal:** Establish database schema, authentication, and real-time subscriptions.

**Depends on:** Phase 2 (INT-001 primarily)

### Features (11)

| ID | Feature | Complexity | Dependencies | Parallel Group |
|----|---------|------------|--------------|----------------|
| SUB-001 | Database Schema | Medium | INT-001 | A |
| SUB-002 | RLS Policies | Easy | SUB-001 | B |
| SUB-003 | Email/Password Auth | Easy | SUB-001, INT-001 | B |
| SUB-004 | Google OAuth | Easy | SUB-001, SUB-003 | C |
| SUB-005 | Profile Management | Easy | SUB-001, SUB-002, SUB-003 | C |
| SUB-006 | Session Handling | Easy | SUB-003 | C |
| SUB-007 | Notification Preferences | Easy | SUB-005 | D |
| SUB-008 | Timezone Handling | Easy | SUB-005 | D |
| SUB-009 | Job: State Transitions | Easy | SUB-001, SUB-008 | E |
| SUB-013 | Real-time Subscriptions | Easy | SUB-001, INT-001 | B |
| AGT-003 | Circuit Breakers | Easy | INF-002 | A |

**Note:** AGT-003 included here as it only depends on INF-002 and is needed for Phase 4 resilience.

### Implementation Sequence

```
SUB-001 → [SUB-002, SUB-003, SUB-013]
                    ↓
          [SUB-004, SUB-005, SUB-006]
                    ↓
          [SUB-007, SUB-008]
                    ↓
               SUB-009
```

### Validation Criteria

| Criterion | Test |
|-----------|------|
| Schema applies | Supabase migrations run without error |
| RLS enforces | Unauthorized queries rejected |
| Email auth works | Register → Login → Session created |
| Google OAuth works | OAuth flow completes, session created |
| Profile CRUD works | Create, read, update profile succeeds |
| Session persists | Refresh token works across browser close |
| Prefs save | Notification preferences persist |
| Timezone works | User timezone stored and retrieved |
| Realtime connects | Subscription receives updates |

### Phase Gate

**Phase 3 is complete when:**
- [ ] Database schema deployed to Supabase
- [ ] RLS policies block unauthorized access
- [ ] Email/password registration and login work
- [ ] Google OAuth flow completes successfully
- [ ] Profile CRUD operations work
- [ ] Real-time subscriptions receive updates
- [ ] All auth integration tests pass

---

## Phase 4: AI Layer

**Goal:** Build the complete agentic infrastructure: orchestration, extractors, and handlers.

**Depends on:** Phase 2 (INT-002), Phase 3 (SUB-001)

### Features (16)

| ID | Feature | Complexity | Dependencies | Parallel Group |
|----|---------|------------|--------------|----------------|
| AGT-001 | Orchestrator Setup | Medium | INF-002, INF-008, INT-001 | A |
| AGT-007 | Model Abstraction | Easy | INT-002 | A |
| INF-007 | Intent Log Recording | Easy | SUB-001, INF-002 | A |
| AGT-004 | Rate Limiting | Easy | AGT-001 | B |
| AGT-005 | Token Budgeting | Easy | SUB-001, INT-002 | B |
| AGT-006 | SSE Streaming | Medium | INT-002, AGT-001 | B |
| AGT-015 | Prompt Versioning | Easy | SUB-001 | B |
| AGT-008 | Extract: Actions | Medium | AGT-007, AGT-015 | C |
| AGT-009 | Extract: Avoidance Weight | Medium | AGT-007, AGT-015 | C |
| AGT-010 | Extract: Complexity | Easy | AGT-007 | C |
| AGT-012 | Extract: Breakdown | Medium | AGT-007, AGT-015 | C |
| AGT-013 | Intent Classifier | Easy | AGT-007 | C |
| AGT-011 | Extract: Confidence | Easy | AGT-008 | D |
| AGT-014 | Coaching Handler | Medium | AGT-007, AGT-006 | D |
| AGT-016 | Extraction Orchestrator | Medium | AGT-008, AGT-009, AGT-010, AGT-011 | E |
| AGT-002 | Request Router | Medium | AGT-001, AGT-007, AGT-013, AGT-016, AGT-014 | F |

### Implementation Sequence

```
[AGT-001, AGT-007, INF-007]
           ↓
[AGT-004, AGT-005, AGT-006, AGT-015]
           ↓
[AGT-008, AGT-009, AGT-010, AGT-012, AGT-013]
           ↓
[AGT-011, AGT-014]
           ↓
AGT-016
           ↓
AGT-002
```

### Validation Criteria

| Criterion | Test |
|-----------|------|
| Orchestrator runs | Request/response cycle works |
| Model abstraction works | Claude calls succeed via abstraction |
| Rate limiting enforces | Requests beyond limit rejected |
| SSE streams | Client receives streaming tokens |
| Action extraction works | Text → structured actions |
| Avoidance detection works | High-avoidance tasks flagged |
| Breakdown works | Complex task → subtasks |
| Intent classification works | Message → intent label |
| Coaching responds | Multi-turn coaching dialogue works |
| Router routes | Different intents hit correct handlers |

### Phase Gate

**Phase 4 is complete when:**
- [ ] Orchestrator handles request/response cycle
- [ ] SSE streaming delivers tokens to client
- [ ] All 5 extractors produce valid outputs
- [ ] Extraction orchestrator coordinates parallel extraction
- [ ] Intent classifier routes to correct handler
- [ ] Coaching handler maintains multi-turn state
- [ ] Request router correctly dispatches all intent types
- [ ] Integration tests pass for each extractor

---

## Phase 5: Notification Layer

**Goal:** Build email, Telegram, and routing infrastructure for proactive notifications.

**Depends on:** Phase 2 (INT-004, INT-005, INT-006), Phase 3 (SUB-007), Phase 4 (AGT-016)

### Features (7)

| ID | Feature | Complexity | Dependencies | Parallel Group |
|----|---------|------------|--------------|----------------|
| NTF-002 | Email Client (Resend) | Easy | INT-005 | A |
| NTF-003 | Telegram Bot Setup | Easy | INT-004, INF-005 | A |
| NTF-004 | Telegram Send | Easy | NTF-003, INT-004 | B |
| NTF-005 | Telegram Receive | Easy | NTF-003, INT-004, AGT-016, INT-006 | C |
| NTF-006 | Telegram Commands | Easy | NTF-004, NTF-005 | D |
| NTF-009 | Channel Router | Easy | SUB-007 | C |
| NTF-001 | Gateway Abstraction | Medium | NTF-002, NTF-004, SUB-007, NTF-009 | E |

### Implementation Sequence

```
[NTF-002, NTF-003]
       ↓
    NTF-004
       ↓
[NTF-005, NTF-009]
       ↓
    NTF-006
       ↓
    NTF-001
```

### Validation Criteria

| Criterion | Test |
|-----------|------|
| Email sends | Test email arrives in inbox |
| Bot initializes | Telegram webhook registered |
| Telegram send works | Bot sends message to test chat |
| Telegram receive works | Bot receives and logs incoming message |
| Commands work | /status, /help commands respond |
| Gateway routes | Message sent via correct channel based on prefs |
| Channel router selects | User prefs → correct channel selected |

### Phase Gate

**Phase 5 is complete when:**
- [ ] Email sends via Resend
- [ ] Telegram bot receives and sends messages
- [ ] Telegram commands respond appropriately
- [ ] Gateway abstraction routes to correct channel
- [ ] Channel router respects user preferences
- [ ] Integration tests pass for all channels

---

## Phase 6: Frontend Layer

**Goal:** Build the frontend infrastructure: API client, real-time handling, and PWA.

**Depends on:** Phase 3 (SUB-013), Phase 4 (AGT-006)

### Features (10)

| ID | Feature | Complexity | Dependencies | Parallel Group |
|----|---------|------------|--------------|----------------|
| FE-001 | API Client | Easy | INT-001, INF-001 | A |
| FE-002 | Optimistic Updates | Easy | FE-001 | B |
| FE-003 | SSE Handler | Easy | AGT-006, FE-001 | B |
| FE-004 | Real-time Handler | Easy | INT-001, SUB-013 | B |
| FE-006 | Action Card Component | Easy | FE-007 | C |
| FE-005 | Action List Component | Easy | FE-006, FE-010 | D |
| FE-012 | PWA Manifest | Easy | INF-001 | A |
| FE-013 | Service Worker | Easy | FE-012, FE-011 | E |
| FE-014 | Responsive Layout | Easy | FE-015, INF-001 | F |
| FE-015 | Navigation Component | Easy | INF-001 | A |

### Implementation Sequence

```
[FE-001, FE-012, FE-015]
          ↓
[FE-002, FE-003, FE-004]
          ↓
      FE-006
          ↓
      FE-005
          ↓
[FE-013, FE-014]
```

### Validation Criteria

| Criterion | Test |
|-----------|------|
| API client works | Fetch actions list succeeds |
| Optimistic updates show | UI updates before server confirms |
| SSE handler receives | Streaming AI response displays |
| Real-time updates | Action changes reflect immediately |
| Action card renders | Card displays all action properties |
| Action list renders | List displays multiple action cards |
| PWA installable | "Add to Home Screen" prompt appears |
| Service worker caches | Offline access to cached resources |
| Layout responsive | UI adapts to mobile/tablet/desktop |
| Navigation works | Routes change, active state shows |

### Phase Gate

**Phase 6 is complete when:**
- [ ] API client successfully fetches data
- [ ] Optimistic updates work with rollback on failure
- [ ] SSE streaming displays in real-time
- [ ] Real-time subscriptions trigger UI updates
- [ ] All components render correctly
- [ ] PWA passes Lighthouse PWA audit
- [ ] Service worker caches appropriately
- [ ] Responsive layout works on all breakpoints

---

## Phase 7: Workflow Features

**Goal:** Build the complete user workflows: Capture, Planning, Execution, Reflection.

**Depends on:** Phase 4 (AGT extractors, AGT-016), Phase 5 (NTF gateway), Phase 6 (FE components)

### Features (26)

#### Capture Workflow (6 features)

| ID | Feature | Complexity | Dependencies |
|----|---------|------------|--------------|
| CAP-001 | Chat Message List | Easy | FE-003 |
| CAP-003 | Chat Voice Input | Medium | INT-003, INT-006 |
| CAP-004 | Ghost Card | Easy | FE-006, AGT-016 |
| CAP-005 | Confidence Validation | Easy | AGT-016, CAP-006 |
| CAP-007 | Voice Error Handling | Easy | CAP-003 |
| CAP-008 | Quick Capture Overlay | Easy | EXE-001* |

*CAP-008 depends on EXE-001 which is built later in this phase.

#### Planning Workflow (7 features)

| ID | Feature | Complexity | Dependencies |
|----|---------|------------|--------------|
| PLN-001 | Inbox View | Easy | FE-006, FE-007, FE-010 |
| PLN-002 | Today View | Easy | FE-010 |
| PLN-003 | Drag to Plan | Easy | PLN-001, PLN-002 |
| PLN-004 | Reorder Tasks | Easy | PLN-002, FE-002 |
| PLN-005 | Day Commit | Easy | PLN-002, EXE-001* |
| PLN-007 | Add More Tasks | Easy | CAP-002, FE-005 |
| PLN-008 | Remove from Today | Easy | PLN-002, FE-002 |

#### Execution Workflow (8 features)

| ID | Feature | Complexity | Dependencies |
|----|---------|------------|--------------|
| EXE-004 | Focus Timer | Easy | FE-008 |
| EXE-002 | Focus Task Card | Easy | FE-007, EXE-003 |
| EXE-001 | Focus Mode Container | Easy | EXE-002, EXE-004 |
| EXE-005 | Breakdown Prompt | Easy | EXE-003 |
| EXE-006 | First Step Suggestions | Medium | AGT-012 |
| EXE-007 | Stuck Button | Easy | EXE-008 |
| EXE-008 | Stuck Options | Easy | EXE-005, EXE-009 |
| EXE-009 | Coaching Overlay | Medium | AGT-014, CAP-001 |
| EXE-012 | Rest Screen | Easy | EXE-001 |
| EXE-010 | Complete Task Flow | Easy | EXE-011, EXE-012 |

*Note: EXE-011 (Avoidance Acknowledgment) is built in Phase 1 as a foundation feature.
*Note: EXE-004 (Focus Timer) now depends on FE-008 (Timer Component).

#### Reflection Workflow (3 features)

| ID | Feature | Complexity | Dependencies |
|----|---------|------------|--------------|
| REF-003 | Win Highlights | Easy | FE-007 |
| REF-005 | Roll/Drop Controls | Easy | FE-007 |
| REF-006 | Tomorrow Quick Capture | Easy | CAP-002 |

### Implementation Sequence

Build workflows in order with careful attention to cross-dependencies:

```
# Stage 1: Foundation components for all workflows
[CAP-001, PLN-001, PLN-002, REF-003, REF-005, REF-006]

# Stage 2: Execution core (needed by PLN-005, CAP-008)
[EXE-002] → [EXE-001, EXE-005, EXE-012]

# Stage 3: Capture completions
[CAP-003, CAP-004, CAP-005] → [CAP-007, CAP-008]

# Stage 4: Planning completions
[PLN-003, PLN-004, PLN-005, PLN-007, PLN-008]

# Stage 5: Execution completions
[EXE-006, EXE-009] → [EXE-008] → [EXE-007, EXE-010]
```

### Validation Criteria

| Criterion | Test |
|-----------|------|
| Chat displays | Messages render in scrollable list |
| Voice captures | Speech → text → action created |
| Ghost card shows | Pending action appears during extraction |
| Confidence prompts | Low-confidence triggers validation |
| Inbox shows actions | All inbox actions displayed |
| Today view works | Today's planned actions display |
| Drag to plan works | Action moves from inbox to today |
| Focus mode shows | Single task in focus view |
| Subtasks check off | Checkbox toggles work |
| Stuck flow works | Button → options → coaching |
| Complete flow works | Finish → acknowledgment → rest |
| Reflection shows | Day summary displays |
| Roll/drop works | Remaining tasks roll or drop |

### Phase Gate

**Phase 7 is complete when:**
- [ ] Full capture flow: voice/text → action created
- [ ] Full planning flow: inbox → today → commit
- [ ] Full execution flow: focus → complete → rest
- [ ] Full reflection flow: summary → roll/drop → tomorrow
- [ ] All workflow integration tests pass
- [ ] E2E test: capture → plan → execute → reflect

---

## Phase 8: Page Orchestrators, Jobs & Polish

**Goal:** Build page orchestrators, implement background jobs, onboarding, and remaining integrations.

**Depends on:** Phase 5 (NTF-001), Phase 7 (workflows)

### Features (13)

| ID | Feature | Complexity | Dependencies |
|----|---------|------------|--------------|
| CAP-009 | Capture Page Container | Medium | CAP-001..008, FE-001, AGT-016 |
| PLN-009 | Planning Page Container | Medium | PLN-001..008, FE-001 |
| EXE-013 | Focus Mode Page | Medium | EXE-001..012, FE-001, AGT-014 |
| SUB-010 | Job: Morning Plan | Medium | SUB-001, SUB-007, SUB-008, NTF-001 |
| SUB-011 | Job: EOD Summary | Medium | SUB-001, SUB-007, SUB-008, NTF-001 |
| SUB-012 | Job: Inactivity Check | Easy | SUB-001, SUB-007, NTF-001 |
| NTF-007 | Morning Plan Content | Easy | SUB-010 |
| NTF-008 | EOD Summary Content | Easy | SUB-011 |
| REF-001 | EOD Trigger | Easy | SUB-008 |
| REF-002 | Day Review Screen | Easy | REF-003, REF-005, REF-004 |
| REF-004 | Day Summary Display | Easy | SUB-011 |
| INF-009 | Health Endpoint | Easy | INF-002 |
| INF-010 | Onboarding Flow | Medium | SUB-003, SUB-005 |

### Implementation Sequence

```
# Stage 1: Page orchestrators (all workflow features complete)
[CAP-009, PLN-009, EXE-013]

# Stage 2: Core jobs
[SUB-010, SUB-011, SUB-012]

# Stage 3: Notification content
[NTF-007, NTF-008]

# Stage 4: Reflection completions
[REF-004] → [REF-002]
[REF-001]  # Independent: depends only on SUB-008 (Phase 3)

# Stage 5: Infrastructure polish
[INF-009, INF-010]
```

### Validation Criteria

| Criterion | Test |
|-----------|------|
| Capture page works | Full state machine handles all user flows |
| Planning page works | Drag-drop and state transitions work |
| Focus Mode page works | All 8 phases (loading→rest) work correctly |
| Morning job runs | Scheduled trigger sends plan notification |
| EOD job runs | Scheduled trigger sends summary |
| Inactivity check works | No activity → nudge sent |
| Morning content correct | Plan includes today's tasks |
| EOD content correct | Summary includes completed/remaining |
| EOD trigger fires | Time-based trigger works |
| Day review shows | Full review screen renders |
| Health returns OK | /health endpoint returns status |
| Onboarding completes | New user → profile → dashboard |

### Phase Gate

**Phase 8 is complete when:**
- [ ] All 3 page orchestrators coordinate their workflows
- [ ] All 3 background jobs run on schedule
- [ ] Morning and EOD notifications deliver correctly
- [ ] Complete reflection flow with job-generated content
- [ ] Onboarding flow works for new users
- [ ] Health endpoint returns correct status
- [ ] All integration tests pass
- [ ] MVP feature complete

---

## Implementation Guidance

### For Each Feature

Follow this workflow per atomic feature (Principle 8):

1. **Assemble Context**
   - Read feature spec from `03_Feature_Specs/`
   - Load dependency code that's already implemented
   - Note validation criteria from spec

2. **Implement**
   - Write code following technical contracts
   - Run immediately, gather feedback
   - Test against validation criteria

3. **Validate**
   - All tests pass
   - No console errors
   - Visual/behavioral inspection clean

4. **Commit**
   - Atomic commit with feature ID in message
   - Format: `[FEATURE-ID] Brief description`

### Parallel Development

When working in parallel:
- Features within same parallel group can be built simultaneously
- Ensure no shared state conflicts
- Merge to main frequently to avoid drift
- Run full test suite after each merge

### Blocker Resolution

If blocked:
1. Check if dependency is truly blocking or just nice-to-have
2. Consider stub/mock for temporary unblocking
3. If truly blocked, switch to another parallel feature
4. Document blockers for resolution

### Progress Tracking

Update as implementation progresses:

```markdown
## Progress

| Phase | Status | Completion |
|-------|--------|------------|
| 1. Foundation | ⬜ Not Started | 0/12 |
| 2. Core Services | ⬜ Not Started | 0/12 |
| 3. Data Layer | ⬜ Not Started | 0/11 |
| 4. AI Layer | ⬜ Not Started | 0/16 |
| 5. Notification | ⬜ Not Started | 0/7 |
| 6. Frontend | ⬜ Not Started | 0/10 |
| 7. Workflows | ⬜ Not Started | 0/26 |
| 8. Page Orchestrators & Jobs | ⬜ Not Started | 0/13 |
```

---

## Feature Checklist

Complete checklist for tracking individual feature implementation:

### Phase 1: Foundation (12)
- [ ] INF-001 Next.js Setup
- [ ] INF-002 FastAPI Setup
- [ ] FE-007 Avoidance Indicator
- [ ] FE-008 Timer Component
- [ ] FE-009 Loading States
- [ ] FE-010 Empty States
- [ ] FE-011 Offline Awareness
- [ ] CAP-002 Chat Text Input
- [ ] CAP-006 Correction Flow
- [ ] EXE-003 Subtask Checklist
- [ ] EXE-011 Avoidance Acknowledgment
- [ ] PLN-006 Time Budget Display

### Phase 2: Core Services (12)
- [ ] INF-003 Vercel Config
- [ ] INF-004 Railway Config
- [ ] INF-005 Environment Config
- [ ] INF-006 Structured Logging
- [ ] INF-011 CORS Configuration
- [ ] INT-001 Supabase Client
- [ ] INT-002 Claude API Client
- [ ] INT-003 Deepgram Client
- [ ] INT-004 Telegram API Client
- [ ] INT-005 Resend Client
- [ ] INT-006 Voice Transcription
- [ ] INF-008 Error Middleware

### Phase 3: Data Layer (11)
- [ ] SUB-001 Database Schema
- [ ] SUB-002 RLS Policies
- [ ] SUB-003 Email/Password Auth
- [ ] SUB-004 Google OAuth
- [ ] SUB-005 Profile Management
- [ ] SUB-006 Session Handling
- [ ] SUB-007 Notification Preferences
- [ ] SUB-008 Timezone Handling
- [ ] SUB-009 Job: State Transitions
- [ ] SUB-013 Real-time Subscriptions
- [ ] AGT-003 Circuit Breakers

### Phase 4: AI Layer (16)
- [ ] AGT-001 Orchestrator Setup
- [ ] AGT-007 Model Abstraction
- [ ] INF-007 Intent Log Recording
- [ ] AGT-004 Rate Limiting
- [ ] AGT-005 Token Budgeting
- [ ] AGT-006 SSE Streaming
- [ ] AGT-015 Prompt Versioning
- [ ] AGT-008 Extract: Actions
- [ ] AGT-009 Extract: Avoidance Weight
- [ ] AGT-010 Extract: Complexity
- [ ] AGT-012 Extract: Breakdown
- [ ] AGT-013 Intent Classifier
- [ ] AGT-011 Extract: Confidence
- [ ] AGT-014 Coaching Handler
- [ ] AGT-016 Extraction Orchestrator
- [ ] AGT-002 Request Router

### Phase 5: Notification Layer (7)
- [ ] NTF-002 Email Client (Resend)
- [ ] NTF-003 Telegram Bot Setup
- [ ] NTF-004 Telegram Send
- [ ] NTF-005 Telegram Receive
- [ ] NTF-006 Telegram Commands
- [ ] NTF-001 Gateway Abstraction
- [ ] NTF-009 Channel Router

### Phase 6: Frontend Layer (10)
- [ ] FE-001 API Client
- [ ] FE-002 Optimistic Updates
- [ ] FE-003 SSE Handler
- [ ] FE-004 Real-time Handler
- [ ] FE-006 Action Card Component
- [ ] FE-005 Action List Component
- [ ] FE-012 PWA Manifest
- [ ] FE-013 Service Worker
- [ ] FE-014 Responsive Layout
- [ ] FE-015 Navigation Component

### Phase 7: Workflow Features (26)
- [ ] CAP-001 Chat Message List
- [ ] CAP-003 Chat Voice Input
- [ ] CAP-004 Ghost Card
- [ ] CAP-005 Confidence Validation
- [ ] CAP-007 Voice Error Handling
- [ ] CAP-008 Quick Capture Overlay
- [ ] PLN-001 Inbox View
- [ ] PLN-002 Today View
- [ ] PLN-003 Drag to Plan
- [ ] PLN-004 Reorder Tasks
- [ ] PLN-005 Day Commit
- [ ] PLN-007 Add More Tasks
- [ ] PLN-008 Remove from Today
- [ ] EXE-004 Focus Timer
- [ ] EXE-002 Focus Task Card
- [ ] EXE-001 Focus Mode Container
- [ ] EXE-005 Breakdown Prompt
- [ ] EXE-006 First Step Suggestions
- [ ] EXE-007 Stuck Button
- [ ] EXE-008 Stuck Options
- [ ] EXE-009 Coaching Overlay
- [ ] EXE-012 Rest Screen
- [ ] EXE-010 Complete Task Flow
- [ ] REF-003 Win Highlights
- [ ] REF-005 Roll/Drop Controls
- [ ] REF-006 Tomorrow Quick Capture

### Phase 8: Page Orchestrators, Jobs & Polish (13)
- [ ] CAP-009 Capture Page Container
- [ ] PLN-009 Planning Page Container
- [ ] EXE-013 Focus Mode Page
- [ ] SUB-010 Job: Morning Plan
- [ ] SUB-011 Job: EOD Summary
- [ ] SUB-012 Job: Inactivity Check
- [ ] NTF-007 Morning Plan Content
- [ ] NTF-008 EOD Summary Content
- [ ] REF-001 EOD Trigger
- [ ] REF-002 Day Review Screen
- [ ] REF-004 Day Summary Display
- [ ] INF-009 Health Endpoint
- [ ] INF-010 Onboarding Flow

---

*Planning Phase Complete. Ready for Implementation Phase.*

*Next Step: Begin Implementation Phase, Step 1 (Context Assembly) for first feature.*
