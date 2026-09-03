# Repository research agent

The research agent is a repository-owned, review-only workflow. Its scheduler,
prompt, schema, tests, and safety rules are version-controlled; it does not
depend on a long-running local assistant task.

## Responsibilities

The deterministic planner in `pipeline/research_agent.py` identifies two kinds
of work:

- `post_match`: the latest finished match is at least 24 hours old, another
  daily research pass is due, and Liverpool's next match has not kicked off.
- `pre_match`: Liverpool's next fixture is between 48 and 72 hours away.

When neither task is due, the workflow exits before reading an AI credential or
making an API request. When work is due, the model may use web search to create
a source-mapped JSON packet that validates against
`schema/agent_research_packet.schema.json`.

A forced run bypasses the schedule only for testing or an intentional manual
refresh. Its task rationale records the actual hours to kickoff and states when
the normal timing gate was bypassed; it must not describe an out-of-window run
as an ordinary scheduled run.

## Deliberate safety boundary

The generated packet is a GitHub Actions artifact retained for 30 days. It is
not committed, deployed, or copied into production data automatically. The
agent has read-only repository permissions and cannot update:

- `data/observations/`
- `data/posteriors/`
- the manager prior
- the lineup projection
- GitHub Pages

A reviewer must verify the cited pages, definitions, provider independence,
and uncertainty before transferring approved evidence into a research draft or
Game Plan change. Existing validators and tests then apply normally.

Every declared URL is compared with the API's web-search source record. An
ungrounded source is discarded together with every dependent claim or
recommendation. Claims and recommendations that cite an undeclared source ID
are discarded as well. The discarded counts are recorded as an uncertainty,
and all remaining grounded evidence must still pass strict validation.

Before discarding a URL, the provenance guard reconciles only harmless URL
presentation differences: host casing, default ports, fragments, a trailing
slash, and recognized marketing parameters. A normalized value is accepted
only when it maps to exactly one API-recorded URL, which then replaces the
model-proposed value. Schemes, paths, and meaningful query parameters remain
significant. Ambiguous matches fail closed.

If packet validation fails after the API response, the workflow uploads a
credential-free diagnostics JSON artifact containing the proposed source URLs,
the API provenance URLs, reconciliation decisions, tasks, and validation error.
It does not contain the API key or bypass validation, and no failed packet is
sent to the review console.

Every retained claim and recommendation must cite at least one grounded source.
For each pre-match task, validation also requires a complete projected XI, a
predicted score, and predicted goalscorer recommendation. These predictions are
low-confidence editorial outputs; their citations support the availability,
recent-selection, opponent, or player premises rather than the prediction
itself. The model receives the current player profiles as well as the squad,
manager prior, and existing lineup projection so matchup reasoning can use the
project's player evidence.

## Configuration

Add an Actions repository secret named `OPENAI_API_KEY`. Optionally add a
repository variable named `OPENAI_RESEARCH_MODEL`; otherwise the workflow uses
`gpt-5.6-luna`, the cost-conscious model for this bounded scheduled task. The
key is read only by a due run and must never be stored in a file, workflow log,
artifact, or commit.

The model service is an explicit external dependency of the optional research
step. The planner and all offline tests run without an API key or network
access.

## Commands

Preview due work without credentials or external calls:

```bash
python3 pipeline/research_agent.py --plan
```

Use a deterministic timestamp when testing timing behavior:

```bash
python3 pipeline/research_agent.py --plan --now 2026-09-02T15:00:00Z
```

Run a due research packet locally only when a real API key has been
intentionally exported:

```bash
OPENAI_API_KEY=... python3 pipeline/research_agent.py
```

Never paste the key into source, shell history, screenshots, or issue text.

## Review procedure

1. Download the `research-agent-packet-*` artifact from the workflow run.
2. Confirm every cited URL is accessible and supports the exact claim.
3. Reject claims whose metric definition, match scope, or measurement provider
   is ambiguous.
4. Treat repeated pages from one provider as one vote.
5. Keep missing evidence null and preserve conflicts.
6. Confirm that pre-match packets contain an opponent-specific XI, score, and
   goalscorer projection and that their reasoning uses current player and
   opponent evidence.
7. Transfer approved post-match evidence into `data/research_drafts/`, then run
   the deterministic resolver. Transfer approved pre-match recommendations into
   the lineup projection only through a normal reviewed pull request.
8. Run the full validation checklist before merging.
