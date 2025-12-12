# Feature Dependency Matrix

**Step 4 of Planning Phase**
**Date:** December 11, 2025 (Updated)
**Total Features:** 107

---

## Overview

This matrix documents the dependencies between all 107 features identified in Step 3 (Feature Specifications). Each feature's dependencies are extracted from Section E of its specification.

**Binary Test Applied:** "Does Feature A require Feature B's specific output, configuration, or functionality to work?"

---

## 1. Dependency Summary by Category

### Foundation Features (No Dependencies)
These features can be built first:

| ID | Feature | Category |
|----|---------|----------|
| INF-001 | Next.js Setup | Infrastructure |
| INF-002 | FastAPI Setup | Infrastructure |
| FE-007 | Avoidance Indicator | Frontend Core |
| FE-008 | Timer Component | Frontend Core |
| FE-009 | Loading States | Frontend Core |
| FE-010 | Empty States | Frontend Core |
| FE-011 | Offline Awareness | Frontend Core |
| CAP-002 | Chat Text Input | Capture |
| CAP-006 | Correction Flow | Capture |
| EXE-003 | Subtask Checklist | Execution |
| EXE-011 | Avoidance Acknowledgment | Execution |
| PLN-006 | Time Budget Display | Planning |

---

## 2. Complete Dependency Matrix

### INF - Infrastructure (11 features)

| Feature ID | Feature Name | Dependencies | Depends On Count |
|------------|--------------|--------------|------------------|
| INF-001 | Next.js Setup | None | 0 |
| INF-002 | FastAPI Setup | None | 0 |
| INF-003 | Vercel Config | INF-001 | 1 |
| INF-004 | Railway Config | INF-002 | 1 |
| INF-005 | Environment Config | INF-001, INF-002 | 2 |
| INF-006 | Structured Logging | INF-002 | 1 |
| INF-007 | Intent Log Recording | SUB-001, INF-002 | 2 |
| INF-008 | Error Middleware | INF-002, INF-006 | 2 |
| INF-009 | Health Endpoint | INF-002 | 1 |
| INF-010 | Onboarding Flow | SUB-003, SUB-005 | 2 |
| INF-011 | CORS Configuration | INF-002 | 1 |

### INT - Integration (6 features)

| Feature ID | Feature Name | Dependencies | Depends On Count |
|------------|--------------|--------------|------------------|
| INT-001 | Supabase Client | INF-005 | 1 |
| INT-002 | Claude API Client | INF-005 | 1 |
| INT-003 | Deepgram Client | INF-005 | 1 |
| INT-004 | Telegram API Client | INF-005 | 1 |
| INT-005 | Resend Client | INF-005 | 1 |
| INT-006 | Voice Transcription | INT-003 | 1 |

### SUB - Substrate (13 features)

| Feature ID | Feature Name | Dependencies | Depends On Count |
|------------|--------------|--------------|------------------|
| SUB-001 | Database Schema | INT-001 | 1 |
| SUB-002 | RLS Policies | SUB-001 | 1 |
| SUB-003 | Email/Password Auth | SUB-001, INT-001 | 2 |
| SUB-004 | Google OAuth | SUB-001, SUB-003 | 2 |
| SUB-005 | Profile Management | SUB-001, SUB-002, SUB-003 | 3 |
| SUB-006 | Session Handling | SUB-003 | 1 |
| SUB-007 | Notification Preferences | SUB-005 | 1 |
| SUB-008 | Timezone Handling | SUB-005 | 1 |
| SUB-009 | Job: State Transitions | SUB-001, SUB-008 | 2 |
| SUB-010 | Job: Morning Plan | SUB-001, SUB-007, SUB-008, NTF-001 | 4 |
| SUB-011 | Job: EOD Summary | SUB-001, SUB-007, SUB-008, NTF-001 | 4 |
| SUB-012 | Job: Inactivity Check | SUB-001, SUB-007, NTF-001 | 3 |
| SUB-013 | Real-time Subscriptions | SUB-001, INT-001 | 2 |

### AGT - Agentic (16 features)

