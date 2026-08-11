# Crewline — kickoff pack

Standing documents for the crew management system (`olivervanderlugt/crew-management-system`).
Written in a Cowork chat, captured here 2026-08-11. Two things live here because they are
*reused every session*, not once: the repo's `CLAUDE.md` and the hostile-review prompt.

The milestone prompts themselves sit in `tasks/crewline-*.md`, one per task, verbatim in the
`## Notes` of each. Nothing here is a task — this is the material the tasks reference.

**Working name.** "Crewline" is a placeholder. The pack says to change it everywhere before
starting. Until Ollie picks a name, the slug prefix `crewline-` is just a handle.

**Gate.** Nothing in this pack starts before §3 and §8 of the strategy brief are answered:
the Clevergig invoice seen, IP/contract sorted. See `tasks/crewline-startgate.md`.

---

## Part 1 — `CLAUDE.md` for the Crewline repo

Drop in the repo root, commit first, before any code.

````markdown
# Crewline — crew management for Dutch flex event crew agencies

## What this is
Multi-tenant SaaS replacing Clevergig for event crew staffing agencies in the Netherlands.
First customer: ~300 flex workers, ~5 planners, peak load on festival weekends.
Built by one non-professional developer with Claude Code. Optimise for code I can read,
not code that is clever.

## Roles
- **planner** — agency staff. Creates projects, publishes shifts, approves hours, sends invoices.
- **crew** — flex worker. Sets availability, signs up for shifts, clocks in/out on a phone.
- **crew_chief** — crew member who leads a shift; confirms headcount on site, reports no-shows.
- **client_contact** — the customer (festival/venue). Read-only view of their crew list.
- **admin** — me. Platform-level access. Every admin action must be audit-logged.

## Domain language (use these exact words in code — never invent synonyms)
- **Project** = a production for one Client (e.g. "Lowlands 2027")
- **Job** = a phase of a Project: `build` | `show` | `strike` (or custom). Jobs belong to a Project.
- **Shift** = a dated block of work within a Job, with a `call_time`, a Role, and a headcount.
- **Role** = rigger, stagehand, forklift, host, crew chief, etc.
- **ShiftAssignment** = one crew member on one Shift. Has a lifecycle:
  `invited → applied → confirmed → (clocked_in → clocked_out) → approved`
  plus terminal states `declined`, `no_show`, `replaced`.
- **Timesheet** = actual hours for one ShiftAssignment.
- **RateCard** = client rate + crew rate per Role, effective-dated, optionally client-specific.
- **SurchargeRule** = a condition (night/weekend/holiday/overtime) → a multiplier or fixed amount.

## Hard rules — violating any of these is a bug, not a style choice

1. **Every table has a non-null `tenant_id`**, even while we have one customer. No exceptions.
2. **Every table has a Postgres RLS policy, added in the SAME pull request as the table.**
   Never rely on app-layer filtering alone.
3. **Background jobs and webhooks run outside a request's RLS context.** They must carry
   `tenant_id` explicitly and use scoped queries. This is the #1 place cross-tenant data leaks.
4. **All uniqueness constraints are scoped by tenant.** Invoice numbers are unique per tenant,
   not globally.
5. **All timestamps are `timestamptz` (UTC).** Never a naive date + time column. Shifts cross
   midnight and cross DST. Display conversion happens in the UI layer only.
6. **Money and rate logic lives in `/packages/domain` with zero framework dependencies.**
   Any change there requires a unit test in the same PR.
7. **Never hand-edit a migration that has been applied to staging or prod.** Create a new one.
8. **Every API route goes through the shared `requireTenant()` / `requireRole()` helpers.**
   No route reads `tenant_id` from user input.
9. **Deletion of personal data = anonymise the PII, keep the financial record.**
   Dutch law requires 7-year retention of wage/hours records. Never hard-delete a Timesheet.
10. **BSN is stored in a segregated, access-restricted column, used only for payroll export.**
    Never a key, never searchable, never rendered in the UI.
11. Files stay under ~300 lines. If one passes 400, split it before adding to it.
12. Run the tests before telling me a task is done. If they fail, say so — don't work around them.

## Dutch compliance constraints baked into the model
- A shift call-up must be logged with a timestamp; changes and withdrawals are appended, never overwritten.
- Warn (don't block) when a shift is published fewer than 4 days before its start.
- Arbeidstijdenwet guardrails when scheduling: max 12h per shift, max 60h per week,
  11h rest between shifts (8h once per 7 days). Warn the planner at plan time.
- Surcharge percentages are NEVER hardcoded. Since 1 Jan 2026 pay must be equivalent to the
  client's own employees, so rates are configured per client and versioned by date.
- For zzp'ers specifically: never auto-assign a shift, never force clock-in, never show a
  ranking/reliability score that gates future work, always allow nominating a substitute.
  These are legal constraints (schijnzelfstandigheid / Wet DBA), not product preferences.

## Stack
Next.js (App Router, TypeScript) · Supabase (Postgres + Auth + Storage + RLS) · Drizzle for
migrations · Trigger.dev for background jobs · Resend for email · Tailwind · Playwright for E2E ·
Vitest for unit · Sentry.

## Repo map
/apps/web            Next.js app — planner dashboard + crew PWA, role-based routes
/packages/db         Drizzle schema + migrations + shared types
/packages/domain     Pure business logic. No imports from next/react/supabase. Heavily tested.
/packages/ui         Shared components
/jobs                Trigger.dev tasks: reminders, cert-expiry alerts, PDF generation, exports
/supabase            RLS policies as SQL, seed scripts
/tests               unit / integration / e2e

## Commands
pnpm dev · pnpm test · pnpm test:e2e · pnpm db:generate · pnpm db:migrate · pnpm db:seed

## How to work with me
- Small diffs. One concern per change.
- Before a multi-file change, tell me the plan in 5 bullets and wait.
- If a requirement is ambiguous, ask. Do not guess at business rules — they have legal consequences.
- Write the test first from a plain-English description, show me the test, then implement.
  I may not be able to audit your implementation, but I can read the test.
````

---

## Standing instruction for review sessions

Paste this whenever Claude Code has written something touching money, RLS or background jobs.
For overnight runs this is the `hangar-checker` brief for any Crewline diff.

````
Review the changes in this PR as a hostile security and correctness reviewer.
You did not write this code. Assume it is wrong.

Check specifically:
1. Can any query in this diff return another tenant's data? Trace every query path,
   including background jobs, which run outside RLS context.
2. Is any money calculation done in more than one place? It must exist only in /packages/domain.
3. Are there tests for the failure cases, not just the happy path?
4. Does any new table lack a tenant_id or an RLS policy?
5. Is any timestamp stored as a naive date/time instead of timestamptz?

List findings most severe first. If you find nothing, say so plainly rather than inventing
minor issues.
````

## Order

`crewline-startgate` → `crewline-foundation` → M1 → M2 → M3 → M4 → M5 → M6 → M7.
The order is not decoration: each milestone assumes the previous one's schema and helpers exist.
