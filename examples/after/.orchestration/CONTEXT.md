# CONTEXT — my-api

Current state snapshot. Updated at each module completion.

---

## Project State: COMPLETE

**All modules done. No pending work.**

```
M1 Auth         ✅ DONE  (2026-06-29 10:38:51)
M2 Product CRUD ✅ DONE  (2026-06-29 11:12:09)
M3 Email        ✅ DONE  (2026-06-29 11:47:22)
```

---

## What Exists

### Database
- PostgreSQL 16, connection via `DATABASE_URL` env var
- Tables: `users`, `products`
- Migrations in `src/db/migrations/` (run in order: 001, 002)
- No ORM — raw `pg` queries via pool in `src/db/pool.js`

### API Surface

```
POST   /auth/register      public
POST   /auth/login         public
GET    /products           protected (JWT)
GET    /products/:id       protected (JWT)
POST   /products           protected (JWT)
PUT    /products/:id       protected (JWT, owner only)
DELETE /products/:id       protected (JWT, owner only)
POST   /email/send         protected (JWT)
```

### Auth Flow
1. Register → bcrypt.hash(password, 12) → store hash → sign JWT (HS256, 24h) → return token
2. Login → bcrypt.compare(password, stored_hash) → sign JWT → return token
3. Protected route → `Authorization: Bearer <token>` → middleware verifies → `req.user = { id, email }`

### Response Envelope (all endpoints)
```json
{ "success": true, "data": { ... } }
{ "success": false, "error": "Human-readable message" }
```

### Environment Variables Required
```
DATABASE_URL=postgres://user:pass@localhost:5432/myapi
JWT_SECRET=<min 32 chars, random>
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=<mailtrap user>
SMTP_PASS=<mailtrap pass>
SMTP_FROM=noreply@myapi.dev
PORT=3000
```

---

## What Was Explicitly Deferred

| Feature | Reason | Where documented |
|---------|--------|-----------------|
| Redis token blocklist | Overkill for v1 single-process | DEC-001 |
| Refresh token rotation | 24h JWT expiry acceptable for v1 | GOAL.md out-of-scope |
| Rate limiting | Deferred to infra/nginx layer | GOAL.md out-of-scope |
| Email queue + retry | Synchronous send accepted for v1 | GOAL.md out-of-scope |
| Hard delete purge job | Can add later without API changes | DEC-003 |

---

## How to Run

```bash
# Install
npm install

# Set up DB (requires Postgres running)
psql $DATABASE_URL -f src/db/migrations/001_init.sql
psql $DATABASE_URL -f src/db/migrations/002_products.sql

# Start
node src/index.js

# Test
npm test
```

---

## Test Coverage

```
File                          | Stmts | Branches | Funcs | Lines
------------------------------|-------|----------|-------|------
src/routes/auth.js            |  100% |     94%  |  100% |  100%
src/routes/products.js        |  100% |     96%  |  100% |  100%
src/routes/email.js           |  100% |     90%  |  100% |  100%
src/services/authService.js   |  100% |    100%  |  100% |  100%
src/services/productService.js|   97% |     88%  |  100% |   97%
src/services/emailService.js  |  100% |     83%  |  100% |  100%
src/middleware/auth.js        |  100% |    100%  |  100% |  100%
------------------------------|-------|----------|-------|------
All files                     |   99% |     93%  |  100% |   99%
```
