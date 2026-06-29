#!/usr/bin/env bash
# demo.sh — Orchestration skill demo setup
# Creates simulated .orchestration/ files for demo.tape
# Idempotent: safe to run multiple times

set -e

DEMO_DIR="/tmp/orchestration-demo"
HUB_DIR="$DEMO_DIR/.orchestration"

# Clean and recreate
rm -rf "$DEMO_DIR"
mkdir -p "$HUB_DIR"

# ─────────────────────────────────────────
# PART 1 output: "before" drift scenario
# ─────────────────────────────────────────
cat > "$DEMO_DIR/before_output.txt" << 'EOF'
User: Build a full REST API — auth (JWT), product CRUD, email.

Claude: I'll start with the auth system. Let me set up JWT...

  [Edit]  src/auth/middleware.js  (+80 lines)
  [Edit]  src/auth/jwt.js         (+40 lines)

  Hmm, the bcrypt comparison is failing in my test...

  [Edit]  src/auth/jwt.js         (fix salt rounds)

  Actually, I need to handle token refresh too.

  [Edit]  src/auth/refresh.js     (+60 lines)
  [Edit]  src/auth/redis-client.js (+30 lines)
  [Edit]  src/auth/refresh.js     (rewrite with Redis)

  The rate limiter needs Redis integration too...

  [Edit]  src/auth/rate-limit.js  (+45 lines)
  [Edit]  src/auth/rate-limit.js  (fix window reset bug)
  [Edit]  src/auth/rate-limit.js  (fix window reset bug)
  [Edit]  src/auth/rate-limit.js  (fix window reset bug)

  ── 30 minutes later. 24 edits. Still only in auth. ──

  I've finished the authentication system! ✅

  What should I work on next?
  Should I do product CRUD or email notifications?

  [Waiting for user input...]
EOF

# ─────────────────────────────────────────
# PART 2: Hub creation output
# ─────────────────────────────────────────
cat > "$DEMO_DIR/hub_create_output.txt" << 'EOF'
Orchestration guard active: /tmp/orchestration-demo

Creating .orchestration/ hub...
  ✓ HUB.md
  ✓ GOAL.md
  ✓ MODULES.md
  ✓ DECISIONS.md
  ✓ MEMORY.md
  ✓ CONTEXT.md
  ✓ ISSUES.md
  ✓ GATE_LOG.md

Hub initialized. Decomposing goal into modules...

  M1  Auth (JWT + bcrypt)
  M2  Product CRUD
  M3  Email (nodemailer)

Spawning Executor → M1 (Auth)...
EOF

# ─────────────────────────────────────────
# PART 2: GOAL.md
# ─────────────────────────────────────────
cat > "$HUB_DIR/GOAL.md" << 'EOF'
# GOAL — my-api

**Objective**: Build a production-ready REST API with JWT auth, product CRUD, and email.

**Status**: IN PROGRESS ⏳

---

## Success Criteria

### Auth
- [ ] POST /auth/register — bcrypt hash (cost 12), returns JWT
- [ ] POST /auth/login — verify + sign JWT (24h expiry)
- [ ] JWT middleware protects /products and /email routes

### Product CRUD
- [ ] GET /products — paginated list (default limit 20)
- [ ] POST /products — requires auth, validates name+price
- [ ] DELETE /products/:id — soft delete (deleted_at timestamp)

### Email
- [ ] POST /email/send — transactional via nodemailer
- [ ] Failed sends return 502 with retry-after header

### Quality Gates
- [ ] All endpoints return { success, data, error } envelope
- [ ] Tests written and passing
EOF

# ─────────────────────────────────────────
# PART 2: Agent spawn output
# ─────────────────────────────────────────
cat > "$DEMO_DIR/agent_spawn.txt" << 'EOF'
[Executor/M1] Starting: Auth (JWT + bcrypt)
  → Writing src/auth/authService.js
  → Writing src/middleware/auth.js
  → Writing tests/auth.test.js
  → Done. Signaling orchestrator...

[Orchestrator] Running gate check on M1...
EOF

# ─────────────────────────────────────────
# PART 2: M1 FAIL → fix → PASS sequence
# ─────────────────────────────────────────
cat > "$DEMO_DIR/gate_fail.txt" << 'EOF'
[GATE M1/attempt-1] FAIL ✗
  Reason: bcrypt compare returning false on valid passwords
  Test:   auth.test.js:14 — POST /auth/login → 401 (expected 200)
  Action: Spawning bugfix agent...

