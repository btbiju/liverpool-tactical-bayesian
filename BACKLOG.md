# Backlog

Single source of truth for everything open on this project. Update this
file whenever something new gets deferred, started, or finished -- don't
let items live only in chat history.

## Known data gaps (flagged, not guessed)

- [ ] **Bournemouth full-season xG totals for 2024/25 and 2025/26** --
      2023/24 confirmed (32.9). football-data.org ruled out as a source
      (2026-08-09 -- live-tested, no xG field at any tier, see below).
      Also retried direct-fetching FotMob/FBref/footystats the same day:
      FotMob's stats pages are client-rendered JS and return "stats not
      available" over a plain fetch, FBref and footystats both 403
      (bot-blocked). A FotMob season-stats URL guessed from a search
      snippet returned 61.9 for "2025/26" but self-described the season as
      still in progress, which contradicts the season already having ended
      by 2026-08-09 -- not recorded, not trustworthy. Needs either a paid
      tactical-stats API (Opta/StatsBomb-backed) or a manual pull from a
      logged-in browser session. (`data/manager_priors/iraola_2026.json`)
- [ ] **Formation prior alpha counts are illustrative, not exact** --
      current values (4-2-3-1: 30, 4-1-4-1: 4, etc.) are calibrated to
      reflect "4-2-3-1 dominant but not certain," not a literal per-match
      formation tally across all three Bournemouth seasons. Worth replacing
      with real match-by-match formation logs if a source for that surfaces.
- [ ] **football-data.org free tier has no tactical stats** -- confirmed
      from the pricing page: free tier gives fixtures/results/tables only,
      no possession%, PPDA, or formation. `extract_match_observation()` in
      `pipeline/fixtures_client.py` fills only score/opponent/date --
      metrics and formation must still come from FotMob per match before
      calling the Bayesian update. Not a blocker, just means the weekly
      update process has a manual/semi-manual layering step, not a single
      clean API call.
- [ ] **football-data.org does not provide xG at all, confirmed live** --
      inspected both `/teams/{id}/matches` and `/matches/{id}` response
      bodies directly (2026-08-09, real API call against a finished
      Bournemouth match) -- fields present are score/venue/referees/odds
      upsell, no expected-goals metric at any tier. This is a fixtures/
      results/odds API, not a stats provider (that's Opta/StatsBomb/
      Understat/FBref territory).
- [ ] **Player profile advanced per-90 metrics mostly null** -- for all four
      profiles built 2026-08-09 (Isak, Wirtz, Muñoz, Chiesa), FBref/FotMob
      detail pages were blocked or client-rendered, so `shots_per90`,
      `xg_per90`, `pass_accuracy_pct`, `progressive_passes_per90` are null
      across the board. Wirtz has `touches_per90`/`duels_won_pct` from an
      Opta-sourced article (theanalyst.com) -- that's the one exception and
      a model for what a "resolved" profile looks like. Needs either a paid
      stats API or manual browser-session pulls per player.
- [ ] **Víctor Muñoz's Real Madrid Castilla 2024/25 stats are disputed
      across sources** -- 34 apps/11 goals/7 assists vs. 48 games/9 goals vs.
      "10 goals as of May 2025" depending on source. Used the most specific
      single figure (34/11/7) with the disagreement flagged in the profile
      note rather than silently picking one. (`data/player_profiles/munoz_victor.json`)
- [ ] **Federico Chiesa's squad status may already be stale** -- as of
      2026-08-09 he's reported in an active, unresolved transfer saga
      (Napoli links, "Liverpool outcast" framing) that could see him leave
      before the season starts. `data/squad/liverpool_2026_27.json` (fetched
      2026-08-08) still lists him with no departure flag. Worth re-checking
      before relying on his profile for 2026/27 projections.

## Not started

- [ ] **Fixtures data** -- `data/fixtures/` is an empty directory. The
      football-data.org client is confirmed working (live-tested
      2026-08-09, real fixture list returned) but nothing has been pulled
      into this directory yet.
- [ ] **Remaining squad player profiles** -- 4 of ~28 squad players now have
      profiles (Isak, Wirtz, Muñoz, Chiesa -- the ones with no/thin
      Liverpool history, chosen to stress-test the positional-logic rules
      first). The rest of the squad still needs profiles.
- [ ] **Dashboard build** -- three tabs discussed: Fixtures, Squad + player
      stats, Game Plan (prior vs. posterior vs. next-match projection). Not
      started.
- [ ] **GitHub Actions weekly automation** -- workflow file that pulls new
      results, runs `pipeline/bayesian_update.py`, commits the updated
      posterior. Repo now exists and is set up (see below) -- this can
      start any time.
