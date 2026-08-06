---
title: Never trigger a workflow or deploy, not even to verify
scope: builders
goal: veiliger, goedkoper
source: night-log 2026-08-06 / learn-live-preview
added: 2026-08-06
status: active
---

## Rule

Never trigger a workflow or a deploy — no `workflow_dispatch`, no `actions_run_trigger`, no Pages or hosting API calls — not even to verify a change works. Verification stops at local and on your own branch. A finish line outside your reach is a `false` with evidence, not a reason to reach further.
