# Percentile — why would anyone use it?

Written 2026-08-08, after checking the current market rather than the market
`docs/05-competitive-landscape.md` was written against. It contains a finding that
undercuts decision 0004's plan, so read it before building the MVP.

## The differentiator is gone

The narrowed product's entire pitch was: *analytics whose primary interface is your
coding agent*. `docs/06-go-to-market.md` calls agent-native distribution "the
differentiated one" and "the one competitors are already moving on".

They finished moving. As of Q1 2026, **ten major analytics vendors ship official MCP
servers** — PostHog, Amplitude, Mixpanel, Heap, Pendo, FullStory, LogRocket, Statsig
and GA4 among them. PostHog's connects Claude Code, Cursor and Windsurf to trends,
funnels, retention and raw query access, and PostHog is free at small scale and
mature in every direction Percentile is not.

So the honest position: **"ask your agent about your metrics" is now a checkbox
feature on products that are free, established and far more complete.** That was the
one real advantage the narrowed product had. It no longer differentiates.

This is not a reason to stop. It is a reason to stop selling analytics.

## What is actually left, ranked honestly

**1. Consent and privacy done for you — the only real gap.**
PostHog and the rest hand you tools and leave compliance to you. They assume a
competent team that knows it needs a consent banner, a lawful basis, a deletion
path and a record of who agreed to what. The person shipping a Lovable app has none
of that knowledge and does not know they need it. Percentile already has the consent
ledger, epoch-independent withdrawal, redaction, special-category detection and GPC
handling built and tested — the work that looked like over-engineering for an
analytics tool is a whole product if sold as compliance.

**2. The PII leak scanner.** Genuinely useful to a total stranger, about their own
app, and it produces the moment where someone discovers they have a problem. Nothing
else in the project acquires users on its own.

**3. Zero-decision setup.** Auto-capture with no event taxonomy to design. Real, but
PostHog has autocapture too, so it is a nicety and not a reason to switch.

**4. The benchmark network.** Cut in decision 0004, and correctly — but note it was
the only thing on this list that no competitor could copy quickly, because it needs
density they would also have to build.

## The reframe this points at

Not "analytics for AI-built apps" — that market has free, mature incumbents with the
same agent integration.

**"Make your AI-built app legally shippable."** Consent banner, consent ledger,
deletion and export requests, PII leak detection, and the analytics that fall out of
having the pipeline anyway. The pain is real and unserved: apps built by people who
cannot read their own code are shipping to EU users with no consent mechanism at all,
and neither Lovable nor Bolt nor PostHog solves that for them.

Why this fits better than the analytics framing:
- It sells what is already built, rather than what still needs building.
- The competitors are consent-banner vendors (Cookiebot, Osano, Iubenda), who charge
  real money, target companies with legal departments, and offer nothing for someone
  who does not know what a data controller is.
- It converts from the leak scanner naturally: *your app is leaking user emails →
  here is what else you are missing → one line fixes it.*
- Compliance is a grudge purchase, which is a worse sale than a desire purchase but a
  much stickier one.

Honest counterweight: a grudge purchase nobody knows they need is the hardest sale
there is. Most hobbyists will never be asked about GDPR and will not pay to prevent
something they cannot imagine happening. The realistic buyer is the narrower group
whose AI-built app got real traction and now has real users in the EU.

## What that means for the MVP

Nothing in `reference/percentile-mvp-prompt.md` is wasted — storage, signup, keys,
deploy and the scanner are needed under either framing. Two changes if the reframe is
accepted:

- Promote the PII scanner from phase 6 to first. It is the wedge under either
  framing and it is the only piece that works standalone.
- Add a drop-in consent banner to the SDK, and self-service deletion and export
  endpoints. Neither is large; both are the product under the reframe rather than
  supporting detail.

## The uncomfortable summary

Under the analytics framing, the answer to "why would anyone use this" is *they
probably wouldn't* — PostHog is free, more capable, and now has the same agent
integration. Under the compliance framing there is a real gap, but it is a harder
sale to a smaller audience.

The third option is legitimate and should be said out loud: keep Percentile as the
best thing in the portfolio and stop trying to make it a company. The red-team
privacy audit is stronger work than most funded startups produce, and it does not
need customers to be worth having done.

## Sources

- [PostHog MCP Server](http://mcp.posthog.com/)
- [PostHog — MCP analytics docs](https://posthog.com/docs/mcp-analytics)
- [PostHog — build insights with MCP](https://posthog.com/docs/product-analytics/build-insights-mcp)
- [Product analytics MCP server comparison, May 2026](https://productleadersdayindia.org/blogs/ai-product-analytics-agent-signals/product-analytics-mcp-server-comparison.html)
