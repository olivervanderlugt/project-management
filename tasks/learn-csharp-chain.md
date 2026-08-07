---
title: Learn — build the C#/.NET chain (Phase-5 Tier 2)
project: learning-website
status: doing
added: 2026-08-07
effort: M
branch: night/learn-csharp-chain
---

## Done means

Three new nodes `prog-csharp` → `prog-csharp-2` → `prog-csharp-3` extend the
existing `programming` domain (no new domain, no new subject) following the
python chain's local-toolchain pattern (no `code` screens — C# does not run in
the JS worker). Skills `csharp`, `dotnet`, `methods` flip gap → covered, so the
🎯 coverage becomes 22 covered / 6 partial / 18 gap of 46. `prog-exam` grows ~4
fresh questions and its prereqs include the new nodes. Every quoted command and
program output is executed against a real dotnet SDK. Gate green: `npm run
build` clean, content validator green on all 136 lessons, map checker zero
crossings in BOTH view tiers, one new lesson browser-played end-to-end. Branch
`night/learn-csharp-chain` pushed with a PR; nothing merged to `main` without
Ollie.

## Notes

Chosen 2026-08-07: Ollie asked for "the next chain"; the repo's CLAUDE.md and
`projects/learning-website.md` both name C#/.NET as the smallest, cleanest next
item ahead of OOP+Java, data & BI and db-depth. Spec: repo
`docs/employability-skills-coverage.md` §2 course 3 (freeCodeCamp Foundational
C# with Microsoft) and §7 item 3. Built per the standing orchestration
instructions (Opus builds, Fable gate-verifies). dotnet SDK installed via
Homebrew on Ollie's Mac for output verification.
