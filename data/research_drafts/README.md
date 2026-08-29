# Post-match research drafts

These files are evidence packets, not production model inputs. A delayed
research pass may collect explicit numerical claims and tactical observations
from permitted web sources here without changing `data/observations/` or the
posterior.

Each candidate records its source, measurement provider, compatibility group,
and exact evidence location (page section or video timestamp). A second page
repeating the same provider's data is corroboration, but not an independent
vote. Qualitative analysis may be retained in notes; it must not be converted
into an invented number.

Run the deterministic resolver with:

```sh
python3 pipeline/resolve_research_draft.py data/research_drafts/MATCH.json --write
```

The resolver uses these rules:

1. Exclude candidates that are not explicitly eligible for consensus.
2. Compare only values with the same metric definition and match scope.
3. Count each disclosed measurement provider once, even if several pages
   repeat its value.
4. Use unanimity or a strict independent-provider majority when one exists.
5. With at least two compatible numeric providers but no majority, record the
   arithmetic mean, full range, between-provider variance, and
   `mean_consensus` label.
6. Never average formations or other categorical claims.

An average is a transparent derived estimate, not a directly sourced fact. It
must receive additional uncertainty during review by adding the recorded
between-provider variance to the normal single-match observation variance. It
must never be promoted silently. `ready_for_review` means resolution logic ran
successfully; it does not mean the draft is approved for the Bayesian model.
