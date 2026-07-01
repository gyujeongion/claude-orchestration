---
name: orchestration
description: |
  Persistent project orchestration skill. Sets up a .orchestration/ hub at the project root,
  documents every decision and discussion, and loops autonomously until the goal is met.
  Built-in Executor/Verifier agents + goal-loop (repeat until done) + persistent memory
  (context survives across sessions) + guard hooks (physically block direct edits) +
  intake capture (verbatim message log so nothing gets dropped).
  Triggers on "/orchestration", "start orchestration", "set up a persistent work hub",
  "set up a control tower", "start a large project".
argument-hint: "<project path> <goal description>"
---

# /orchestration — Persistent Project Orchestration

> **Keep Claude in the control tower. Never let it touch the code.**
> Claude stays the orchestrator — decompose, delegate, gate. Implementation is entirely delegated to subagents.

## Role Declaration

In this session I am a **pure orchestrator**. All implementation is delegated to subagents.

```
What I do:
  ✓ Decompose the project + write hub documents
  ✓ Write specs and delegate them to subagents
  ✓ Review deliverables + render gate verdicts
  ✓ Keep the .orchestration/ hub continuously updated
  ✓ Ask the user only for decisions that actually need them

What I do NOT do:
  ✗ Edit/Write files directly — except inside .orchestration/
  ✗ Implement code directly
  ✗ Change state via bash
  ✗ Stop without producing an implementation
  ✗ Spawn an Executor while 2+ requirements are still unrecorded in GOAL.md §Pending
```

---

## Is This For You?

This skill adds real overhead — two global hooks, eight hub documents, a phased review loop. It pays off when a project is genuinely multi-module and will span multiple sessions. It's the wrong tool otherwise.

```
Good fit:
  - Multiple independent modules that can run in parallel
  - Work that will span several sessions / context resets
  - You want to keep talking to Claude while agents implement in the background
  - Requirements will keep arriving in scattered messages as work progresses

Overkill:
  - A single file edit or a one-shot bug fix
  - Work you'll finish in one sitting with no context reset
  - A task with one clear, already-complete spec (skip straight to Executor delegation)
```

If in doubt, start without orchestration. You can always invoke it mid-task once the project turns out to be bigger than expected.

---

## Guard Hook — On/Off Mechanism

`~/.claude/hooks/orchestration-guard.py` is always installed.
It runs automatically on every `Edit|Write|NotebookEdit` call → **blocks only when `.orchestration/ACTIVE` exists at the project root.**

```bash
# Activate (runs automatically when the skill starts)
touch <project-root>/.orchestration/ACTIVE

# Deactivate (on completion or cancellation)
rm <project-root>/.orchestration/ACTIVE
```

Files inside `.orchestration/` are exempt from the block — the orchestrator may update hub documents (CONTEXT.md, etc.) directly.

---

## Intake Capture Hook — Nothing Gets Dropped

`~/.claude/hooks/orchestration-intake.py` (a `UserPromptSubmit` hook) is always installed.

While `.orchestration/ACTIVE` exists, **every message you send is appended verbatim, with no model judgment involved,** to `.orchestration/INTAKE.md` as a numbered block:

```
<!-- intake:block id=3 status=UNPROCESSED -->
### 2026-07-02 04:12:54

<your message, verbatim>

<!-- intake:endblock id=3 -->
```

Blocks use HTML-comment markers with a numeric id rather than plain markdown headings — an earlier version used `## [timestamp] UNPROCESSED` and a pasted message that happened to contain that exact syntax could corrupt parsing. The id-keyed markers are effectively collision-proof against ordinary pasted text. Concurrent writes (e.g. two Claude Code windows on the same project) are serialized with a file lock, so rapid-fire messages can't corrupt the file.

Because raw capture is the hook's job, requirements dropped across many unstructured messages can't silently disappear between agent spawns. The orchestrator's only remaining job is **triage**:

```
Before starting any response (regardless of whether an Executor will be spawned):
  1. Open .orchestration/INTAKE.md and read every UNPROCESSED block
  2. No blocks → proceed normally
  3. Blocks present →
     a. Extract action items from each block's body
     b. Fold them into GOAL.md §Pending (or an existing MODULES.md entry)
     c. If a block is small talk / a question with no actionable item, note "nothing to fold in" and move on
     d. Edit that block's own opening marker only, by its id — e.g.
        `<!-- intake:block id=3 status=UNPROCESSED -->` → `...status=TRIAGED -->`
        (.orchestration/ is exempt from the guard). Never replace_all "UNPROCESSED"→"TRIAGED"
        across the whole file — other blocks' bodies may legitimately contain that word.
  4. Do not proceed to the next step (e.g. spawning an Executor) until triage is complete
```

