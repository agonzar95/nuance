# Implementation Bridge: From Plan to Working Software

A companion to the AI Coding Framework Guide, addressing the practical mechanics of transitioning from completed planning artifacts to iterative feature implementation.

---

## The Three Gaps This Document Fills

1. **State Tracking** - How does a new session know what's been implemented?
2. **Context Construction** - How do you actually build a context package?
3. **Session Continuity** - How do you hand off between sessions without losing progress?

---

# Section 1: The Implementation Record

The Implementation Record is a living document that tracks the actual state of your implementation. It's the "twin" of your planning artifacts - where specs describe *intent*, the record describes *reality*.

## Two-Tier Architecture

To prevent context window bloat as features accumulate, the record uses a two-tier system:

| Location | Purpose | Size |
|----------|---------|------|
| `implementation-record.md` | Active work + summaries | Always small |
| `implementation-archive/` folder | Per-phase historical details | Read only specific phases when needed |

**The main record stays bounded to: `O(current phase features)`** instead of `O(all features)`.

## File Structure

```
/docs/
  implementation-record.md              # Active - read every session
  implementation-archive/
    phase-01-foundation.md              # Full details for Phase 1
    phase-02-core-features.md           # Full details for Phase 2
    phase-03-api-layer.md               # Full details for Phase 3
    ...
```

This mirrors the planning folder structure (e.g., `03_Feature_Specs/`) and allows reading just the specific phase needed.

## Main Record Structure

```markdown
# Implementation Record

## Project Status
- **Current Phase:** [Phase number from Implementation Plan]
- **Total Features:** [X completed of Y total]
- **Last Updated:** [Date]
- **Last Commit:** [hash + message]

---

## In Progress

### [FEATURE-ID]: [Feature Name]
**Status:** IN PROGRESS
**Started:** [Date]
**Current State:** [Brief description of where implementation stands]

**Completed So Far:**
- [What's done]

**Remaining:**
- [What's left]

**Blockers:**
- [Any issues encountered]

---

## Current Phase: Phase [N] - [Phase Name]

### [FEATURE-ID]: [Feature Name]
**Status:** COMPLETE
**Completed:** [Date]
**Commit:** [hash]

**Implemented Artifacts:**
- `/path/to/file.ts` - [Brief description]
- `/tests/path/to/test.ts` - [Test coverage]

**Deviations from Spec:**
- [Differences with reasoning, or "None"]

**Integration Points:**
- Exports `functionName()` used by [OTHER-FEATURE-ID]
- Depends on `otherFunction()` from [DEPENDENCY-ID]

**Implementation Notes:**
- [Gotchas, patterns established, decisions]

---

## Completed Phases (Summary)

### Phase 1: [Phase Name] ✓
**Completed:** [Date] | **Features:** 5 | **Archive:** `implementation-archive/phase-01-[name].md`

| Feature ID | Name | Key Exports |
|------------|------|-------------|
| CORE-001 | User Auth | `authenticateUser()`, `validateToken()` |
| CORE-002 | Session Mgmt | `createSession()`, `destroySession()` |

**Integration Note:** [One-liner about what this phase provides to later phases]

---
```

## Archive File Structure (Per-Phase)

Each phase gets its own file in `implementation-archive/`:

```markdown
# Phase 1: Foundation - Implementation Archive

**Phase Status:** COMPLETE
**Completed:** [Date]
**Validation:** [How phase completion was verified]

---

## CORE-001: User Authentication
**Completed:** [Date]
**Commit:** [hash]

**Implemented Artifacts:**
- `/src/auth/login.ts` - Login handler with rate limiting
- `/src/auth/types.ts` - Auth interfaces and token types
- `/tests/auth/login.test.ts` - 15 test cases covering happy path and errors

**Deviations from Spec:**
- Used JWT instead of session tokens (reason: stateless scaling)

**Integration Points:**
- Exports `authenticateUser()` used by API-101, API-102
- Exports `validateToken()` used by middleware

**Implementation Notes:**
- Established pattern: all auth functions return Result<T, AuthError>
- Token expiry set to 1 hour, refresh tokens to 7 days

---

## CORE-002: Session Management
**Completed:** [Date]
**Commit:** [hash]

[Full details...]

---

## Phase Summary

**Total Features:** 5
**Key Patterns Established:**
- Result<T, Error> return type convention
- Test file naming: `[feature].test.ts`

**Provided to Later Phases:**
- Auth middleware for API layer
- Session management for stateful features
```

## Phase Archival Process

When a phase completes:

1. **Create phase archive file** in `implementation-archive/` folder
2. **Move full details** from main record to that phase file
3. **Keep summary** in main record's "Completed Phases" section
4. **Update project status** counts

```
Phase 1 in progress → Full details in main record
Phase 1 completes   → Create phase-01-foundation.md, move details there
                    → Keep summary in main record
Phase 2 starts      → Full details for Phase 2 in main record
```

## Smart Reading Protocol

| Situation | What to Read |
|-----------|--------------|
| Starting new session | Main record only |
| Working on feature depending on Phase 1 | Main record + `phase-01-*.md` |
| Debugging integration across phases | Main record + relevant phase files |

**Default: Read main record. Read specific phase archives only when needed.**

## When to Update

