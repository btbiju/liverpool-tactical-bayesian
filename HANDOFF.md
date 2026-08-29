# Project handoff

## Current status

The repository contains a complete preseason manager prior, a 30-player squad,
30 corresponding player profiles, and all 38 Liverpool Premier League fixtures
for 2026/27. The React dashboard is implemented and reads committed JSON through
a generated static-data directory. The observation contract and deterministic
posterior builder are implemented. Matchweek one now has a reviewed production
observation and deterministic posterior snapshot. CI, post-match result
automation, a weekly fallback refresh, and GitHub Pages deployment are active.

## Existing data flow

```text
Iraola seasons + player research
              -> committed prior/squad/profile JSON
football-data.org
              -> committed raw fixture/result JSON
separate tactical-stat enrichment
              -> match observation
Python Bayesian update
              -> posterior snapshot JSON
dashboard sync script
              -> generated public/data
React/Vite build
              -> static site
```

The tactical-stat enrichment stage is not implemented. football-data.org can
provide scores, opponents, dates, and statuses, but not the possession, PPDA,
formation, or related tactical evidence expected by the update engine.

## Modeling approach

Six continuous metrics use an intended Normal-Normal conjugate model:
possession percentage, PPDA, shots on target per match, goals conceded per
match, accurate passes per match, and accurate crosses per match. Formation
choice uses a Dirichlet-Multinomial model.

The method is deliberately transparent and modest about simplifications. In
particular, Normal possession is an approximation for a bounded percentage.
Formation alpha counts are calibrated pseudo-counts, not exact historical
tallies.

The continuous update uses precision-weighted Normal-Normal conjugacy. Stored
`variance` represents uncertainty in the current mean. A single match's noise
defaults to `variance * effective_n`, making the default update equivalent to
adding one equally noisy observation to the existing virtual-match sample.
Explicit per-metric observation variance is supported and persisted so
sequential updates remain consistent. Missing metrics and null formations are
ignored rather than converted into evidence.

## Completed major features

- Manager tactical prior across three Bournemouth seasons.
- Sourced current-squad snapshot with injuries and departures.
- Full set of 30 player career/playstyle profiles, including the August 2026
  Ronald Araujo loan.
- JSON Schemas for prior, player, and posterior data.
- football-data.org fixture client and 38 committed fixture files.
- React/Vite dashboard with Fixtures, Squad & Stats, and Game Plan tabs.
- Expanded played-match result cards containing the complete useful metadata
  supplied by football-data.org, with explicit unavailable-field labels.
- Player cards, player detail views, playing-style descriptions, and sourcing
  presentation.
- Evidence-led projected 4-2-3-1 starting XI with recent manager selections,
  injury exclusion, source links, positional fallback, and role analysis.
- Responsive layout, dark/light styling, loading/error/empty states, and a
  GitHub Pages base-path configuration.
- Deterministic standard-library Python tests for Bayesian weighting, variance,
  formation updates, missing observations, and project-data validation.
- Dependency-free offline schema and squad/profile consistency validation.
- Sourced match-observation schema for automated result-only or human-reviewed
  evidence, deterministic posterior rebuild/check command, and a controlled
  end-to-end integration fixture.
- First production observation and posterior snapshot, using official Premier
  League/Liverpool evidence for the Newcastle 2-2 draw and leaving unsupported
  metrics null.
- Dashboard posterior summary, metric deltas, formation belief, evidence log,
  and source links (replacing the raw JSON presentation).
- CI, gated post-match football-data.org refresh, automated result-only
  observations/posteriors, weekly fallback, history-aware secret scanning, and
  GitHub Pages deployment workflows.
- Historical StatsBomb/Understat experiment separated into an ignored archive
  because it does not support the current model's data flow or portfolio story.

## Known gaps

- Only one posterior snapshot exists; early-season conclusions must remain
  strongly qualified because the manager prior still carries ten virtual
  matches of weight.
- No reliable automated source is defined for tactical match statistics. The
  automated path can update only score-derived goals conceded.
- Most advanced player per-90 fields remain null because accessible sources are
  blocked, client-rendered, or subscription-gated.
- Formation pseudo-counts are illustrative.
- The squad was refreshed on 2026-08-24, including Ronald Araujo's loan and
  competitive debut. Transfers and injuries remain time-sensitive.
- Tactical role projections remain deliberately in the presentation layer:
  they are sourced editorial analysis, not Bayesian state. Moving them into
  model JSON would incorrectly imply that the current engine computes them.
- Only the 4-2-3-1 pitch layout is supported.
- The projected XI currently reflects the unchanged Como/Newcastle selection,
  including Ngumoha at RW and Szoboszlai in the double pivot. It remains
  provisional while Liverpool pursue another winger and should be refreshed
  when new competitive lineups arrive.
- Role projections and playing-style descriptions are hand-authored from
  sourced inputs; they are not generated posterior predictions.
- Matchweek one is now a verified `FINISHED` API record. It can support the
  reviewed 2-2 Newcastle observation, but tactical metrics still require
  separate field-level sources.
- The football-data.org credential is configured as the encrypted
  `FOOTBALL_DATA_API_KEY` repository secret. The exposed original should still
  be rotated when the provider offers a supported replacement path.

See `BACKLOG.md` for player-specific uncertainty and source disagreements.

## Recommended next steps

1. Rotate the exposed football-data.org key when the provider supplies a
   supported rotation path, then update the existing repository secret.
2. Monitor the first automated post-match run. Human enrichment is optional,
   but remains necessary for possession, shots, PPDA, passing, crossing, and
   formation unless a licensed provider is connected.
3. Continue reviewing transfer and injury changes through the window close.
4. Replace provisional observation-variance hyperparameters only when a
   documented match-level calibration dataset is available.

## Verification checklist

- [ ] Working tree contains only intentional source/data/documentation changes.
- [ ] No credentials or local permission files are tracked or untracked.
- [ ] All committed JSON parses successfully.
- [ ] Manager prior validates against its schema.
- [ ] All player profiles validate against their schema.
- [ ] Posterior snapshots, when present, validate against their schema.
- [ ] Squad and profiles agree on FotMob ID, name, and squad number.
- [ ] `python3 -m unittest discover -s tests -v` passes.
- [ ] `python3 pipeline/validate_data.py` passes.
- [ ] Python pipeline compiles and its offline smoke entry point passes.
- [ ] No validation command performs a live API request.
- [ ] `cd dashboard && npm run lint` completes without errors.
- [ ] `cd dashboard && npm run build` completes successfully.
- [ ] Generated `dashboard/public/data/` and `dashboard/dist/` remain ignored.
- [ ] A history-aware secret scan passes before the repository becomes public.
- [ ] Public-facing text labels projections and data uncertainty honestly.