[Executor/M1-fix] Diagnosing bcrypt compare...
  → authService.js:32: bcrypt.compare(password, user.password_hash)
  → Bug: password_hash stored with extra whitespace (trim() missing)
  → Fix: user.password_hash.trim() applied
  → Re-running tests...
EOF

cat > "$DEMO_DIR/gate_pass.txt" << 'EOF'
[GATE M1/attempt-2] PASS ✓
  auth.test.js: 14/14 passing

[Orchestrator] M1 complete. Spawning Executor → M2 (Product CRUD)...
[Executor/M2] Starting: Product CRUD
  → Done. Signaling orchestrator...
[GATE M2/attempt-1] PASS ✓  products.test.js: 11/11 passing
[Orchestrator] M2 complete. Spawning Executor → M3 (Email)...
[Executor/M3] Starting: Email (nodemailer)
  → Done. Signaling orchestrator...
[GATE M3/attempt-1] PASS ✓  email.test.js: 6/6 passing
EOF

# ─────────────────────────────────────────
# PART 2: GATE_LOG.md (partial — mid-run)
# ─────────────────────────────────────────
cat > "$HUB_DIR/GATE_LOG.md" << 'EOF'
# GATE LOG — my-api

| Time     | Module | Attempt | Result | Notes                          |
|----------|--------|---------|--------|-------------------------------|
| 09:31:04 | M1     | 1       | FAIL   | bcrypt.compare whitespace bug  |
| 09:34:17 | M1     | 2       | PASS   | trim() fix applied             |
| 09:51:22 | M2     | 1       | PASS   | 11/11 tests passing            |
| 10:08:45 | M3     | 1       | PASS   | 6/6 tests passing              |
EOF

# ─────────────────────────────────────────
# PART 2: CONTEXT.md
# ─────────────────────────────────────────
cat > "$HUB_DIR/CONTEXT.md" << 'EOF'
# CONTEXT — my-api
*Auto-updated by orchestrator after each gate*

## Current State

**Phase**: COMPLETE ✅
**Last Action**: M3 (Email) gated PASS at 10:08:45
**Completed Modules**: M1 ✅ M2 ✅ M3 ✅

## Next Immediate Actions

All modules complete. Final integration check pending.

## Watch-outs

- bcrypt compare: always .trim() password_hash before compare
  (see ISSUES.md for full root cause)

## User Decisions Required

None outstanding.
EOF

# ─────────────────────────────────────────
# PART 3: HUB.md (session recovery)
# ─────────────────────────────────────────
cat > "$HUB_DIR/HUB.md" << 'EOF'
# PROJECT HUB — my-api

**Status**: COMPLETE ✅
**Started**: 09:14:03  |  **Completed**: 10:08:45
**Total Duration**: 54m 42s

---

## Module Status

| ID | Module               | Status   | Attempts |
|----|----------------------|----------|----------|
| M1 | Auth (JWT + bcrypt)  | DONE ✅  | 2        |
| M2 | Product CRUD         | DONE ✅  | 1        |
| M3 | Email (nodemailer)   | DONE ✅  | 1        |

---

## Session Re-entry (after context reset)

1. Read HUB.md (this file)      ← you are here
2. Check CONTEXT.md → Current State
3. Check GOAL.md → completion status
4. Resume from last incomplete module

---

## Key Files

- GOAL.md      — success criteria
- CONTEXT.md   — current state + next actions
- GATE_LOG.md  — full gate history
- ISSUES.md    — bcrypt bug: root cause + fix
EOF

# ─────────────────────────────────────────
# PART 4: Final GATE_LOG (all PASS)
# ─────────────────────────────────────────
cat > "$HUB_DIR/GATE_LOG_FINAL.md" << 'EOF'
# GATE LOG — my-api

| Time     | Module | Attempt | Result | Notes                         |
|----------|--------|---------|--------|-------------------------------|
| 09:31:04 | M1     | 1       | FAIL   | bcrypt.compare whitespace bug |
| 09:34:17 | M1     | 2       | PASS   | trim() fix applied            |
| 09:51:22 | M2     | 1       | PASS   | 11/11 tests passing           |
| 10:08:45 | M3     | 1       | PASS   | 6/6 tests passing             |

---

✅ 3/3 modules complete. 0 user interruptions.
EOF

echo "✓ Demo files ready in $DEMO_DIR"
ls -la "$HUB_DIR"
