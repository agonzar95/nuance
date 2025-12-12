# The AI Coding Framework: A Cure for the Vibe Coding Hangover

A complete guide to building maintainable, understandable software with AI coding agents.

---

## The Problem: Vibe Coding

**Vibe coding** is the low-spec, zero-planning approach to AI-accelerated development that *feels* productive but results in brittle, unmaintainable demo-ware.

The pattern is familiar:
1. Inspiration strikes—you've got an idea
2. You fire up your AI coding agent and jam in prompts
3. The app works! You feel like a 10x engineer
4. Monday rolls around. You want to add a feature or change something
5. You realize you don't understand it, can't maintain it, and have to throw most or all of it away

**The hangover** is the resulting despair when you try to build maintainable, understandable software this way.

---

## Who This Framework Is For

This framework is for you if:

- You value programming as a daily learning experience
- You want to understand and own the software you write using AI coding agents
- You want to be the boss of the coding agents, not their confused intern
- Working with agents makes you feel like a prompt jockey rather than an AI engineer
- You're sick of throwing away code, burning time and tokens
- You want to use coding agents to build production applications that do real work

This framework is **not** for you if:

- Programming is just a job, not a craft you're refining
- You're satisfied having AI "do it for you" without understanding how or why
- Vibe coding gets you what you need and that's good enough

---

## Framework Overview

The framework comprises three pillars:

| Pillar | Description |
|--------|-------------|
| **Principles** | The philosophy underpinning everything |
| **Process** | The workflow for getting software built using AI |
| **Tools** | Accelerators and enablers that reflect the principles |

This framework is adaptive to all types of software. Examples of production applications built with this approach include specialized litigation support applications, real-time appliance monitoring packages, and digital publishing systems.

---

# Part 1: Principles

The 10 principles broadly map across three categories:
- General principles (overarching)
- Planning-phase principles
- Implementation-phase principles

## General Principles

### Principle 1: AI Engineering Is Accelerated Learning

**The Problem:** Treating AI coding agents as pure productivity tools just to crank out code faster. Using AI to generate software without learning anything from the process. Six months later, you're no better as an engineer—having plateaued or worse, becoming dependent on AI for debugging, modifications, and architectural decisions.

**The Big Idea:** The framework is not just about building faster—it's about learning as you go. Every step creates specific learning opportunities. You're not just shipping software; you're building yourself. The software is valuable, but the engineer you become is exponentially more valuable.

> **Mantra:** "Always Be Learning"

---

### Principle 2: You Are the Architect, the Agent Is the Implementer

**The Problem:** Treating AI agents as replacements for architectural thinking rather than implementers of your well-specified decisions.

**The Big Idea:** Keep the architect/implementer boundary crystal clear.

**You own the thinking:**
- Architecture and interfaces
- Intent of the system
- Structure and design decisions
- Associated tradeoffs

**The agent handles the doing:**
- Implementation
- Typing code
- Following patterns
- Implementing tests you specify
- Banging out boilerplate

> **Mantra:** "Delegate the Doing, Not the Thinking"

---

### Principle 3: Slow Down and Iterate to Go Fast

**The Problem:** The starting-over cycle. Without deliberate iteration on validated work, you end up repeatedly starting from scratch. Three months in, you've had multiple abandoned attempts instead of consistently improving one single system.

**The Big Idea:** Deliberate iteration enables compounding returns on both understanding and productivity.

- Week 1 feels slow
- Week 2 builds momentum
- Week 3 is dramatically faster

> **Mantra:** "Compound Progress, Accelerate Velocity"

---

## Planning-Phase Principles

### Principle 4: Specification >> Prompt Engineering

**The Problem:** Prompt engineering treats AI interactions as an optimization problem rather than a communication problem—trying to find magic words that produce the right output rather than clearly defining what "right" means.

**The Big Idea:** Specifications are very different than prompts. Specifications are structured, precise definitions of:
- Requirements
- Behavior
- Interfaces
- Acceptance criteria

**Why specifications matter:**
- Writing specifications forces architectural thinking
- You must understand the problem completely
- You must define interfaces precisely
- You must anticipate edge cases
- Specifications provide clear, unambiguous direction
- The agent implements what you specified, not what it interprets from conversational prompts

> **Mantra:** "Write the Blueprint, Not the Prompt"

---

### Principle 5: Define Done Before Implementing

