# Repository instructions

## Project purpose

This is a portfolio project for technical consulting, data, and AI roles. It
models Liverpool FC's evolving tactical identity under Andoni Iraola during
the 2026/27 season. The distinguishing idea is not another football-statistics
dashboard: it is an auditable example of reasoning under uncertainty that
changes as real evidence arrives.

The model begins with a tactical prior derived from Iraola's three Bournemouth
seasons and player-level career/playstyle profiles. Weekly match observations
are intended to update that prior into posterior snapshots. A static React
dashboard presents the fixtures, squad, projected lineup, tactical prior, and
eventual posterior history.

## Architecture and data flow

1. `data/manager_priors/iraola_2026.json` contains the manager prior.
2. `data/squad/` and `data/player_profiles/` contain the current squad and
   player-level inputs.
3. `pipeline/fixtures_client.py` and `pipeline/pull_fixtures.py` retrieve
   fixture/result records from football-data.org.
4. A finished football-data.org result may automatically create a result-only
   observation that updates goals conceded and leaves every tactical field
   null. Possession, PPDA, formation, xG, and related evidence must still be
   enriched separately.
5. Delayed web research may collect source-mapped candidates in
   `data/research_drafts/`; these drafts never update the model directly.
   The optional repository research agent may propose evidence in a temporary
   GitHub Actions artifact, but it has read-only repository permissions and
   cannot promote or deploy its output.
6. Every observation in `data/observations/` must declare whether it is
   `automated_result_only` or `human_reviewed`, cite every non-null field, and
   validate against `schema/match_observation.schema.json`. Automation must
   never overwrite a human-reviewed observation.
7. `pipeline/build_posteriors.py` deterministically rebuilds the snapshot series
   through `pipeline/bayesian_update.py`.
8. `dashboard/scripts/sync-data.mjs` copies committed JSON into ignored
   `dashboard/public/data/` before development and builds.
9. The React/Vite dashboard is intended for static GitHub Pages deployment.

## Bayesian methodology

- Continuous tactical metrics are intended to use Normal-Normal conjugate
  updates with explicit prior and observation uncertainty.
- Formation choice uses a Dirichlet-Multinomial update.
- Prior influence must decline as observed matches accumulate; implementations
  must demonstrate this behavior in deterministic tests.
- Possession is bounded and would be modeled more precisely with a Beta-family
  model. The Normal approximation is an explicit, documented simplification,
  not a claim of textbook purity.
- Formation alpha values are currently calibrated illustrative pseudo-counts,
  not literal match-by-match formation tallies.
- Do not describe projection-layer role text or predicted lineups as confirmed
  team news. Clearly distinguish sourced facts, model outputs, and editorial
  tactical interpretation.

## Working agreements

- Keep `BACKLOG.md` as the durable record of open work, known gaps, completed
  milestones, and important decisions. Update it when project state changes.
- Never invent a statistic or select a plausible value to fill a gap. Use
  `null`, lower confidence, or an explicit note when evidence is unavailable or
  contradictory.
- Preserve provenance and uncertainty. When sources disagree, record the
  disagreement and why one value was selected.
- Resolve conflicts only among compatible definitions and independent
  measurement providers. Prefer unanimity or a strict majority. If compatible
  numeric providers have no majority, an arithmetic mean may be retained only
  as a labeled derived consensus with every input and the full range preserved;
  categorical claims must never be averaged.
- Do not reintroduce the archived historical analysis into the main product
  unless it gains a real data-flow or narrative connection to the Bayesian
  model. A focused portfolio story is more valuable than unrelated features.
- Prefer small, auditable transformations over opaque model logic.
- Avoid systematic scraping that conflicts with a source's terms. The fixture
  workflow may poll the authorized football-data.org API around expected full
  time, but tactical websites must not be systematically scraped.
- Do not commit generated dashboard data, build output, dependencies, caches,
  editor settings, OS metadata, or local credentials.

## Data-source hierarchy

Use sources in this order when practical:

1. Official club or league statements for transfers, appointments, injuries,
   and other discrete facts.
2. FotMob for current squad truth, career stints, and current statistics.
3. Reputable statistical or tactical analysis citing Opta or equivalent data.
4. Mainstream sports reporting for corroborating discrete facts.
5. Wikipedia only as a last-resort cross-check, never the primary source for
   time-sensitive data.

FotMob pages may be client-rendered and its terms do not permit systematic
scraping. FBref and FootyStats have returned bot-block responses. Understat's
accessible archived coverage is historical. football-data.org is the stable
fixture/result source but is not a tactical-statistics provider.

## Repository layout

- `schema/`: JSON Schemas for manager prior, player profile, and posterior.
- `data/manager_priors/`: sourced/calibrated manager prior.
- `data/squad/`: current squad snapshot.
- `data/player_profiles/`: one profile per squad player.
- `data/fixtures/`: raw football-data.org fixtures/results.
- `data/observations/`: field-cited observations, either automated result-only
  records or human-reviewed tactical evidence.
- `data/research_drafts/`: delayed web-research evidence packets; never direct
  posterior inputs.
- `data/posteriors/`: posterior snapshots, expected to grow during the season.
- `pipeline/`: Python fixture client, pull command, and Bayesian update engine.
- `prompts/`: version-controlled instructions for the optional review-only
  repository research agent.
- `dashboard/`: React/Vite static dashboard.
- `archive/`: ignored historical reference work with no current production
  data flow; do not modify or ship it casually.

## Validation requirements

Before handing off a material change, run checks proportionate to its scope:

- `cd dashboard && npm run lint`
- `cd dashboard && npm run build`
- `python3 -m unittest discover -s tests -v`
- `python3 pipeline/validate_data.py`
- `python3 pipeline/build_posteriors.py --check`
- `python3 -m compileall -q pipeline`
- The offline validator must parse committed JSON, apply the repository schemas,
  and check squad/profile identifiers, names, and squad numbers.
- Add or run deterministic pipeline tests for any modeling change.
- Validate research drafts and run their deterministic conflict resolver when
  collection or consensus logic changes.
- Confirm `git status --short` contains no generated `dist/`, `public/data/`,
  `node_modules/`, bytecode, secrets, or unrelated files.

Do not run live API calls during routine validation. Tests must not require a
real credential or external writes.

## Security and deployment

- Never hardcode credentials. Read `FOOTBALL_DATA_API_KEY` from the environment
  locally and use a GitHub Actions secret for automation.
- The optional research agent reads `OPENAI_API_KEY` only on a due GitHub
  Actions run. Its output is an untrusted review artifact, never a direct
  production input. The project must not depend on a local assistant task or
  desktop schedule for normal operation.
- Do not commit `.env` files, local agent/editor permissions, access tokens, or
  API responses that contain private account data.
- If a credential is found in any local file, redact it in reports, remove the
  file if it is disposable, and ask the owner to rotate it. Do not rotate or
  revoke credentials automatically.
- Run a history-aware secret scanner before making the portfolio repository
  public.
- Keep deployment static and cost-conscious. GitHub Actions and GitHub Pages
  are the intended hosting path; there should be no always-on server.
- Automation must validate data and build output before updating or deploying
  the public site.
