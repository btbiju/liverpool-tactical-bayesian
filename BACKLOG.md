# Backlog

Single source of truth for everything open on this project. Update this
file whenever something new gets deferred, started, or finished -- don't
let items live only in chat history.

## Known data gaps (flagged, not guessed)

- [ ] **Bournemouth full-season xG totals for 2024/25 and 2025/26** --
      2023/24 confirmed (32.9), but the other two seasons' FotMob pages
      only returned partial-season snapshots via search that couldn't be
      reliably distinguished from final totals. Resolve via football-data.org
      once the API key is in. (`data/manager_priors/iraola_2026.json`)
- [ ] **Formation prior alpha counts are illustrative, not exact** -- current
      values (4-2-3-1: 30, 4-1-4-1: 4, etc.) are calibrated to reflect "4-2-3-1
      dominant but not certain," not a literal per-match formation tally across
      all three Bournemouth seasons. Worth replacing with real match-by-match
      formation logs if a source for that surfaces.

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
      bodies directly (2025-08-09, real API call against a finished
      Bournemouth match) -- fields present are score/venue/referees/odds
      upsell, no expected-goals metric at any tier. This is a fixtures/
      results/odds API, not a stats provider (that's Opta/StatsBomb/
      Understat/FBref territory). The 2024/25 and 2025/26 Bournemouth xG
      nulls in `data/manager_priors/iraola_2026.json` are NOT resolvable
      via this API -- still an open gap, needs a different source or
      stays flagged null.

## Not started

- [ ] **Player-level career profiles** -- schema exists
      (`schema/player_profile.schema.json`), squad list exists
      (`data/squad/liverpool_2026_27.json`), but no individual player files
      populated yet. Priority candidates: Isak, Wirtz, Muñoz, Chiesa (no
      Liverpool history -- these are the cases that actually test the
      positional-logic rules).
- [ ] **Fixtures data** -- `data/fixtures/` is an empty directory. Needs the
      football-data.org integration.
- [ ] **Dashboard build** -- three tabs discussed: Fixtures, Squad + player
      stats, Game Plan (prior vs. posterior vs. next-match projection). Not
      started.
- [ ] **GitHub Actions weekly automation** -- workflow file that pulls new
      results, runs `pipeline/bayesian_update.py`, commits the updated
      posterior. Needs the repo to exist and be public first.
- [ ] **GitHub Secrets setup** -- once Actions is being built, the
      football-data.org key goes into repo secrets, never into a committed
      file. Reminder for that step specifically.
- [ ] **Manager positional-deployment overlay** -- currently only captured
      as prose in `style_notes`, not as a structured model. The three-layer
      positional logic (Liverpool minutes -> prior club minutes -> Iraola
      overlay) needs layer 3 actually implemented, not just described.
## In progress / built this session

- [x] Manager prior populated (Iraola / Bournemouth) -- 6 continuous metrics,
      formation prior, style notes, source citations
- [x] Squad confirmed via FotMob (28 players, injuries, summer departures)
- [x] Bayesian update engine (`pipeline/bayesian_update.py`) -- built and
      smoke-tested, Normal-Normal + Dirichlet-Multinomial
- [x] Three JSON schemas (manager prior, player profile, posterior state)
- [x] Source hierarchy documented in README after the Wikipedia staleness issue
- [x] Full-season xG for 2023/24 confirmed (32.9)
- [x] Fixtures client built (`pipeline/fixtures_client.py`) -- reads API key
      from environment variable, structurally verified, live network test
      pending (see Blocked)

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
  Moved to `archive/` for reference, not deleted. Good standalone work, just
  not part of this story.
