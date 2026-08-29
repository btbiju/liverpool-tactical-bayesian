# Matchweek observation workflow

## Purpose

The Bayesian engine may receive either human-reviewed tactical evidence or a
strictly result-only observation generated from a finished API record. Each
production observation lives in `data/observations/`, declares its
`observation_kind`, cites every non-null field, and validates against
`schema/match_observation.schema.json` before it can generate a posterior.

The workflow deliberately separates collection from inference:

```text
football-data.org fixture/result
            +
reviewed tactical match facts
            +
field-level source citations
            ↓
validated match observation
            ↓
deterministic posterior rebuild
```

## Field sourcing

| Field | Preferred source | Fallback and rule |
|---|---|---|
| Match ID, date, opponent, score | football-data.org fixture record | Official Premier League match page if the API record is delayed |
| Goals conceded | Derived directly from the verified final score | Never take it from a tactical-stat summary |
| Possession | Official league match statistics | FotMob match facts when the official page does not expose it |
| Shots on target | Official league match statistics | FotMob match facts |
| Accurate passes | FotMob match facts | Leave null unless another reputable source defines the same metric clearly |
| Accurate crosses | FotMob match facts | Leave null unless the definition is compatible |
| Formation | Official lineup or FotMob lineup | Record the starting formation; explain later tactical changes in notes |
| PPDA | Reputable Opta-derived analysis or a documented event-data calculation | Leave null when neither is available; never infer it from possession or pressing descriptions |

FotMob may be used for a single reviewed match, but must not be polled or
systematically scraped. Source URLs and access dates belong in the observation,
and every non-null metric must reference at least one declared source ID.

## Review procedure

1. Refresh the raw fixture/result with `pipeline/pull_fixtures.py` only when a
   real `FOOTBALL_DATA_API_KEY` is intentionally configured.
2. Confirm that the raw fixture status is `FINISHED` and that its score, date,
   opponent, matchweek, result string, and goals-conceded value agree with the
   proposed observation. Production validation enforces the final four fields.
3. Collect the tactical facts using the hierarchy in `AGENTS.md`.
4. Copy `data/observations/observation.template.json` to a match-specific name
   such as `matchweek_01_560550.json`.
5. Enter only values actually exposed by the cited source. Keep unavailable
   values null. Do not convert prose such as “pressed intensely” into PPDA.
6. Populate `sources` and map each non-null metric plus `formation` through
   `metric_sources`.
7. Run `python3 pipeline/validate_data.py`.
8. Rebuild deterministically with `python3 pipeline/build_posteriors.py --write`.
9. Run the unit tests, validator, dashboard lint, and dashboard build.
10. Review the posterior shifts for plausibility and provenance before merging.

## Observation-variance policy

The manager prior now records explicit single-match variances. They are
modeling hyperparameters, not claimed historical statistics. Each is currently
calibrated as `prior mean variance × pseudo_n`, which makes the preseason prior
equivalent to ten equally noisy virtual matches:

| Metric | Single-match variance | Implied standard deviation |
|---|---:|---:|
| Possession percentage | 40.0 | 6.32 percentage points |
| PPDA | 15.0 | 3.87 |
| Shots on target | 3.0 | 1.73 per match |
| Goals conceded | 0.8 | 0.89 per match |
| Accurate passes | 1000.0 | 31.62 per match |
| Accurate crosses | 3.0 | 1.73 per match |

This policy is transparent and internally consistent, but still provisional.
Replace a value only with a documented calibration from comparable match-level
data. A one-off `observation_variances` override is allowed only when the
measurement itself has meaningfully different uncertainty and the reason is
recorded in observation notes.

## Automation boundary

The scheduled workflow checks whether an unfinished fixture is near expected
full time before calling football-data.org. Once the raw record reaches
`FINISHED`, `pipeline/sync_result_observations.py` may create an
`automated_result_only` observation and deterministically rebuild the posterior.
That record may update only `goals_conceded_per_match`, which follows exactly
from the final score. All tactical metrics and formation remain null.

Automation never overwrites a `human_reviewed` observation. A later review may
enrich the result-only file with compatible tactical evidence and change its
kind to `human_reviewed`; the deterministic rebuild then replaces the snapshot
without counting the match twice. No tactical website is polled or scraped.
