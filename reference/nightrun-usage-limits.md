# The nightly routine vs. Claude usage limits

Researched 2026-08-07 (claude-code-guide agent, sources below). Each claim is
tagged: **[docs]** = official Anthropic documentation, **[3rd]** = third-party
write-ups, **[inferred]** = plausible but not documented — treat with care.

## What actually happens

- **Mid-run limit hit (5-hour or weekly): the session stops immediately.**
  No grace period, no notification, no automatic resume after the window
  resets. Committed work survives; anything uncommitted is lost. [docs][3rd]
- **Firing while already at the limit: the run is skipped, not queued.**
  There is no retry and no catch-up — that night simply doesn't happen.
  [3rd, consistent across sources; not contradicted by docs]
- **Routines share the same usage pool** as interactive Claude Code and
  claude.ai — there is no separate metering for scheduled work. [docs]
- **Separate daily routine-run cap** on top of usage limits: ~5 runs/day on
  Pro, ~15 on Max, across all routines on the account. [3rd]
- **No documented pre-flight headroom check.** `/usage` works interactively;
  the only programmatic route is an undocumented OAuth endpoint
  (`api.anthropic.com/api/oauth/usage`) that could change or break at any
  time — not something to build the night run on. [3rd/inferred]
- **Usage credits** (opt-in, paid): with credits enabled a session that hits
  the subscription limit continues at metered API rates instead of dying.
  [docs]
- The 5-hour window is rolling; the weekly window resets at a fixed
  day/time visible at claude.ai/settings/usage. [docs]

## What the Hangar now does about it (implemented 2026-08-07)

Overnight rules 8–10 in `CLAUDE.md`:

1. **Trail before work** — task → `doing` and the night-log's opening block
   are written *before* the first expensive step, and the run commits to its
   night branch after every self-contained step. A cutoff can then never lose
   more than one step, and the morning state is always readable.
2. **Stale-`doing` recovery** — every run starts by sweeping tasks stuck on
   `doing` from a cut-off run back to `ready`/`blocked`, with a night-log
   note. No task can be silently wedged by a dead session.
3. **Downgrade on limit pressure** — on any usage-limit error the run stops
   building, commits, records honest status, and exits. Cheap work
   (sharpening `inbox` tasks) is preferred when a run knows it's late in a
   usage window.

## What cannot be fixed from inside the Hangar (Ollie's decisions)

Captured as `tasks/nightrun-limits-decisions.md` (blocked, waiting on Ollie):

- **Firing time.** Best zero-cost mitigation: schedule the routine to fire
  shortly *after* the weekly reset moment and outside the evening 5-hour
  window Ollie actually uses. Needs the reset time from
  claude.ai/settings/usage — only visible to Ollie.
- **Usage credits with a monthly cap.** The only fix that makes a mid-run
  cutoff impossible; costs real money, so per guard rules it is not enabled
  by an agent, ever.
- **A catch-up firing** (second scheduled run a few hours later that only
  acts when the night-log shows the first one died or never ran). Cheap
  insurance, but it spends more of the daily run cap — Ollie's call.

## Sources

Official: code.claude.com/docs (routines, costs, errors, monitoring-usage);
support.claude.com usage-credit articles. Third-party: truefoundry.com,
mindstudio.ai, openhelm.ai write-ups on Claude Code limits and routines;
github.com/zed-industries/zed#55501 (broken post-limit session state);
github.com/ohugonnot/claude-code-statusline (undocumented usage endpoint).
