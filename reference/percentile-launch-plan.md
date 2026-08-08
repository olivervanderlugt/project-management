# Percentile — what's left before launch, and how to roll it out

Written 2026-08-08, against the narrowed product in decision 0004 (analytics + MCP,
no data co-op). Read from the code and from `docs/06-go-to-market.md` and
`docs/07-roadmap.md`, not from memory.

## How far from launch: the hard half is done, the boring half hasn't started

Percentile is currently a **library with an API server attached**, not a product. The
difficult, genuinely impressive engineering — the privacy maths, the consent ledger, the
adversarial test suite, the MCP server — is finished and well tested. The unglamorous
plumbing that turns it into something a stranger can sign up for does not exist at all.

What the code says today:

| Piece | State |
|---|---|
| Privacy core, consent, redaction, aggregation | Built and tested (200 tests) |
| Browser SDK, MCP server, API routes | Built |
| Revenue-share settlement | Built — and now unnecessary under 0004 |
| **Storage** | **In-memory only.** `src/api/store.ts` is a `MemoryStore`; restart the process and every event, consent record and workspace is gone. Its own header calls it "a stand-in for the real storage tier". |
| **Signup / API keys** | **Missing.** `workspaceFromRequest` looks a bearer token up in the store, and its comment says "Real impl: hashed key lookup + rate limit". Nothing anywhere issues a key. |
| **Hosting** | **Missing.** Nothing is deployed. There is no URL an app could send events to. |
| **Dashboard** | **Missing.** Zero HTML, JSX or TSX files in the entire repo. |
| **Billing** | **Missing.** No Stripe, no plans. Two runtime dependencies total (`hono`). |

`docs/07-roadmap.md` already knows this — its Phase 0 lists exactly four unticked items:
storage, auth/keys/rate-limiting, hosted ingest, minimal dashboard. That list is still
accurate, and it is the whole gap.

**Estimate: 4–8 focused weekends**, solo, alongside study. Not because any single item is
hard, but because there are five of them and the last 10% of deployment always costs more
than expected.

## The MVP, cut to the bone

Ordered. Each line is shippable on its own.

1. **Fix the two consent bugs.** The SDK writes a persistent id before consent, and reads
   jurisdiction from the browser clock. Do not put a product in front of strangers with
   these open — see `tasks/percentile-b3-b4-sdk-blockers.md`. Prompt ready in
   `reference/percentile-fix-prompt.md`.
2. **Postgres behind the existing store interface.** One database, not the
   ClickHouse+Kafka+Postgres architecture in `docs/03`. The interface was deliberately
   written to make this a driver swap; hold to that and resist rebuilding. Managed Postgres
   on Neon or Supabase, free tier.
3. **Signup and API keys.** Email, password, one workspace, one key, hashed at rest. No
   teams, no roles, no SSO, no invitations.
4. **Deploy it.** Fly.io, Railway or Render. One region. A real URL and a health check.
5. **The smallest possible dashboard.** One page: your events, your numbers, your install
   snippet, your API key. It exists so people believe the data arrived — not to be a
   competitor to Amplitude's UI.
6. **Polish the MCP install path.** This is the actual product, so it deserves more care
   than the dashboard: copy-paste config for Claude Code, Cursor and Windsurf, and docs
   written for a model to follow rather than a human to read.

**Deliberately not in the MVP:** billing, teams, the co-op, benchmarks, cohorts, SOC 2, the
ClickHouse tier, and the revenue-share code that already exists. Charge nobody at first —
you need to know whether people come back before you find out whether they will pay.

## The go-to-market has to be rewritten, and that is not a small note

`docs/06-go-to-market.md` opens with: *"The whole GTM problem is one number: get ~10
comparable apps and 500 subjects into the same cohort."* The entire strategy — the density
trap, targeting `lovable × b2b_saas × 100-1k`, turning away qualified leads outside the
target cohort — exists to serve the benchmark network. **Decision 0004 cuts the benchmark
network, so that strategy is void.** Not wrong; it answers a question the product no longer
asks.

What survives is, conveniently, the two strongest channels in it.

### Channel 1 — the free PII leak scanner (the wedge)

`check_pii_leaks` already exists in the codebase. Productise it as a public page: paste a
URL, get a report on whether the app is leaking user emails and other personal data into
event properties. No account, no signup, no payment.

It works because it is alarming, specific, true distressingly often, and about *their* app
rather than about you. It demonstrates the privacy posture instead of asserting it, and it
is the kind of finding people screenshot into a Discord. It needs no cohort, no density and
no other user — so unlike everything else in the old plan, it works on day one.

**This should probably ship before the analytics product**, as a standalone page. It builds
the audience the product then launches to.

### Channel 2 — agent-native distribution (the differentiator)

Nobody else is selling analytics whose primary interface is the coding agent. Make the MCP
server trivial to install in Claude Code, Cursor and Windsurf; publish `llms.txt` and a
clean OpenAPI spec so agents can wire it up unattended; get into a Lovable or Bolt starter
template, which is worth more than any amount of content marketing.

The old plan already ranked this first and called it "the one competitors are already moving
on". That is still true and the clock is still running.

### Channel 3 — builder communities

Lovable Discord, Bolt, r/vibecoding, Indie Hackers. Participate, don't advertise. The
contribution is now the free scan rather than benchmark numbers — which is a *better* fit,
because a scan is about the reader's own app and a benchmark is about strangers.

### Dead until the product is large

Published benchmark reports (*State of AI-Built Apps*) and the embedded-widget partnerships
with Lovable and Bolt both require benchmark data that will not exist. Park them; do not
quietly keep them in the plan as though they were still coming.

## Rollout, in stages

| Stage | What ships | Done when |
|---|---|---|
| 0 | Consent fixes, Postgres, keys, deploy | You can install it in a throwaway app from a clean machine and the data survives a restart |
| 1 | Private beta, 5–10 apps you personally know | People you know have it running and you have watched one of them ask their agent about their metrics |
| 2 | The PII scanner, public, no signup | It is live, it works on any URL, and it has been posted in three communities |
| 3 | Open signup, free, no billing | Strangers install it without you in the room |
| 4 | Billing | Only after stage 3 shows people returning |

## The number that decides everything

Not signups, and not installed apps. **Do people ask their agent about their metrics more
than once?**

The whole premise is that an agent-readable analytics tool gets used differently from a
dashboard nobody opens. If people install it and never query it twice, the premise is wrong,
and no amount of go-to-market repairs that. Instrument this from stage 1 and treat two
consecutive weeks of near-zero repeat queries as a reason to stop and re-plan rather than
push harder.

This replaces the old plan's exit criteria, which were all cohort-density measures.

## Open risks

- **Analytics is a crowded, well-funded market.** PostHog, Amplitude, Mixpanel and Plausible
  all have free tiers. The MCP angle is the only real differentiator, so if it turns out to
  be a novelty rather than a habit, there is no second line of defence.
- **The audience may not pay.** People shipping Lovable apps are price-sensitive and churn
  fast. A free tier generous enough to be useful may be the whole product for most of them.
- **Consent-first is a cost, not yet a feature.** It becomes a selling point only if a
  customer is asked about GDPR by someone. For a hobbyist that day may never come.
- **Time.** This is being built by one first-year student alongside a degree, and the four
  remaining Phase 0 items are the least interesting work in the project. That is the usual
  place solo projects stop.
