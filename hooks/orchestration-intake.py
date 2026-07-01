#!/usr/bin/env python3
"""
Orchestration Intake Capture — appends every user message verbatim to
.orchestration/INTAKE.md while an orchestration session is active, with
zero model judgment involved. This guarantees nothing gets dropped even
when requirements arrive scattered across many unstructured messages.

Blocks are delimited by HTML-comment markers with a numeric id, not by
generic markdown syntax like "## [...]" — a pasted message containing
that syntax would otherwise corrupt parsing (a real bug found in an
earlier version of this hook during council review).

Active only when the project root (searched upward from cwd) contains
.orchestration/ACTIVE. Otherwise this hook is a complete no-op.
"""
import json, sys, os, re, fcntl, datetime, traceback

MAX_ROOT_SEARCH_DEPTH = 12

HEADER = (
    "# Intake Log\n\n"
    "> Verbatim log of user messages, append-only. The orchestrator must fold each "
    "UNPROCESSED block's content into GOAL.md §Pending, then flip that block's own "
    "`status=` marker to TRIAGED — never a find-and-replace across the whole file.\n\n"
)

BLOCK_RE = re.compile(
    r'<!--\s*intake:block id=(?P<id>\d+) status=(?P<status>\w+)\s*-->'
    r'(?P<body>.*?)'
    r'<!--\s*intake:endblock id=(?P=id)\s*-->\s*',
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


def render_block(block_id, status, timestamp, text):
    return (
        f"<!-- intake:block id={block_id} status={status} -->\n"
        f"### {timestamp}\n\n"
        f"{text}\n\n"
        f"<!-- intake:endblock id={block_id} -->\n\n"
    )


try:
    data = json.load(sys.stdin)
    prompt = data.get('prompt', '') or ''
    if not prompt.strip():
        sys.exit(0)

    project_root = find_project_root(os.getcwd())
    if not project_root:
        sys.exit(0)

    orch_dir = os.path.join(project_root, '.orchestration')
    intake_path = os.path.join(orch_dir, 'INTAKE.md')
    lock_path = os.path.join(orch_dir, '.intake.lock')
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Serialize concurrent hook invocations (e.g. multiple fast messages,
    # or another Claude Code window active on the same project).
    with open(lock_path, 'a+') as lock_f:
        fcntl.flock(lock_f, fcntl.LOCK_EX)

        existing = ''
        if os.path.exists(intake_path):
            with open(intake_path, 'r', encoding='utf-8') as f:
                existing = f.read()

        existing_ids = [int(m.group('id')) for m in BLOCK_RE.finditer(existing)]
        next_id = max(existing_ids, default=0) + 1

        new_block = render_block(next_id, 'UNPROCESSED', now, prompt)

        with open(intake_path, 'a', encoding='utf-8') as f:
            if not existing.strip():
                f.write(HEADER)
            f.write(new_block)

        with open(intake_path, 'r', encoding='utf-8') as f:
            final_content = f.read()

        fcntl.flock(lock_f, fcntl.LOCK_UN)

    unprocessed = sum(
        1 for m in BLOCK_RE.finditer(final_content) if m.group('status') == 'UNPROCESSED'
    )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": (
                f"[ORCHESTRATION INTAKE] This message was saved verbatim to {intake_path} "
                f"as block id={next_id}, status=UNPROCESSED. {unprocessed} block(s) currently "
                "untriaged. Before responding, read every UNPROCESSED block in INTAKE.md, move "
                "any action item into GOAL.md §Pending (or MODULES.md), and flip that block's "
                "own id's status marker to TRIAGED (do not touch other blocks or the header). "
                "A separate gate hook physically blocks the next Agent/Task spawn until this "
                "is done."
            )
        }
    }))

except Exception:
    # Never block the session on a hook error, but don't go fully silent either —
    # a swallowed exception here would otherwise disable capture with no signal.
    print(f"[orchestration-intake] hook error: {traceback.format_exc()}", file=sys.stderr)
    sys.exit(0)
