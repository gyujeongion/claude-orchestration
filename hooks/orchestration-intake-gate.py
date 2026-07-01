#!/usr/bin/env python3
"""
Orchestration Intake Gate — physically blocks spawning a new subagent
(Agent/Task tool) while .orchestration/INTAKE.md still has any
UNPROCESSED block. This is what makes triage a real gate instead of a
reminder the orchestrator can lose track of.

Scope note: this only intercepts the Agent/Task tool call path, the same
way orchestration-guard.py only intercepts Edit/Write/NotebookEdit. It
does not sandbox arbitrary shell execution — a determined orchestrator
could still spawn work via Bash. Treat this as a strong nudge with a
hard stop on the intended path, not an unconditional guarantee.

Active only when the project root (searched upward from cwd) contains
.orchestration/ACTIVE. Otherwise this hook is a complete no-op.
"""
import json, sys, os, re, fcntl, traceback

MAX_ROOT_SEARCH_DEPTH = 12
SUBAGENT_TOOLS = {'Agent', 'Task'}

BLOCK_RE = re.compile(
    r'<!--\s*intake:block id=(?P<id>\d+) status=(?P<status>\w+)\s*-->'
    r'(?P<body>.*?)'
    r'<!--\s*intake:endblock id=(?P=id)\s*-->',
    re.DOTALL,
)


def find_project_root(cwd):
    search_path = cwd
    for _ in range(MAX_ROOT_SEARCH_DEPTH):
        candidate = os.path.join(search_path, '.orchestration', 'ACTIVE')
        if os.path.exists(candidate):
            return search_path
        parent = os.path.dirname(search_path)
        if parent == search_path:
            return None
        search_path = parent
    return None


try:
    data = json.load(sys.stdin)
    tool_name = data.get('tool_name', '') or data.get('tool', '') or ''

    if tool_name not in SUBAGENT_TOOLS:
        sys.exit(0)

    project_root = find_project_root(os.getcwd())
    if not project_root:
        sys.exit(0)

    orch_dir = os.path.join(project_root, '.orchestration')
    intake_path = os.path.join(orch_dir, 'INTAKE.md')
    lock_path = os.path.join(orch_dir, '.intake.lock')
    if not os.path.exists(intake_path):
        sys.exit(0)

    with open(lock_path, 'a+') as lock_f:
        fcntl.flock(lock_f, fcntl.LOCK_SH)
        with open(intake_path, 'r', encoding='utf-8') as f:
            content = f.read()
        fcntl.flock(lock_f, fcntl.LOCK_UN)

    unprocessed_ids = [m.group('id') for m in BLOCK_RE.finditer(content) if m.group('status') == 'UNPROCESSED']
    if not unprocessed_ids:
        sys.exit(0)

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                f"[ORCHESTRATION INTAKE GATE] {tool_name} spawn blocked. "
                f"{intake_path} still has {len(unprocessed_ids)} UNPROCESSED block(s) "
                f"(id: {', '.join(unprocessed_ids)}).\n\n"
                "Triage every UNPROCESSED block first: fold action items into "
                "GOAL.md §Pending (or MODULES.md), then flip that block's own status "
                "marker from UNPROCESSED to TRIAGED. Retry the spawn once INTAKE.md has "
                "zero UNPROCESSED blocks."
            )
        }
    }))
    print(f"BLOCKED: {tool_name} spawn — triage .orchestration/INTAKE.md first.", file=sys.stderr)
    sys.exit(2)

except Exception:
    print(f"[orchestration-intake-gate] hook error: {traceback.format_exc()}", file=sys.stderr)
    sys.exit(0)
