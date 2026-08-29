# Backlog

Single source of truth for everything open on this project. Update this
file whenever something new gets deferred, started, or finished -- don't
let items live only in chat history.

## Known data gaps (flagged, not guessed)

- [ ] **Advanced per-90 metrics null for almost the entire squad** -- of all
      30 player profiles now built, only Wirtz (`touches_per90`,
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
      re-check then, not before. Availability was refreshed on 2026-08-28:
      Liverpool's official injury list says he is currently unavailable with a
      small muscle injury sustained against Como; no return date was supplied.
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

## Completed work (2026-08-09 onward)

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
- [x] **Initial 29-player squad fully profiled** -- full coverage of the
      2026-08-10 squad snapshot (up from the initial four priority profiles).
      Ronald Araujo became the 30th profile after his August loan. Research was
      divided by position group; every profile
      schema-validated (required fields present, no null values in
      strictly-typed fields, `basis` within the enum) and cross-checked
      against `data/squad/liverpool_2026_27.json` for fotmob_id/
      squad_number/name consistency. See "Known data gaps"
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
      Deployed through GitHub Actions to
      `https://btbiju.github.io/liverpool-tactical-bayesian/` on 2026-08-28.
- [x] **Game Plan tab: predicted starting XI** (2026-08-11; evidence update
      2026-08-28) -- `dashboard/src/lib/predictLineup.js` computes a
      most-likely 4-2-3-1 XI from real data. Recent sourced manager selections
      now take priority, with position estimates and confidence retained as
      fallbacks and injured players excluded entirely. The current projection
      is grounded in Iraola naming the same XI against Como and Newcastle:
      Ngumoha at right wing and Szoboszlai beside Gravenberch, replacing the
      original position-only picks of Chiesa and Mac Allister. The source-mapped
      selection snapshot lives in `data/lineup_projection/`. Rendered as a
      clickable pitch graphic
      (`PredictedLineup.jsx`); clicking a player opens the existing
      `PlayerDetail` modal extended with a new "Projected role under
      Iraola" section. This is genuinely the manager positional-deployment
      overlay item below, arrived at from the UI side rather than the data
      side -- worth reconciling if layer 3 gets built into the schema
      later.
  - The original algorithm surfaced a real squad problem rather than hiding
        it: with Gomez and Leoni injured, Jérémy Jacquet was the only fit
        centre-back partner for Van Dijk, while Chiesa became the RW pick only
        by elimination. Subsequent evidence validated Jacquet's selection but
        disproved the Chiesa projection: Iraola used Ngumoha on the right and
        repeated the same XI in the competitive opener. The projector now
        allows actual selections to correct static position assumptions.
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
- [x] **Notes & Sourcing reorganized, twice** (2026-08-11)
      -- was a single flat bulleted list mixing methodology caveats and
      citations. `dashboard/src/lib/parseSources.js` splits the
      "Sources: ..." note (present in every profile) into a proper
      two-column table (source name + parenthetical context, with a header
      row and card borders so it reads as a table even when the context
      column is empty). The methodology/data-quality notes are now
      collapsed behind a `<details>` disclosure rather than shown open by
      default -- still there for the project's sourcing-rigor story, just
      not the first thing you see.
- [x] **Playing Style section added for the full squad** (2026-08-11) --
      the original modal read primarily as a stat board, so
      `dashboard/src/lib/playingStyle.js`, a qualitative "how do they
      actually play" description per player, grounded in facts already
      present in their `career_stints` notes and `playstyle_metrics`
      (nothing new researched, just synthesized into narrative form).
      Shown prominently near the top of the player detail modal, ahead of
      the career table.
- [x] **Role projections deepened into real tactical analysis**
      (2026-08-11) -- the first pass was primarily a career recap rather than
      analysis. `roleProjections.js` was rewritten with a
      structured `{ zone, reasoning, outlook }` shape per player instead
      of one flowing paragraph, reasoning from three real inputs: the
      player's own sourced skills/stats, Iraola's actual tactical
      signature (9.45 PPDA elite press, 2.65 accurate crosses/match --
      "through the middle, not width-and-crosses", direct vertical
      buildup, centre-backs instructed to aggressively step and man-mark),
      and standard 4-2-3-1 zonal geometry. `outlook` is a hedged,
      reasoned expectation grounded in real trend data (e.g. Wirtz's
      in-season touches/90 and duel-win% climb) -- never a fabricated
      specific stat prediction. Rendered as labeled Zone/Why/Outlook
      fields in the UI so the analytical structure is visible, not buried
      in prose.

## Remaining work

- [ ] **Observe the delayed-research automation across several matchweeks.**
      The research-draft contract and deterministic resolver are implemented,
      but source availability, provider disclosure, video transcript access,
      and the usefulness of a second 48–72 hour pass must be evaluated using
      real matches. Promotion into `data/observations/` remains a review step;
      do not silently turn qualitative analysis into PPDA or other numbers.

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
      of the 4** -- discovered while researching their profiles. Time-sensitive
      transfer history was verified against live sources rather than prior
      knowledge. Real transfer history: Isak
      joined Sept 2025, Wirtz joined July 2025, Chiesa joined summer 2024
      (all already had real LFC minutes); only Muñoz (Osasuna, summer 2026)
      genuinely had none. All 4 profiles were built with real data
      regardless, using the schema's existing `liverpool_recent_minutes`
      basis for the three who needed it -- no schema change was needed.
      Same live-verification discipline was applied throughout the
      25-profile squad-wide build that followed, specifically to avoid
      repeating this mistake (see the findings folded into "Known data gaps"
      above).

## Decisions made (for reference, not action items)

- Update cadence: gated GitHub Actions checks around expected full time, plus a
  weekly fallback. API calls occur only inside the match window. A separate
  delayed research task may use ordinary web search after 24–72 hours, but
  tactical sites are not systematically polled or crawled.
- Conflicting match statistics: compare only compatible definitions, collapse
  repeated pages from the same measurement provider, use a strict independent-
  provider majority where available, and otherwise retain a numeric arithmetic
  mean only as a labeled derived consensus with its full input range. Never
  average categorical claims.
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
  `.gitignore` rather than committed. A local development-tool permission file
  briefly captured the football-data.org API key in plaintext. It never entered
  Git history; the file was removed during the neutral handoff and the key must
  be rotated manually.

## Handoff findings (2026-08-24)

- [x] **Continuous Bayesian update implementation corrected.** The engine now
      uses precision-weighted Normal-Normal conjugacy. Default single-match
      variance is inferred from current mean uncertainty and the effective
      virtual-match count, while explicit per-metric observation variance is
      supported and persisted. Deterministic tests cover prior weighting,
      sequential updates, variance behavior, and invalid uncertainty inputs.
- [x] **Null metrics and formations are ignored during updates.** Missing data no
      longer creates evidence or increments the formation `other` bucket; this
      behavior is covered by tests.
- [x] **Tactical observation enrichment stage defined.**
      `docs/MATCHWEEK_WORKFLOW.md` specifies field-level source preferences,
      null handling, human review, source mapping, and the boundary between raw
      fixture automation and tactical evidence.
- [x] **Repeatable offline Python validation added.** Standard-library tests and
      `pipeline/validate_data.py` cover the JSON Schema features used by the
      repository, parse project JSON, and cross-check squad/profile identities.
      Dashboard checks and a history-aware Gitleaks scan are included in CI.
- [x] **Manager role projections remain presentation-layer analysis.** This is
      now an explicit modeling boundary: the prose combines sourced player facts
      with tactical interpretation, while the Bayesian state currently updates
      team metrics and formation only. Moving the prose into posterior JSON now
      would imply a computation that does not exist. Revisit only if a structured,
      evidence-updating player-role model is implemented.
- [x] **Reviewed observation and posterior pipeline implemented.** Added a
      source-mapped observation schema, neutral matchweek workflow, explicit
      calibrated observation variances, deterministic snapshot builder/checker,
      and a synthetic end-to-end integration fixture that never enters production
      data. The dashboard now renders posterior deltas and an evidence log rather
      than dumping raw JSON.
- [x] **Automation workflows activated.** CI runs tests, schema/data validation,
      posterior reproducibility, lint/build, and Gitleaks v3. A Monday fixture
      refresh workflow commits only football-data.org response changes. A Pages
      workflow validates and deploys the static Vite artifact. The handover was
      merged through PR #1 on 2026-08-28, Pages was configured for Actions, and
      the repository secret is stored under `FOOTBALL_DATA_API_KEY`. The first
      manual refresh completed successfully and committed the raw API changes as
      `b625bc7`; the weekly schedule remains enabled.
      The refresh workflow explicitly dispatches the Pages workflow after a
      fixture commit because ordinary pushes made with `GITHUB_TOKEN` do not
      trigger other workflows. This keeps the published data current without a
      personal access token or recursive workflow chain.
- [x] **Neutral project handoff documentation added.** Durable operating
      instructions now live in `AGENTS.md`; implementation status and the
      verification checklist live in `HANDOFF.md`.
- [x] **Squad/profile display-name consistency corrected.** Vítězslav Jaroš's
      squad entry used an unaccented/incompletely accented spelling while his
      profile used the canonical spelling. The squad entry now matches the
      profile; all FotMob IDs, names, and squad numbers cross-check.
- [x] **Squad refreshed from current official/FotMob sources (2026-08-24).**
      Added Ronald Araujo after Liverpool confirmed his season-long Barcelona
      loan and No.33 shirt; added a sourced player profile using the official
      Opta-derived factfile and FotMob career/current-season records. Confirmed
      Alisson No.1, Jaroš No.56, and Jacquet No.5. Jacquet's profile now records
      his competitive start at Newcastle, while Araujo's records his 20-minute
      debut. Current coverage is 30 squad players and 30 profiles.
- [x] **Raw matchweek-one fixture refreshed through football-data.org.** The
      2026-08-28 Actions run changed match `560550` from `TIMED` to `FINISHED`
      and supplied the 2-2 full-time score, 1-0 half-time score, referee Stuart
      Attwell, and a fresh source timestamp. The raw response was committed by
      automation as `b625bc7`; it was not hand-edited.
- [x] **First production observation and posterior completed.** The reviewed
      Newcastle observation selects the official Premier League values of 60.8%
      possession and seven shots on target, plus two goals conceded from the
      verified result. An earlier TNT review reported 58% possession; that
      disagreement is preserved in the observation and the official league
      source wins under the repository hierarchy. PPDA, exact completed passes,
      exact completed crosses, and formation remain null because the accessible
      evidence does not expose compatible exact values. The deterministic
      matchweek-one posterior shifts possession 50.55 -> 51.48, shots on target
      4.55 -> 4.77, and goals conceded 1.32 -> 1.38 while leaving unsupported
      metrics and formation unchanged.
- [x] **Played-match details expanded in the dashboard.** Finished fixtures now
      render dedicated result cards containing the complete useful metadata
      supplied by football-data.org: full-time and half-time score, Liverpool
      outcome, teams and crests, competition, matchweek, stage, duration,
      referee, match ID, and API update time. Missing fields are labeled `Not
      supplied`; no tactical statistic is inferred from the fixture feed.
- [x] **First weekly availability and lineup review completed (2026-08-28).**
      No new competitive observation was possible because matchweek two had not
      yet been played. The review instead captured Chiesa's newly confirmed
      muscle injury, added RW as a sourced secondary estimate for Ngumoha, and
      replaced the position-only projected XI with a source-mapped selection
      projection based on the final Como friendly and Newcastle opener. The
      projection remains explicitly provisional because Liverpool are publicly
      seeking another winger before the transfer deadline.
- [x] **Post-match result analysis automated (2026-08-28).** The refresh
      workflow now wakes twice per hour but gates external API use to the window
      around expected full time, with Monday retained as a forced fallback.
      When football-data.org marks a fixture `FINISHED`, a deterministic script
      creates a source-mapped `automated_result_only` observation, updates only
      goals conceded, rebuilds posterior snapshots, validates, commits, and
      dispatches Pages deployment. Unsupported tactical fields remain null and
      existing human-reviewed observations are never overwritten.
- [x] **Delayed post-match research stage implemented (2026-08-28).** Added a
      source-mapped research-draft schema, offline validation, and deterministic
      conflict resolver. The resolver counts disclosed measurement providers
      rather than web pages, selects unanimity or a strict majority, and labels
      compatible no-majority numeric averages with their full range. A
      Newcastle evidence packet demonstrates the process without replacing the
      official value already used by the production observation. The dashboard
      now explains that scores can update immediately while tactical evidence
      follows after a 24–72 hour collection and validation window.