- [ ] **GitHub Secrets setup** -- once Actions is being built, the
      football-data.org key goes into repo secrets, never into a committed
      file.
- [ ] **Manager positional-deployment overlay** -- currently only captured
      as prose in `style_notes`, not as a structured model. The three-layer
      positional logic (Liverpool minutes -> prior club minutes -> Iraola
      overlay) needs layer 3 actually implemented, not just described. The
      player_profile schema's `basis` enum (`liverpool_recent_minutes`,
      `prior_club_recent_minutes`, `manager_overlay_adjusted`,
      `in_season_observed`) already anticipates this -- `manager_overlay_adjusted`
      isn't used by any profile yet.

## In progress / built this session (2026-08-09)

- [x] football-data.org API live-tested and confirmed working (real
      fixture list returned) -- the earlier `host_not_allowed` sandbox
      issue is resolved now that this runs in Claude Code on real network
      access.
- [x] Git repo initialized, `.gitignore` and MIT `LICENSE` added, pushed to
      https://github.com/btbiju/liverpool-tactical-bayesian . Excluded the
      un-archived StatsBomb/Understat raw data (113MB+171MB) from git via
      `.gitignore` rather than committing it -- kept locally, not part of
      the Bayesian project's data flow. Also excluded `.claude/settings.local.json`
      (Claude Code's own permission-allowlist file briefly captured the
      football-data.org API key in plaintext when a command was approved --
      never made it into git, but worth knowing this file needs to stay
      gitignored going forward).
- [x] Four player profiles built (`data/player_profiles/`): Isak, Wirtz,
      Muñoz, Chiesa -- schema-validated. See "Known data gaps" above for
      what's still null/uncertain in each.
- [x] Manager prior populated (Iraola / Bournemouth) -- 6 continuous metrics,
      formation prior, style notes, source citations
- [x] Squad confirmed via FotMob (28 players, injuries, summer departures)
- [x] Bayesian update engine (`pipeline/bayesian_update.py`) -- built and
      smoke-tested, Normal-Normal + Dirichlet-Multinomial
- [x] Three JSON schemas (manager prior, player profile, posterior state)
- [x] Source hierarchy documented in README after the Wikipedia staleness issue
- [x] Full-season xG for 2023/24 confirmed (32.9)
- [x] Fixtures client built (`pipeline/fixtures_client.py`) -- reads API key
      from environment variable, live-tested and working

## Correction to a prior assumption (2026-08-09)

- **"Isak, Wirtz, Muñoz, Chiesa have no Liverpool history" was wrong for 3
      of the 4** -- discovered while researching their profiles. This
      session's knowledge cutoff is January 2026, so anything after that
      had to be checked live, not recalled. Real transfer history:
  - **Isak**: joined Liverpool September 2025 -- already ~1 season of LFC
        minutes by now.
  - **Wirtz**: joined Liverpool July 1, 2025 (official, liverpoolfc.com) --
        already a full 2025/26 LFC season.
  - **Chiesa**: joined Liverpool summer **2024** (BBC/Goal.com confirmed) --
        already two LFC seasons, and is currently in an active transfer saga
        (Napoli/Juventus links) as of August 2026 -- may not stay on the
        squad.
  - **Muñoz**: this one checks out -- genuinely Iraola's first Liverpool
        signing, arrived from Osasuna summer 2026, no Liverpool history.
  - The original "no Liverpool history, tests the positional-logic rules"
        framing only actually holds for Muñoz. User decision (2026-08-09):
        build all 4 profiles anyway, giving Isak/Wirtz/Chiesa a real
        Liverpool `career_stint` using the schema's existing
        `liverpool_recent_minutes` basis -- the schema was already designed
        to handle this case, so no schema change needed, just correct data.

## Decisions made (for reference, not action items)

- Update cadence: manual/weekly via GitHub Actions, not live polling (cost + ToS reasons)
- Model rigor: real conjugate-prior Bayesian updating, not a hand-rolled weighted average
- FotMob is source of truth for squad data over Wikipedia
- Wikipedia demoted to last-resort cross-check only
- Historical event data (StatsBomb, Understat archive) stops around 2015/16-2021/22 --
  no free full-season event-level data exists post-2020, which is why the
  project pivoted from "analyze past matches" to "project from player/manager priors"
- Historical 2015/16 StatsBomb passing-network module cut from the main project --
  no data-flow connection to the Bayesian model, dilutes the project's focus.
  Kept locally in `archive/` for reference, not deleted, but excluded from
  git (see "In progress" above) since it's not part of this story and is
  too large for a portfolio repo.
