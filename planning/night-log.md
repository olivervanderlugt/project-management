# Night log

What the overnight run did, newest first. One short entry per night: the task,
the outcome, and anything it refused to do and why.

This exists so Ollie can see what happened while he slept without opening five
pull requests to find out.

---

## 2026-08-07 — first run produced nothing (fixed)

- The nachtrun fired at 00:04 UTC but its Routine had **no repository attached**:
  the session woke up in an empty VM with no clone of the Hangar and no push
  credentials. Nothing reached GitHub — no commits, no branch, no PR, and this
  log stayed empty. Its prompt also targeted `claude/hangar-project-setup-kvhcad`,
  which is the repo's default branch and another session's working branch.
- Ruled out: the guard and autosave hooks. All guard tests pass and every
  command a nightrun would use is allowed.
- Fix, same day: the Routine now fires into a dedicated persistent session
  ("Hangar — nachtrun (vaste sessie)") with the repo attached and its own
  outcome branch `claude/nightrun`; a live check confirmed it can push. The
  broken trigger was disabled, not deleted. Project repos get attached at run
  time via `add_repo`; if that fails during a run, the task goes to `blocked`
  instead of being built.
