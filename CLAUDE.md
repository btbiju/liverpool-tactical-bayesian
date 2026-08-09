# Project context for Claude

This file is read automatically by Claude Code. It exists so a new session
has the reasoning behind this project, not just the files. Read this before
doing anything else, then check `BACKLOG.md` for current status.

## What this is

A portfolio project for a CS student applying to tech consulting / data / AI
roles (PwC-track). It's the "unique, memorable" project in a three-project
portfolio strategy -- the other two are a personal finance app (full-stack)
and a data migration risk analyzer (PwC-relevant). This one exists to show
technical curiosity and genuine analytical depth, not just CRUD competence.

**The core idea**: Liverpool FC has a new manager (Andoni Iraola, appointed
July 2026) with no track record at this specific club. Rather than building
another sports-stats dashboard, this project treats "how will this team
actually play" as a **Bayesian inference problem**:

- **Prior**: Iraola's tactical fingerprint from 3 seasons at Bournemouth,
  combined with each player's individual career playstyle data (weighted
  toward players' most recent role/club, since many players are recent
  signings with no Liverpool history).
- **Evidence**: real 2026/27 match results, pulled weekly.
- **Posterior**: belief updates automatically via conjugate priors as
  evidence accumulates -- the prior's influence provably shrinks with each
  match, no hand-tuned decay schedule required.

The point isn't "build a football app." It's "demonstrate reasoning under
uncertainty, cited data sourcing judgment, and a system that visibly
changes over time" -- a static repo screenshot can't show that; a live,
weekly-updating GitHub Pages dashboard can.

## How we got here (context that matters)

The project went through several real pivots, each for a documented reason
-- worth knowing so you don't re-litigate settled decisions:

1. **Started as historical analytics** (2015/16 StatsBomb data: passing
   networks, PPDA, xG maps). Built and working, but the user correctly
   pushed back: "what is there to predict if the games already happened?"
2. **Tried a player-career-aggregation approach** for a static current
   squad -- discovered mid-build that no free source has full recent-season
   event-level data (StatsBomb stops ~2015/16, Understat live blocks bots,
   FBref blocks bots). This is WHY the project doesn't do passing networks
   for the current squad.
3. **Landed on the Bayesian prior/posterior model** -- the user proposed
   this framing themselves ("piece together a puzzle... AI would be
   helping"). This turned the data limitation into the actual point of the
   project: since nobody has "chemistry data" for players who haven't
   played together, projecting from individual + manager priors and
   updating with evidence IS the right approach, not a workaround.
4. **Cut the original 2015/16 module** -- built, working, but has zero
   data-flow connection to the Bayesian model and dilutes the pitch. Moved
   to `archive/`, not deleted. Decision reasoning: a focused project beats
   two projects bolted together, and "I already built it" isn't a reason to
   ship something that doesn't serve the story.

## Working conventions established this session

**Follow these without being asked again:**

- **Track everything in `BACKLOG.md`.** Every deferred item, decision, and
  known gap goes there, not just in conversation. Update it proactively
  when something changes state -- the user explicitly asked for this to be
  automatic going forward.
- **Never guess a number and present it as fact.** If a source is
  ambiguous (see the Bournemouth 2024/25 and 2025/26 xG totals -- flagged
  `null` with an explanation rather than picking a plausible-looking
  number from a partial-season snapshot), say so explicitly and log it as
  a known gap. The user has been explicit about wanting flagged gaps over
  confident-sounding guesses.
- **Source hierarchy** (established after Wikipedia's squad table was
  caught stale -- missing a confirmed signing that FotMob already had):
  1. Official club/league statements
  2. FotMob (squad truth, career stints, current stats)
  3. Reputable stats/tactical analysis citing Opta or similar
  4. Mainstream sports news (for verifying discrete facts)
  5. Wikipedia -- last resort only, never a primary citation
- **Never hardcode API keys into files**, even in a "private for now"
  repo, since this is headed toward being public. Read from environment
  variables; real key values go into GitHub Actions secrets when that's
  set up, never into committed JSON/code.
- **Bayesian rigor over hand-waving, but honestly scoped**: real conjugate
  priors (Normal-Normal for continuous metrics, Dirichlet-Multinomial for
  formation choice) rather than a dressed-up weighted average -- but the
  README explicitly documents the Beta-vs-Normal simplification rather
  than overclaiming textbook purity.
- **Cost-consciousness**: user does not want ongoing server costs. Update
  cadence is weekly via GitHub Actions (free tier, scheduled workflows on
  a public repo), not live polling. This was a deliberate trade-off
  discussion, not a default.

## Known open issue at handoff time

`pipeline/fixtures_client.py` (football-data.org integration) is written
and structurally correct but has never received a live 200 response.
Blocked by a Claude.ai sandbox network-egress setting that appeared not to
propagate to an already-running conversation even after being correctly
added in account settings. This should be a non-issue in Claude Code, which
runs on the user's real network -- this is the main reason for the move to
Claude Code in the first place. First thing to verify in the new
environment: `export FOOTBALL_DATA_API_KEY=<key>` then
`python3 pipeline/fixtures_client.py` and confirm a real fixture list comes
back.

## Immediate next steps (see BACKLOG.md for full detail)

1. Confirm the football-data.org API actually returns data now that we're
   on real network access.
2. Build player-level profiles for the squad, starting with players who
   have NO Liverpool history (Isak, Wirtz, Muñoz, Chiesa) since those are
   the cases that actually exercise the positional-logic rules -- not the
   easy cases.
3. Get clean full-season Bournemouth xG for 2024/25 and 2025/26 now that
   the API works (currently `null` with a documented reason).
4. Build the dashboard (Fixtures / Squad+Stats / Game Plan tabs).
5. GitHub Actions weekly automation once there's something worth automating.
