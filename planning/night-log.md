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
- Fix, same day: first patched via a dedicated persistent session with the repo
  attached (a live check confirmed it could push to `claude/nightrun`), then
  replaced by the real thing: Ollie recreated the Routine in the claude.ai UI
  with all seven repos attached, so every run clones them with push access —
  no runtime repo-attaching, no standing session. The temporary trigger and
  session were removed, the broken trigger deleted. Next run: tonight 00:04 UTC.
