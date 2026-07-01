#!/usr/bin/env python3
"""
Orchestration Guard — blocks direct Edit/Write while the /orchestration
skill is active.

Active only when the project root (searched upward from cwd) contains
.orchestration/ACTIVE. Otherwise this hook is a complete no-op.
"""
import json, sys, os, traceback

MAX_ROOT_SEARCH_DEPTH = 12

try:
    data = json.load(sys.stdin)
    tool_name = data.get('tool_name', '') or data.get('tool', '') or ''

    # Only block Edit, Write, NotebookEdit
    if tool_name not in ('Edit', 'Write', 'NotebookEdit'):
        sys.exit(0)

    # Search upward from cwd for the ACTIVE flag
    cwd = os.getcwd()
    file_path = str(data.get('file_path', '') or data.get('path', ''))

    search_path = cwd
    active_found = False
    project_root = None
    for _ in range(MAX_ROOT_SEARCH_DEPTH):
        candidate = os.path.join(search_path, '.orchestration', 'ACTIVE')
        if os.path.exists(candidate):
            active_found = True
            project_root = search_path
            break
        parent = os.path.dirname(search_path)
        if parent == search_path:
            break
        search_path = parent

    if not active_found:
        sys.exit(0)

    # Files inside .orchestration/ are exempt — hub docs are the orchestrator's own responsibility
    if '.orchestration/' in file_path or file_path.endswith('.orchestration'):
        sys.exit(0)

    # Block
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                f"[ORCHESTRATION GUARD] Direct {tool_name} blocked.\n"
                f"Project: {project_root}\n"
                f"Target file: {file_path}\n\n"
                "Orchestration mode is active — implementation must be delegated to an Executor agent:\n"
                "  Spawn Agent(description='...', prompt='<SKILL.md §2-1 Executor prompt + task spec>')\n\n"
                "If you need to edit directly, end orchestration first:\n"
                "  rm <project-root>/.orchestration/ACTIVE"
            )
        }
    }))
    print(f"BLOCKED: {tool_name} — delegate to a subagent instead.", file=sys.stderr)
    sys.exit(2)

except Exception:
    # Never block the session on a hook error, but don't go fully silent either.
    print(f"[orchestration-guard] hook error: {traceback.format_exc()}", file=sys.stderr)
    sys.exit(0)
