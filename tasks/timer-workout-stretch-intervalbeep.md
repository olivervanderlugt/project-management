---
title: Interval beep toggle for the stretch/long timer — beep every 30 or 60s
project: timer-workout
status: done
added: 2026-08-08
effort: M
branch: claude/audio-background-and-silent-switch
---

## Done means

1. Timer mode has a toggle, off by default. ✅
2. When on, a period is chosen (default 60s, adjustable 5–600s in 5s steps)
   and a cue lands on every boundary for the whole duration. ✅ Verified in
   Chromium: a 15-minute run fires boundary tones exactly 60s apart, each with
   three countdown beeps ahead of it.
3. Total duration unchanged; a remainder is its own short final stretch. ✅
   Covered by unit tests including 5 min ÷ 90s → 3 × 90s + 30s.
4. The run screen shows "INTERVAL 3/15". ✅
5. Saved with a preset and restored with it. ✅
6. Existing modes and tests untouched and green. ✅ 34/34.

## Notes

Asked for on 2026-08-08: "a beep like every 30 or 60 seconds for switching
stretching pose … I want a long one with many intervals, but not need to add
every interval manually."

The interval count is derived from duration ÷ period, never entered. Two
generic additions carry the UI: a `toggle` field type and `showWhen` on a
field descriptor, so the period row stays hidden until the beep is on — both
in the generic form builder, no mode hardcoded in the UI.
