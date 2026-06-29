#!/usr/bin/env python3
"""
Orchestration Guard — /orchestration 스킬 활성 시 Edit/Write 직접 수정 차단.

활성화: 프로젝트 루트에 .orchestration/ACTIVE 파일이 있을 때만 작동.
비활성: ACTIVE 파일 없으면 완전히 통과.
"""
import json, sys, os

try:
    data = json.load(sys.stdin)
    tool_name = data.get('tool_name', '') or data.get('tool', '') or ''

    # Edit, Write, NotebookEdit 만 차단
    if tool_name not in ('Edit', 'Write', 'NotebookEdit'):
        sys.exit(0)

    # 현재 작업 디렉토리 + 파일 경로로 프로젝트 루트 탐색
    cwd = os.getcwd()
    file_path = str(data.get('file_path', '') or data.get('path', ''))

    # ACTIVE 플래그 탐색: CWD 기준 상위 5단계까지
    search_path = cwd
    active_found = False
    project_root = None
    for _ in range(6):
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

    # .orchestration/ 내부 파일은 허용 (허브 문서 갱신은 오케스트레이터 몫)
    if '.orchestration/' in file_path or file_path.endswith('.orchestration'):
        sys.exit(0)

    # 차단
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": (
                f"[ORCHESTRATION GUARD] {tool_name} 직접 수정 차단됨.\n"
                f"프로젝트: {project_root}\n"
                f"대상 파일: {file_path}\n\n"
                "오케스트레이션 모드 활성 중 — 구현은 반드시 Executor 에이전트에게 위임:\n"
                "  Agent(description='...', prompt='<SKILL.md §2-1 Executor 프롬프트 + 태스크 스펙>') 으로 스폰\n\n"
                "오케스트레이션 종료 후 직접 수정이 필요하다면:\n"
                "  rm <프로젝트>/.orchestration/ACTIVE"
            )
        }
    }))
    # 차단을 위해 stderr로 에러 출력 + non-zero exit
    print(f"BLOCKED: {tool_name} → 서브에이전트에게 위임하세요.", file=sys.stderr)
    sys.exit(2)

except Exception as e:
    # 훅 오류는 조용히 패스 (작업 방해 안 함)
    sys.exit(0)
