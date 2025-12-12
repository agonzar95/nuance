# Start Here

Entry point for implementing Nuance. Read this first at the start of every session.

---

## Project Overview

**Nuance** is an Executive Function Prosthetic for neurodivergent users (ADHD, Anxiety, Burnout). It eliminates the "Admin Tax" of traditional productivity tools by providing:

- **Automated Structure:** Voice/chat input → structured actions (no manual filing)
- **Shame-Free Visibility:** Progress framing, not overdue lists
- **Bridge to Action:** AI breaks down tasks into micro-steps
- **Proactive System:** Reaches out via Telegram/Email at the right moments

**Tech Stack:** Next.js (frontend) + FastAPI (backend) + Supabase (data) + Claude (AI)

---

## Document Map

| Document | Purpose | When to Read |
|----------|---------|--------------|
| `docs/implementation-record.md` | **Live state** - what's done, what's next | Every session start |
| `planning/03_Feature_Specs/03X_*.md` | Detailed specs (see lookup below) | When implementing a feature |
| `planning/05_Implementation_Plan.md` | Phase structure, dependencies, validation | When planning work or checking phase gates |
| `implementation-bridge.md` | Session mechanics, context assembly | When unsure about process |
| `ai-coding-framework-guide.md` | Full methodology and principles | Reference when needed |

### Feature Spec Lookup

Feature specs are grouped by category. Use this table to find the right file:

| Feature Prefix | Spec File |
|----------------|-----------|
| INF-XXX | `planning/03_Feature_Specs/03a_Infrastructure_Specs.md` |
| INT-XXX | `planning/03_Feature_Specs/03b_Integration_Specs.md` |
| SUB-XXX | `planning/03_Feature_Specs/03c_Substrate_Specs.md` |
| AGT-XXX | `planning/03_Feature_Specs/03d_Agentic_Specs.md` |
| FE-XXX | `planning/03_Feature_Specs/03e_Frontend_Core_Specs.md` |
| CAP-XXX | `planning/03_Feature_Specs/03f_Capture_Specs.md` |
| PLN-XXX | `planning/03_Feature_Specs/03g_Planning_Specs.md` |
| EXE-XXX | `planning/03_Feature_Specs/03h_Execution_Specs.md` |
| REF-XXX | `planning/03_Feature_Specs/03i_Reflection_Specs.md` |
| NTF-XXX | `planning/03_Feature_Specs/03j_Notification_Specs.md` |

**Default reading order:** `implementation-record.md` → feature spec (use lookup) → start coding

---

## Session Lifecycle

### Starting a Session

1. **Read** `docs/implementation-record.md`
   - What phase are we in?
   - What's in progress?
   - What patterns have been established?

2. **Pick** next feature from "Current Phase" table
   - Respect dependencies (check Implementation Plan if unsure)
   - Features in same parallel group can be done simultaneously

3. **Read** feature spec (use Feature Spec Lookup table above)
   - Find spec file by feature prefix (e.g., INF-001 → `03a_Infrastructure_Specs.md`)
   - Search for feature ID heading within the file
   - Note user story, technical contracts, validation criteria

4. **Load** dependency code (if any)
   - Check Implementation Record for file paths
   - Understand interfaces you'll consume

5. **Update** Implementation Record
   - Move feature to "In Progress" section

### During Implementation

Follow the implementation loop:

```
Write Code → Execute & Sense → Test → Correlate → Check Convergence
     ↑                                                    |
     └──────────────── (if not converged) ────────────────┘
```

- **Write:** Follow technical contracts from spec
- **Sense:** Gather visual/auditory/tactile feedback
- **Test:** Run validation criteria
- **Correlate:** Cross-reference sensors + test results
- **Converge:** All tests pass + all sensors clean = done

Update "In Progress" section as you make progress.

### Ending a Session

**Critical Rule:** Do NOT start a new feature until completed features are committed. Follow "Complete One, Commit One, Continue."

**If feature is complete:**
1. Verify all tests pass
2. Verify all sensors are clean (no console errors, UI renders correctly)
3. Create atomic commit: `[FEATURE-ID] Brief description`
4. Update Implementation Record:
   - Move feature from "In Progress" to completed in phase table
   - Fill in: artifacts, deviations, integration points, notes
   - Update counts

**If feature is in progress:**
1. Commit work-in-progress (or stash)
2. Update Implementation Record "In Progress" section:
   - What's done
   - What's remaining
   - Any blockers
3. Note what next session should start with

### End of Session Checklist

Before closing, verify:

- [ ] Git initialized (`git init` if needed)
- [ ] All completed features committed: `git commit -m "[ID] description"`
- [ ] Implementation Record status matches reality
- [ ] "In Progress" section reflects actual partial work (or empty if none)
- [ ] Patterns & Conventions updated if new patterns established
- [ ] Next session guidance noted at bottom of record
- [ ] No uncommitted completed features
- [ ] No half-started features without record update

---

## Phase Transitions

When all features in a phase are complete:

### 1. Verify Phase Gate
Check all items in the phase's "Phase Gate" checklist (in Implementation Plan).

### 2. Archive Phase Details
Create `docs/implementation-archive/phase-XX-[name].md` with:
- Full details for each completed feature
- Patterns established
- Integration points provided to later phases

### 3. Update Main Record
- Move full details to archive file
- Keep summary table in main record's "Completed Phases" section
- Update "Current Phase" to next phase
- Reset phase feature table

### 4. Commit Archive
```
[PHASE-XX] Archive Phase X - [Name] complete
```

---

## Current State

**Check:** `docs/implementation-record.md`

Quick reference:
- **Phase 1:** Foundation (12 features) - Next.js, FastAPI, UI components
- **Phase 2:** Core Services (12 features) - Deployments, integrations
- **Phase 3:** Data Layer (11 features) - Database, auth, subscriptions
- **Phase 4:** AI Layer (16 features) - Orchestration, extractors
- **Phase 5:** Notifications (7 features) - Email, Telegram, routing
- **Phase 6:** Frontend (10 features) - API client, PWA
- **Phase 7:** Workflows (26 features) - Capture, Plan, Execute, Reflect
- **Phase 8:** Polish (13 features) - Page orchestrators, jobs, onboarding

**Total:** 107 features across 8 phases

---

## Key Principles

| # | Principle | Mantra |
|---|-----------|--------|
| 1 | AI Engineering Is Accelerated Learning | Always Be Learning |
| 2 | You Are the Architect, Agent Is Implementer | Delegate the Doing, Not the Thinking |
| 3 | Slow Down to Go Fast | Compound Progress, Accelerate Velocity |
| 4 | Specification >> Prompt Engineering | Write the Blueprint, Not the Prompt |
| 5 | Define Done Before Implementing | Specify Success, Then Build |
| 6 | Feature Atomicity | Reduce Until Irreducible |
| 7 | Dependency-Driven Development | Schedule Implementation by Dependencies |
| 8 | One Atomic Feature at a Time | Complete One, Commit One, Continue |
| 9 | Context Engineering | Curate Context, Don't Accumulate It |
| 10 | Make It Work, Make It Right, Make It Fast | Build, Learn, Improve |

---

## Quick Commands

```bash
# Frontend (Next.js)
cd frontend && npm run dev      # Start dev server (port 3000)
cd frontend && npm test         # Run tests
cd frontend && tsc --noEmit     # Type check

# Backend (FastAPI)
cd backend && uvicorn main:app --reload  # Start dev server (port 8000)
cd backend && pytest                      # Run tests
cd backend && mypy .                      # Type check
```

---

*Last updated: December 12, 2025*
