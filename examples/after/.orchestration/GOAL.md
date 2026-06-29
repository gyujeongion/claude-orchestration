# GOAL — my-api

**Objective**: Build a production-ready REST API with JWT authentication, product CRUD, and transactional email.

**Status**: COMPLETE ✅ (2026-06-29 11:47:22)

---

## Success Criteria

### Auth
- [x] ✅ POST /auth/register — creates user, hashes password with bcrypt (cost 12), returns JWT
- [x] ✅ POST /auth/login — verifies credentials, returns signed JWT (expires 24h)
- [x] ✅ JWT middleware protects all /products and /email routes
- [x] ✅ Invalid/expired tokens return 401 with clear error message
- [x] ✅ Passwords never returned in any response payload

### Product CRUD
- [x] ✅ GET /products — returns paginated list (default limit 20)
- [x] ✅ GET /products/:id — returns single product or 404
- [x] ✅ POST /products — creates product, requires auth, validates name+price
- [x] ✅ PUT /products/:id — updates product, ownership check enforced
- [x] ✅ DELETE /products/:id — soft delete (deleted_at timestamp, not hard delete)

### Email
- [x] ✅ POST /email/send — sends transactional email via nodemailer
- [x] ✅ HTML + plain text multipart supported
- [x] ✅ Failed sends return 502 with retry-after header (not 500)
- [x] ✅ Email address validated before SMTP call

### Quality Gates
- [x] ✅ All endpoints return consistent JSON envelope: `{ success, data, error }`
- [x] ✅ Input validation via express-validator on all POST/PUT routes
- [x] ✅ Database errors caught and sanitized (no raw pg errors to client)
- [x] ✅ Tests written and passing (31/31)
- [x] ✅ .env.example documents all required environment variables

---

## Out of Scope (documented, not built)

- Rate limiting (noted in DECISIONS.md — deferred to infra layer)
- Refresh token rotation (JWT 24h expiry accepted for v1)
- Email queue / retry mechanism (synchronous send accepted for v1)