**The Problem:** Starting implementation without executable tests and observable success criteria. Agents lack clear completion criteria and immediate feedback—they can't self-validate, self-correct, or know when they're done consistent with your specifications.

**The Big Idea:** Defining "done" before implementation:
- Keeps you thinking deeply about requirements
- Enables the agent to work autonomously

By defining tests up front, you give agents:
- Clear stop conditions
- Immediate feedback during implementation
- Self-correction capability

**Multi-Sensory Validation:** Enable agents to observe through:
- **Visual senses:** What renders
- **Auditory senses:** Logs and errors
- **Tactile senses:** How they interact with the system

Tests verify correctness of implementation. Sensors reveal actual behavior.

**Done = Tests pass + Sensors validate**

> **Mantra:** "Specify Success, Then Build"

---

### Principle 6: Feature Atomicity

**The Problem:** Writing non-atomic features means leaving decomposition work for implementation time, which forces agents to make architectural decisions on the fly.

**The Big Idea:** Feature atomicity forces you to completely decompose each feature during specification, enabling agents to implement within a manageable scope.

Features become implementation work units: atomic, irreducible tasks ready for an agent to execute completely.

**Keep features as small as possible to make agent implementation as successful as possible.**

> **Mantra:** "Reduce Until Irreducible"

---

### Principle 7: Dependency-Driven Development

**The Problem:** Implementing without explicit dependency analysis means treating all features as independent when they actually form an interconnected graph.

**The Big Idea:** Dependency-driven development forces you to understand how features relate and integrate, ensuring agents never implement features that depend on incomplete work.

> **Mantra:** "Schedule Implementation by Dependencies"

---

## Implementation-Phase Principles

### Principle 8: Implement One Atomic Feature at a Time

**The Problem:** Working on multiple features treats implementation as parallel streams that can be context-switched freely. But implementation quality is contingent on sustained focus, complete context, and tight feedback loops. Jumping between features fragments focus.

**The Big Idea:** One feature at a time:
1. Agent implements one single atomic feature
2. You study and understand it
3. You validate that it works
4. You commit it as a checkpoint
5. You move on to the next feature

This rhythm creates both momentum and deepening understanding.

> **Mantra:** "Complete One, Commit One, Continue"

---

### Principle 9: Context Engineering and Management

**The Problem:** Treating context as something that happens automatically rather than something you actively engineer. Letting conversation history passively accumulate instead of curating what matters. Not building context resilience means state will not persist, and you lose continuity.

**The Big Idea:** 
- Do not rely on conversational state persisting
- Capture architectural decisions in persistent documents (specifications, plans, design documents)
- Build context from these artifacts, not from memory

> **Mantra:** "Curate Context, Don't Accumulate It"

---

### Principle 10: Make It Work, Make It Right, Make It Fast

**The Problem:** Treating all three phases as equal from the start or trying to achieve them simultaneously.

**The Big Idea:** Focus on getting to "make it work"—working software that can be shipped and used. Only after real usage reveals what matters do you selectively invest in "make it right" and "make it fast."

- Stop pursuing elegance and performance upfront
- Direct agents to "make it work"
- Simple, functional implementation that passes tests
- Ship quickly
- Let real usage reveal what deserves further investment

> **Mantra:** "Build, Learn, Improve"

---

# Part 2: Process

The process puts all principles to work—principles in action.

## Two Distinct Phases

| Phase | Description |
|-------|-------------|
| **Planning** | Architectural thinking to define what to build |
| **Implementation** | Agent executes your specifications with oversight and validation |

Planning produces artifacts that enable autonomous agent implementation. Implementation uses those artifacts to build working software feature by feature.

---

## Planning Phase

Planning is where you complete your architectural thinking. You transform a vague project idea into atomic, sequenced, fully specified features ready for implementation.

**This is purely your work:** architectural decisions, decomposition, specification writing, dependency analysis. The agent can assist as a thinking partner, but you make every decision.

### The Five Planning Steps

```
Vision → Features → Specification → Dependencies → Plan
```

Each step builds on the previous. Inputs and outputs are templates and completed templates respectively.

---

### Step 1: Vision Capture

**Purpose:** Transform your vague project idea into a complete, structured Master Project Specification that articulates the problem, users, functionality, scope, and workflows.

**The Problem Solved:** Your initial project idea exists only in your head and is incomplete. You have a general sense of the problem and approach, but details are fuzzy, assumptions are unexamined, and critical aspects are uninformed.

