# Paste-ready prompt: the three Percentile fixes

Written 2026-08-08. Paste the block below into a fresh Claude Code session.
Fixes 1 and 2 are worth doing whatever happens to the co-op; fix 3 only matters
if the benchmark/data-licensing side stays in the product. See
`projects/percentile.md` for why.

---

```
Work on github.com/olivervanderlugt/percentile. Clone it to /workspace/percentile
if it isn't there already, and read docs/11-privacy-audit.md and
docs/10-legal-review.md before touching anything.

Branch off main as fix/consent-and-jurisdiction. Never commit to main. Open a PR
when done — do not merge it.

Three fixes. Do them in this order, committing after each.

1. The SDK creates a tracking id before consent exists.
   src/sdk/browser.ts:95-108 writes a persistent uuid to localStorage in the
   constructor, gated only on optedOut(). That is an opt-OUT check; it must be
   opt-IN. Write nothing to localStorage, mint no persistent id and send no
   requests until consent is 'granted'. Queue events in memory only until then.
   Done when: a fresh SDK instance with no consent state writes zero localStorage
   keys and issues zero network requests, with a test proving it.

2. Jurisdiction is decided by the browser's clock.
   detectJurisdiction() at src/sdk/browser.ts:43-54 reads the timezone, and
   src/core/ingest.ts:64 trusts raw.context.jurisdiction as given. Anyone can set
   their clock to America/New_York and get the US consent posture instead of the
   EU one. Resolve jurisdiction server-side from the request IP. Where the client
   hint and the server determination disagree, apply whichever is stricter.
   Done when: an event carrying jurisdiction 'US' from an EU-resolved IP is
   handled under EU rules, with a test proving it.

3. The query budget is bypassable by renaming things.
   src/core/privacy/release-gate.ts:128 builds the budget key from the cohort
   label and the metric name, both attacker-supplied. Measured today: 50 of 50
   releases of one identical population pass a budget that permits 10, just by
   varying ?period=; 50 of 50 again by appending a space to the metric name.
   Fix: key the budget on the population — sha256 of the sorted distinct
   workspaceIds, plus a metric id resolved from a fixed registry so a metric
   cannot be renamed into a fresh budget. Add a per-workspace epsilon ledger in
   differential-privacy.ts that charges every contributing workspace on every
   release including it, capped at 1.0 per workspace per period. Also make
   narrowestReleasableCohort binding: at most one rung per (workspace, metric,
   period).
   Done when: the three VULN-3 tests and two VULN-3b tests become HOLDS-* guards
   that go red against the old code, and HOLDS-C0 still passes.

Rules:
- test/adversarial.test.ts is a red-team suite where VULN-* tests pass BECAUSE an
  attack works. Read its header before you touch it.
- npm test and npm run typecheck must be green before you push. If they go red,
  stop and report — do not push red code.
- Add a dated note to docs/10-legal-review.md against B3 and B4, and to
  docs/11-privacy-audit.md against F-3 and F-4.
- Do not touch credentials, deploys, or anything that costs money.
- PR #1 (night/percentile-f16-count-ladder) may still be open. If so, branch off
  main anyway and say so in the PR description so the two can be ordered.
```