| Feature ID | Feature Name | Dependencies | Depends On Count |
|------------|--------------|--------------|------------------|
| AGT-001 | Orchestrator Setup | INF-002, INF-008, INT-001 | 3 |
| AGT-002 | Request Router | AGT-001, AGT-007, AGT-013, AGT-016, AGT-014 | 5 |
| AGT-003 | Circuit Breakers | INF-002 | 1 |
| AGT-004 | Rate Limiting | AGT-001 | 1 |
| AGT-005 | Token Budgeting | SUB-001, INT-002 | 2 |
| AGT-006 | SSE Streaming | INT-002, AGT-001 | 2 |
| AGT-007 | Model Abstraction | INT-002 | 1 |
| AGT-008 | Extract: Actions | AGT-007, AGT-015 | 2 |
| AGT-009 | Extract: Avoidance Weight | AGT-007, AGT-015 | 2 |
| AGT-010 | Extract: Complexity | AGT-007 | 1 |
| AGT-011 | Extract: Confidence | AGT-008 | 1 |
| AGT-012 | Extract: Breakdown | AGT-007, AGT-015 | 2 |
| AGT-013 | Intent Classifier | AGT-007 | 1 |
| AGT-014 | Coaching Handler | AGT-007, AGT-006 | 2 |
| AGT-015 | Prompt Versioning | SUB-001 | 1 |
| AGT-016 | Extraction Orchestrator | AGT-008, AGT-009, AGT-010, AGT-011 | 4 |

### FE - Frontend Core (15 features)

| Feature ID | Feature Name | Dependencies | Depends On Count |
|------------|--------------|--------------|------------------|
| FE-001 | API Client | INT-001, INF-001 | 2 |
| FE-002 | Optimistic Updates | FE-001 | 1 |
| FE-003 | SSE Handler | AGT-006, FE-001 | 2 |
| FE-004 | Real-time Handler | INT-001, SUB-013 | 2 |
| FE-005 | Action List Component | FE-006, FE-010 | 2 |
| FE-006 | Action Card Component | FE-007 | 1 |
| FE-007 | Avoidance Indicator | None | 0 |
| FE-008 | Timer Component | None | 0 |
| FE-009 | Loading States | None | 0 |
| FE-010 | Empty States | None | 0 |
| FE-011 | Offline Awareness | None | 0 |
| FE-012 | PWA Manifest | INF-001 | 1 |
| FE-013 | Service Worker | FE-012, FE-011 | 2 |
| FE-014 | Responsive Layout | FE-015, INF-001 | 2 |
| FE-015 | Navigation Component | INF-001 | 1 |

### CAP - Capture (9 features)

| Feature ID | Feature Name | Dependencies | Depends On Count |
|------------|--------------|--------------|------------------|
| CAP-001 | Chat Message List | FE-003 | 1 |
| CAP-002 | Chat Text Input | None | 0 |
| CAP-003 | Chat Voice Input | INT-003, INT-006 | 2 |
| CAP-004 | Ghost Card | FE-006, AGT-016 | 2 |
| CAP-005 | Confidence Validation | AGT-016, CAP-006 | 2 |
| CAP-006 | Correction Flow | None | 0 |
| CAP-007 | Voice Error Handling | CAP-003 | 1 |
| CAP-008 | Quick Capture Overlay | EXE-001 | 1 |
| CAP-009 | Capture Page Container | CAP-001..008, FE-001, AGT-016 | 11 |

### PLN - Planning (9 features)

| Feature ID | Feature Name | Dependencies | Depends On Count |
|------------|--------------|--------------|------------------|
| PLN-001 | Inbox View | FE-006, FE-007, FE-010 | 3 |
| PLN-002 | Today View | FE-010 | 1 |
| PLN-003 | Drag to Plan | PLN-001, PLN-002 | 2 |
| PLN-004 | Reorder Tasks | PLN-002, FE-002 | 2 |
| PLN-005 | Day Commit | PLN-002, EXE-001 | 2 |
| PLN-006 | Time Budget Display | None | 0 |
| PLN-007 | Add More Tasks | CAP-002, FE-005 | 2 |
| PLN-008 | Remove from Today | PLN-002, FE-002 | 2 |
| PLN-009 | Planning Page Container | PLN-001..008, FE-001 | 10 |

### EXE - Execution (13 features)

