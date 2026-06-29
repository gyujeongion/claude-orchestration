# ✅ WITH /orchestration — Automatic Recovery, Zero Drift

**Task:** "Build a REST API with user auth, product CRUD, and email notifications"

---

```
User: Build a full REST API — user auth (JWT), product CRUD, and email notifications.
      Make it production-ready.
```

```bash
Orchestrator: Initializing orchestration hub...

  mkdir -p .orchestration/{gates,agents,logs}
  touch .orchestration/PLAN.md
  touch .orchestration/GATE_LOG.md
  touch .orchestration/STATUS.md

Hub ready. Decomposing task into modules...
```

```
# .orchestration/PLAN.md

PROJECT: REST API — Auth + Product CRUD + Email
CREATED: 2026-06-29T09:00:00Z
ORCHESTRATOR: active (no direct implementation)

MODULES:
  M1 — user-auth      (JWT, bcrypt, middleware)       [SPAWNING]
  M2 — product-crud   (CRUD routes, validation)       [SPAWNING]  ← parallel with M1
  M3 — email-notify   (nodemailer, event hooks)       [BLOCKED: M1]

DEPENDENCY GRAPH:
  M1 ──────────────────────────────────→ DONE
  M2 ──────────────────────────────────→ DONE
       M1 ∩ M2 done → unblock M3

GATE POLICY:
  Each module must pass UNIT_TEST gate before M3 can start.
  Orchestrator reviews gate output only — does NOT write code.
```

```bash
[09:00:14] Spawning M1-executor (auth)...
[09:00:14] Spawning M2-executor (product-crud)...
[09:00:14] M3 queued — waiting on M1 gate PASS
```

---

```bash
── M1-EXECUTOR ───────────────────────────────────────────────────────────────
[09:00:18] Writing auth/jwt.js        (token sign/verify, bcrypt hash)
[09:00:21] Writing auth/middleware.js (Bearer extraction, req.user injection)
[09:00:25] Writing routes/auth.js     (POST /register, POST /login)
[09:00:28] Writing auth/jwt.test.js
[09:00:30] Running tests...

  FAIL auth/jwt.test.js
  ● register › password hash should verify correctly

    expect(received).toBe(true)

    Expected: true
    Received: false

      14 |   const hash = await hashPassword(password);
      15 |   const result = await bcrypt.compare(password, hash);
    > 16 |   expect(result).toBe(true);
         |                  ^

    bcrypt.hash called with saltRounds=undefined — defaulting to NaN
    Hint: check SALT_ROUNDS env var or pass integer literal

[09:00:30] M1-EXECUTOR → GATE: UNIT_TEST FAIL
[09:00:30] Reporting to orchestrator...
```

```bash
── ORCHESTRATOR ──────────────────────────────────────────────────────────────
[09:00:31] GATE_LOG entry: M1 UNIT_TEST FAIL
           Error: bcrypt saltRounds=undefined (SALT_ROUNDS env missing)

[M1 hit a bug] → Spawning M1-bugfix-executor... [M2 and M3-prep continue in parallel]

[09:00:31] Spawning M1-bugfix-executor...
[09:00:31] M2-executor: continue uninterrupted
[09:00:31] M3-prep-executor: begin scaffolding (no M1 dep yet)
```

---

```bash
── M2-EXECUTOR (uninterrupted) ───────────────────────────────────────────────
[09:00:31] Writing models/Product.js        (Mongoose schema)
[09:00:34] Writing routes/products.js       (GET/POST/PUT/DELETE)
[09:00:37] Writing middleware/validate.js   (Joi schema validation)
[09:00:40] Writing routes/products.test.js
[09:00:43] Running tests...

  PASS routes/products.test.js
  ✓ GET /products returns empty array (42ms)
  ✓ POST /products creates product (67ms)
  ✓ PUT /products/:id updates fields (51ms)
  ✓ DELETE /products/:id removes product (38ms)
  ✓ POST /products rejects missing title (29ms)

  Test Suites: 1 passed
  Tests:       5 passed
  Time:        1.8s

[09:00:44] M2-EXECUTOR → GATE: UNIT_TEST PASS
[09:00:44] Reporting to orchestrator...
```

```bash
── M1-BUGFIX-EXECUTOR ────────────────────────────────────────────────────────
[09:00:32] Reading M1 gate log...
           Root cause: SALT_ROUNDS loaded from process.env before dotenv.config()
           Fix: move dotenv.config() to top of auth/jwt.js; fallback to integer 12

[09:00:34] Editing auth/jwt.js — line 1: require('dotenv').config()
[09:00:34] Editing auth/jwt.js — saltRounds: parseInt(process.env.SALT_ROUNDS) || 12
[09:00:35] Re-running tests...

  PASS auth/jwt.test.js
  ✓ register — password hashes correctly (310ms)
  ✓ login — valid credentials return JWT (88ms)
  ✓ login — wrong password returns 401 (91ms)
  ✓ middleware — valid token sets req.user (44ms)
  ✓ middleware — expired token returns 401 (46ms)

  Test Suites: 1 passed
  Tests:       5 passed
  Time:        2.1s

[09:00:36] M1-BUGFIX-EXECUTOR → GATE: UNIT_TEST PASS
[09:00:36] Reporting to orchestrator...
```

