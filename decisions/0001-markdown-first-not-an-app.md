---
title: Markdown first, a real app only if a project starts earning
status: accepted
date: 2026-08-06
---

## Context

The Hangar could have been a proper web app — Next.js, a database, auth, task
CRUD. That is the most capable version and the one most likely to be abandoned
half-built, because it needs maintenance before it delivers anything.

The competing option was plain markdown in a git repo with a generated
dashboard: less capable, useful on day one, and readable from anywhere without
running a server.

## Decision

Markdown is the source of truth. The dashboard is a generated, self-contained
HTML file with no dependencies and no build toolchain.

A real web app is deferred until one of the projects in here produces actual
revenue — and preferably profit. Revenue is the trigger, not enthusiasm.

## Consequences

Easy: starting, editing from any device, working on it with Claude, keeping it
alive for years, moving it somewhere else later. Nothing to deploy or pay for.

Hard: no multi-user access, no notifications, no mobile write UI beyond the
GitHub app, and no querying beyond what `build.py` computes. The dashboard has
to be rebuilt after edits rather than updating itself.

Migration path stays open: flat frontmatter parses trivially into rows, so the
markdown becomes the seed data for an app rather than something to throw away.
