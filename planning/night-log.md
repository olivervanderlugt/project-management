# Night log

What the overnight run did, newest first. One short entry per night: the task,
the outcome, and anything it refused to do and why.

This exists so Ollie can see what happened while he slept without opening five
pull requests to find out.

---

## 2026-08-07 — daytime manager session (Ollie present)

Not an overnight run — Ollie drove this one, but it followed the same
manager/builder/checker rules, so it belongs here.

**Shipped, both as PRs for Ollie to merge (nothing auto-merged to `main`):**

- **Learn — C#/.NET chain** (PR olivervanderlugt/learning-website#3, branch
  `night/learn-csharp-chain`). Three nodes (prog-csharp → -2 → -3), skills
  csharp/dotnet/methods → covered, coverage 22/6/18. Opus built, checker
  refuted the first pass (rendering: 39 fenced code blocks would have
  collapsed to one line — a bug that also hit already-merged lessons), builder
  fixed it with a RichText fence renderer, checker shipped the fix, manager
  browser-verified the rendering in both themes end-to-end. .NET SDK 10.0.302
  installed to execute every quoted output for real.
- **Percentile — F-16** (PR olivervanderlugt/percentile#1, branch
  `night/percentile-f16-count-ladder`). Published counts → k-threshold bands;
  one-query shortfall-explanation leak closed. Checker refuted the first pass
  (the bisection attack still worked via the public dominance-cap constant, and
  a guard was a strawman); builder retracted the overclaim, closed the prose
  leak, and re-labeled the residual honestly as KNOWN-OPEN (it's F-6's root
  cause, not F-16's). Tests 200/200.

**Shipped directly to the Hangar branch (no PR — Hangar convention):**

- **Dashboard redesign** — build.py rewritten around an all-projects status
  view + "waiting on you" strip + per-project Preview buttons (live vs derived
  Pages URL, never the code page). Manager added a missing `<meta charset>`.
- **Night-run vs usage limits** — researched (findings in
  `reference/nightrun-usage-limits.md`), implemented overnight rules 8–10
  (trail-before-work, stale-`doing` sweep, downgrade on limit pressure). Three
  account-level mitigations only Ollie can decide are parked as a blocked task.

**Refused / left for Ollie:** did not enable usage credits or change the
routine schedule (costs money / needs his usage-reset time). Did not build
`weekly-review-automatic` despite it being `ready` — it writes to the same
Hangar repo the dashboard redesign was rewriting, and two writers in one tree
is the exact failure the rules forbid. Left the F-6 dominance-cap oracle open
on purpose — it's the audit's next item, not this task's.

---

_No overnight runs yet. The first scheduled one is still to come._
