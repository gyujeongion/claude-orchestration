Output demo.gif
Set FontSize 14
Set Width 1200
Set Height 800
Set Theme "Dracula"
Set Shell "bash"
Set TypingSpeed 35ms

# ── SETUP (fast) ───────────────────────────────────────────────────────────
Type@5ms "bash demo.sh"
Enter
Sleep 1.5s
Type@5ms "clear"
Enter
Sleep 0.3s

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 1 — THE PROBLEM (target ~10s)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type@8ms "printf '\\033[1;33m  ── WITHOUT /orchestration ──────────────────────────────────────────\\033[0m\\n\\n'"
Enter
Sleep 0.4s

Type@5ms "cat /tmp/orchestration-demo/before_output.txt"
Enter
Sleep 4.5s

Type@5ms "clear"
Enter
Sleep 0.3s

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 2 — THE SOLUTION (target ~30s)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type@8ms "printf '\\033[1;36m  ── WITH /orchestration ─────────────────────────────────────────────\\033[0m\\n\\n'"
Enter
Sleep 0.4s

# Show the /orchestration command being invoked (medium speed — this is the hero moment)
Type "/orchestration ~/my-api 'Build REST API: auth + CRUD + email'"
Enter
Sleep 0.8s

Type@5ms "cat /tmp/orchestration-demo/hub_create_output.txt"
Enter
Sleep 1.8s

# Hub directory
Type@5ms "ls -la /tmp/orchestration-demo/.orchestration/"
Enter
Sleep 1.5s

# GOAL.md
Type@8ms "printf '\\n\\033[1;34m── GOAL.md ──\\033[0m\\n'"
Enter
Sleep 0.3s
Type@5ms "cat /tmp/orchestration-demo/.orchestration/GOAL.md"
Enter
Sleep 2.5s

# Agent spawn
Type@5ms "cat /tmp/orchestration-demo/agent_spawn.txt"
Enter
Sleep 1.5s

# ── M1 FAIL ────────────────────────────────────────────────────────────────
Type@8ms "printf '\\033[1;31m[GATE M1/attempt-1] FAIL ✗\\033[0m\\n  Reason: bcrypt.compare returning false on valid passwords\\n  Action: Spawning bugfix agent...\\n'"
Enter
Sleep 1.8s

# Auto-fix
Type@8ms "printf '  \\033[90m[Executor/M1-fix]\\033[0m password_hash whitespace bug → .trim() applied\\n'"
Enter
Sleep 1.2s

# ── M1 PASS ────────────────────────────────────────────────────────────────
Type@8ms "printf '\\033[1;32m[GATE M1/attempt-2] PASS ✓\\033[0m  auth.test.js: 14/14 passing\\n'"
Enter
Sleep 0.8s

Type@5ms "cat /tmp/orchestration-demo/gate_pass.txt"
Enter
Sleep 2s

# GATE_LOG mid-run
Type@8ms "printf '\\n\\033[1;34m── GATE_LOG.md ──\\033[0m\\n'"
Enter
Sleep 0.3s
Type@5ms "cat /tmp/orchestration-demo/.orchestration/GATE_LOG.md"
Enter
Sleep 2s

Type@5ms "clear"
Enter
Sleep 0.3s

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 3 — SESSION RECOVERY (target ~10s)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type@8ms "printf '\\033[1;35m  ── SESSION RESET ───────────────────────────────────────────────────\\033[0m\\n\\n'"
Enter
Sleep 0.4s

Type "echo '--- Context window cleared. New session. ---'"
Enter
Sleep 1.2s

Type@8ms "printf '\\033[90mReading .orchestration/HUB.md ...\\033[0m\\n'"
Enter
Sleep 0.4s
Type@5ms "cat /tmp/orchestration-demo/.orchestration/HUB.md"
Enter
Sleep 2.5s

Type@8ms "printf '\\n\\033[1;36mResuming from CONTEXT.md...\\033[0m\\n'"
Enter
Sleep 0.4s
Type@5ms "cat /tmp/orchestration-demo/.orchestration/CONTEXT.md"
Enter
Sleep 2s

Type@5ms "clear"
Enter
Sleep 0.3s

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PART 4 — COMPLETION (target ~5s)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type@8ms "printf '\\033[1;34m── GATE_LOG.md (final) ──\\033[0m\\n'"
Enter
Sleep 0.3s
Type@5ms "cat /tmp/orchestration-demo/.orchestration/GATE_LOG_FINAL.md"
Enter
Sleep 2s

Type@8ms "printf '\\n\\033[1;32m  ✅ 3/3 modules complete. 0 user interruptions.\\033[0m\\n\\n'"
Enter
Sleep 4s
