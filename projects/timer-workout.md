---
title: Workout Timer
status: shipped
next:
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
