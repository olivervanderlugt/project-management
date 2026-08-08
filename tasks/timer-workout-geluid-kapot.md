---
title: Sound cuts out on laptop and mobile in the workout timer
project: timer-workout
status: inbox
added: 2026-08-08
effort: M
branch:
---

## Done means

Draft (confirm symptom with Ollie before promoting to ready):

1. With the phone screen locked or the app backgrounded mid-workout and then
   reopened, cues play again without touching pause — AudioContext is resumed
   on visibilitychange/focus and the current segment is rescheduled.
2. On a laptop, cues keep firing for every segment while the tab is
   backgrounded — the full remaining schedule is queued in Web Audio up front
   (immune to timer throttling), and cancel/reschedule on pause, skip, stop.
3. On iPhone with the silent switch on, cues are audible
   (`navigator.audioSession.type = 'playback'` where available) or the UI
   says clearly why not.
4. Existing tests green; a new harness check covers reschedule-after-resume.

## Notes

Diagnosis 2026-08-08 (code read, not yet reproduced on device):

- Audio is scheduled one segment at a time: `segmentStart` comes from a 250ms
  `setInterval` in `engine.js:115`, and only then does `scheduleSegmentAudio`
  queue that segment's 3 countdown beeps + boundary tone.
- **Laptop, backgrounded tab:** browsers throttle timers to ~1/min. The
  already-queued segment still sounds, but the next `segmentStart` fires
  late and `scheduleCue` skips notes in the past (`audio.js:192`) — sound
  dies from the next segment on.
- **Mobile, screen lock / app switch:** the OS suspends the AudioContext
  ('interrupted' on iOS). Nothing resumes it: `system.js`'s visibilitychange
  handler only re-acquires the wake lock, and the one-shot `pointerdown`
  unlock in `app.js:92` has already removed itself. Cues stay silent until
  pause/resume happens to call `playNow` (which resumes as a side effect).
  Also: while suspended, `ctx.currentTime` freezes but `performance.now()`
  runs on, so `perfToCtx` (`audio.js:197`) mappings made during suspension
  land in the past → skipped.
- **iPhone silent switch** mutes Web Audio entirely; code does nothing about
  it (no audioSession hint, no muted `<audio>` keepalive).
