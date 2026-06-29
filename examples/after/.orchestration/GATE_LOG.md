# GATE LOG — my-api

Chronological record of all gate evaluations.

---

## 2026-06-29 10:03:07 — M1 Gate Attempt 1 — FAIL ❌

**Module**: M1 (Auth)
**Attempt**: 1 of N

### Test Run

```
$ npm test -- --testPathPattern=auth

FAIL tests/auth.test.js (4.1s)
  Auth — Register
    ✓ POST /auth/register returns 201 with token (318ms)
    ✓ POST /auth/register hashes password (not plaintext in DB) (301ms)
    ✓ POST /auth/register rejects duplicate email (204ms)
    ✓ POST /auth/register rejects missing email (48ms)
    ✓ POST /auth/register rejects missing password (46ms)
    ✓ POST /auth/register rejects password under 8 chars (44ms)
  Auth — Login
    ✕ POST /auth/login returns 200 for valid credentials (3847ms)
    ✕ POST /auth/login returns JWT in response (3851ms)
    ✓ POST /auth/login rejects wrong password (273ms)
    ✓ POST /auth/login rejects unknown email (91ms)
  Auth — Protected Routes
    ✓ GET /products returns 401 without token (36ms)
    ✓ GET /products returns 401 with malformed token (31ms)
    ✓ GET /products returns 401 with expired token (33ms)
    ✗ GET /products returns 200 with valid token (skipped — login failed)

Tests:  2 failed, 11 passed, 1 skipped, 14 total
```

### Failure Detail

```
● Auth — Login › POST /auth/login returns 200 for valid credentials

  expect(received).toBe(expected)

  Expected: 200
  Received: 401

  Response body: {"success":false,"error":"Invalid credentials"}

    at Object.<anonymous> (tests/auth.test.js:58:32)
```

### Gate Decision: FAIL

**Reason**: Core login functionality broken. 2 tests failing, 1 skipped (dependent on login).
**Action**: Investigate authService.js login() — register works (password stored correctly) but login always rejects. Likely comparison bug.
**Logged**: ISS-001 opened.

---

## 2026-06-29 10:38:44 — M1 Gate Attempt 2 — PASS ✅

**Module**: M1 (Auth)
**Attempt**: 2 of 2
**Time since attempt 1**: 35m 37s (investigation + fix for ISS-001)

### Fix Applied

```diff
src/services/authService.js line 34:
- const match = await bcrypt.compare(password, password);
+ const match = await bcrypt.compare(password, user.rows[0].password_hash);
```

### Test Run

```
$ npm test -- --testPathPattern=auth

PASS tests/auth.test.js (2.1s)
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

Tests:  14 passed, 14 total
Time:   2.147s
```

### Gate Decision: PASS ✅

**ISS-001**: Resolved. Root cause documented.
**Proceeding to**: M2 (Product CRUD)

---

## 2026-06-29 11:12:01 — M2 Gate Attempt 1 — PASS ✅

**Module**: M2 (Product CRUD)
**Attempt**: 1 of 1

### Test Run

```
$ npm test -- --testPathPattern=products

PASS tests/products.test.js (0.9s)
  Products — List
    ✓ GET /products returns paginated list (143ms)
    ✓ GET /products excludes soft-deleted products (138ms)
    ✓ GET /products respects ?limit and ?offset params (141ms)
  Products — Single
    ✓ GET /products/:id returns product (89ms)
    ✓ GET /products/:id returns 404 for unknown id (41ms)
    ✓ GET /products/:id returns 404 for soft-deleted product (87ms)
  Products — Create
    ✓ POST /products creates product (112ms)
    ✓ POST /products rejects missing name (38ms)
    ✓ POST /products rejects negative price (36ms)
  Products — Update & Delete
    ✓ PUT /products/:id updates product (108ms)
    ✓ DELETE /products/:id soft-deletes (sets deleted_at) (97ms)

Tests:  11 passed, 11 total
Time:   0.934s
```

### Gate Decision: PASS ✅

**Proceeding to**: M3 (Email)

---

## 2026-06-29 11:47:14 — M3 Gate Attempt 1 — PASS ✅

**Module**: M3 (Email)
**Attempt**: 1 of 1

### Test Run

```
$ npm test -- --testPathPattern=email

PASS tests/email.test.js (0.4s)
  Email — Send
    ✓ POST /email/send returns 200 for valid request (88ms)
    ✓ POST /email/send rejects invalid email address (37ms)
    ✓ POST /email/send rejects missing subject (35ms)
    ✓ POST /email/send rejects missing body (html and text) (34ms)
    ✓ POST /email/send returns 401 without auth token (29ms)
    ✓ POST /email/send returns 502 with Retry-After on SMTP failure (41ms)

Tests:  6 passed, 6 total
Time:   0.412s
```

### Gate Decision: PASS ✅

**All modules complete. Running full test suite.**

---

## 2026-06-29 11:47:22 — Final Full Suite — PASS ✅

```
$ npm test

PASS tests/auth.test.js
PASS tests/products.test.js
PASS tests/email.test.js

Test Suites: 3 passed, 3 total
Tests:       31 passed, 31 total
Snapshots:   0 total
Time:        3.601s
```

**Project status set to COMPLETE.**

---

## Summary

| Time | Module | Attempt | Result | Notes |
|------|--------|---------|--------|-------|
| 10:03:07 | M1 Auth | 1 | ❌ FAIL | bcrypt.compare bug (ISS-001) |
| 10:38:44 | M1 Auth | 2 | ✅ PASS | ISS-001 fixed |
| 11:12:01 | M2 CRUD | 1 | ✅ PASS | Clean first pass |
| 11:47:14 | M3 Email | 1 | ✅ PASS | Clean first pass |
| 11:47:22 | Full suite | — | ✅ PASS | 31/31 |
