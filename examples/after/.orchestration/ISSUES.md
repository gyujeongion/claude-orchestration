# ISSUES — my-api

---

## ISS-001 — bcrypt.compare called with plaintext instead of stored hash

**Status**: RESOLVED ✅
**Severity**: Critical
**Module**: M1 (Auth)
**Discovered**: 2026-06-29 10:03:19
**Fixed**: 2026-06-29 10:31:44
**Resolution time**: 28m 25s

---

### Symptom

Gate test `POST /auth/login returns 200 for valid credentials` failed with 401:

```
FAIL tests/auth.test.js
  Auth — Login
    ✕ POST /auth/login returns 200 for valid credentials (3847ms)

  ● Auth — Login › POST /auth/login returns 200 for valid credentials

    expect(received).toBe(expected)
    Expected: 200
    Received: 401

    Response body: { "success": false, "error": "Invalid credentials" }
```

The user had been successfully registered in the test setup (register returned 201). Login was receiving correct credentials but returning 401 every time.

---

### Investigation

Checked `authService.js` login path step by step:

1. Email lookup: `SELECT * FROM users WHERE email=$1` → returned correct row ✅
2. Password compare: `bcrypt.compare(password, password)` ← **bug found here**

The compare call was passing `password` (the plaintext input) as both arguments instead of `password` and `user.password_hash`.

```js
// BUGGY CODE in authService.js login()
const user = await db.query(
  'SELECT id, email, password_hash FROM users WHERE email = $1',
  [email]
);
if (!user.rows.length) throw new Error('Invalid credentials');

// Bug: comparing plaintext to plaintext, not plaintext to stored hash
const match = await bcrypt.compare(password, password);
if (!match) throw new Error('Invalid credentials');
```

**Why bcrypt.compare(plaintext, plaintext) always returns false**: bcrypt.compare(a, b) expects `b` to be a bcrypt hash string starting with `$2b$`. When `b` is plaintext, bcrypt cannot extract the salt and algorithm version from it, and the comparison fails. No exception is thrown — it simply resolves to `false`.

---

### Root Cause

Copy-paste error during initial implementation. The variable `user.rows[0].password_hash` was correctly referenced one line above (in the `if (!user.rows.length)` check) but the wrong variable name was used in the compare call.

---

### Fix

```diff
- const match = await bcrypt.compare(password, password);
+ const match = await bcrypt.compare(password, user.rows[0].password_hash);
```

File: `src/services/authService.js`, function `login()`, line 34.

---

### Verification

After fix, re-ran full auth test suite:

```
PASS tests/auth.test.js
  Auth — Register
    ✓ POST /auth/register returns 201 with token (312ms)
    ✓ POST /auth/register hashes password (not plaintext in DB) (289ms)
    ✓ POST /auth/register rejects duplicate email (198ms)
    ✓ POST /auth/register rejects missing email (45ms)
    ✓ POST /auth/register rejects missing password (43ms)
    ✓ POST /auth/register rejects password under 8 chars (41ms)
  Auth — Login
    ✓ POST /auth/login returns 200 for valid credentials (267ms)
    ✓ POST /auth/login returns JWT in response (265ms)
    ✓ POST /auth/login rejects wrong password (271ms)
    ✓ POST /auth/login rejects unknown email (88ms)
  Auth — Protected Routes
    ✓ GET /products returns 401 without token (34ms)
    ✓ GET /products returns 401 with malformed token (29ms)
    ✓ GET /products returns 401 with expired token (31ms)
    ✓ GET /products returns 200 with valid token (142ms)

14 passing (2.1s)
```

---

### Prevention

Added note to MEMORY.md (MEM-001) documenting the correct bcrypt.compare signature. In future, a code review checklist should verify that the second argument to bcrypt.compare is always sourced from the database row, never from request input.
