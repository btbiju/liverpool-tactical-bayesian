# Backlog

Single source of truth for everything open on this project. Update this
file whenever something new gets deferred, started, or finished -- don't
let items live only in chat history.

## Known data gaps (flagged, not guessed)

- [ ] **Advanced per-90 metrics null for almost the entire squad** -- of all
      29 player profiles now built, only Wirtz (`touches_per90`,
      `duels_won_pct`), Gravenberch (`touches_per90`), and Ekitiké
      (`touches_per90`) have any advanced per-90 field populated. Every
      other player has `shots_per90`, `xg_per90`, `pass_accuracy_pct`,
      `progressive_passes_per90`, `touches_per90`, and `duels_won_pct` all
      null. This is a systemic, structural gap, not a one-off: FBref and
      footystats return HTTP 403 (bot-blocked), FotMob's stats pages are
      client-rendered JS, and even theanalyst.com's (Opta) per-player stats
      sub-pages are subscription/full-page-load gated over a fetch --
      only occasionally does a written article happen to quote the numbers
      directly (that's how Wirtz/Gravenberch/Ekitiké's partial data came
      through). Needs a paid tactical-stats API or manual browser-session
      pulls to actually resolve, not more search attempts.
- [ ] **Formation prior alpha counts are illustrative, not exact** --
      current values (4-2-3-1: 30, 4-1-4-1: 4, etc.) are calibrated to
      reflect "4-2-3-1 dominant but not certain," not a literal per-match
      formation tally across all three Bournemouth seasons. Worth replacing
      with real match-by-match formation logs if a source for that surfaces.
- [ ] **football-data.org free tier has no tactical stats** -- confirmed
      from the pricing page: free tier gives fixtures/results/tables only,
      no possession%, PPDA, or formation, and (separately confirmed
      2026-08-09) no xG at any tier either -- it's a fixtures/results/odds
      API, not a stats provider. `extract_match_observation()` in
      `pipeline/fixtures_client.py` fills only score/opponent/date --
      metrics and formation must still come from FotMob per match before
      calling the Bayesian update.
- [ ] **Federico Chiesa's squad status may already be stale** -- as of
      2026-08-09/10 he's reported in an active, unresolved transfer saga
      (Napoli links, "Liverpool outcast" framing) that could see him leave
      before the season starts. Per instruction, he stays listed as a
      current Liverpool player (with the transfer-saga flag already in his
      profile notes) until the window closes or a departure is confirmed --
      re-check then, not before.
- [ ] **Joseph Gomez's Liverpool future is also uncertain** -- found
      2026-08-10 during profile research: contract runs to 30 June 2027, but
      he's publicly said "anything can happen" re: a summer exit, with
      reported interest from AC Milan, Newcastle, Crystal Palace, Aston
      Villa. England's transfer window doesn't close until 1 September
      2026. Same treatment as Chiesa -- stays listed as current, re-check
      once the window closes.
- [ ] **`data/squad/liverpool_2026_27.json` was missing two current
      injuries**, caught only through live player-profile research on
      2026-08-10, not from the original squad fetch (2026-08-08) -- now
      added directly to the squad file:
  - **Vítezslav Jaroš**: serious knee injury (ACL-type), Ajax loan training
        accident Feb 2026, surgery, expected back late 2026.
  - **Joseph Gomez**: pre-season muscle injury (vs Sunderland, late July
        2026), confirmed to miss the Aug 23 season opener, no firmer
        return date yet.
  - Worth treating the squad file as due for a general refresh rather than
        assuming it's still fully current -- it's now over two weeks stale
        relative to some of what the player-profile research turned up.
- [ ] **A cluster of source disagreements were resolved by using the more
      specific/corroborated figure rather than picking arbitrarily** --
      flagged in each profile's notes, listed here for visibility:
  - **Kerkez**: a "100 apps/4g/7a pre-Liverpool" aggregate was arithmetically
        inconsistent with season-level AZ + Bournemouth numbers -- not used.
  - **Ramsay**: worst data quality in the squad -- no substantial minutes
        anywhere since Aberdeen 2021/22 (4 years stale), every loan since
        thin/injury-cut-short. playstyle_metrics confidence set very low
        (0.35) as a result. Wigan Athletic 2024/25 app counts also disagree
        across sources.
  - **Tsimikas**: Serie A start-count disagreement (18 vs 6 starts) while on
        loan at Roma -- used the more corroborated figure.
  - **Endo**: two sources gave conflicting 2025/26 totals (12 apps/455 min
        vs 8 apps/170 min) -- used the more specific PL-only figure; his
        2025/26 minutes were judged too thin either way, so a combined
        2023/24-2024/25 Liverpool aggregate was used for playstyle_metrics
        instead (flagged as a judgment call).
  - **Szoboszlai**: an unsupported "5G/5A" 2025/26 snippet conflicted with a
        better-sourced 13G/12A all-competitions figure -- the snippet wasn't
        used.
  - **Ekitiké**: a "32 goals/17 assists in 99 apps across 3 clubs" aggregate
        contradicted more detailed club-by-club data (e.g. 22 goals in 48
        Frankfurt apps alone, 2024/25) -- the detailed figures were used,
        the aggregate wasn't.
  - **Gravenberch**: a ~99-apps Liverpool career aggregate surfaced but
        couldn't be cross-verified -- not used; his 2025/26 PL-only apps
        (35/5G/3A) used instead.
  - **Van Dijk**: his 2025/26 goal tally is disputed (3 vs 5 vs 6 across
        sources) -- resolved by using Transfermarkt's career-aggregate PL
        figures rather than picking one of the three.