---

```bash
── ORCHESTRATOR ──────────────────────────────────────────────────────────────
[09:00:36] GATE_LOG entry: M1-bugfix UNIT_TEST PASS

# .orchestration/GATE_LOG.md (current state)
─────────────────────────────────────────────
[09:00:30] M1        UNIT_TEST  FAIL  bcrypt saltRounds=undefined
[09:00:36] M1-bugfix UNIT_TEST  PASS  dotenv load order fixed, fallback=12
[09:00:44] M2        UNIT_TEST  PASS  5/5 product CRUD tests green
─────────────────────────────────────────────

M1 ✅  M2 ✅ — M3 dependency satisfied.
Unblocking M3-executor...

[09:00:45] Spawning M3-executor (email-notify)...
```

---

```bash
── M3-EXECUTOR ───────────────────────────────────────────────────────────────
[09:00:49] Reading M1 auth contracts (req.user shape, event names)
[09:00:49] Reading M2 product contracts (POST /products response shape)
[09:00:52] Writing services/email.js         (nodemailer transport, templates)
[09:00:55] Writing services/email.test.js    (nodemailer mock)
[09:00:57] Writing hooks/productCreated.js   (M2 event → email trigger)
[09:01:00] Writing hooks/userRegistered.js   (M1 event → welcome email)
[09:01:02] Running tests...

  PASS services/email.test.js
  ✓ sendWelcomeEmail — calls transport.sendMail with correct to/subject (18ms)
  ✓ sendProductNotification — includes product title in body (22ms)
  ✓ transport failure — rejects with EmailSendError (14ms)

  Test Suites: 1 passed
  Tests:       3 passed
  Time:        0.9s

[09:01:03] M3-EXECUTOR → GATE: UNIT_TEST PASS
[09:01:03] Reporting to orchestrator...
```

---

```bash
── ORCHESTRATOR ──────────────────────────────────────────────────────────────
[09:01:03] GATE_LOG entry: M3 UNIT_TEST PASS

All module gates cleared. Running final integration check...

[09:01:05] Spawning integration-verifier...
```

```bash
── INTEGRATION-VERIFIER ──────────────────────────────────────────────────────
[09:01:08] Booting test server (in-memory MongoDB)
[09:01:10] POST /auth/register    → 201 ✓  welcome email queued ✓
[09:01:10] POST /auth/login       → 200 ✓  JWT returned ✓
[09:01:11] POST /products         → 201 ✓  notification email queued ✓
[09:01:11] GET  /products         → 200 ✓  [product] returned ✓
[09:01:11] PUT  /products/:id     → 200 ✓
[09:01:11] DELETE /products/:id   → 204 ✓
[09:01:12] POST /products (no auth) → 401 ✓  middleware blocking ✓

  All integration paths green.

[09:01:12] INTEGRATION-VERIFIER → GATE: INTEGRATION PASS
```

---

```bash
── ORCHESTRATOR ──────────────────────────────────────────────────────────────
[09:01:13] GATE_LOG entry: INTEGRATION PASS

Writing final status...
```

```
# .orchestration/STATUS.md  (final)
═══════════════════════════════════════════════════════════
ORCHESTRATION COMPLETE
═══════════════════════════════════════════════════════════
Task:    REST API — user auth, product CRUD, email notifications
Result:  3/3 features delivered ✅

GATE LOG SUMMARY:
  [09:00:30] M1        UNIT_TEST   FAIL  (bcrypt saltRounds=undefined)
  [09:00:36] M1-bugfix UNIT_TEST   PASS  (auto-recovered, 6s elapsed)
  [09:00:44] M2        UNIT_TEST   PASS
  [09:01:03] M3        UNIT_TEST   PASS
  [09:01:12] INTEGRATION           PASS

FILES DELIVERED:
  auth/jwt.js                routes/auth.js
  auth/middleware.js         routes/products.js
  models/Product.js          services/email.js
  middleware/validate.js     hooks/productCreated.js
                             hooks/userRegistered.js

STATS:
  Total wall time:       59 seconds
  Agents spawned:        5  (M1-exec, M2-exec, M1-bugfix, M3-exec, verifier)
  Bugs encountered:      1
  Bugs auto-resolved:    1
  User interruptions:    0
  Orchestrator code edits: 0

Orchestrator stayed above the code the entire time.
═══════════════════════════════════════════════════════════
```

---

## What went right

| Situation | How orchestration handled it |
|-----------|------------------------------|
| **Same bcrypt bug appeared** | Detected at gate boundary. Spawned a targeted bugfix executor. M2 never paused. |
| **M1 and M2 had no dependency** | Ran in parallel from the start. Combined wall time, not summed. |
| **M3 needed M1's auth contracts** | Blocked correctly at the plan level. Unblocked automatically when both gates passed. |
| **Bug fix needed** | Orchestrator read the gate log, delegated to a new executor, moved on. Never touched the code itself. |
| **All 3 features in scope** | PLAN.md listed them upfront. Every agent knew the full picture. |
| **User never asked "what next?"** | Orchestrator held the map. Work continued without interruption. |

**Result:** User gets 3 of 3 features. Walked away at `User:` line. Came back to a complete STATUS.md.
