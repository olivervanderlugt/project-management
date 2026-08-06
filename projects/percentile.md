---
title: Percentile
status: active
next:
due:
started:
repo: olivervanderlugt/percentile
stack: TypeScript, Node 22, SDK + API + MCP server
tags: startup, analytics, mcp
---

## What this is

Consent-first analytics and a benchmark data network for apps built by AI. One line of SDK
in the page; the coding agent reads the metrics back through MCP; apps that opt in earn a
share of the revenue from the anonymous benchmark datasets they help create.

The pitch it makes: millions of people now ship apps whose code they cannot read, and have
no idea whether 14% activation is good or terrible. Percentile answers that by aggregating
across the network.

## Where it stands

Imported 2026-08-06, updated the same day: it now has its own repo, split out of
`claude` as `scripts/split-out-repo.sh` intended. It also picked up its own
`CLAUDE.md` so sessions inherit the invariants instead of re-deriving them.

Source is split across `src/api`, `src/core`, `src/sdk` and `src/mcp`. Tests
cover privacy, consent durability, adversarial cases, special-category data,
rollup and pipeline.

An earlier commit in the old location recorded a red-team re-audit: finding F-1
confirmed fixed, and two of the fixes made things worse.

## Open questions

- Those two regressions from the re-audit — still open? This is the obvious candidate for
  `next`, but it's your call to set it.
- This is the one project with a revenue model in it. Per decision 0001, that makes it the
  project that would justify a real app.