- [ ] **A few players have genuinely thin/low-confidence data, which is
      itself a finding, not a gap to force-fill:**
  - **Nyoni**: 6 career senior appearances total, largest single-season
        sample 14 minutes. `basis: manager_overlay_adjusted`,
        confidence 0.3. Reports of a possible 2026/27 loan are unresolved.
  - **Davies**: `has_liverpool_minutes: false` -- his only "Liverpool debut"
        found was a 2022 preseason friendly, not senior competitive
        minutes. Confidence 0.35.
  - **Leoni**: only 1 Liverpool minute ever (injured on debut) -- basis
        fell back to a single Parma season (17 apps), confidence 0.45.
  - **Ngumoha**: correctly shows 0 senior Chelsea appearances (academy
        only, a true fact) before his Liverpool breakthrough.

## Resolved this session (2026-08-09/10)

- [x] **Fixtures data pulled** -- `pipeline/pull_fixtures.py` (new) calls
      the existing `fixtures_client.get_liverpool_fixtures()` and writes
      each match as its own file in `data/fixtures/` (38 fixtures, full
      2026/27 Premier League season, all `TIMED` since the season hasn't
      started). Also fixed a small dashboard UX issue this surfaced: the
      Fixtures tab was showing a redundant gray "TIMED" badge on every
      upcoming row next to the already-shown kickoff time -- `SCHEDULED`/
      `TIMED` now render a plain "—" instead, badges reserved for actually
      notable statuses (finished, live, postponed).
- [x] **Bournemouth full-season xG for 2024/25 and 2025/26** --
      **2024/25: 67.25. 2025/26: 62.93.** Found via statmuse.com;
      corroborated (not just single-sourced) by cross-checking the season
      records bundled with each figure against independently-run searches
      -- both matched exactly (2024/25: 58 goals/46 conceded/15W-11D-12L/9th;
      2025/26: 58 goals/54 conceded/13W-18D-7L/6th/57pts). Recorded as
      `"confidence": "corroborated"` rather than `"confirmed"` like 2023/24,
      since no second source confirmed the xG number itself directly.
      (`data/manager_priors/iraola_2026.json`)
- [x] **Víctor Muñoz's Castilla 2024/25 stats dispute** -- resolved. Two
      further independent sources (besoccer.com, a separate web search)
      both confirmed the 34 apps/11 goals/7 assists figure already in use.
      Now treated as confirmed rather than disputed.
      (`data/player_profiles/munoz_victor.json`)
- [x] **`goals_conceded_per_match` corrected** -- was using a stale 2025/26
      partial-season snapshot (1.6). Real full-season totals: 1.21 (2024/25,
      46/38) and 1.42 (2025/26, 54/38), both corroborated alongside the xG
      work above. Mean corrected 1.4 -> 1.32, variance lowered 0.15 -> 0.08
      (the wide variance was specifically compensating for the old pairing's
      larger, wrong disagreement -- no longer warranted with two solid
      full-season figures). (`data/manager_priors/iraola_2026.json`)
- [x] **All 29 squad player profiles built** -- full squad coverage as of
      2026-08-10 (was 4/29 as of the previous session). Built via 3
      parallel background agents split by position group; every profile
      schema-validated (required fields present, no null values in
      strictly-typed fields, `basis` within the enum) and cross-checked
      against `data/squad/liverpool_2026_27.json` for fotmob_id/
      squad_number/name consistency -- 29/29 clean. See "Known data gaps"
      above for what's still null/uncertain per player.
- [x] **Dashboard built** -- React + Vite, three tabs (Fixtures, Squad &
      Stats, Game Plan), all reading `data/` directly via
      `dashboard/scripts/sync-data.mjs` (copies committed JSON into
      `dashboard/public/data/` on every dev/build -- no data duplicated,
      no second source of truth). Chose React over plain HTML/JS
      specifically for resume purposes (2026-08-10 discussion) even though
      the app itself doesn't need a framework at this scale. Verified in
      browser: all 3 tabs render with real data, light + dark mode, mobile
      responsive (375px), player detail modal, production build (`npm run
      build`) compiles clean, no console errors. `vite.config.js` sets
      `base: '/liverpool-tactical-bayesian/'` for GitHub Pages on build.
      Not yet deployed -- see "Not started" below.
