---
title: Generate the weekly review from what actually changed
project: hangar
status: doing
added: 2026-08-06
effort: M
branch: claude/hangar-project-setup-w61m5q
---

## Done means

A script reads the commit history of every repo listed in a project's `repo:`
field since the last weekly file, and writes `planning/weekly/YYYY-Www.md` with
Wins filled in from real commits. Slips and Next week stay empty for Ollie.

Running it twice for the same week does not produce two files or duplicate
lines.

## Notes

`git log --since` per repo against the shallow clones is enough; no need for
full history. Repos with no commits that week are skipped rather than listed as
empty.

Never invent a win. If a week has no commits anywhere, the file says so.
