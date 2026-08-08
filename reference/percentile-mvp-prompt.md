# Paste-ready prompt: take Percentile from library to launchable

Written 2026-08-08. Covers everything that can be done in code right now: the two
consent bugs, real storage, signup and API keys, free-tier deploy config, a minimal
dashboard, and the public PII scanner.

**Run this in two or three sessions, not one.** It is six phases and each ends in a
commit. Tell the next session which phase to start from.

**Cost:** the prompt forbids anything that needs a card or costs money. Target stack
is Cloudflare Workers (free, no card) plus Neon Postgres (free tier). Expected bill
at beta scale: €0. See the note at the bottom on what happens if it grows.

---

```
Work on github.com/olivervanderlugt/percentile.

Clone to /workspace/percentile if it isn't already there. Before writing anything,
read: README.md, CLAUDE.md, docs/03-architecture.md, docs/07-roadmap.md, and
src/api/store.ts. Run `npm install && npm test && npm run typecheck` first and
confirm the suite is green before you change a line.

CONTEXT — read this or you will build the wrong thing.
Percentile was designed as two products: (1) analytics for AI-built apps, where a
coding agent reads the metrics back over MCP, and (2) a benchmark data network that
pools opted-in apps into anonymous cohort statistics and licenses them. Product 2
has been cut — it needs thousands of apps per cohort before it says anything and it
carries a large legal bill. You are shipping product 1 only.

Do NOT delete the co-op code (release gate, k-anonymity, differential privacy,
revenue-share). It stays in the repo, tested and dormant. Just don't build on it,
don't put it in the UI, and don't wire it into signup.

HARD CONSTRAINTS — these are not preferences.
- Zero cost. Do not use any service that requires a credit card or bills by usage
  beyond a free tier. If a step cannot be done free, STOP and write what you would
  need in a file called DEPLOY-NOTES.md instead of doing it.
- Do not deploy anything, do not create cloud accounts, do not touch credentials or
  secrets, and do not add a paid dependency. Produce config and instructions; Ollie
  runs them.
- Never commit to main. Never force-push.
- `npm test` and `npm run typecheck` must be green at the end of every phase. If they
  go red, fix it or stop and report — never commit red code.
- test/adversarial.test.ts is a red-team suite where VULN-* tests pass BECAUSE an
  attack works. Read its header before touching it. Do not "fix" a VULN test by
  making it pass.

BRANCH: create mvp/launchable off main. One PR at the end. Do not merge it.
Commit after each phase with a clear message.

────────────────────────────────────────────────────────
PHASE 1 — the two consent bugs. Do these first, alone.

1a. The SDK creates a tracking id before consent exists.
src/sdk/browser.ts:95-108 writes a persistent uuid to localStorage in the
constructor, gated only on optedOut(). That is an opt-OUT check; it must be opt-IN.
Write nothing to localStorage, mint no persistent id, and send no network requests
until consent is 'granted'. Queue events in memory until then, and flush once
consent arrives.
Done when: a fresh SDK instance with no consent state writes zero localStorage keys
and issues zero requests, proven by a test.

1b. Jurisdiction is decided by the browser's clock.
detectJurisdiction() at src/sdk/browser.ts:43-54 reads the timezone, and
src/core/ingest.ts:64 trusts raw.context.jurisdiction as given. Anyone can set their
clock to America/New_York and get the US consent posture instead of the EU one.
Resolve jurisdiction server-side from the request IP. Where the client hint and the
server determination disagree, apply whichever is STRICTER. Keep the client value as
a hint only.
Done when: an event carrying jurisdiction 'US' from an EU-resolved IP is handled
under EU rules, proven by a test.

Add a dated note to docs/10-legal-review.md against B3 and B4.
COMMIT.

────────────────────────────────────────────────────────
PHASE 2 — real storage.

src/api/store.ts is a MemoryStore; a restart loses every event, consent record and
workspace. Its interface was written deliberately so the backend is a driver swap
rather than a rewrite. Hold to that.

Use ONE Postgres database. Do NOT build the ClickHouse + Kafka + Postgres
architecture described in docs/03 — that is the someday shape, not the MVP.
Target Neon (free tier) via its serverless HTTP driver, so it works from an edge
runtime. Connection string from process.env.DATABASE_URL. Never hardcode it.

- Write the schema as plain .sql migration files in migrations/, applied by a small
  script. No heavyweight ORM, no migration framework.
- Implement a PostgresStore satisfying the same interface as MemoryStore.
- Keep MemoryStore — the test suite should keep using it so tests stay fast and
  offline. Pick the implementation from an env var.
- Consent ledger and workspace records must persist. Events persist with the
  existing PERCENTILE_RETENTION_DAYS TTL honoured by a cleanup query.
Done when: the server boots against Postgres, ingests an event, restarts, and the
event and its consent record are still there. Add an integration test that is
skipped when DATABASE_URL is unset.
COMMIT.

────────────────────────────────────────────────────────
PHASE 3 — signup and API keys.

Nothing currently issues a key. workspaceFromRequest (src/api/server.ts:46) looks a
bearer token up and its own comment says "Real impl: hashed key lookup + rate limit".

Build the smallest real thing:
- Email + password signup and login. Argon2id or scrypt from node:crypto — no paid
  auth service, no OAuth.
- One user, one workspace, one API key. No teams, no roles, no invitations, no SSO.
- Keys shown once at creation, stored hashed (SHA-256 is fine for a high-entropy
  random key), prefixed so they are recognisable, revocable and regenerable.
- Per-key rate limiting. In-process is acceptable for the MVP; write down the limit.
- Sessions via signed httpOnly cookies.
Done when: a stranger can sign up, get a key, send an event with it, and see it
counted — with no manual step by Ollie. Tests for signup, login, key auth, key
revocation and rate limiting.
COMMIT.

────────────────────────────────────────────────────────
PHASE 4 — deploy config, written but NOT run.

Target: Cloudflare Workers (free plan, no card) for the app, Neon (free) for the
database. Hono already runs natively on Workers, so this should be a small change.
If something in the codebase genuinely cannot run on Workers, say so plainly and
fall back to a Dockerfile plus Fly.io config — do not silently paper over it.

Produce:
- wrangler.toml (or the Docker/fly.toml fallback), with node compatibility set
  correctly and no secrets in the file.
- .env.example listing every variable, with a comment per variable.
- DEPLOY.md: exact numbered steps Ollie follows, including which free tiers to sign
  up for, which secrets to set, how to run migrations, and how to verify with a curl
  against /health.
- A hard spend guard: document the free-tier request and storage limits and how to
  set caps so an overrun fails closed instead of billing.
Do NOT deploy. Do NOT create accounts. Do NOT set secrets.
COMMIT.

────────────────────────────────────────────────────────
PHASE 5 — the smallest dashboard that makes people believe it works.

There is currently no HTML, JSX or TSX in the repo at all. Keep it that way as far
as possible: server-rendered HTML from Hono, no React, no build step, no CSS
framework. One stylesheet.

Four pages, no more: signup, login, your metrics (event counts and the basic
funnel over the last 7 and 30 days), and settings (install snippet, API key,
regenerate key, delete everything).

This page exists so a developer believes their data arrived. It is not competing
with Amplitude's UI and should not try to. No charts library — a simple bar drawn
with divs is enough.

Also: the install snippet and the MCP config must be copy-pasteable from settings,
and the MCP config must be correct for Claude Code, Cursor and Windsurf. Verify the
MCP server (src/mcp/server.ts) actually starts and its four tools respond
(get_metrics, get_benchmark, check_pii_leaks, explain_suppression). get_benchmark
will have nothing to return under the narrowed product — make it say so honestly
rather than error or return zeros.
COMMIT.

────────────────────────────────────────────────────────
PHASE 6 — the public PII scanner. Only if phases 1-5 are green.

check_pii_leaks already exists (src/mcp/server.ts:53). Expose it as a public page:
paste a URL, get a report on whether the app leaks emails or other personal data
into event properties. No account, no signup, no key.

This is the acquisition wedge — it is useful to someone who has never heard of
Percentile, so it must work standalone. Rate-limit by IP, cache results briefly,
and never store the scanned URL beyond that cache. Be honest in the output about
what the scan can and cannot see from outside.
COMMIT.

────────────────────────────────────────────────────────
FINISH
Open ONE pull request from mvp/launchable. In the description: what shipped per
phase, what you did not do and why, every free-tier limit you are relying on, and
anything you found that Ollie needs to decide. Do not merge it.

If any phase turns out bigger than it looks, stop and say so rather than
half-finishing it. Half-done auth is worse than none.
```

---

## On the money question

The stack above is genuinely free at beta scale: Cloudflare Workers' free plan gives
100,000 requests a day with no card, and Neon's free tier covers a small database.
For ten beta apps that is not close to a limit.

It stops being free if Percentile succeeds. Analytics is request-heavy — every event
is a request — so a few busy apps could pass 100k/day, and that is the point at which
either the free tier caps out or Ollie starts paying. Phase 4 asks for spend caps that
fail closed rather than bill, so the failure mode is "ingest stops" and not "surprise
invoice". That is the right default while there is no revenue, but it does mean the
launch cannot quietly scale past the cap without a decision.

Rough shape when it does: the first paid step is about €5/month for Workers plus
around €19/month for Neon once the free database is outgrown. Well under €100/month,
but not €0 — and by then charging users should be on the table anyway.
