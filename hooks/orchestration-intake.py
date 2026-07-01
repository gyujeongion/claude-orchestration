#!/usr/bin/env python3
"""
Orchestration Intake Capture — appends every user message verbatim to
.orchestration/INTAKE.md while an orchestration session is active, with
zero model judgment involved. This guarantees nothing gets dropped even
when requirements arrive scattered across many unstructured messages.

Active only when the project root (searched upward from cwd) contains
.orchestration/ACTIVE. Otherwise this hook is a complete no-op.
"""
import json, sys, os, datetime

try:
    data = json.load(sys.stdin)
    prompt = data.get('prompt', '') or ''
    if not prompt.strip():
        sys.exit(0)

    cwd = os.getcwd()

    # Search upward for the ACTIVE flag, up to 6 levels
    search_path = cwd
    project_root = None
    for _ in range(6):
        candidate = os.path.join(search_path, '.orchestration', 'ACTIVE')
        if os.path.exists(candidate):
            project_root = search_path
            break
        parent = os.path.dirname(search_path)
        if parent == search_path:
            break
        search_path = parent

    if not project_root:
        sys.exit(0)

    intake_path = os.path.join(project_root, '.orchestration', 'INTAKE.md')
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not os.path.exists(intake_path):
        with open(intake_path, 'w', encoding='utf-8') as f:
            f.write(
                "# Intake Log\n\n"
                "> Verbatim log of user messages. The orchestrator must move each "
                "UNPROCESSED block into GOAL.md §Pending, then mark it TRIAGED.\n\n"
            )

    with open(intake_path, 'a', encoding='utf-8') as f:
        f.write(f"## [{now}] UNPROCESSED\n\n{prompt}\n\n---\n\n")

    with open(intake_path, 'r', encoding='utf-8') as f:
        content = f.read()
    unprocessed = content.count('] UNPROCESSED')

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                f"[ORCHESTRATION INTAKE] This message was saved verbatim to {intake_path} "
                f"as UNPROCESSED. {unprocessed} block(s) currently untriaged. "
                "Before responding, read every UNPROCESSED block in INTAKE.md, move any "
                "action item into GOAL.md §Pending (or MODULES.md), and mark that block "
                "TRIAGED. Do not spawn the next Executor until triage is complete."
            )
        }
    }))

except Exception:
    # Never block the session on a hook error
    sys.exit(0)
