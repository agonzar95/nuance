# Master Project Specification: The Executive Function Prosthetic

**Version:** 1.0 (The "Make It Work" Release)
**Date:** December 9, 2025
**Status:** Approved for Development

---

## 1. Project Purpose

### 1.1 The Problem

Traditional productivity tools impose an "Admin Tax": they require users to be their own project managers. For neurodivergent brains (ADHD, Anxiety, Burnout), this friction creates:

- **The Shame Cycle:** Overdue lists trigger avoidance ("The Wall of Awful")
- **Initiation Paralysis:** Inability to start vague or large tasks
- **Time Blindness:** Inability to estimate effort or feel the passage of time
- **Structure Burden:** Managing the system becomes the work itself

### 1.2 Who Experiences It

Users with executive function challenges who:
- Struggle to hold context, estimate time, and self-initiate
- Get abandoned by apps at the moment of execution
- Experience shame when plans aren't followed
- Need scaffolding during work, not just task lists

### 1.3 Core Value Proposition

| Value | Description |
|-------|-------------|
| **Automated Structure** | Input is chaos (voice/chat); Output is structure. No manual filing. |
| **Shame-Free Visibility** | Progress framing everywhere. Show what's done, not what's left. |
| **Bridge to Action** | Deconstructs tasks into micro-steps to solve paralysis. |
| **Proactive System** | App reaches out through channels user already uses (Telegram/Email). |
| **Contextual Intelligence** | AI acts as compassionate coach, learns patterns, never judges. |

---

## 2. Essential Functionality (Core Workflows)

The system operates through **four fundamental workflows**:

| # | Workflow | Purpose |
|---|----------|---------|
| 1 | **Capture & Extract** | Eliminate the "Admin Tax" of entry |
| 2 | **Plan & Commit** | Cure time blindness and overwhelm |
| 3 | **Focus & Execute** | Overcome initiation paralysis |
| 4 | **Reflect & Close** | Replace shame with momentum |

---

## 3. Scope Boundaries

### 3.1 NOW (MVP - "Dogfood" Version)

**Platform:**
- Web PWA (Primary interface)
- Telegram Bot (Mobile capture + notifications)
- Email notifications (via Resend)

**Core Loop:**
- Capture → Plan → Execute → Reflect

**AI Capabilities:**
- Extraction of actions/blockers/emotions from text
- Task complexity detection (atomic vs. composite vs. project)
- Avoidance weight scoring (1-5 scale)
- Breakdown suggestions for complex tasks
- Coaching conversations for emotional blocks

**Data:**
- Supabase (Postgres) with Row Level Security
- User profiles with notification preferences
- Actions, conversations, themes, extractions

**Time Model:**
- Relative scheduling (Today vs. Later)
- Morning/Evening check-ins
- No hard calendar integration

### 3.2 NOT (Out of Scope)

- **Native Mobile Apps:** No iOS/Android builds
- **External Calendar Sync:** No Google/Outlook integration
- **Gamification:** No streaks, badges, or points
- **Collaboration:** Single-player mode only
- **Rich Media:** Text-only tasks (no file attachments)
- **Auto Theme Clustering:** User-defined themes only
- **Visual Canvas:** Deferred to post-MVP
- **Advanced Voice:** Browser-based only (no native streaming)

### 3.3 NEXT (Future Enhancements)

- Visual Canvas with spatial task arrangement
- Goals layer with momentum visualization
- Native in-browser voice streaming
- Long-term pattern analytics
- Auto-clustering of themes
- Graph-based entity relationships
- WhatsApp integration

---

## 4. Technical Context

### 4.1 Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | Next.js 14 + React + Tailwind | PWA support, fast iteration |
| **Backend** | Python 3.11 + FastAPI | AI ecosystem native, async |
| **Database** | Supabase (Postgres 15) | Managed, auth included, RLS |
| **AI Model** | Anthropic Claude API | Superior coaching quality |
| **Voice** | Deepgram Nova-2 | Streaming, confidence scores |
| **Notifications** | Telegram Bot API + Resend | Two-way capable, reliable |
| **Hosting** | Vercel (FE) + Railway (BE) | Zero-config, cron support |

### 4.2 System Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                        INPUT CHANNELS                            │
│     Web App (PWA)  ←→  Telegram Bot  ←→  Voice (Deepgram)       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AGENTIC LAYER (Railway)                    │
│   Orchestrator → Extraction Engine → Intent Classifier          │
│   Circuit breakers, rate limiting, token budgeting              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUBSTRATE LAYER (Supabase)                    │
│   Profiles, Actions, Conversations, Themes, Intent Log         │
│   Row Level Security on all tables                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT CHANNELS                             │
│         Telegram Notifications  ←→  Email (Resend)              │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 How Users Interact

1. **Web PWA:** Primary interface for planning and execution
2. **Telegram Bot:** Quick capture on mobile, receives notifications, can respond
3. **Voice Input:** Speak thoughts, Deepgram transcribes, AI extracts structure
4. **Email:** Receives morning plans, EOD summaries (read-only)

---

## 5. Workflow Details

### 5.1 Workflow: Capture & Extract

**Goal:** Eliminate the "Admin Tax" of entry

**Trigger:** User sends raw message via Web Chat or Telegram (voice/text)

