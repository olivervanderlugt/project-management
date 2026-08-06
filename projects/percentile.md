---
title: Percentile
status: active
next:
due:
started:
repo: olivervanderlugt/claude
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

Imported from the repo on 2026-08-06.

Lives inside the `claude` repo under `percentile/`, not in its own repo — though
`scripts/split-out-repo.sh` exists, so splitting it out was already the plan. Source is
split across `src/api`, `src/core`, `src/sdk` and `src/mcp`. Tests cover privacy, consent
durability, adversarial cases, special-category data, rollup and pipeline. CI runs from
`.github/workflows/percentile-ci.yml`.

Last commit, 2026-08-06: a red-team re-audit recording that finding F-1 is confirmed fixed
and that two of the fixes made things worse.

## Open questions

- Those two regressions from the re-audit — still open? This is the obvious candidate for
  `next`, but it's your call to set it.
- Split `percentile/` out into its own repo, or leave it nested?
- This is the one project with a revenue model in it. Per decision 0001, that makes it the
  project that would justify a real app.
