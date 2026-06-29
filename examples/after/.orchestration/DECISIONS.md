# DECISIONS — my-api

Architecture and implementation decisions made during this session.

---

## DEC-001 — Token storage: in-memory Map (not Redis)

**Date**: 2026-06-29 09:31:17
**Module**: M1 (Auth)
**Decision**: Use in-memory Map for token blocklist (logout/revocation). Do NOT add Redis dependency.

**Options considered**:

| Option | Pro | Con |
|--------|-----|-----|
| In-memory Map | Zero deps, instant setup | Lost on restart, single-process only |
| Redis | Persistent, scales horizontally | Adds infra dependency, overkill for v1 |
| Stateless (no revocation) | Simplest | Can't invalidate tokens on logout |

**Rationale**: This is a v1 API targeting a single-process deployment. Redis adds operational overhead (connection pooling, failover, auth) that isn't justified until horizontal scaling is needed. Documented in MEMORY.md as a prod upgrade trigger.

**Rejected**: Redis (DEC-001-REJECTED-redis)

---

## DEC-002 — Email transport: nodemailer + SMTP (not SendGrid SDK)

**Date**: 2026-06-29 11:14:03
**Module**: M3 (Email)
**Decision**: Use nodemailer with generic SMTP config. Do NOT use SendGrid's proprietary SDK.

**Options considered**:

| Option | Pro | Con |
|--------|-----|-----|
| nodemailer + SMTP | Provider-agnostic, free tier via any SMTP | More env vars to configure |
| @sendgrid/mail SDK | Simple API, good deliverability | Vendor lock-in, $20+/mo at scale |
| AWS SES via nodemailer | Cheapest at volume | AWS account + IAM setup overhead |

**Rationale**: nodemailer with SMTP keeps the codebase portable. Switching from Mailtrap (dev) to SES or Postmark (prod) is a 3-line env var change, not a code change. SendGrid SDK would require refactoring emailService.js to swap providers later.

**Rejected**: @sendgrid/mail (DEC-002-REJECTED-sendgrid)

---

## DEC-003 — Soft delete for products (not hard delete)

**Date**: 2026-06-29 10:58:44
**Module**: M2 (Product CRUD)
**Decision**: DELETE /products/:id sets `deleted_at` timestamp. Row is never removed from DB.

**Rationale**: Hard deletes are irreversible and break audit trails. Soft delete costs one nullable column and one WHERE clause. All queries filter `WHERE deleted_at IS NULL`. If storage becomes a concern, a separate nightly purge job can hard-delete rows older than 90 days — this does not require API changes.

**Implication**: GET /products and GET /products/:id both exclude soft-deleted rows. A future admin endpoint could expose them with `include_deleted=true`.

---

## DEC-004 — bcrypt cost factor: 12 (not default 10)

**Date**: 2026-06-29 09:44:02 (revised after ISS-001 fix)
**Module**: M1 (Auth)
**Decision**: Use bcrypt salt rounds = 12.

**Rationale**: Default of 10 hashes in ~65ms on modern hardware. Cost 12 = ~250ms, which is acceptable for a login endpoint and meaningfully increases brute-force cost. Cost 14+ would push register/login latency above 1s, hurting UX with no meaningful security gain at this scale.

**Note**: This decision was initially implemented correctly but the bug in ISS-001 (compare called before hash stored) masked the cost factor during M1 attempt 1.