| Feature ID | Feature Name | Dependencies | Depends On Count |
|------------|--------------|--------------|------------------|
| EXE-001 | Focus Mode Container | EXE-002, EXE-004 | 2 |
| EXE-002 | Focus Task Card | FE-007, EXE-003 | 2 |
| EXE-003 | Subtask Checklist | None | 0 |
| EXE-004 | Focus Timer | FE-008 | 1 |
| EXE-005 | Breakdown Prompt | EXE-003 | 1 |
| EXE-006 | First Step Suggestions | AGT-012 | 1 |
| EXE-007 | Stuck Button | EXE-008 | 1 |
| EXE-008 | Stuck Options | EXE-005, EXE-009 | 2 |
| EXE-009 | Coaching Overlay | AGT-014, CAP-001 | 2 |
| EXE-010 | Complete Task Flow | EXE-011, EXE-012 | 2 |
| EXE-011 | Avoidance Acknowledgment | None | 0 |
| EXE-012 | Rest Screen | EXE-001 | 1 |
| EXE-013 | Focus Mode Page | EXE-001..012, FE-001, AGT-014 | 15 |

### REF - Reflection (6 features)

| Feature ID | Feature Name | Dependencies | Depends On Count |
|------------|--------------|--------------|------------------|
| REF-001 | EOD Trigger | SUB-008 | 1 |
| REF-002 | Day Review Screen | REF-003, REF-004, REF-005 | 3 |
| REF-003 | Win Highlights | FE-007 | 1 |
| REF-004 | Day Summary Display | SUB-011 | 1 |
| REF-005 | Roll/Drop Controls | FE-007 | 1 |
| REF-006 | Tomorrow Quick Capture | CAP-002 | 1 |

### NTF - Notification (9 features)

| Feature ID | Feature Name | Dependencies | Depends On Count |
|------------|--------------|--------------|------------------|
| NTF-001 | Gateway Abstraction | NTF-002, NTF-004, SUB-007, NTF-009 | 4 |
| NTF-002 | Email Client (Resend) | INT-005 | 1 |
| NTF-003 | Telegram Bot Setup | INT-004, INF-005 | 2 |
| NTF-004 | Telegram Send | NTF-003, INT-004 | 2 |
| NTF-005 | Telegram Receive | NTF-003, INT-004, AGT-016, INT-006 | 4 |
| NTF-006 | Telegram Commands | NTF-004, NTF-005 | 2 |
| NTF-007 | Morning Plan Content | SUB-010 | 1 |
| NTF-008 | EOD Summary Content | SUB-011 | 1 |
| NTF-009 | Channel Router | SUB-007 | 1 |

---

## 3. Dependency Statistics

### Most Depended Upon (Foundation Features)

These features are critical path - many others depend on them:

| Rank | Feature ID | Feature Name | Depended Upon By |
|------|------------|--------------|------------------|
| 1 | INF-002 | FastAPI Setup | 10 features |
| 2 | SUB-001 | Database Schema | 12 features |
| 3 | INF-001 | Next.js Setup | 7 features |
| 4 | AGT-007 | Model Abstraction | 8 features |
| 5 | INT-001 | Supabase Client | 6 features |
| 6 | INF-005 | Environment Config | 6 features |
| 7 | FE-007 | Avoidance Indicator | 5 features |
| 8 | AGT-001 | Orchestrator Setup | 4 features |
| 9 | SUB-003 | Email/Password Auth | 4 features |
| 10 | PLN-002 | Today View | 4 features |

### Most Dependencies (Complex Features)

These features require the most prerequisites:

| Rank | Feature ID | Feature Name | Dependency Count |
|------|------------|--------------|------------------|
| 1 | EXE-013 | Focus Mode Page | 15 |
| 2 | CAP-009 | Capture Page Container | 11 |
| 3 | PLN-009 | Planning Page Container | 10 |
| 4 | AGT-002 | Request Router | 5 |
| 5 | SUB-010 | Job: Morning Plan | 4 |
| 5 | SUB-011 | Job: EOD Summary | 4 |
| 5 | AGT-016 | Extraction Orchestrator | 4 |
| 5 | NTF-001 | Gateway Abstraction | 4 |
| 5 | NTF-005 | Telegram Receive | 4 |
| 10 | SUB-005 | Profile Management | 3 |

