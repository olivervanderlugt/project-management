# Night-run rules

**These rules apply to the unattended nightly Routine and to nothing else.**

If you are reading this in a session Ollie started himself — he typed a prompt,
he is there, he can answer — then this file is background, not law. Close it and
work under his direction. Every rule below is a consequence of one fact: *nobody
is awake to catch a mistake.* When someone is awake, the reason is gone and so
is the rule.

They used to live in `CLAUDE.md`, which meant every session read them as
standing law and quietly obeyed them — capping itself at one task, refusing to
build past three open PRs, filing its trail in the night-log — in sessions where
none of that was ever the point. That is what decision `0004` moved out.

The night run gets them by being told to read this file. See
`reference/startprompt-nightrun.md` for the prompt that does it.

---

## The rules

A Routine fires nightly and works the queue in `tasks/`. These are not
suggestions — they exist because nobody is awake to catch a mistake:

1. **One task per night.** Highest `ready` task, oldest first. Not the whole
   queue — the limit is Ollie's usage budget, not the machine.
2. **`ready` only.** An `inbox` task gets investigated and sharpened into a
   proposal. Never built.
3. **Its own branch, then a PR.** Never commit to `main`, never to a branch
   Ollie is working on. Record the branch in the task's `branch:` field.
4. **Tests must pass.** If the project has tests, run them. Red means: do not
   push code, write down what broke, set the task to `blocked`.
5. **Stop at three open overnight PRs.** Review debt compounds. At the limit,
   skip building and spend the night sharpening `inbox` tasks instead.
6. **Never touch credentials, deploys or anything that costs money.**
7. **Leave a trail.** Every night writes to `planning/night-log.md`: what it
   did, what it refused to do, and why.
8. **No subagents? Play both roles yourself.** Routine-fired sessions may lack
   the Agent/Task tool (seen on 2026-08-08) — check at the start. If delegation
   works, use the builder and checker agents as designed. If not: build first,
   then, as a separate step, adversarially check your own diff against the
   task's `## Done means` as if someone else wrote it and you must prove it is
   *not* done. Never push a build that skipped the check, and note in the
   night-log that the check ran inline.
9. **Trail before work, not after.** Set the task to `doing` and write the
   night-log's opening block BEFORE the first expensive step, and commit to
   the night branch after every self-contained step. A usage-limit cutoff
   (5-hour or weekly) kills the session mid-run with no warning and no
   notification — whatever is uncommitted at that moment is gone. Small
   commits are the only recovery mechanism that survives it.
10. **Never leave `doing` behind.** A task found `doing` at the start of a run,
    with no session actually on it, is the residue of a cut-off run: set it
    back to `ready` (or `blocked`, with whatever the night-log and branch
    show), note the reset in the night-log, and only then pick work.

    Careful: a task can also be `doing` because a session Ollie is running
    right now is on it. `planning/now.md` says which, and so does the branch —
    if it has commits from today and its PR is open, someone is on it. Reset
    only what is genuinely residue.
11. **On limit pressure, downgrade.** If a usage-limit error appears mid-run,
    stop building immediately: commit what exists, set the task's status
    honestly, write the night-log line, exit. And know that a firing skipped
    because the account was already at its limit is simply gone — runs are
    not queued or made up. Background and limits: see
    `reference/nightrun-usage-limits.md`.

If a task turns out to be bigger or vaguer than it looked, stop and rewrite it
as two smaller `ready` tasks. Half-finished code is worse than none.

## What is not a night-run rule

These bind every session, including this one, because they are about the Hangar
being correct rather than about being unattended. They live in `CLAUDE.md`:

- Never invent status, dates or progress.
- Rebuild the dashboard after every content change.
- Capture what Ollie says into `tasks/` immediately.
- Decisions are append-only.
- The guard (`scripts/guard.py`) — which is a wall, not a rule, and fires for
  everyone whether or not they read anything.
