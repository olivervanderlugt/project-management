---
title: Crewline: skelet dat deployt — auth, multi-tenancy, RLS en CI
project: crew-management-system
status: inbox
added: 2026-08-11
effort: M
branch:
---

## Done means

The repo has `CLAUDE.md` from `reference/crewline-kickoff-pack.md` committed as its first
commit, and on top of that a deployable skeleton with no business features:

- A pnpm monorepo matching the repo map in `CLAUDE.md`. Next.js App Router + TypeScript +
  Tailwind in `/apps/web`, Vitest configured in `/packages/domain`.
- Supabase local dev + Drizzle, first migration with exactly two tables, both with a
  non-null `tenant_id` and RLS enabled: `tenants` (name, kvk, btw_number, iban, plan) and
  `users` (auth_id, email, phone, role, tenant_id).
- RLS policies as plain SQL in `/supabase`, tenant id coming from a JWT custom claim set by
  a Supabase custom access token hook. The hook and each policy are explained in plain
  English — what it allows, what it denies.
- `requireTenant()` and `requireRole()` exist, and one example protected route uses them.
- An integration test proves two things: an unauthenticated request gets 401, and a user in
  tenant A querying tenant B's data gets **zero rows, not an error**.
- GitHub Actions CI runs typecheck, lint, unit tests, and a schema-drift check (generate
  migrations against a throwaway DB, fail if the diff is non-empty). CI green.
- `/docs/DECISIONS.md` exists and records every architectural decision made here, one line
  of rationale each.

## Notes

Blocked by `crewline-startgate`. Do not build while that is open.

Anything needing a secret or an account Ollie has to create is a **stop and report**, never
a placeholder that silently breaks later. Expect at least a Supabase project.

Prompt, verbatim from the kickoff pack:

````
Read CLAUDE.md first. Then set up the foundation for this project.

Goal for this session: a deployable skeleton with working auth, multi-tenancy and CI.
No business features yet.

Do these in order, pausing after each for me to confirm:

1. Scaffold a pnpm monorepo matching the repo map in CLAUDE.md. Next.js App Router +
   TypeScript + Tailwind in /apps/web. Vitest configured in /packages/domain.

2. Set up Supabase (local dev via the CLI) and Drizzle. Create the first migration with
   exactly these tables, all with tenant_id, all with RLS enabled:
   - tenants (name, kvk, btw_number, iban, plan)
   - users (auth_id, email, phone, role, tenant_id)
   - Write RLS policies in /supabase as plain SQL. Tenant id comes from a JWT custom claim
     set by a Supabase custom access token hook. Show me the hook and the policies and
     explain in plain English what each policy allows and denies.

3. Build requireTenant() and requireRole() helpers and a single example protected route
   that uses them. Then write an integration test that proves:
   - an unauthenticated request gets 401
   - a user in tenant A querying tenant B's data gets zero rows (not an error — zero rows)

4. Set up GitHub Actions CI that runs: typecheck, lint, unit tests, and a schema-drift check
   (generate migrations against a throwaway DB and fail if the diff is non-empty).

5. Add a /docs/DECISIONS.md and record every architectural decision you made above with a
   one-line rationale. Keep appending to this file for the rest of the project.

Constraints:
- Explain your choices as you go — I'm learning this stack, not just shipping it.
- If any step needs a secret or an account I have to create, stop and tell me exactly what
  to do rather than inventing a placeholder that silently breaks later.
````

The "pause after each step for me to confirm" instruction is written for an interactive
session. An overnight run cannot pause — so it does the five steps in order, commits after
each, and writes anything it would have asked into the PR description.
