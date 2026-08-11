# Liverpool Tactical Intelligence — Iraola Era

A Bayesian model of Liverpool's evolving tactical identity under new manager
Andoni Iraola, updated weekly as the 2026/27 season unfolds.

## The idea

When a new manager arrives, there's no data yet on "how this specific group
of players performs under this specific manager." This project treats that
as a Bayesian inference problem instead of a dashboard problem:

- **Prior**: built from Iraola's three seasons at Bournemouth (2023/24-2025/26)
  plus each player's individual career playstyle data -- weighted toward
  their most recent club/role, since a player's identity two clubs ago
  matters less than what they were doing right before signing.
- **Evidence**: real 2026/27 match results, pulled weekly.
- **Posterior**: the model's current belief, which shifts toward observed
  reality as the season accumulates evidence, automatically de-weighting
  the Bournemouth-derived prior over time -- no manual decay schedule.

## Why Bayesian, specifically

Two conjugate update mechanisms, chosen per data type rather than forced
into one:

- **Continuous metrics** (possession%, PPDA, shots on target, goals conceded,
  passing volume, crossing volume) use **Normal-Normal conjugate updates**.
  This is a known simplification -- a bounded percentage like possession is
  technically better modeled as Beta -- but values stay well clear of the
  0/100 boundaries in practice, and it keeps every metric under one simple,
  auditable formula.
- **Formation choice** (4-2-3-1 vs alternatives) uses a **Dirichlet-Multinomial
  conjugate update**, which is the textbook-correct model for categorical
  data -- no approximation needed here.

Both mechanisms share the key property that matters for the story: the
prior's weight (`pseudo_n` / Dirichlet alpha totals) grows by one with each
observed match, so its influence shrinks automatically as real evidence
accumulates. Early season, the model is mostly still describing Bournemouth.
By December, it should be describing Liverpool.

## Positional assignment

Multi-position players are the norm (Szoboszlai alone is tagged AM/DM/RW/RB/
CM/LW). Position is derived, not looked up, via three layers:

1. Recency-weighted actual position from Liverpool minutes, if any exist.
2. If no Liverpool minutes: recency-weighted position from the player's most
   recent prior club.
3. Overlaid with Iraola's own positional-deployment tendencies (e.g. a player
   who was a wide winger under a previous manager may be an inverted forward
   or AM under Iraola) -- itself a prior that updates as real 2026/27
   lineups are observed.

## Source hierarchy

Ranked by trust, used in this order when sources disagree:

1. **Official club/league statements** (liverpoolfc.com, premierleague.com) -- ground truth for transfers/appointments, but slow and doesn't cover advanced stats.
2. **FotMob** -- squad truth, career stints, current-season stats.
3. **Reputable stats/tactical analysis citing Opta or similar underlying data** (The Analyst, totalfootballanalysis) -- used for PPDA, formation, and style metrics.
4. **Mainstream sports news** (ESPN, Sky, BBC, Athletic) -- for verifying discrete facts (e.g. confirming a departure actually happened).
5. **Wikipedia** -- last-resort cross-check only, never a primary citation. During this project's research phase, Wikipedia's Liverpool squad table was missing a confirmed live signing (Víctor Muñoz) that FotMob already had -- a concrete example of the staleness risk that justifies ranking it last for anything time-sensitive.

## Data sources and their limits

| Source | Used for | Constraint |
|---|---|---|
| StatsBomb open data | 2015/16 historical event data (separate module) | Free, full event-level, but no coverage post-2015/16 for the Premier League |
| Understat (GitHub-archived) | 2020/21 shot-level xG data | Live site blocks automated access; archived dataset stops at 2021/22 |
| FotMob | Current squad (source of truth), career stints, current-season stats | ToS disallows automated/systematic scraping -- data pulled sparingly to seed/refresh, never polled live in a loop |
| football-data.org (planned) | Fixtures, results feed for weekly updates | Free tier, built for this use case -- the stable backbone for the actual update pipeline |

## Update cadence

Weekly, via GitHub Actions (free scheduled workflows on a public repo --
no server cost). Each run pulls the week's results, applies
`pipeline/bayesian_update.py`, and commits the updated posterior back to the
repo. The commit history itself becomes a visible log of the model learning
over the season.

## Structure

```
schema/                 JSON Schemas for prior, player profile, posterior state
data/manager_priors/    Iraola's Bournemouth-derived prior (populated)
data/squad/             Current Liverpool squad, FotMob as source of truth
data/player_profiles/   Per-player career + playstyle data (all 29 players populated)
data/fixtures/          Upcoming/played fixtures (client built, not yet pulled)
data/posteriors/        Weekly posterior snapshots (grows over the season)
pipeline/               Bayesian update engine + football-data.org fixtures client
dashboard/              React (Vite) dashboard -- Fixtures / Squad & Stats / Game
                         Plan tabs, reads the data/ JSON files directly (see
                         dashboard/scripts/sync-data.mjs). Deploys to GitHub
                         Pages as a static site.
archive/                Historical 2015/16 StatsBomb passing-network work --
                         kept for reference, deliberately excluded from the
                         main project. Different era, no data-flow connection
                         to the Bayesian model, and diluted the project's
                         focus. See BACKLOG.md decision log.
```

## Status

See `BACKLOG.md` for the full tracked list of open items, blockers, and
known data gaps -- kept up to date as the single source of truth so nothing
gets lost across sessions.

- [x] Manager prior populated (Iraola / Bournemouth, 6 metrics + formation)
- [x] Squad confirmed (FotMob, 29 players + summer departures logged)
- [x] Bayesian update engine built and smoke-tested
- [x] Player-level career profiles (all 29 squad players)
- [x] football-data.org fixtures client (live-tested, working)
- [x] Dashboard: Fixtures / Squad & Stats / Game Plan tabs (React + Vite)
- [x] Fixtures data pulled (38 fixtures, full 2026/27 PL season)
- [ ] GitHub Actions weekly automation
- [ ] GitHub Pages deployment workflow for the dashboard
