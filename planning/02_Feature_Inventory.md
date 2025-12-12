# Feature Inventory: The Executive Function Prosthetic

**Version:** 1.0
**Date:** December 9, 2025
**Source:** Master Project Specification v1.0
**Status:** Complete

---

## 1. Systematic Extraction

### 1.1 From Project Purpose (MPS §1)

| Question | Extracted Capabilities |
|----------|----------------------|
| What foundational capabilities? | User accounts, profiles, preferences, timezone handling |
| What enables "Automated Structure"? | AI extraction, automatic categorization |
| What enables "Shame-Free Visibility"? | Progress framing in UI, hiding backlog |
| What enables "Bridge to Action"? | Task breakdown, first-step prompts |
| What enables "Proactive System"? | Background jobs, push notifications |

### 1.2 From Essential Functionality (MPS §2)

| Workflow | Discrete Capabilities |
|----------|----------------------|
| Capture & Extract | Text input, voice input, Telegram input, transcription, AI extraction, ghost cards, validation |
| Plan & Commit | Candidate generation, inbox display, drag-to-plan, reordering, day commitment |
| Focus & Execute | Focus mode, breakdown prompts, stuck handling, coaching, completion, rest |
| Reflect & Close | Day review, acknowledgments, summaries, roll/drop, tomorrow prep |

### 1.3 From Scope Boundaries - NOW (MPS §3)

| Infrastructure | Capabilities |
|----------------|--------------|
| Web PWA | Installable app, offline awareness, responsive |
| Telegram Bot | Two-way messaging, webhook handling |
| Email | Transactional sends via Resend |
| Supabase | Schema, RLS, real-time subscriptions |
| AI | Extraction, complexity detection, coaching |

### 1.4 From Technical Context (MPS §4)

| Platform Integration | Capabilities |
|---------------------|--------------|
| Next.js Frontend | Pages, components, PWA manifest |
| FastAPI Backend | API endpoints, SSE streaming |
| Supabase | Auth, database client, real-time |
| Claude API | Chat completions, structured extraction |
| Deepgram | Voice transcription |
| Telegram Bot API | Send/receive messages |
| Resend | Email delivery |

### 1.5 From Workflows (MPS §5)

| Workflow Step | Input Handling | Processing | Output | Error Handling | Feedback |
|---------------|----------------|------------|--------|----------------|----------|
| Capture | Text, voice, Telegram | Transcribe, extract | Action created | Low confidence prompt | Ghost card |
| Plan | Inbox load | Candidate generation | Day plan | Empty state | Visual budget |
| Focus | Task selection | Breakdown check | Progress | Stuck flow | Timer, steps |
| Reflect | EOD trigger | Summary generation | Clean slate | Roll prompts | Acknowledgment |

### 1.6 Cross-Cutting Concerns

| Concern | Capabilities |
|---------|--------------|
| Security | RLS policies, API auth, input sanitization |
| Reliability | Circuit breakers, rate limiting, token budgets |
| Observability | Structured logging, intent log, error tracking |
| Configuration | User preferences, system settings |

---

## 2. Raw Feature List

### Substrate Layer
1. Database schema creation (all tables)
2. Row Level Security policies
3. User authentication (email/password)
4. OAuth authentication (Google)
5. User profile management
6. Session token handling
7. Notification preferences storage
8. Timezone handling
9. Background job: state transitions
10. Background job: morning plan generation
11. Background job: EOD summary generation
12. Background job: inactivity check
13. Real-time subscriptions

### Agentic Layer
14. API orchestrator setup
15. Request routing
16. Circuit breaker implementation
17. Rate limiting
18. Token budgeting
19. Streaming response coordination (SSE)
20. Model abstraction layer
21. Extraction engine: action extraction
22. Extraction engine: avoidance weight detection
23. Extraction engine: complexity detection
24. Extraction engine: confidence scoring
25. Extraction engine: breakdown suggestions
26. Intent classifier
27. Coaching conversation handler
28. Prompt versioning system

