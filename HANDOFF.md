# Project handoff

## Current status

The repository contains a complete preseason manager prior, a 30-player squad,
30 corresponding player profiles, and all 38 Liverpool Premier League fixtures
for 2026/27. The React dashboard is implemented and reads committed JSON through
a generated static-data directory. The observation contract and deterministic
posterior builder are implemented, but no production observation/posterior is
committed yet. CI, weekly fixture refresh, and GitHub Pages workflows are ready
for review and activation.

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
- Player cards, player detail views, playing-style descriptions, and sourcing
  presentation.
- Projected 4-2-3-1 starting XI with injury exclusion and role analysis.
- Responsive layout, dark/light styling, loading/error/empty states, and a
  GitHub Pages base-path configuration.
- Deterministic standard-library Python tests for Bayesian weighting, variance,
  formation updates, missing observations, and project-data validation.
- Dependency-free offline schema and squad/profile consistency validation.
- Reviewed match-observation schema, sourcing workflow, deterministic posterior
  rebuild/check command, and a controlled end-to-end integration fixture.
- Dashboard posterior summary, metric deltas, formation belief, evidence log,
  and source links (replacing the raw JSON presentation).
- CI, weekly football-data.org fixture refresh, history-aware secret scanning,
  and GitHub Pages deployment workflows.
- Historical StatsBomb/Understat experiment separated into an ignored archive
  because it does not support the current model's data flow or portfolio story.

## Known gaps

- No posterior snapshots or end-to-end matchweek update have been produced.
- No reliable automated source is defined for tactical match observations.
- Most advanced player per-90 fields remain null because accessible sources are
  blocked, client-rendered, or subscription-gated.
- Formation pseudo-counts are illustrative.
- The squad was refreshed on 2026-08-24, including Ronald Araujo's loan and
  competitive debut. Transfers and injuries remain time-sensitive.
- Tactical role projections remain deliberately in the presentation layer:
  they are sourced editorial analysis, not Bayesian state. Moving them into
  model JSON would incorrectly imply that the current engine computes them.
- Only the 4-2-3-1 pitch layout is supported.
- Role projections and playing-style descriptions are hand-authored from
  sourced inputs; they are not generated posterior predictions.
- The raw matchweek-one fixture still says `TIMED`. It must be refreshed through
  football-data.org before the reviewed 2-2 Newcastle observation is committed.
- Workflows are implemented locally but have not run on GitHub. Pages must be
  configured to use GitHub Actions, and the rotated API key must be added as the
  `FOOTBALL_DATA_API_KEY` repository secret.

See `BACKLOG.md` for player-specific uncertainty and source disagreements.

## Recommended next steps

1. Rotate the exposed football-data.org key and configure the replacement as a
   GitHub Actions repository secret.
2. Review and merge the handover branch, then enable Pages with GitHub Actions
   as its publishing source.
3. Run the fixture refresh workflow and confirm matchweek one becomes final.
4. Create the reviewed Newcastle observation using the official result and
   compatible tactical-stat sources; leave PPDA/passing/crossing fields null
   unless they can be sourced precisely.
5. Rebuild and review the first production posterior.
6. Continue reviewing transfer and injury changes through the window close.
7. Replace provisional observation-variance hyperparameters only when a
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