**What You Do:** Think out loud with an agent to refine and capture your vision through five sections:

1. **Project Purpose**
   - Clarify the problem you're solving
   - Who experiences it
   - Core value your software delivers

2. **Essential Functionality**
   - Identify 3-5 fundamental workflows that solve the problem

3. **Scope Boundaries**
   - Make explicit "Now / Not / Next" decisions
   - **Now:** Must have for make-it-work version
   - **Not:** Out of scope
   - **Next:** Future enhancements

4. **Technical Context**
   - Where does it run?
   - How do users interact?
   - What systems does it connect to?

5. **Workflow Details**
   - For each core workflow: goal, high-level steps, expected outcome

**Output:** Master Project Specification (MPS)—a structured artifact capturing your complete vision for the make-it-work version.

---

### Step 2: Feature Identification and Categorization

**Purpose:** Systematically extract all units of functionality from your MPS and organize them into a categorized feature inventory.

**The Problem Solved:** You can't jump directly from high-level vision to detailed specifications. You need an intermediate step that progressively refines thinking into concrete, manageable units.

**What You Do:**

1. **Systematic Extraction** - Work through MPS section by section with targeted questions:
   - Project Purpose → What foundational capabilities are needed?
   - Essential Functionality → What discrete capabilities for each workflow?
   - Scope Boundaries → What infrastructure for make-it-work?
   - Technical Context → What platform integrations and interfaces?
   - Workflows → What handles input? Processing? Output? Errors? Feedback?
   - Cross-cutting → What security, logging, configuration, testing spans the system?

2. **Build Raw Feature List** - Capture every capability without organizing yet

3. **Challenge Completeness** - "What handles errors? What validates input? What provides feedback?"

4. **Analyze and Categorize** - Identify 3-7 natural groupings, assign features to categories

5. **Create Feature IDs** - e.g., CORE-001, API-101

6. **Estimate Complexity** - Easy / Medium / Hard for each feature

**Output:** Feature Inventory—a complete categorized list with unique IDs, descriptions, complexity estimates, and source traceability to MPS.

---

### Step 3: Iterative Specification Development

**Purpose:** Transform each feature from your inventory into a complete, atomic, implementation-ready specification.

**The Problem Solved:** You can't jump from feature inventory to implementation. Each feature needs full specification before a coding agent can implement it.

**What You Do:** For each feature, use a three-level refinement pattern:

#### A. Draft User Story
```
As a [user type], I want to [action] so that I can [benefit]
```

#### B. Implementation Contracts (Three Levels)

| Level | Format | Description |
|-------|--------|-------------|
| 1 | Plain English | Describe what the feature does naturally |
| 2 | Logic Flow | Input → Logic → Output in structured pseudo-code |
| 3 | Formal Interfaces | Exact signatures, data structures, API specs |

#### C. Validation Contracts (Three Levels)

| Level | Format | Description |
|-------|--------|-------------|
| 1 | Plain English | Describe scenarios (happy path, errors, edge cases) |
| 2 | Test Logic | Given/When/Then structure |
| 3 | Formal Tests | Exact test interfaces with setup, assertions, teardown |

#### D. Validate Atomicity
Can this be implemented in a single focused session? If specification feels scattered or describes multiple capabilities, **split into multiple features** and repeat.