### Frontend Layer
29. API client with typed endpoints
30. Optimistic update patterns
31. Streaming response handling
32. Real-time subscription handling
33. Chat message list component
34. Chat input component (text)
35. Chat input component (voice)
36. Ghost card (extraction preview)
37. Confidence validation UI
38. Action list component
39. Inbox view (candidates)
40. Today view (committed plan)
41. Drag-to-plan functionality
42. Reorder functionality
43. Day commit flow
44. Focus mode container
45. Focus task card
46. Timer component
47. Breakdown prompt UI
48. First-step suggestions display
49. Stuck button and options
50. Coaching conversation overlay
51. Task completion flow
52. High-avoidance acknowledgment
53. Rest screen
54. EOD review screen
55. Day summary display
56. Roll/drop UI
57. Tomorrow quick capture
58. Settings page
59. Notification preferences UI
60. Profile management UI

### Notification Layer
61. Notification gateway abstraction
62. Email integration (Resend)
63. Telegram bot setup
64. Telegram: send message
65. Telegram: receive message (webhook)
66. Telegram: handle commands
67. Morning plan notification content
68. EOD summary notification content
69. Channel routing logic

### Integration Layer
70. Supabase client initialization
71. Claude API client
72. Deepgram SDK integration
73. Voice transcription handler
74. Telegram Bot API client
75. Resend API client

### Infrastructure Layer
76. Next.js project setup
77. PWA manifest and service worker
78. FastAPI project setup
79. Vercel deployment config
80. Railway deployment config
81. Railway cron configuration
82. Environment variable management
83. Structured logging setup
84. Intent log recording
85. Error handling middleware
86. Health check endpoint

---

## 3. Completeness Challenge