**Steps:**
1. **Ingest:** System receives input (e.g., "Need to email Chen, feeling anxious about it")
2. **Transcribe:** If voice, Deepgram converts to text with confidence scores
3. **Extract (AI):** Claude parses for:
   - Action (what to do)
   - Context (why it matters)
   - Time estimate
   - Avoidance weight (1-5)
   - Complexity (atomic/composite/project)
4. **Display:** Ghost card appears immediately, updates with structured data
5. **Validate:** If confidence < threshold, prompt user confirmation

**Outcome:** Structured action in inbox, zero cognitive load on user

---

### 5.2 Workflow: Plan & Commit

**Goal:** Cure time blindness and overwhelm

**Trigger:** Morning notification or user opens app

**Steps:**
1. **Generate:** Background job surfaces candidates based on:
   - Rolled items from yesterday
   - Approaching deadlines
   - AI-suggested based on patterns
2. **Select:** User views Inbox (candidates) vs Today (committed)
3. **Constrain:** Maximum 12 candidates shown (prevents overwhelm)
4. **Arrange:** User drags tasks to Today, reorders as needed
5. **Commit:** User clicks "Start Day" → Inbox vanishes, Focus mode available

**Outcome:** Bounded, committed day plan user believes in

---

### 5.3 Workflow: Focus & Execute

**Goal:** Overcome initiation paralysis

**Trigger:** User enters Focus Mode on a task

**Steps:**
1. **Isolate:** UI dims everything except active task (navbar hidden)
2. **Breakdown Check:** If task is composite/project:
   - AI prompts: "What's the smallest possible first step?"
   - Shows 2-3 suggestions based on task type
   - User picks or writes their own (must be ≤5 minutes)
3. **Execute:** User works on task with timer visible (subtle, not stressful)
4. **Handle Blocks:** If user clicks "Stuck":
   - AI asks: "What's getting in the way?"
   - Quick options: Don't know where to start / Too big / Missing something / Not feeling it
   - Opens coaching conversation if needed
5. **Complete:** User marks done → celebration acknowledgment (not confetti)
6. **Rest:** Brief break offered before next task

**Outcome:** Task completed with scaffolding, or productively rescheduled

---

### 5.4 Workflow: Reflect & Close

**Goal:** Replace shame with momentum

**Trigger:** End of day (user-configured time) or manual

**Steps:**
1. **Review:** AI lists what was completed today
2. **Acknowledge:** Special callout for high-avoidance tasks completed:
   - "You did [task] today. That one carried weight. You did it anyway."
3. **Summarize:** AI generates narrative of day's effort (progress framing)
4. **Clean Up:** User decides to Roll or Drop unfinished items
5. **Plan Tomorrow:** Optional quick capture of tomorrow's intentions
6. **Reset:** Today list clears to zero

**Outcome:** Day closed with momentum, not shame. Tomorrow prepped.

---

## 6. Key Data Entities

### 6.1 Action (Task)

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Owner |
| title | String | Task name (imperative, <60 chars) |
| status | Enum | inbox, planned_today, in_progress, done, rolled, dormant |
| avoidance_weight | Integer | 1-5 (AI-inferred emotional resistance) |
| complexity | Enum | atomic, composite, project |
| estimated_minutes | Integer | Time estimate |
| parent_action_id | UUID | If this is a subtask |
| first_step | String | The tiny first step user committed to |
| confidence | Float | AI extraction confidence (0-1) |

### 6.2 Conversation

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | Owner |
| type | Enum | onboarding, stuck, end_of_day, planning, quick_add |
| status | Enum | active, completed, abandoned |
| transcript | Text | Full conversation |
| summary | Text | AI-generated recap |

### 6.3 Profile

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key (matches auth.users) |
| timezone | String | User's timezone |
| notification_channel | Enum | email, telegram |
| telegram_chat_id | String | For Telegram notifications |
| morning_time | Time | When to send morning plan |
| evening_time | Time | When to send EOD summary |

---

## 7. UX/UI Guidelines

### 7.1 The "Calm" Aesthetic

- No red badges or aggressive alerts
- Neutral colors with soft accents
- Progress framing: "4 completed" not "3 remaining"
- Momentum dots (●●○○○) not percentages

### 7.2 Interaction Philosophy

- **Chat:** Always available for "I'm stuck"
- **List:** Main stage, source of truth
- **Focus Mode:** Strictly removes all navigation
- **Immediate Feedback:** Optimistic UI for all actions

### 7.3 Information Density

**Target: 3/10 (Minimal)**
- Generous whitespace
- One primary action per screen
- Information revealed progressively
- Visual breathing room

---

## 8. Success Criteria (Definition of Done for MVP)

| Criteria | Measurement |
|----------|-------------|
| User can capture via chat | Text input → action created |
| User can capture via Telegram | Message → action in inbox |
| User can plan day | Drag to Today, commit plan |
| User can execute with breakdown | Focus mode with first-step prompt |
| User can get unstuck | Coaching conversation helps |
| User receives morning notification | Telegram/email with plan |
| User receives EOD summary | Telegram/email with wins |
| All data isolated per user | RLS policies enforced |
| System handles AI failures | Circuit breakers, graceful degradation |

---

*End of Master Project Specification*