#### E. Identify Dependencies
What other features must exist before this one? Document explicit, binary dependencies (depends or doesn't—no partial).

**Output:** Complete Atomic Feature Specification containing:
- User story
- Technical blueprint (3 levels)
- Validation strategy (3 levels)
- Dependencies
- Implementation notes

---

### Step 4: Dependency Analysis

**Purpose:** Transform feature specifications into a validated dependency matrix defining exact implementation order.

**The Problem Solved:** Dependencies are scattered across individual specifications. You have the local picture but not the global view needed to see circular dependencies, natural phases, and required sequencing.

**What You Do:**

1. **Extract Matrix**
   - Create a grid: rows = features, columns = features
   - Mark X where row-feature depends on column-feature

2. **Generate Graph**
   - Create visual diagram (GraphViz, Mermaid)
   - Features as nodes, dependencies as edges
   - Circular dependencies visible as closed loops

3. **Validate and Clean**
   - Apply binary dependency test: "Does row-feature require column-feature's specific output, configuration, or functionality to work?"
   - If yes → keep. If no → remove.
   - Clarify "coordination only" vs. true dependencies

4. **Detect and Resolve Cycles**
   - Visually inspect for circular dependencies
   - Resolution strategies (in order):
     1. **Dependency Elimination:** Re-examine with binary test
     2. **Revised Specification:** Rethink interfaces so features don't need each other's output
     3. **Feature Splitting:** Maybe it's not atomic
     4. **Consolidation:** Last resort

5. **Iterate** until zero cycles remain

**Outputs:**
- Validated Dependency Matrix
- Dependency Graph (visual diagram)

---

### Step 5: Implementation Plan Development

**Purpose:** Transform your validated dependency matrix into a comprehensive, phase-organized implementation roadmap.

**The Problem Solved:** Without a comprehensive plan, you can't answer: Which features first? What order? Which can be parallel? How to validate feature groups? When is it safe to start dependent features?

**What You Do:**

1. **Organize Phases (Topological Sort)**
   - Phase 1: Features with no dependencies
   - Phase 2: Features depending only on Phase 1
   - Continue pattern...
   - Verify no intra-phase dependencies
   - Identify critical path (longest dependency chain)

2. **Validation Strategy Planning**
   - For each phase, define binary success criteria
   - What tests must pass?
   - What integration points must work?
   - How to verify features work together?
   - Establish feedback loops for autonomous agent refinement

3. **Implementation Sequencing**
   - **Phase Gates:** How to determine phase completion
   - **Task Assignment:** How agents select next feature
   - **Blocker Management:** How to handle and resolve blockers
   - **Progress Tracking:** Feature-level, phase-level, critical path

**Output:** Implementation Plan—comprehensive phased execution strategy with:
- Features sequenced into dependency layers
- Parallel development opportunities identified
- Binary validation gates per phase
- Guidance for autonomous agent sessions

---

## Implementation Phase

Implementation is where planning artifacts guide transformation of specifications into working, tested software.

Unlike planning (linear, 5 steps), implementation is a **tight, rapid loop** executed repeatedly for each atomic feature.

### The Multi-Sensory Feedback Loop

The agent implements code, executes it, and gathers feedback through three digital senses:

| Sense | What It Observes |
|-------|------------------|
| **Visual** | What renders, what exists |
| **Auditory** | What the system reports (logs, errors) |
| **Tactile** | How interactions respond |

The agent runs formal tests AND correlates sensory feedback. This reveals both **what failed** (tests) and **why it failed** (sensors).

Loop continues until: All acceptance criteria pass + All sensors report clean execution.

---

### Step 1: Context Assembly

**Purpose:** Transform planning artifacts into a curated context package enabling autonomous feature implementation in a single coding session.

**The Problem Solved:** You can't dump everything at the agent and hope it figures things out. Without systematic assembly, you waste context window, force agent decisions without critical context, and turn autonomous sessions into constant back-and-forth.

**What You Do:**

1. **Feature Specification Assembly**
   - Include complete specification (user story, technical contracts, acceptance criteria)
   - @reference all dependencies

2. **Dependency Context Gathering**
   - Follow all @references
   - Pull in dependency specifications AND implemented code
   - All dependencies must already be implemented

3. **Implementation Guidance**
   - Extract relevant sections from implementation plan
   - What phase? Completion criteria? Validation strategy?

4. **Enable Sensory Capabilities**
   - Read acceptance criteria for required sensors
   - "sees, displays, renders" → Visual tools
   - "logs, errors" → Auditory tools
   - "clicks, submits, completes" → Tactile tools
   - @reference appropriate tool usage guides

**Output:** Curated Context Package containing:
- Feature specification
- Dependency code
- Relevant implementation guidance
- Sensory tool instructions

---

### Step 2: The Implementation Loop

**Purpose:** Transform an atomic feature specification into working, tested code.

**This is the only step where AI writes code.**

**The Problem Solved:** Without structure, agents either write all code before testing (problems compound) or write/test ad hoc (guessing game). Tests might pass but UI doesn't render, or workflow completes but errors fill logs.

**Why This Works:** Because features are atomic, complete implementation fits in one context window. The agent maintains full understanding from start to finish—no context loss, no reconstruction, no degraded fidelity.

**The Loop:**

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  1. WRITE CODE                                      │
│     Follow technical contracts                      │
│     Match interfaces, inputs, outputs exactly       │
│                    ↓                                │
│  2. EXECUTE AND SENSE                               │
│     Run code immediately                            │
│     Gather visual/auditory/tactile feedback         │
│                    ↓                                │
│  3. TEST AND VALIDATE                               │
│     Run all test scenarios                          │
│     Get binary pass/fail signals                    │
│                    ↓                                │
│  4. CORRELATE                                       │
│     Cross-reference sensors + test results          │
│     Multiple sensors confirming = confirmed issue   │
│     Understand WHAT failed AND WHY                  │
│                    ↓                                │
│  5. CHECK CONVERGENCE                               │
│     All tests pass?                                 │
│     All sensors clean?                              │
│        YES → Exit loop                              │
│        NO  → Refine and loop again                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Convergence Criteria:**
- All tests pass
- All sensors report clean execution (no log errors, no UI issues, interactions work)

**On Completion:**
- Create atomic git commit with only this feature's changes
- Structured commit message: Feature ID, specification summary, validation confirmation, implementation notes

**Output:** Fully working, tested feature that passed all acceptance criteria and sensor validation, ready for integration.

---

# Part 3: Tools

The framework requires four foundational capabilities.

## 1. Coding Environment

A complete development workspace supporting two types of work:
- Your architectural thinking and planning
- Agent's autonomous implementation and testing

### Core Components

| Component | Purpose |
|-----------|---------|
| **AI Coding Agent** | The implementation partner |
| **Execution Sandbox** | Safe, isolated environment for agent code execution. Freedom to experiment, iterate, break things. Disposable, risk-free, easy reset. |
| **IDE/Text Editor** | Your choice |
| **Voice Input** | Rapid capture converting speech to text at thinking speed. Planning involves externalizing architectural thinking—often incomplete, exploratory, iterative. Voice removes the typing bottleneck. |

---

## 2. Multi-Sensory Feedback System

Comprehensive validation infrastructure giving agents the ability to observe implementations through three digital sensors.

### Visual Sense Tools
**What was produced, what exists**
- UI rendering (screenshots, layout, styling)
- System state (database contents, configuration, session data)
- Code structure (actual implementation)

Catches problems logs and tests miss: broken rendering, incorrect state, structural issues.

### Auditory Sense Tools
**What the system reports**
- Logs (system narrating operations)
- Errors and warnings (problems detected)
- API responses (inter-system communications)
- Stack traces (detailed failure information)

Explains **why** things fail, not just that they failed.

### Tactile Sense Tools
**Active interaction testing**
- User workflow simulation (completing tasks end-to-end)
- API interactions (request/response cycles)
- Performance validation (response times, resource usage)
- Security checks
- Integration testing

Reveals whether software behaves correctly under actual use.

---

## 3. Context Engineering and Assembly Tools

Systematic approach to assembling focused, complete context packages through:

### Cross-Referencing System
Declarative linking (@references) allowing documents to explicitly reference other documents, code files, or sections. Enables automatic context assembly by following dependency chains.

### Slash Commands
Process automation mechanisms triggering multi-step framework workflows through single invocation. Useful for:
- Context assembly
- Template instantiation
- Implementation session initialization

### Template System
Structured document templates for every framework artifact:
- Master Project Specification
- Feature Specification
- Dependency Matrix
- Implementation Plan
- Implementation Record

Ensures consistent format and completeness. Without templates, you reinvent structure every time.

### Markdown Documentation
Universal format that agents understand deeply. Anything you want to communicate to an agent should be instantly convertible to markdown.

---

## 4. Version Control and Progress Tracking

Dual mechanism system:

### Git (Version Control)
- Implementation history through atomic feature commits
- "What changed and when"
- Like saving progress in a video game

### Implementation Plan (Progress Tracking)
- The planning artifact also serves as progress tracker
- Feature completion tracking
- "Project state"—which features are done, which remain

---

# Quick Reference: The 10 Principles

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

# Quick Reference: The Process

## Planning Phase (5 Steps)
1. **Vision Capture** → Master Project Specification
2. **Feature Identification** → Feature Inventory
3. **Iterative Specification** → Feature Specifications
4. **Dependency Analysis** → Dependency Matrix + Graph
5. **Implementation Planning** → Implementation Plan

## Implementation Phase (2 Steps, Looped)
1. **Context Assembly** → Curated Context Package
2. **Implementation Loop** → Working, Tested Features

---

*Source: "The Vibe Coding Hangover" by Corey*
*Resource: vibecodinghangover.com*