- [x] **Game Plan tab: predicted starting XI** (2026-08-11, user-requested)
      -- `dashboard/src/lib/predictLineup.js` computes a most-likely 4-2-3-1
      XI from real data: formation_prior's dominant formation, each
      player's `position_estimate` (primary/secondary/confidence), and
      current `injury_status` (injured players excluded from selection
      entirely). Rendered as a clickable pitch graphic
      (`PredictedLineup.jsx`); clicking a player opens the existing
      `PlayerDetail` modal extended with a new "Projected role under
      Iraola" section. This is genuinely the manager positional-deployment
      overlay item below, arrived at from the UI side rather than the data
      side -- worth reconciling if layer 3 gets built into the schema
      later.
  - The algorithm surfaces a real, honest squad problem rather than
        hiding it: with Gomez and Leoni both injured, the only fit
        centre-back partner for Van Dijk is Jérémy Jacquet -- a
        2026/27 debutant with zero senior Liverpool minutes and the
        lowest confidence (55%) of any starter. Chiesa (50% confidence,
        transfer-saga flagged) is similarly the RW pick only by
        elimination. Both are called out explicitly in their role
        projections rather than presented as confident picks.
  - Role/specialization text for the 11 selected players is hand-authored
        (`dashboard/src/lib/roleProjections.js`), grounded in each
        player's real profile data and Iraola's real tactical prior
        (PPDA, possession%, cross volume, style_notes) -- explicitly
        labeled in the UI as "a model projection... not confirmed team
        news," consistent with the project's honesty conventions. If the
        algorithm ever selects a player not in that lookup (injury
        reshuffle, new signing), the UI shows a generic fallback message
        rather than breaking or silently showing nothing.
  - Only 4-2-3-1 has a visualized layout (the dominant formation at 83%);
        4-1-4-1/4-3-3/other aren't built out. Fine for now given the
        probability gap, but worth knowing if formation_prior ever shifts.
- [x] **Notes & Sourcing reorganized** (2026-08-11, user-requested) -- was
      a single flat bulleted list mixing methodology caveats and citations.
      `dashboard/src/lib/parseSources.js` splits the "Sources: ..." note
      (present in all 29 profiles) into a proper two-column table (source
      name + parenthetical context), separate from a "Methodology &
      data-quality notes" list for everything else.

## Not started

- [ ] **GitHub Pages deployment for the dashboard** -- builds clean locally
      but there's no deploy workflow yet. Natural to bundle with the
      GitHub Actions weekly automation below (one workflow: pull results ->
      run bayesian_update.py -> commit -> rebuild dashboard -> deploy to
      Pages), rather than two separate workflows.
- [ ] **GitHub Actions weekly automation** -- workflow file that pulls new
      results, runs `pipeline/bayesian_update.py`, commits the updated
      posterior. Repo exists and is set up -- this can start any time.
- [ ] **GitHub Secrets setup** -- once Actions is being built, the
      football-data.org key goes into repo secrets, never into a committed
      file.
- [ ] **Manager positional-deployment overlay, data-model side** -- the
      dashboard's predicted-XI feature (above) implements a version of this
      at the presentation layer (JS-computed selection + hand-authored role
      text), but the underlying data model still doesn't have it: layer 3
      of the three-layer positional logic (Liverpool minutes -> prior club
      minutes -> Iraola overlay) is still just prose in `style_notes`, not
      structured data on each player_profile. The schema's `basis` enum
      already anticipates this -- `manager_overlay_adjusted` is used by one
      profile (Nyoni) but only for lack of real data, not a deliberate
      overlay computation. Worth deciding whether the dashboard's role
      projections should eventually move into the data layer (per-player
      JSON) instead of living in dashboard source code, once this gets
      built properly.

## Correction to a prior assumption (2026-08-09)

- **"Isak, Wirtz, Muñoz, Chiesa have no Liverpool history" was wrong for 3
      of the 4** -- discovered while researching their profiles. This
      session's knowledge cutoff is January 2026, so anything after that
      had to be checked live, not recalled. Real transfer history: Isak
      joined Sept 2025, Wirtz joined July 2025, Chiesa joined summer 2024
      (all already had real LFC minutes); only Muñoz (Osasuna, summer 2026)
      genuinely had none. All 4 profiles were built with real data
      regardless, using the schema's existing `liverpool_recent_minutes`
      basis for the three who needed it -- no schema change was needed.
      Same live-verification discipline was applied throughout the
      25-profile squad-wide build that followed, specifically to avoid
      repeating this mistake (see agent reports folded into "Known data
      gaps" above).

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
  git since it's not part of this story and is too large for a portfolio repo.
- Git repo initialized, `.gitignore` and MIT `LICENSE` added, pushed to
  https://github.com/btbiju/liverpool-tactical-bayesian . Un-archived
  StatsBomb/Understat raw data (113MB+171MB) excluded from git via
  `.gitignore` rather than committed. `.claude/settings.local.json` also
  gitignored (Claude Code's own permission-allowlist file briefly captured
  the football-data.org API key in plaintext when a command was approved --
  never made it into git, but needs to stay gitignored going forward).