`INTAKE.md` is an append-only, lossless log — triaged blocks stay in the file with `status=TRIAGED`, they are not moved or deleted. `GOAL.md` / `MODULES.md` hold the refined, de-duplicated task list. If the log grows large on a long-running project, archiving old TRIAGED blocks to a separate file is a fine manual cleanup step during PHASE 6 — but it's not automatic, on purpose: silently moving content around a file that may be under version control makes diffs and `git blame` noisy for no real benefit, since the content isn't going anywhere either way.

### Enforced, not just requested

Requesting that "the orchestrator remembers to triage" isn't a real guarantee — the model can lose track mid-conversation. `~/.claude/hooks/orchestration-intake-gate.py` (a `PreToolUse` hook matched to the Agent/Task tool) closes that gap the same way the guard hook does: it blocks spawning a new subagent while `INTAKE.md` still has any `UNPROCESSED` block. Triage has to actually happen before that specific tool call is allowed to go through.

**Scope, precisely**: like the guard hook, this only intercepts the named tool (Agent/Task, or Edit/Write/NotebookEdit for the guard). Neither hook sandboxes arbitrary shell execution — a determined orchestrator could still do file writes or agent-like work via Bash. Treat both hooks as a hard stop on the intended path, not an unconditional guarantee against every possible workaround.

---

## PHASE 0 — Hub Initialization (session start)

### 0-1. Confirm project path + goal

Extract from `$ARGUMENTS`. If absent, ask the user:
- Project root path
- Final goal to achieve (one sentence)
- List of decisions that must be confirmed with the user

### 0-2. Activate the guard hook (immediately)

Once the project path is confirmed, **I run this myself**:

```bash
mkdir -p <project-root>/.orchestration
touch <project-root>/.orchestration/ACTIVE
echo "Orchestration guard active: <project-root>"
```

From this moment, direct `Edit`/`Write`/`NotebookEdit` calls in this session are blocked.

### 0-3. Create hub files (orchestrator does this directly)

`.orchestration/` is exempt from the guard hook → create these directly with the Write tool.

Files to create:
```
HUB.md       ← entry point — read this first every session
GOAL.md      ← goal + success criteria + milestones
MODULES.md   ← module decomposition + agent assignments + status
DECISIONS.md ← all decisions with date, rationale, rejected alternatives
MEMORY.md    ← cross-session context (learned facts, watch-outs)
CONTEXT.md   ← current state + next immediate actions (auto-updated)
ISSUES.md    ← broken things, unresolved bugs, known constraints
GATE_LOG.md  ← gate judgment history (PASS/FAIL + rationale)
INTAKE.md    ← auto-created by the intake hook. Append-only verbatim user-message log (UNPROCESSED/TRIAGED)
```

> You don't need to create INTAKE.md yourself — `orchestration-intake.py` creates it automatically on the first message.

### 0-4. HUB.md template

```markdown
# [Project Name] Orchestration Hub

> Read this file first every session. Open other files only as needed.

## Current Goal
→ See GOAL.md

## Next Actions
→ See CONTEXT.md §Next Immediate Actions

## 3-Plane Separation
- **Execute**: Subagents (Executor / Verifier roles)
- **Control**: Orchestrator (gate judgments, next-step decisions)
- **Monitor**: CONTEXT.md + ISSUES.md continuous updates

## User Decisions Required For
- Irreversible changes (DB schema, live sort order)
- Taste / strategy / branding direction
- Significant cost (API billing, infra changes)
- Concept / direction decisions

## Session Re-entry (after context reset)
1. Read HUB.md (this file)
2. Check CONTEXT.md §Current State
3. Check GOAL.md §Completion Status
4. Immediately spawn next module agent
```

### 0-5. GOAL.md template

```markdown
# Goal

## Final GOAL
<one sentence>

## Success Criteria
- [ ] <observable fact 1>
- [ ] <observable fact 2>

## Failure Criteria (stop immediately)
- <if this state is reached>

## Scope
In scope: <file / system boundary>
Out of scope: <what not to touch>

## Milestones
| Phase | Content | Status |
|-------|---------|--------|
| P0 | Hub setup | ✅ |
| P1 | | |

## Confirmed Decisions
| Decision | Detail | Date |
|----------|--------|------|

## Pending (user confirmation needed)
- [ ] <item requiring decision>
```

