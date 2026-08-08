---
title: Sound cuts out on laptop and mobile in the workout timer
project: timer-workout
status: done
added: 2026-08-08
effort: M
branch: claude/audio-background-and-silent-switch
---

## Done means

1. Screen locked or app backgrounded mid-workout, then reopened: cues play
   again without touching pause. ✅ AudioContext is resumed on
   `visibilitychange` and the run is re-queued.
2. Backgrounded laptop tab: cues keep firing for every segment. ✅ The whole
   remaining run is queued on the Web Audio clock up front, immune to timer
   throttling, with cancel/re-queue on pause, resume and skip.
3. iPhone silent switch: `navigator.audioSession.type = 'playback'` where
   available, a toast explaining it where not. ✅
4. Tests green, plus new coverage for the reschedule math. ✅ 34/34 unit tests,
   and four browser suites driving the real app.

## Notes

Diagnosis 2026-08-08, confirmed by instrumenting the AudioContext in Chromium
and comparing the fixed build against the pristine one:

- **Before:** a 4-minute Tabata queued 4 oscillator nodes reaching 7s ahead —
  only the prep segment. Returning to a visible tab changed nothing.
- **After:** the same run queues 66 nodes reaching 237s ahead, and re-queues
  on return to visible.

Cause was queueing one segment at a time on each engine `segmentStart`, which
comes off a 250ms `setInterval`. Browsers throttle that to ~1/min in a
background tab and freeze it entirely on a locked phone, so the late event
scheduled cues that were already in the past, where `scheduleCue` drops them.
Mobile additionally never resumed the suspended context: the one-shot
`pointerdown` unlock in `app.js` had already removed itself.

A 15-minute horizon bounds the node count on long runs, topped up additively
so a top-up landing on a boundary never clips that boundary's tone.
