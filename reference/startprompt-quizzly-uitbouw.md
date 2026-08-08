# Startprompt: Quizzly uitbouw (2026-08-08)

Voor een verse Claude Code (Fable 5) terminal in de quizzly-repo. Gemaakt op
Ollie's verzoek; dekt zijn wensen van 2026-08-08 plus verkenning. Plak alles
onder de streep als eerste bericht.

---

Work on Quizzly, the live quiz platform in this repo
(github.com/olivervanderlugt/quizzly). Read CLAUDE.md and docs/ARCHITECTURE.md
before writing any code, and treat every invariant in CLAUDE.md as hard:
players never receive correct answers before the reveal; src/lib/collab.ts is
the only read path for group-quiz questions; live games run from
Game.quizSnapshot, never the live quiz row; app chrome and the themed quiz
surface (`--q-*` variables from themeToCssVars()) are two separate colour
systems that must not mix.

First, establish the state of the repo:

1. Check PR #1 (branch claude/quizzly-finalization — password reset, GDPR
   export, age gate, e2e suite, fly.toml, launch checklist). If it is merged,
   build on main. If it is still open, branch from main, do not duplicate any
   of its work, avoid rewriting the files it touches where you can, and list
   the overlaps in your final report instead of resolving them silently.
2. Run `npm run typecheck && npm test && npm run build` before you start and
   before every commit — CI runs exactly that trio.

Then work through five phases, in this order. Ship each phase as its own
commit(s) and push before starting the next.

Phase 1 — password visibility toggle (quick win, ship first). Every password
field in the app (login, signup, and any change-password or reset fields that
exist by the time you start) gets a show/hide toggle: hidden by default,
keyboard operable, `aria-pressed` plus a clear label, no autocomplete or
password-manager regressions.

Phase 2 — real image uploads for slides. Today a question's presentation
already carries an image URL with required alt text and three image layouts
(mediaTop, mediaSplit, banner — see presentationSchema in src/lib/theme.ts);
only uploading is missing. Build a self-hosted upload path that fits the
single-container deploy: quiz-owner-only endpoint, size cap around 5 MB, file
type verified by magic bytes rather than extension, EXIF stripped, files
stored in a Docker volume outside the repo tree and served same-origin. Keep
the URL option working, wire uploads into the question editor with a preview,
and add the unused cover-image field for quizzes while you are there. Add the
volume to docker-compose.yml and document the limits in the README. Validate
every input with Zod at the boundary, as the codebase already does everywhere.

Phase 3 — design pass on the app chrome, as a design expert. Goal: lighter and
friendlier than the current very dark chrome. Write the direction down first
in DESIGN.md — palette tokens, type scale, spacing, and the reasoning — then
apply it consistently across every page. Hard constraints: touch only app
chrome, never the quiz surface (all ten built-in themes must render exactly as
before); keep 44px touch targets, visible focus states, and WCAG AA contrast.

Phase 4 — explore the slide designer, build only its first slice. The vision:
editing a quiz should feel like designing slides — a live interactive slide
preview while editing, per-question design overrides, emoji, GIFs, stickers,
per-slide backgrounds, sounds and music. Do not build the vision. Produce
docs/SLIDE-DESIGNER.md containing: the full brainstormed possibility space
(add your own ideas — transitions, sound effects on correct/wrong answers,
music per round, a host soundboard, an emoji picker, GIPHY/Tenor integration);
a feasibility verdict per item against this codebase (what presentationSchema,
the theme system and the GameRoom snapshot already carry, what needs schema
migrations, what needs new asset infrastructure, and what has licensing or
privacy strings attached — flag those, do not decide them); and a phased
roadmap where every phase is independently shippable and phase one is small
enough for a single session. Then build phase one.

Phase 5 — compliance review for western markets. Review the privacy and terms
pages, SECURITY.md, docs/LEGAL.md, and the actual data flows in the code —
verify against the code, not the docs, since recent work may already cover
parts (data export, age gate, retention). Test against: EU GDPR including
children and consent, UK GDPR, US COPPA and CCPA/CPRA, Canada PIPEDA, and the
Australian Privacy Act. Deliver docs/COMPLIANCE-REVIEW.md listing, per item:
already handled, missing, or needs a decision from Ollie (contact details,
hosting region, minimum age), each marked must/should/could. State plainly in
the document that this is an engineering compliance review, not legal advice,
and mark anything that needs a professional before commercial use — including
the patent-litigation risk docs/LEGAL.md already flags.

Working rules: develop everything on one branch named claude/quizzly-uitbouw,
one feature per commit with messages that still make sense in a year, push
after every phase. Never merge to main yourself — report and wait for Ollie to
say "merge". Never add a paid service, an external API dependency, or any
telemetry without asking first. If you change the wire contract in
src/types/realtime.ts, update client and server in the same commit. End with a
report in plain language: what shipped, what is proposed in the two new docs,
and the shortlist of decisions only Ollie can make.
