![orchestration](assets/banner.png)

# orchestration — Persistent Project Orchestration

**Keep Claude in the control tower. Never let it touch the code.**

A Claude Code skill that forces Claude to stay in the orchestrator role — decomposing, delegating, and gating — while disposable agents do every line of the actual work.

---

## The Problem

You ask Claude to build three features. It starts as orchestrator — then gets distracted by one bug, fixes it directly, forgets the other two, and stops 30 minutes later asking "what should I do next?"

The orchestrator role collapses the moment Claude is allowed to edit files. It becomes a single-threaded implementer with no memory of the original goal. Session ends. Context is gone. You start over.

→ See [examples/before/transcript.md](examples/before/transcript.md)

---

## The Solution

`/orchestration` enforces a strict separation between planning and doing:

- **Decomposes** the goal into discrete modules before touching anything
- **Spawns** Executor agents per module — Claude never edits files itself
- **Gates** on user confirmation before irreversible decisions
- **Persists** all state in `.orchestration/` — re-entry picks up exactly where it left off
- **Loops** Executor → Verifier automatically until each module passes or escalates

→ See [examples/after/transcript.md](examples/after/transcript.md)

---

## How It Works

```
[User] → /orchestration ~/project "goal"
             ↓
[Orchestrator] decomposes → spawns → gates → documents
             ↓                  ↓
[Executor agents]    [Verifier agents]
implement            validate (read-only)
             ↓
[.orchestration/ hub] — persists across sessions
```

**Orchestrator** — reads the hub, decomposes the goal, delegates to agents, never edits source files.

**Executor agents** — receive a single-module brief, implement, report back. Isolated, replaceable.

**Verifier agents** — read-only validation pass. Flag failures. Trigger the bugfix loop or escalate.

**.orchestration/ hub** — the shared brain. Survives context resets. Makes re-entry instant.

---

## The Guard Hook — Why Claude Can't Cheat

`hooks/orchestration-guard.py` is a physical enforcement layer, not a rule Claude can talk itself out of.

When `.orchestration/ACTIVE` exists, the hook blocks every `Edit`, `Write`, and `NotebookEdit` call from the orchestrator session. Only Executor sub-agents — spawned into separate contexts — are allowed to touch files. The orchestrator commands; it does not implement.

**Install:**

```bash
cp hooks/orchestration-guard.py ~/.claude/hooks/
```

Add to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [{ "command": "python3 ~/.claude/hooks/orchestration-guard.py" }]
  }
}
```

---

## Getting Started

```bash
# 1. Install the guard hook
cp hooks/orchestration-guard.py ~/.claude/hooks/

# 2. Start orchestrating
/orchestration ~/my-project "your goal in one sentence"
```

Claude sets up the hub, decomposes your project into modules, and runs Executor → Verifier loops until done. You only get pulled in for GATE decisions.

---

## The Command Hub (`.orchestration/`)

| File | Contents |
|------|----------|
| `GOAL` | Original goal statement, immutable |
| `MODULES` | Module list with status (pending / active / done / failed) |
| `DECISIONS` | Gate decisions made by the user |
| `MEMORY` | Facts the orchestrator must not forget |
| `CONTEXT` | Background the user injected |
| `ISSUES` | Escalated failures awaiting user input |
| `GATE_LOG` | Record of every gate event and outcome |
| `ACTIVE` | Presence file — activates the guard hook |

---

## Examples

→ [examples/README.md](examples/README.md)

---

## Influenced By

- [oh-my-claudecode (omc)](https://github.com/Yeachan-Heo/oh-my-claudecode) — Executor and Verifier agent role definitions

---

## License

MIT