---

## 4. Circular Dependencies - Resolved

The following circular dependencies were identified during analysis. Per the framework's binary test, **weak links have been removed from the dependency matrix above**. Only strong (true prerequisite) dependencies remain.

### 4.1 PLN-002 ↔ PLN-004 (Today View ↔ Reorder Tasks)

**Analysis:**
- PLN-002 (Today View) originally listed PLN-004 (Reorder) as dependency
- PLN-004 (Reorder) needs PLN-002 (Today View)

**Resolution:** PLN-002 can display today's tasks WITHOUT reordering.
- PLN-002 → PLN-004: **REMOVED** (nice-to-have integration, not prerequisite)
- PLN-004 → PLN-002: **KEPT** (reorder must operate on Today View)

### 4.2 PLN-002 ↔ PLN-005 (Today View ↔ Day Commit)

**Analysis:**
- PLN-002 shows "Start Day" button which triggers PLN-005
- PLN-005 navigates to focus mode after committing

**Resolution:** PLN-002 can exist with a disabled/placeholder button.
- PLN-002 → PLN-005: **REMOVED** (button can be added later)
- PLN-005 → PLN-002: **KEPT** (commit requires selected actions from view)

### 4.3 EXE-005 ↔ EXE-006 (Breakdown Prompt ↔ First Step Suggestions)

**Analysis:**
- EXE-005 shows breakdown prompt with manual input OR AI suggestions
- EXE-006 provides AI suggestions as alternative to manual input

**Resolution:** These are alternatives, not true dependencies.
- EXE-005 → EXE-006: **REMOVED** (can work with just manual input)
- EXE-006 → EXE-005: **REMOVED** (suggestions can stand alone)

Both features now have no mutual dependency and can be built independently.

### 4.4 EXE-010 ↔ EXE-011 ↔ EXE-012 (Complete Flow ↔ Acknowledgment ↔ Rest)

**Analysis:**
- EXE-010 (Complete Task) shows acknowledgment for high-avoidance, then rest screen
- EXE-011 (Acknowledgment) is shown BY EXE-010 (child component)
- EXE-012 (Rest Screen) is shown AFTER EXE-010 (child component)

**Resolution:** EXE-010 is the parent container that USES the others.
- EXE-010 → EXE-011: **KEPT** (needs acknowledgment component)
- EXE-010 → EXE-012: **KEPT** (needs rest screen component)
- EXE-011 → EXE-010: **REMOVED** (acknowledgment is self-contained)
- EXE-012 → EXE-010: **REMOVED** (rest screen is self-contained)

EXE-011 is now a foundation feature (no dependencies).

### 4.5 REF-002 ↔ REF-005 (Day Review ↔ Roll/Drop Controls)

**Analysis:**
- REF-002 (Day Review) contains roll/drop controls for remaining tasks
- REF-005 (Roll/Drop Controls) is a component used within REF-002

**Resolution:** REF-005 is a child component.
- REF-002 → REF-005: **KEPT** (needs controls to function)
- REF-005 → REF-002: **REMOVED** (controls are self-contained)

### 4.6 NTF-001 ↔ NTF-009 (Gateway ↔ Channel Router)

**Analysis:**
- NTF-001 (Gateway) sends notifications through available channels
- NTF-009 (Channel Router) decides which channel based on user preferences
- Gateway needs Router to determine which channel to use
- Router just reads preferences, doesn't need Gateway

**Resolution:** One-way dependency.
- NTF-001 → NTF-009: **KEPT** (Gateway needs Router to pick channel)
- NTF-009 → NTF-001: **REMOVED** (Router is stateless preference lookup)

---

## 5. Dependency Clusters

Features naturally cluster into implementation groups:

### Cluster 1: Core Infrastructure (Build First)
```
INF-001, INF-002 → INF-005 → INT-001..INT-005
                           → INF-003, INF-004, INF-006
```

### Cluster 2: Database & Auth
```
INT-001 → SUB-001 → SUB-002 → SUB-003 → SUB-004, SUB-005, SUB-006
                                                 → SUB-007, SUB-008
```

