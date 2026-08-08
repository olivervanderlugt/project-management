---
title: Workout Timer
status: active
next: Test the audio fix on Ollie's phone and laptop, then merge claude/audio-background-and-silent-switch
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
were queued one segment at a time off a 250ms interval, which browsers
throttle in a background tab and freeze on a locked phone, so everything after
the first backgrounded segment landed in the past and was dropped. Mobile also
never resumed the suspended AudioContext. Branch
`claude/audio-background-and-silent-switch` queues the whole run on the Web
Audio clock up front, re-unlocks and re-queues on `visibilitychange`, and opts
out of the iOS silent switch via `navigator.audioSession`. The same branch
adds an interval beep to Timer mode — a toggle plus a period, for stretching
sessions that need a cue every 30 or 60 seconds without entering each interval
by hand. 34 unit tests plus four browser suites green; not yet tried on
Ollie's own devices.
