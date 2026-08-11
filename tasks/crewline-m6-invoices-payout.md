---
title: Crewline M6: facturen, creditnota's en één payroll-export
project: crew-management-system
status: inbox
added: 2026-08-11
effort: L
branch:
---

## Done means

Invoicing and payroll export work:

- An Invoice moves DRAFT → REVIEWED → SENT. Once SENT it is immutable; a correction is a
  credit note, never a mutation of a sent invoice or its lines.
- Invoice numbers are sequential **per tenant** with no gaps, proven by a test that creates
  invoices concurrently.
- PDF generation runs in a Trigger.dev job, not a Vercel function.
- A reconciliation report: for a given period, total approved timesheet hours equals total
  invoiced hours — and when it does not, it names exactly which assignments are unaccounted for.
- Payout export: one clean internal `PayoutLine` model plus **one** exporter, matching the exact
  format the first customer's payroll system needs. Not a plugin system, not two exporters.
- Tests green.

## Notes

Blocked by `crewline-startgate` through `crewline-m5-rates-hours`.

**Open question that must be answered before this goes `ready`:** which payroll system does the
first customer use? The prompt says "Ask me which system it is before you start", and an export
format is not something to guess — a wrong format is silently wrong until someone's wages are
late. Write the answer in this file's Notes, then promote.

Prompt, verbatim from the kickoff pack:

````
Read CLAUDE.md.

Build invoicing and payroll export.

Requirements:
- An Invoice is DRAFT → REVIEWED → SENT. Once SENT it is immutable. Corrections happen via a
  credit note, never by mutating a sent invoice or its lines.
- Invoice numbers are sequential PER TENANT with no gaps. Prove this with a test that creates
  invoices concurrently.
- PDF generation runs in a Trigger.dev job, not a Vercel function.
- A reconciliation report: for a given period, total approved timesheet hours must equal total
  invoiced hours. If they don't, show me exactly which assignments are unaccounted for.
- Payout export: one clean internal PayoutLine model, then ONE exporter matching the exact
  format my first customer's payroll system needs. Do not build multiple exporters.
  Ask me which system it is before you start.
````