| Question | Verification |
|----------|--------------|
| What handles errors in extraction? | Low confidence → validation UI (#37), Circuit breakers (#16) |
| What validates user input? | Input sanitization in API (#85), Frontend validation |
| What provides feedback on actions? | Ghost cards (#36), Optimistic UI (#30), Acknowledgments (#52) |
| What happens when AI is down? | Circuit breakers (#16), Graceful degradation |
| What handles empty states? | Inbox empty, Today empty, No candidates |
| What happens on first use? | Onboarding flow needed → **ADD** |
| How does user know task was saved? | Ghost card → solid card transition |
| What if voice transcription fails? | Fallback to text, error message → **ADD** |
| What if Telegram webhook fails? | Retry logic, error logging → **ADD** |

### Added Features (from completeness check):
87. Onboarding conversation flow
88. Voice transcription error handling
89. Telegram webhook retry logic
90. Empty state handling (all views)
91. Loading state components
92. Offline awareness UI

---

## 4. Feature Categories

| Category | Code | Description | Count |
|----------|------|-------------|-------|
| **Substrate** | SUB | Database, auth, background jobs | 13 |
| **Agentic** | AGT | AI processing, orchestration | 16 |
| **Frontend Core** | FE | UI components and state | 15 |
| **Frontend Capture** | CAP | Chat, voice, extraction UI | 9 |
| **Frontend Planning** | PLN | Inbox, Today, planning flows | 9 |
| **Frontend Execution** | EXE | Focus mode, breakdown, completion | 13 |
| **Frontend Reflection** | REF | EOD, summaries, acknowledgments | 6 |
| **Notification** | NTF | Telegram, email, routing | 9 |
| **Integration** | INT | External service clients | 6 |
| **Infrastructure** | INF | Setup, deployment, cross-cutting | 11 |

---

## 5. Feature Inventory (Categorized)

### SUB: Substrate Layer

| ID | Feature | Description | Complexity | MPS Source |
|----|---------|-------------|------------|------------|
| SUB-001 | Database Schema | Create all tables (profiles, actions, conversations, themes, extractions, intent_log) | Medium | §4, §6 |
| SUB-002 | RLS Policies | Row Level Security on all user-owned tables | Medium | §3.1 |
| SUB-003 | Email/Password Auth | User registration and login with email | Easy | §4.3 |
| SUB-004 | Google OAuth | OAuth integration for Google sign-in | Medium | §4.3 |
| SUB-005 | Profile Management | CRUD operations on user profile | Easy | §6.3 |
| SUB-006 | Session Handling | Token refresh, session validation | Easy | §4.3 |
| SUB-007 | Notification Preferences | Store and retrieve notification settings | Easy | §6.3 |
| SUB-008 | Timezone Handling | Store and apply user timezone | Easy | §6.3 |
| SUB-009 | Job: State Transitions | Daily job: rolled→active, active→dormant | Medium | §5.2 |
| SUB-010 | Job: Morning Plan | Generate plan candidates, send notification | Medium | §5.2 |
| SUB-011 | Job: EOD Summary | Generate summary, send notification | Medium | §5.4 |
| SUB-012 | Job: Inactivity Check | Detect 3+ days silent, send check-in | Easy | §3.1 |
| SUB-013 | Real-time Subscriptions | Supabase real-time for action updates | Medium | §4.2 |

---

### AGT: Agentic Layer

| ID | Feature | Description | Complexity | MPS Source |
|----|---------|-------------|------------|------------|
| AGT-001 | Orchestrator Setup | FastAPI app with routing, middleware | Medium | §4.1, §4.2 |
| AGT-002 | Request Router | Route intents to appropriate handlers | Easy | §4.2 |
| AGT-003 | Circuit Breakers | Fail-fast after repeated AI failures | Medium | §8 |
| AGT-004 | Rate Limiting | Per-user request limits | Easy | §4.2 |
| AGT-005 | Token Budgeting | Track and limit token usage per user/day | Medium | §4.2 |
| AGT-006 | SSE Streaming | Stream AI responses to frontend | Medium | §4.2 |
| AGT-007 | Model Abstraction | Interface to swap AI providers | Easy | §4.1 |
| AGT-008 | Extract: Actions | Parse actions from raw text | Hard | §5.1 |
| AGT-009 | Extract: Avoidance Weight | Detect emotional resistance (1-5) | Hard | §5.1, §6.1 |
| AGT-010 | Extract: Complexity | Classify atomic/composite/project | Medium | §5.1, §6.1 |
| AGT-011 | Extract: Confidence | Self-assess extraction certainty | Medium | §5.1 |
| AGT-012 | Extract: Breakdown | Suggest first steps for complex tasks | Hard | §5.3 |
| AGT-013 | Intent Classifier | Classify user message intent | Medium | §5.1 |
| AGT-014 | Coaching Handler | Manage stuck/coaching conversations | Hard | §5.3 |
| AGT-015 | Prompt Versioning | Version and track prompt changes | Easy | §4.2 |
| AGT-016 | Extraction Orchestrator | Coordinate parallel extraction pipeline | Medium | §5.1 |

---

### FE: Frontend Core

| ID | Feature | Description | Complexity | MPS Source |
|----|---------|-------------|------------|------------|
| FE-001 | API Client | Typed client for all backend endpoints | Medium | §4.2 |
| FE-002 | Optimistic Updates | Update UI before API confirms | Medium | §7.2 |
| FE-003 | SSE Handler | Handle streaming responses | Medium | §4.2 |
| FE-004 | Real-time Handler | Subscribe to Supabase changes | Medium | §4.2 |
| FE-005 | Action List Component | Display list of actions | Easy | §5.2 |
| FE-006 | Action Card Component | Single action display with indicators | Easy | §6.1 |
| FE-007 | Avoidance Indicator | Dot display for avoidance weight | Easy | §7.1 |
| FE-008 | Timer Component | Elapsed/remaining time display | Easy | §5.3 |
| FE-009 | Loading States | Skeleton/spinner components | Easy | §7.2 |
| FE-010 | Empty States | "No items" displays for all views | Easy | §3 |
| FE-011 | Offline Awareness | Detect and display offline status | Easy | §3.1 |
| FE-012 | PWA Manifest | Installable app configuration | Easy | §3.1 |
| FE-013 | Service Worker | Basic offline/caching strategy | Medium | §3.1 |
| FE-014 | Responsive Layout | Mobile/tablet/desktop breakpoints | Medium | §7.3 |
| FE-015 | Navigation Component | Navbar (desktop) / Bottom tabs (mobile) | Easy | §7.2 |

---

### CAP: Frontend Capture

| ID | Feature | Description | Complexity | MPS Source |
|----|---------|-------------|------------|------------|
| CAP-001 | Chat Message List | Display conversation messages | Easy | §5.1 |
| CAP-002 | Chat Text Input | Text input with send button | Easy | §5.1 |
| CAP-003 | Chat Voice Input | Voice recording with Deepgram | Medium | §5.1 |
| CAP-004 | Ghost Card | Immediate placeholder during extraction | Medium | §5.1 |
| CAP-005 | Confidence Validation | "Did you mean...?" prompt for low confidence | Medium | §5.1 |
| CAP-006 | Correction Flow | Edit extracted action before saving | Easy | §5.1 |
| CAP-007 | Voice Error Handling | Display error when transcription fails | Easy | §5.1 |
| CAP-008 | Quick Capture Overlay | Minimal capture during focus mode | Easy | §5.3 |
| CAP-009 | Capture Page Container | Orchestrate capture flow state machine | Medium | §5.1 |

---

### PLN: Frontend Planning

| ID | Feature | Description | Complexity | MPS Source |
|----|---------|-------------|------------|------------|
| PLN-001 | Inbox View | Display candidate actions (max 12) | Medium | §5.2 |
| PLN-002 | Today View | Display committed day plan | Medium | §5.2 |
| PLN-003 | Drag to Plan | Drag action from Inbox to Today | Medium | §5.2 |
| PLN-004 | Reorder Tasks | Drag to reorder within Today | Medium | §5.2 |
| PLN-005 | Day Commit | "Start Day" button and flow | Easy | §5.2 |
| PLN-006 | Time Budget Display | Visual indicator of day capacity | Easy | §5.2 |
| PLN-007 | Add More Tasks | Button to open capture from Today | Easy | §5.2 |
| PLN-008 | Remove from Today | Swipe/button to remove task | Easy | §5.2 |
| PLN-009 | Planning Page Container | Orchestrate planning flow state | Medium | §5.2 |

---

### EXE: Frontend Execution

| ID | Feature | Description | Complexity | MPS Source |
|----|---------|-------------|------------|------------|
| EXE-001 | Focus Mode Container | Full-screen focus with hidden nav | Medium | §5.3 |
| EXE-002 | Focus Task Card | Large task display with details | Easy | §5.3 |
| EXE-003 | Subtask Checklist | Display and check off subtasks | Easy | §5.3 |
| EXE-004 | Focus Timer | Elapsed time display (subtle) | Easy | §5.3 |
| EXE-005 | Breakdown Prompt | "What's the smallest first step?" | Medium | §5.3 |
| EXE-006 | First Step Suggestions | AI-suggested micro-steps | Medium | §5.3 |
| EXE-007 | Stuck Button | Trigger stuck flow | Easy | §5.3 |
| EXE-008 | Stuck Options | Quick options for what's blocking | Easy | §5.3 |
| EXE-009 | Coaching Overlay | Conversation for stuck users | Medium | §5.3 |
| EXE-010 | Complete Task Flow | Mark done with optional reflection | Easy | §5.3 |
| EXE-011 | Avoidance Acknowledgment | Special callout for hard wins | Easy | §5.3 |
| EXE-012 | Rest Screen | Break between focus blocks | Easy | §5.3 |
| EXE-013 | Focus Mode Page | Orchestrate focus mode phase transitions | Medium | §5.3 |

---

### REF: Frontend Reflection

| ID | Feature | Description | Complexity | MPS Source |
|----|---------|-------------|------------|------------|
| REF-001 | EOD Trigger | Time-based or manual trigger | Easy | §5.4 |
| REF-002 | Day Review Screen | List completed and remaining | Medium | §5.4 |
| REF-003 | Win Highlights | Special display for high-avoidance wins | Easy | §5.4 |
| REF-004 | Day Summary Display | AI narrative of the day | Easy | §5.4 |
| REF-005 | Roll/Drop Controls | Buttons to defer or drop tasks | Easy | §5.4 |
| REF-006 | Tomorrow Quick Capture | Brief input for tomorrow's thoughts | Easy | §5.4 |

---

### NTF: Notification Layer

| ID | Feature | Description | Complexity | MPS Source |
|----|---------|-------------|------------|------------|
| NTF-001 | Gateway Abstraction | Unified send interface | Easy | §4.1 |
| NTF-002 | Email Client (Resend) | Send emails via Resend API | Easy | §4.1 |
| NTF-003 | Telegram Bot Setup | Register bot, configure webhook | Medium | §4.1 |
| NTF-004 | Telegram: Send | Send message to user | Easy | §4.1 |
| NTF-005 | Telegram: Receive | Handle incoming webhook | Medium | §4.1 |
| NTF-006 | Telegram: Commands | Handle /start, /help, etc. | Easy | §4.1 |
| NTF-007 | Morning Plan Content | Format morning notification | Easy | §5.2 |
| NTF-008 | EOD Summary Content | Format EOD notification | Easy | §5.4 |
| NTF-009 | Channel Router | Route to user's preferred channel | Easy | §4.3 |

---

### INT: Integration Layer

| ID | Feature | Description | Complexity | MPS Source |
|----|---------|-------------|------------|------------|
| INT-001 | Supabase Client | Initialize and configure client | Easy | §4.1 |
| INT-002 | Claude API Client | Wrapper for Anthropic API | Medium | §4.1 |
| INT-003 | Deepgram Client | Wrapper for transcription | Medium | §4.1 |
| INT-004 | Telegram API Client | Wrapper for Bot API | Easy | §4.1 |
| INT-005 | Resend Client | Wrapper for email API | Easy | §4.1 |
| INT-006 | Voice Transcription | End-to-end voice→text flow | Medium | §5.1 |

---

### INF: Infrastructure Layer

| ID | Feature | Description | Complexity | MPS Source |
|----|---------|-------------|------------|------------|
| INF-001 | Next.js Setup | Initialize project with Tailwind | Easy | §4.1 |
| INF-002 | FastAPI Setup | Initialize project with structure | Easy | §4.1 |
| INF-003 | Vercel Config | Deployment configuration | Easy | §4.1 |
| INF-004 | Railway Config | Backend deployment + cron | Medium | §4.1 |
| INF-005 | Environment Config | Env var management | Easy | §4.1 |
| INF-006 | Structured Logging | JSON logging with context | Easy | §4.2 |
| INF-007 | Intent Log Recording | Log all user intents for training | Easy | §6.2 |
| INF-008 | Error Middleware | Global error handling | Easy | §4.2 |
| INF-009 | Health Endpoint | /health for monitoring | Easy | §4.2 |
| INF-010 | Onboarding Flow | First-use conversation | Medium | §5.1 |
| INF-011 | CORS Configuration | Allow frontend origins | Easy | §4.2 |

---

## 6. Summary Statistics

| Category | Easy | Medium | Hard | Total |
|----------|------|--------|------|-------|
| SUB | 6 | 7 | 0 | 13 |
| AGT | 4 | 7 | 5 | 16 |
| FE | 10 | 5 | 0 | 15 |
| CAP | 4 | 5 | 0 | 9 |
| PLN | 4 | 5 | 0 | 9 |
| EXE | 7 | 6 | 0 | 13 |
| REF | 5 | 1 | 0 | 6 |
| NTF | 7 | 2 | 0 | 9 |
| INT | 4 | 2 | 0 | 6 |
| INF | 9 | 2 | 0 | 11 |
| **Total** | **60** | **42** | **5** | **107** |

---

## 7. High-Risk Features (Hard Complexity)

| ID | Feature | Risk Factor | Mitigation |
|----|---------|-------------|------------|
| AGT-008 | Extract: Actions | Prompt engineering, accuracy | Synthetic test set, iteration |
| AGT-009 | Extract: Avoidance Weight | Subjective detection | Calibration with real examples |
| AGT-012 | Extract: Breakdown | Context-dependent suggestions | Template library, user feedback |
| AGT-014 | Coaching Handler | Multi-turn conversation state | Clear conversation types, exits |

---

*End of Feature Inventory*
