---
title: Priority board double-escapes the empty-effort placeholder
project: hangar
status: doing
added: 2026-08-10
effort: S
branch: night/hangar-priority-effort-escaping
---

## Done means

`dashboard/build.py`'s `render_priority`, priority-table effort column
(currently line 757): a task with no `effort:` renders the plain entity
`&mdash;` (an em dash on the page), never the literal text `&amp;mdash;`.
Fix the same way the slug/project cell one line above already does it —
`escape()` only the real value, not the hardcoded fallback entity, e.g.
`escape(eff) if eff else "&mdash;"` instead of
`escape(meta.get("effort", "") or "&mdash;")`. Add a case to
`scripts/test_priority.py` (or wherever fits how that file is already
organised) that renders a task with a blank/missing `effort:` and asserts
the output contains `&mdash;` and not `&amp;mdash;`. `python3
dashboard/build.py` still builds clean and `scripts/test_priority.py` still
passes.

## Notes

Found by the `hangar-checker` while reviewing `hangar-prioriteit-score`
(2026-08-10 night run), not by Ollie — capturing it rather than fixing it
inline to keep that task's diff scoped, sharpened straight to `ready` the
same night once the exact line and fix were already known from the check.

Latent today: every open task in `tasks/` currently has an `effort:` value,
so nothing on the live board shows it. It will surface the first time a task
is captured without one.