| Event | Action |
|-------|--------|
| Feature starts | Add to "In Progress" |
| Feature completes | Add full details to "Current Phase" section |
| Phase completes | Archive phase details, add summary to main |
| Session ends mid-feature | Update "In Progress" with current state |

## The Critical Rule

**Update the Implementation Record BEFORE ending a session.** This is the handoff mechanism. A session that doesn't update the record leaves the next session blind.

---

# Section 2: Context Assembly Checklist

The framework describes *what* goes in a context package. This section describes *how* to build one.

## The Universal Checklist

Before starting any feature implementation, assemble context using this checklist:

```markdown
## Context Assembly Checklist for [FEATURE-ID]

### 1. Feature Specification
- [ ] Located feature spec document
- [ ] Read and understood user story
- [ ] Read and understood technical contracts (all 3 levels)
- [ ] Read and understood validation contracts (all 3 levels)
- [ ] Noted acceptance criteria

### 2. Dependencies
- [ ] Listed all @referenced dependencies from spec
- [ ] For each dependency:
  - [ ] Located dependency spec
  - [ ] Located implemented code (from Implementation Record)
  - [ ] Understand the interfaces this feature will use

### 3. Implementation Context
- [ ] Read relevant section of Implementation Plan
- [ ] Identified current phase
- [ ] Understood phase completion criteria
- [ ] Reviewed Implementation Record for:
  - [ ] Patterns established by prior features
  - [ ] Relevant implementation notes
  - [ ] Integration points to connect with

### 4. Sensor Requirements
- [ ] Identified which sensors needed from acceptance criteria:
  - [ ] Visual (if spec mentions: renders, displays, shows, UI)
  - [ ] Auditory (if spec mentions: logs, errors, reports, outputs)
  - [ ] Tactile (if spec mentions: clicks, submits, completes, interacts)
- [ ] Have access to required sensor tools

### 5. Project Foundation (First Feature Only)
- [ ] Project scaffold exists (folders, config)
- [ ] Dependencies installed
- [ ] Build/run commands work
- [ ] Test framework configured
```

## First Feature: The Bootstrap Case

When implementing the first feature (or first in a new phase with no prior code):

**Additional Considerations:**
1. **Scaffold first** - Create project structure before feature code
2. **Establish patterns** - First feature sets conventions others follow
3. **Document patterns** - Note in Implementation Record what patterns were established
4. **Minimal viable foundation** - Only create what this feature needs, not speculative infrastructure

**First Feature Context Package:**
- Feature spec (no dependency code yet)
- Implementation Plan (for phase context)
- Technology decisions from Master Project Specification
- Empty Implementation Record (you'll populate it after)

## Dependent Features: The Common Case

When implementing a feature that depends on completed features:

**Additional Considerations:**
1. **Read dependency code** - Don't just read specs, read actual implementation
2. **Verify dependencies work** - Run their tests before starting
3. **Understand actual interfaces** - Implementation may differ slightly from spec

**Dependent Feature Context Package:**
- Feature spec
- Dependency specs
- Dependency implementation code (actual files)
- Implementation Record (for integration points and patterns)
- Implementation Plan section

---

# Section 3: Session Handoff Protocol

How to start a new session without losing continuity.

## Starting a New Session

Every new implementation session should begin with this reading sequence:

### Minimum Required Reading

1. **Implementation Record** - Understand current state
   - What features are complete?
   - What's in progress?
   - What phase are we in?
   - Any notes from previous session?

2. **Current Feature Spec** - If resuming mid-feature
   - Full spec for the feature in progress
   - Or next feature if starting fresh

3. **Implementation Plan** - For context
   - Current phase details
   - What comes next

### The 5-Minute Orientation

Before writing any code, answer these questions:

1. What phase of implementation are we in?
2. What feature are we working on?
3. What's already been implemented that this feature depends on?
4. What patterns have been established that we should follow?
5. What's the acceptance criteria we're building toward?

If you can't answer these questions, read more before coding.

## Ending a Session

Before ending any implementation session:

### If Feature is Complete

1. Verify all tests pass
2. Verify all sensors are clean
3. Create atomic commit
4. Update Implementation Record:
   - Move feature to "Completed"
   - Fill in all fields (artifacts, deviations, integration points, notes)
   - Update project status

### If Feature is In Progress

1. Commit work-in-progress (or stash)
2. Update Implementation Record:
   - Update "In Progress" section with current state
   - Note what's done, what's remaining
   - Document any blockers or decisions made
3. Leave breadcrumbs:
   - What was the last thing you were working on?
   - What should the next session start with?

### The Golden Rule

**A session that doesn't update the Implementation Record is a session that didn't happen.** The next session will have to rediscover everything.

---

# Quick Reference

## New Session Startup
```
1. Read Implementation Record
2. Read current/next Feature Spec
3. Run Context Assembly Checklist
4. Begin Implementation Loop
```

## End Session Shutdown
```
1. Run tests
2. Commit (complete or WIP)
3. Update Implementation Record
4. Note next steps
```

## Implementation Record Update Triggers
- Feature started → Add to In Progress
- Feature completed → Move to Completed, full details
- Phase completed → Archive to phase file, keep summary
- Session ending → Update current state
- Decision made → Add to Implementation Notes

---

*Companion to: The AI Coding Framework Guide*