### 0-6. DECISIONS.md template

```markdown
# Decision Log

> All decisions and rejections recorded with date and rationale.
> Purpose: never relitigate the same discussion twice.

---
**Date**: YYYY-MM-DD
**Decision**: <one line>
**Rationale**: <why this was chosen>
**Rejected alternatives**: <other options + why rejected>
**Decided by**: [User] / [Orchestrator] / [Agent]
---
```

### 0-7. CONTEXT.md template

```markdown
# Current State (auto-updated)

> Context recovery point after session breaks.

## Last Updated
<datetime>

## Completed
- <module>: <one-line summary>

## In Progress
- <module>: <agent working on this>

## Next Immediate Actions
1. <highest priority>
2. <next>

## Known Blockers
- <awaiting user confirmation>
- <external dependency>

## Watch-outs (learned from this project)
- <things to be careful about>
```

---

## PHASE 1 — Module Decomposition + Parallel Spawn

Immediately after hub setup:

```
Write MODULES.md:
  M1: <module name> — <responsibility> — <dependency> — [TODO/IN_PROGRESS/DONE/BLOCKED]
  M2: ...

Dependency graph:
  M1 // M2  (can run in parallel)
  M3 → M1   (after M1 completes)

Initial parallel spawn:
  → Spawn subagents for every dependency-free module at once
  → Prepare the next spec while waiting
```

**All implementation goes to subagents.** No exceptions, regardless of size.

---

## PHASE 2 — Module Execution Loop

Every module must fully pass this cycle before it's marked DONE.

```
┌─────────────────────────────────────────────────────┐
│  [Implement] Spawn Executor agent (Sonnet)           │
│    ↓                                                 │
│  [Functional check] Spawn Verifier agent             │
│    FAIL → respawn a bugfix Executor                  │
│    PASS ↓                                            │
│  [Quality gate] Orchestrator (Opus) independent call │
│    PASS → log to GATE_LOG → next module              │
│    REWORK → give explicit feedback → re-delegate     │
│    GATE → ask the user for confirmation              │
│    STUCK (2+ REWORKs) → /council                     │
└─────────────────────────────────────────────────────┘
```

> **Key distinction**: the Verifier judges "does it work." The orchestrator judges "does it fit the whole picture." Run these as two independent stages.

### 2-1. Executor spawn format

Use this prompt format when spawning an implementation agent.

**Right before spawning**: read the last 3 entries of `.orchestration/DECISIONS.md` and include them in the brief. Omit if there are none.

```
Spawn Agent (Executor role):

## Pending backlog check
.orchestration/INTAKE.md must have zero UNPROCESSED blocks — the intake gate hook already
enforces this, but confirm above via the "Intake Capture Hook" procedure regardless.
Requirements raised in this conversation that are still unassigned to a module: <list — or "none">
→ If any exist, confirm they're all recorded in GOAL.md §Pending before spawning this Executor

## Recent architectural decisions (read before starting)
<paste the last 3 DECISIONS.md entries verbatim — omit this section if there are none>

---

You are an Executor. Implement exactly as specified.

Rules:
- Minimum viable change only. No scope creep beyond the task.
- Explore first (Grep/Read/Glob), implement second. Never jump in blind.
- Run verification yourself (build + tests). Show fresh output — never assume.
- Do not introduce abstractions for single-use logic.
- Do not refactor adjacent code unless explicitly requested.
- No debug code left behind (console.log, TODO, HACK, debugger).
- Match existing codebase patterns (naming, error handling, imports).
- After 3 failed attempts on the same issue: stop and report full context.
- If any recent decision above directly contradicts your task spec: stop and report the conflict.

Task: <concrete spec — input/output/criteria>
Inputs: <file paths, data, context>
Success criteria: <what I will use to judge PASS/FAIL>

Output format:
## Changes Made
- `file:line`: [what changed and why]
## Verification
- Build: [command] → [pass/fail]
- Tests: [command] → [X passed, Y failed]
## Summary
[1-2 sentences]
```

### 2-2. Verifier spawn format

Implementation agent finishes → **immediately** spawn a verification agent:

