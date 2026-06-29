# MODULES — my-api

Last updated: 2026-06-29 11:47:22

---

## M1 — Auth (JWT + bcrypt)

**Status**: DONE ✅
**Attempts**: 2 (failed gate on attempt 1 — see ISSUES.md)
**Completed**: 2026-06-29 10:38:51

### Scope
- User model: `users` table (id, email, password_hash, created_at)
- POST /auth/register: validate email uniqueness, bcrypt hash, insert, return JWT
- POST /auth/login: lookup by email, bcrypt.compare, sign JWT
- `middleware/auth.js`: extract Bearer token, jwt.verify, attach `req.user`

### Files Produced
- `src/routes/auth.js`
- `src/services/authService.js`
- `src/middleware/auth.js`
- `src/db/migrations/001_init.sql` (users table)
- `tests/auth.test.js` (14 tests)

### Gate Result (Attempt 1) — FAIL
```
FAIL tests/auth.test.js
  ✕ POST /auth/login returns 200 for valid credentials (3847ms)
    Expected: 200
    Received: 401
    Error: "Invalid credentials"
```
Root cause: bcrypt.compare called on plaintext password instead of stored hash.
See ISSUES.md → ISS-001.

### Gate Result (Attempt 2) — PASS ✅
```
PASS tests/auth.test.js
  14 passing (1.2s)
```

---

## M2 — Product CRUD

**Status**: DONE ✅
**Attempts**: 1
**Completed**: 2026-06-29 11:12:09

### Scope
- Product model: `products` table (id, user_id, name, price, description, deleted_at, created_at, updated_at)
- GET /products — paginated, excludes soft-deleted
- GET /products/:id — 404 if not found or soft-deleted
- POST /products — auth required, validates name (required, max 200), price (required, positive number)
- PUT /products/:id — auth required, ownership enforced (403 if not owner)
- DELETE /products/:id — sets deleted_at, does not remove row

### Files Produced
- `src/routes/products.js`
- `src/services/productService.js`
- `src/db/migrations/002_products.sql`
- `tests/products.test.js` (11 tests)

### Gate Result — PASS ✅
```
PASS tests/products.test.js
  11 passing (0.9s)
```

---

## M3 — Email (nodemailer)

**Status**: DONE ✅
**Attempts**: 1
**Completed**: 2026-06-29 11:47:22

### Scope
- POST /email/send — auth required
- Body: `{ to, subject, html, text }`
- emailService.js wraps nodemailer transporter (SMTP via env vars)
- Validates `to` with validator.isEmail before SMTP call
- On SMTP error: returns 502 + `Retry-After: 60` header

### Files Produced
- `src/routes/email.js`
- `src/services/emailService.js`
- `tests/email.test.js` (6 tests, uses nodemailer-mock)

### Gate Result — PASS ✅
```
PASS tests/email.test.js
  6 passing (0.4s)
```

---

## Summary

```
M1 Auth         DONE ✅  attempts=2  duration=84m32s
M2 Product CRUD DONE ✅  attempts=1  duration=33m18s
M3 Email        DONE ✅  attempts=1  duration=35m13s
─────────────────────────────────────────────────────
Total                    attempts=4  duration=153m3s
```
