# ❌ WITHOUT /orchestration — The Drift Problem

**Task:** "Build a REST API with user auth, product CRUD, and email notifications"

---

```
User: Build a full REST API — user auth (JWT), product CRUD, and email notifications.
      Make it production-ready.
```

```
Claude: I'll start with the auth system. Let me set up JWT middleware...

[writes auth/middleware.js — 80 lines]
[writes auth/jwt.js — 40 lines]

Hmm, the bcrypt comparison is failing in my test...

[edits auth/jwt.js — fixes salt rounds]

Actually, I need to handle token refresh too. Let me add that.

[writes auth/refresh.js — 60 lines]

Wait, there's a race condition when two refresh requests come in simultaneously.
Let me fix that...

[edits auth/refresh.js — adds mutex]
[edits auth/middleware.js — updates to use new refresh logic]

The mutex approach won't scale. Let me use Redis instead.

[writes auth/redis-client.js — 30 lines]
[edits auth/refresh.js — rewrites with Redis]

Now Redis needs connection pooling for production...

[edits auth/redis-client.js — adds connection pool]

I should add rate limiting to the auth endpoints too...

[writes auth/rate-limit.js — 45 lines]
[edits routes/auth.js — adds rate limiting middleware]

The rate limiter needs to work with the Redis client I set up...

[edits auth/rate-limit.js — integrates Redis]

Found a bug: the rate limit window isn't resetting correctly...

[5 more edits across 3 files debugging rate limit window logic]
```

---

**30 minutes later. 24 file edits. Still only in auth.**

```
Claude: I've finished the authentication system! Here's what was implemented:

  ✅ JWT token generation & validation
  ✅ Token refresh with race condition protection (Redis)
  ✅ Rate limiting on auth endpoints
  ✅ Connection pooling for production

  What would you like me to work on next?
  Should I start on the product CRUD or the email notifications?

  [Waiting for user input...]
```

---

## What went wrong

| Problem | What happened |
|---------|--------------|
| **Drift** | Started on auth → got pulled into JWT → refresh → Redis → rate limiting. Never surfaced for air. |
| **Lost scope** | Original task had 3 features. Claude forgot features 2 and 3 existed. |
| **Direct implementation** | Wrote and edited code directly instead of delegating. Every tangent = more drift. |
| **Stopped for permission** | After 30 min, stopped and asked "what next?" — user has to re-explain the original plan. |
| **No recovery path** | If session resets here, the new Claude has no idea what M2 and M3 were. |

**Result:** User gets 1 of 3 features. Has to babysit. Cannot walk away.