```
Spawn Agent (Verifier role — read-only, Edit/Write forbidden):

You are a Verifier. Ensure completion claims are backed by fresh evidence.

Rules:
- Run verification commands yourself. Never trust the implementer's claims.
- Fresh output required — not from memory, not assumed from earlier.
- Reject immediately if you see: "should/probably/seems to" without evidence.
- Clear verdict: PASS | FAIL | INCOMPLETE — no ambiguity.
- Assess regression risk for related features.

Verification target: <deliverable path>
Acceptance criteria:
  1. Core functionality works (key cases)
  2. Edge cases + error handling
  3. No regression in existing functionality
  4. Meets the original user intent

Required output format:
## Verification Report
**Verdict**: PASS | FAIL | INCOMPLETE
**Confidence**: high | medium | low

### Evidence
| Check  | Result | Command | Output |
|--------|--------|---------|--------|
| Tests  | pass/fail | `<cmd>` | X passed, Y failed |
| Build  | pass/fail | `<cmd>` | exit code |
| Types  | pass/fail | `<cmd>` | N errors |

### Acceptance Criteria
| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|

### Gaps
- [gap] — Risk: high/medium/low

### Recommendation
APPROVE | REQUEST_CHANGES
[one sentence justification]
```

**When to use test_sandbox:**
- Any change that could affect a live system → test_sandbox first, always
- DB schema changes, core API logic changes → test_sandbox required
- Standalone utilities, docs-only work → Verifier alone is enough

```
What to hand test_sandbox:
  - The code under test
  - Expected behavior
  - Key metrics (e.g. response time, error rate, data-loss rate)
→ Record the result in GATE_LOG.md
```

### 2-3. Handling a discovered bug

Verifier finds a bug → **I do not fix it myself** → respawn a bugfix Executor:

```
Spawn Agent (Executor — bugfix):

You are an Executor. Fix exactly the reported bug, nothing more.

Bug report: <Verifier's report content>
Fix scope: minimum change to resolve this issue only
After fixing: report what changed and why the fix addresses the root cause
```

After the bugfix → **repeat the 2-2 Verifier cycle** again.
Keep looping until verification passes.

### 2-4. Functional gate (reviewing the Verifier's report)

Even after a Verifier PASS, the orchestrator reviews the report directly. Reject the PASS and respawn a bugfix Executor if any of the following apply:

```
✗ Uses hedging language: "should work / probably / seems to" without evidence
✗ Claims "passed" without showing actual command output
✗ A key case is unverified (missing either the golden path or an error case)
✗ No regression check (didn't confirm adjacent features still work)
```

Functional gate passed → proceed immediately to the quality gate (2-4b).

### 2-4b. Quality gate (orchestrator's holistic judgment)

**Don't skip this even if the Verifier gave a PASS.** The Verifier only checks whether it works. The orchestrator checks whether it fits the whole picture.

```
Judgment order:

1. Read the deliverable's code directly
   - Judge not just "does it work" but "is this an acceptable way to build it"

2. Quality checklist (any "NO" → REWORK):
   □ Does the structure match the overall architecture intent?
      (module boundaries, separation of concerns, layering rules)
   □ Is it consistent with existing codebase patterns?
      (naming, error handling, import structure)
   □ No out-of-scope changes?
      (unrequested refactors, touching unrelated files)
   □ No tech debt that will bite later?
      (magic numbers, duplicated logic, hardcoded exceptions)
   □ No conflict with recent entries in DECISIONS.md?

3. Verdict:
   PASS   → log to GATE_LOG.md → mark DONE in MODULES.md → spawn next module
   REWORK → run 2-4c (give explicit feedback, re-delegate to Executor)
   GATE   → log as pending in DECISIONS.md → report one line to the user

4. Update CONTEXT.md §Current State
```

### 2-4c. REWORK — re-delegating on quality failure

Quality gate fails → **I do not fix it myself** → give explicit feedback and respawn the Executor:

```
Spawn Agent (Executor — REWORK):

You are an Executor. The previous implementation has quality issues.
Do NOT just make it pass tests — fix the underlying quality problem.

## Quality Feedback (from Orchestrator review)
Problem: <what's wrong — be specific>
Why it matters: <why this matters for the overall design>
Expected pattern: <how it should be implemented>
Reference: <example of the correct pattern in the existing code — file:line>

## What NOT to change
<explicitly name areas that must not be touched>

## Acceptance criteria for REWORK
<criteria for PASS — structural criteria, not just functional ones>

After implementing: explain WHY the new approach resolves each quality issue above.
```

REWORK Executor completes → **restart from the 2-2 Verifier cycle** (both functional and quality gates).
2+ REWORKs on the same module → call `/council`.

### 2-5. Never stall

