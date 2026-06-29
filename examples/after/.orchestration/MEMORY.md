# MEMORY — my-api

Watch-outs and lessons learned. Future agents working on this codebase read this first.

---

## MEM-001 — bcrypt.compare must receive the STORED HASH, not the plaintext input again

**Discovered**: 2026-06-29 10:03:19 (M1, attempt 1 gate failure)
**Severity**: Critical — caused silent auth failure (always returned 401)

**Wrong**:
```js
// authService.js — BUG (what was written initially)
const hash = await bcrypt.hash(password, 12);
const match = await bcrypt.compare(password, password); // ← compared plaintext to plaintext
```

**Correct**:
```js
const user = await db.query('SELECT password_hash FROM users WHERE email=$1', [email]);
const match = await bcrypt.compare(password, user.rows[0].password_hash); // ← compare against stored hash
```

**Why it's easy to miss**: bcrypt.compare(a, b) returns true if `a` is the plaintext that produced hash `b`. Passing plaintext for both `a` and `b` causes bcrypt to hash `a` again and compare — which will never match the stored value. No runtime error is thrown; it just silently returns false.

---

## MEM-002 — pg connection pool: set max to 10, not default 100, for single-process API

**Discovered**: 2026-06-29 10:52:31 (M2, during productService.js review)
**Severity**: Medium — not a bug now, but a prod time-bomb

**Context**: `new Pool({ connectionString })` defaults to `max: 10` in pg v8+, but earlier docs showed `max: 100`. Verify the pg version's default before deploying.

**Current config** (`src/db/pool.js`):
```js
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});
```

**Prod upgrade trigger**: When adding Redis (see DEC-001), revisit pool sizing. Horizontal scaling with multiple processes each holding 10 connections can exhaust Postgres's `max_connections` (default 100) quickly. PgBouncer or a connection proxy becomes necessary at that point.

---

## MEM-003 — nodemailer transporter must be created once, not per-request

**Discovered**: 2026-06-29 11:28:44 (M3, during emailService.js implementation)
**Severity**: Medium — per-request creation causes connection churn and SMTP auth overhead

**Wrong**:
```js
// emailService.js — naive implementation
async function sendEmail(opts) {
  const transporter = nodemailer.createTransport({ ... }); // ← recreated every call
  await transporter.sendMail(opts);
}
```

**Correct**:
```js
// emailService.js — singleton transporter
const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST,
  port: Number(process.env.SMTP_PORT) || 587,
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
});

async function sendEmail(opts) {
  await transporter.sendMail(opts); // ← reuses SMTP connection pool
}
```

**Note**: nodemailer's transporter maintains a connection pool internally. Module-level singleton is the intended usage pattern.

---

## MEM-004 — Soft-delete queries: always add `AND deleted_at IS NULL` or rows leak

**Discovered**: 2026-06-29 11:05:12 (M2, productService.js code review)
**Severity**: High — without this clause, deleted products appear in GET /products

**Checklist** — every query that touches the `products` table must include:
- `WHERE deleted_at IS NULL` (list queries)
- `AND deleted_at IS NULL` (single-row lookups)

**Currently safe**:
- `productService.getAll()` ✅
- `productService.getById()` ✅
- `productService.update()` ✅ (ownership check also filters deleted)

**Future risk**: If a new developer adds a query without this clause, deleted products silently reappear. Consider adding a Postgres view `active_products AS SELECT * FROM products WHERE deleted_at IS NULL` and querying that instead of the base table.