### Cluster 3: AI/Agentic
```
INT-002 → AGT-007 → AGT-008, AGT-009, AGT-010, AGT-012, AGT-013, AGT-014
AGT-008..011 → AGT-016 (Extraction Orchestrator)
INF-002 + INF-008 + INT-001 → AGT-001 → AGT-002, AGT-004, AGT-006
SUB-001 → AGT-015 → AGT-008, AGT-009, AGT-012
```

### Cluster 4: Frontend Foundation
```
INF-001 → FE-015 → FE-014
INT-001 → FE-001 → FE-002, FE-003
FE-007 → FE-006 → FE-005
```

### Cluster 5: Notification Layer
```
INT-005 → NTF-002
INT-004 → NTF-003 → NTF-004 → NTF-006
NTF-003 + INT-004 + AGT-016 + INT-006 → NTF-005
SUB-007 → NTF-009
NTF-002 + NTF-004 + SUB-007 + NTF-009 → NTF-001
```

### Cluster 6: User Flows (Build Last)
```
Capture: FE-003 → CAP-001, AGT-016 + FE-006 → CAP-004, CAP-005 → CAP-009 (Page)
Planning: FE-006 + FE-007 + FE-010 → PLN-001, PLN-002 → PLN-009 (Page)
Execution: FE-008 → EXE-004, EXE-003 → EXE-002 → EXE-001 → EXE-013 (Page)
Reflection: FE-007 → REF-003, REF-005 → REF-002; SUB-008 → REF-001
```

---

## 6. Cross-Category Dependencies

| From Category | To Category | Count | Examples |
|---------------|-------------|-------|----------|
| SUB → INT | 2 | SUB-001→INT-001, SUB-003→INT-001 |
| SUB → NTF | 3 | SUB-010→NTF-001, SUB-011→NTF-001, SUB-012→NTF-001 |
| AGT → INT | 2 | AGT-001→INT-001, AGT-007→INT-002 |
| AGT → INF | 3 | AGT-001→INF-002, AGT-003→INF-002, etc. |
| AGT → SUB | 2 | AGT-005→SUB-001, AGT-015→SUB-001 |
| AGT → AGT | 2 | AGT-002→AGT-001, AGT-002→AGT-007 |
| FE → INT | 2 | FE-001→INT-001, FE-004→INT-001 |
| FE → AGT | 1 | FE-003→AGT-006 |
| FE → SUB | 1 | FE-004→SUB-013 |
| CAP → INT | 2 | CAP-003→INT-003, CAP-003→INT-006 |
| CAP → AGT | 3 | CAP-004→AGT-016, CAP-005→AGT-016, CAP-009→AGT-016 |
| CAP → FE | 3 | CAP-001→FE-003, CAP-004→FE-006, CAP-009→FE-001 |
| CAP → EXE | 1 | CAP-008→EXE-001 |
| PLN → FE | 5 | PLN-001→FE-006, PLN-001→FE-007, PLN-009→FE-001, etc. |
| PLN → CAP | 1 | PLN-007→CAP-002 |
| PLN → EXE | 1 | PLN-005→EXE-001 |
| EXE → FE | 3 | EXE-002→FE-007, EXE-004→FE-008, EXE-013→FE-001 |
| EXE → AGT | 3 | EXE-006→AGT-012, EXE-009→AGT-014, EXE-013→AGT-014 |
| EXE → CAP | 1 | EXE-009→CAP-001 |
| REF → FE | 2 | REF-003→FE-007, REF-005→FE-007 |
| REF → SUB | 2 | REF-001→SUB-008, REF-004→SUB-011 |
| REF → CAP | 1 | REF-006→CAP-002 |
| NTF → INT | 5 | NTF-002→INT-005, NTF-003→INT-004, NTF-005→INT-006, etc. |
| NTF → SUB | 3 | NTF-001→SUB-007, NTF-007→SUB-010, NTF-008→SUB-011 |
| NTF → AGT | 1 | NTF-005→AGT-016 |
| NTF → INF | 1 | NTF-003→INF-005 |
| INF → SUB | 2 | INF-007→SUB-001, INF-010→SUB-003 |

---

*Companion document: 04_Dependency_Graph.md with Mermaid visualization*