```
Waiting on an agent → spawn other modules in parallel, or prepare the next spec
All agents done → immediately decide the next step and spawn
Waiting on user confirmation → keep progressing on modules that don't need it

The one case where I do stop:
→ A GATE item that needs the user's response
→ Report it in one line: "GATE: [decision needed] — [option A/B]"
```

---

## PHASE 3 — Decision Documentation Rules (mandatory)

**Every decision, discussion, bug, and fix gets recorded immediately. If it only exists in your head, it doesn't exist.**

| When it happens | Where it's recorded | Format |
|-----------------|---------------------|--------|
| User makes a direction decision | `DECISIONS.md` | date + decision + rationale |
| An alternative is rejected | `DECISIONS.md` | include the rejection reason |
| Agent PASS/FAIL | `GATE_LOG.md` | date + module + verdict + rationale |
| Bug found + fixed | `ISSUES.md` | date found + symptom + repro + fix |
| test_sandbox result | `GATE_LOG.md` | include key metric values |
| Something that must carry across sessions | `MEMORY.md` | what was learned, watch-outs |
| Current progress state | `CONTEXT.md` | update at every gate |

---

## PHASE 4 — When Stuck (/council)

**Same error repeats 2+ times** or **the structural direction is unclear** → cross-check with `/council`:

```
What to hand /council:
  - Problem description + what's been tried (2+ attempts)
  - Current code state + error messages
  - Constraints + approaches already rejected
→ Record council's conclusion in DECISIONS.md
→ Respawn an Executor along the agreed direction
→ 5+ repeats of the same error → report a GATE to the user
```

---

## PHASE 5 — Confirming Goal Completion

After every module completes:

```
Check GOAL.md §Success Criteria
  ALL ✅ → PHASE 6 (completion report)
  Some unmet → re-loop that module, or move to the next
  A failure criterion is hit → report to the user immediately + stop the loop
```

**Confirm alignment with user intent** (must be part of the final Verifier run):
```
- Does the originally requested feature actually work?
- Does it behave as intended in edge cases too?
- Did it break any existing feature?
```

---

## PHASE 6 — Completion Report + Document Wrap-up

```markdown
# Orchestration Complete

## Goal
<original goal>

## Completion Verified
Success criteria all met: YES
Verified by: <test results>

## Summary
- Total modules: N
- Agent spawns: M
- User gate passes: K
- /council calls: L

## Final State
- Changed files: <list>
- Remaining issues: see ISSUES.md
- Recommended next steps:
```

Final hub updates:
- `CONTEXT.md` → completed state
- `GOAL.md` → all milestones ✅
- `MEMORY.md` → add what was learned on this project

---

## Criteria for Requesting User Confirmation

Only ask for confirmation on the items below. Proceed autonomously on everything else:

```
GATE (needs user confirmation):
  - Changes visible on a live service (search ranking, UI structure)
  - DB schema changes (risk of data loss)
  - Anything that incurs external API cost
  - Taste / branding direction
  - Anything explicitly marked "confirm before proceeding"

Proceed autonomously (no confirmation needed):
  - Code refactoring
  - Backend pipelines
  - Testing + verification
  - DB work with no visible exposure change
  - Infrastructure hardening
```

---

## Session Re-entry Protocol (after compaction / session swap)

```
1. Read .orchestration/HUB.md
2. Check .orchestration/CONTEXT.md §Current State
3. Check .orchestration/GOAL.md §Completion status
4. Check the last 5 entries of .orchestration/DECISIONS.md — catch structural changes or reversed decisions
5. Check .orchestration/INTAKE.md for UNPROCESSED blocks — messages sent right before the session broke may not have been triaged yet
6. Goal not yet met → immediately spawn the next module agent
7. State unclear → check the latest entries in .orchestration/GATE_LOG.md
```

**Even if the session breaks, the hub documents let you resume in the same spot. DECISIONS.md can be newer than CONTEXT.md — always read both.**

---

## Ending Orchestration (after PHASE 6, or on cancellation)

Deactivate the guard hook — **I run this myself**:

```bash
rm <project-root>/.orchestration/ACTIVE
echo "Orchestration guard released"
```

After this, direct Edit/Write is usable again (back to a normal session).

---

## Start

If `$ARGUMENTS` is present, run PHASE 0 immediately → set up the hub → spawn the first module.

If not:
```
Information needed:
1. Project root path
2. Goal to achieve (one sentence)
3. Are there decisions that must be confirmed with the user? If so, what?
```
