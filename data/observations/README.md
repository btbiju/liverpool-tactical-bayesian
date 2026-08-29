# Reviewed match observations

Production observations are added here only after a Liverpool match is final
and its tactical fields have been reviewed and cited according to
`docs/MATCHWEEK_WORKFLOW.md`.

Automated web discovery belongs in `data/research_drafts/`. A
`ready_for_review` research draft is not consumed by the posterior builder and
must not be copied here without reviewing its provenance, compatibility, and
any derived consensus value.

Copy `observation.template.json` to `matchweek_NN_MATCHID.json`, replace every
placeholder, validate it, and rebuild posterior snapshots. The template itself
is not consumed by the pipeline.
