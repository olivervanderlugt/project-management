---
title: Workout Timer
description: A zero-dependency interval timer — EMOM, Tabata, AMRAP and three more modes, drift-free off the wall clock, runs offline from a local file.
status: active
next: Run a real 1s-on/1s-off set and check the cues on your own phone
due:
started: 2026-08-07
repo: olivervanderlugt/timer-workout
preview: https://olivervanderlugt.github.io/timer-workout/
stack: vanilla HTML/CSS/JS, static, GitHub Pages
tags: tool, fitness
---

## What this is

A zero-dependency interval-training timer that runs entirely in the browser —
as a hosted site or straight from a local `index.html`, no build step, no
server. Six modes (EMOM, Intervals, Tabata, AMRAP, Timer, Stopwatch with
laps), custom presets in browser storage, drift-free timing off the wall
clock, synthesized audio cues with multiple sound packs, four themes,
fullscreen and keyboard shortcuts.

## Where it stands

Built and shipped on 2026-08-07: six commits from scaffold to QA polish, unit
tests and an audio benchmark under `test/`, and three green `pages build and
deployment` runs — the Pages deploy at the `preview:` URL is live. Works
offline as a plain file; only screen wake lock needs the HTTPS copy.

On 2026-08-08 Ollie reported sound failing on laptop and mobile. Cause: cues
were queued one segment at a time off a 250ms interval, which browsers throttle
in a background tab and freeze on a locked phone, so everything after the first
backgrounded segment landed in the past and was dropped. Mobile also never
resumed the suspended AudioContext. PR #1 queues the whole run on the Web Audio
clock up front, re-unlocks and re-queues on `visibilitychange`, and opts out of
the iOS silent switch via `navigator.audioSession`. It also added an interval
beep to Timer mode. Merged to `main` on 2026-08-08.

On 2026-10-04 Ollie's physiotherapist prescribed 5s on / 5s off with the working
seconds going up about a second a week — not expressible, because every duration
stepper moved in fixed 5s jumps and work/rest/interval had a hard floor of 5s.
PR #2 makes each stepper row four buttons, `−− − value + ++`: the inner pair
moves by 1, the outer pair lands on the adjacent multiple of the field's grid
(15s for seconds, 5 for minutes and rounds), and the seconds floor drops to 1.
`BIG_SNAP` in `modes.js` is the single knob — set a type's entry to 0 and its
big press becomes a plain fixed step, which is the whole revert if the snap ever
feels wrong in the hand.

That unlocked a latent audio bug, found before it could bite: `scheduleSegmentAudio`
queued countdown beeps at end−3s/−2s/−1s unconditionally, and on a 1s segment the
−3s and −2s beeps fall before the segment begins. Since PR #1 pre-queues the whole
run they were no longer harmlessly dropped as past — they were real cues piling onto
the previous boundary, which would have made 1s-on/1s-off one unbroken buzz.
`countdownLeadsFor` now keeps only the beeps that fall strictly inside a segment, so
a 1s stretch is marked by its boundary tone alone. Tests went 34 → 49.

PR #2 shipped green and the origin served the new code, but the change was invisible
on Ollie's phone: Pages serves unversioned assets with `cache-control: max-age=600`
behind a shared CDN, so Safari revalidated `index.html` and reused the cached JS —
and since every change lives in JS and CSS, the page rendered byte-identical to the
old app. A private tab proved it. PR #3 puts `?v=<date>` on all 17 assets, verified
to still work from `file://`. The version is bumped by hand (`sed` one-liner in the
README under "Deploying"); forget it and a future deploy silently will not reach
anyone who has visited before. This is the one sanctioned exception to `index.html`
being frozen.

All three PRs are on `main` and live. The four-button stepper is confirmed working
on Ollie's phone. Still unverified on real hardware: the audio itself — the PR #1
background/lock fix, and now the 1s cue behaviour.
