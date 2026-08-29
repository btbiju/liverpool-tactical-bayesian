"""Resolve compatible, independently sourced claims in a research draft.

The resolver preserves every candidate. It first collapses duplicate pages
that rely on the same measurement provider, then looks for unanimity or a
strict majority. When numeric providers still disagree, their arithmetic mean
is recorded as a derived consensus together with the full range. Categorical
claims are never averaged.

The output remains a research draft. This command does not alter production
observations or posterior snapshots.
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

try:
    from .validate_data import REPO_ROOT, validate_file
except ImportError:  # Support direct execution.
    from validate_data import REPO_ROOT, validate_file


RESEARCH_SCHEMA = REPO_ROOT / "schema" / "research_draft.schema.json"


def _unresolved(rationale, compatibility_group=None):
    return {
        "status": "unresolved",
        "value": None,
        "method": "unresolved",
        "source_ids": [],
        "measurement_providers": [],
        "compatibility_group": compatibility_group,
        "range": None,
        "between_provider_variance": None,
        "rationale": rationale,
    }


def _provider_claims(candidates):
    """Return one independent claim per provider or an ambiguity message."""
    by_provider = defaultdict(list)
    for candidate in candidates:
        if candidate.get("eligible_for_consensus", False):
            by_provider[candidate["measurement_provider"]].append(candidate)

    claims = []
    ambiguous = []
    for provider, items in sorted(by_provider.items()):
        values = {item["value"] for item in items}
        if len(values) != 1:
            ambiguous.append(provider)
            continue
        claims.append(
            {
                "provider": provider,
                "value": items[0]["value"],
                "source_ids": sorted({item["source_id"] for item in items}),
            }
        )
    return claims, ambiguous


def resolve_metric(candidates):
    eligible = [item for item in candidates if item.get("eligible_for_consensus", False)]
    if not eligible:
        return _unresolved("No candidate is eligible for consensus.")

    groups = defaultdict(list)
    for candidate in eligible:
        groups[candidate["compatibility_group"]].append(candidate)
    provider_counts = {
        group: len({item["measurement_provider"] for item in items})
        for group, items in groups.items()
    }
    largest_count = max(provider_counts.values())
    largest_groups = [group for group, count in provider_counts.items() if count == largest_count]
    if len(largest_groups) != 1:
        return _unresolved(
            "No unique compatibility group has the broadest independent-provider coverage."
        )

    group = largest_groups[0]
    claims, ambiguous = _provider_claims(groups[group])
    if ambiguous:
        return _unresolved(
            "A measurement provider published conflicting values: " + ", ".join(ambiguous),
            group,
        )
    if len(claims) < 2:
        return _unresolved(
            "At least two independent measurement providers are required.", group
        )

    values = [claim["value"] for claim in claims]
    value_types = {"number" if isinstance(value, (int, float)) else "string" for value in values}
    if len(value_types) != 1:
        return _unresolved("Compatible candidates use incompatible value types.", group)

    counts = Counter(values)
    winning_value, winning_count = counts.most_common(1)[0]
    if winning_count == len(values):
        method = "unanimous"
        resolved_value = winning_value
        selected = claims
    elif winning_count > len(values) / 2:
        method = "majority"
        resolved_value = winning_value
        selected = [claim for claim in claims if claim["value"] == winning_value]
    elif value_types == {"number"}:
        method = "mean_consensus"
        resolved_value = round(sum(values) / len(values), 3)
        selected = claims
    else:
        return _unresolved(
            "Categorical candidates have no strict majority and cannot be averaged.", group
        )

    source_ids = sorted(
        {source_id for claim in selected for source_id in claim["source_ids"]}
    )
    providers = sorted(claim["provider"] for claim in selected)
    value_range = None
    between_provider_variance = None
    if value_types == {"number"}:
        value_range = {"minimum": min(values), "maximum": max(values)}
        provider_mean = sum(values) / len(values)
        between_provider_variance = round(
            sum((value - provider_mean) ** 2 for value in values) / len(values), 4
        )
    rationale = {
        "unanimous": "Independent measurement providers report the same compatible value.",
        "majority": "A strict majority of independent measurement providers report this value.",
        "mean_consensus": (
            "No strict majority exists; this is the arithmetic mean of compatible independent "
            "provider values and must be labeled as derived when reviewed."
        ),
    }[method]
    return {
        "status": "resolved",
        "value": resolved_value,
        "method": method,
        "source_ids": source_ids,
        "measurement_providers": providers,
        "compatibility_group": group,
        "range": value_range,
        "between_provider_variance": between_provider_variance,
        "rationale": rationale,
    }


def resolve_draft(draft):
    draft["resolutions"] = {
        metric: resolve_metric(candidates)
        for metric, candidates in sorted(draft.get("candidates", {}).items())
    }
    draft["status"] = "ready_for_review"
    return draft


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("draft", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    validate_file(args.draft, RESEARCH_SCHEMA)
    with args.draft.open(encoding="utf-8") as handle:
        draft = resolve_draft(json.load(handle))
    rendered = json.dumps(draft, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        args.draft.write_text(rendered, encoding="utf-8")
        validate_file(args.draft, RESEARCH_SCHEMA)
        print(f"Resolved research draft: {args.draft}")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
