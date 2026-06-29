# Orchestration Examples

## The Problem This Solves

Claude Code without orchestration has a predictable failure mode on multi-feature tasks:

- **Drifts into direct implementation** — instead of delegating, Claude starts writing files itself
- **Gets absorbed in one sub-problem** — spends 20 minutes debugging bcrypt, forgets the other 2 features exist
- **Loses the big picture** — after a detour, can't reconstruct what was originally requested
- **Stops mid-task for user input** — "Should I use JWT or sessions?" — halts everything
- **No recovery if session resets** — all context is gone, must restart from scratch

---

## The Scenario

**Task:** "Build a REST API with user auth, product CRUD, and email notifications"

Same task. Two outcomes.

---

## Before (without /orchestration)

See: [before/transcript.md](before/transcript.md)

Claude immediately opens files and starts coding `auth.js`. Gets blocked on a bcrypt version conflict. Spends 18 minutes on it. Delivers a working auth module, then asks the user what to do next. Product CRUD and email never started.

**Stats:**
- Time: 30 minutes
- Direct file edits by Claude: 24
- Features delivered: 1 of 3
- User interruptions required: 3
- Recovery if session resets: none

---

## After (with /orchestration)

See: [after/transcript.md](after/transcript.md)

Orchestrator reads the task, writes `GOAL.md`, decomposes into 3 parallel tracks, spawns Executor agents for each. When auth hits the bcrypt conflict, a bugfix agent handles it while product CRUD and email continue. All 3 features land. No user input needed until final review.

**Stats:**
- Time: same task
- Features delivered: 3 of 3
- User interruptions: 0 (1 final review gate)
- Bug recovery: automatic, non-blocking
- Session reset recovery: resume from CONTEXT.md

---

## What the .orchestration/ Hub Looks Like

See: [after/.orchestration/](after/.orchestration/)

| File | Purpose |
|------|---------|
| `GOAL.md` | Original task + success criteria, never modified |
| `PLAN.md` | Decomposed phases and agent assignments |
| `CONTEXT.md` | Current state snapshot — the recovery point |
| `DECISIONS.md` | Irreversible choices made (with rationale) |
| `agents/auth.md` | Auth agent brief + output log |
| `agents/crud.md` | CRUD agent brief + output log |
| `agents/email.md` | Email agent brief + output log |

---

## The Key Difference

| Without /orchestration | With /orchestration |
|------------------------|---------------------|
| Claude writes code directly | Delegates to Executor agents |
| Gets stuck on one bug | Spawns bugfix agent, continues in parallel |
| Forgets original scope | GOAL.md always visible |
| Stops for user input mid-task | Only gates on irreversible decisions |
| No recovery if session resets | CONTEXT.md = full recovery point |
| 1 of 3 features | 3 of 3 features |
