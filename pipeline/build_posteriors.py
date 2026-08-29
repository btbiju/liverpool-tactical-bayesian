"""Deterministically rebuild posterior snapshots from validated observations."""

import argparse
import json
from pathlib import Path

try:
    from .bayesian_update import apply_matchweek
    from .validate_data import REPO_ROOT, ValidationError, validate_observations
except ImportError:  # Support direct execution: python3 pipeline/build_posteriors.py
    from bayesian_update import apply_matchweek
    from validate_data import REPO_ROOT, ValidationError, validate_observations


DEFAULT_PRIOR = REPO_ROOT / "data" / "manager_priors" / "iraola_2026.json"
DEFAULT_OBSERVATIONS = REPO_ROOT / "data" / "observations"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "posteriors"


def load_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def initial_state(prior):
    return {
        "as_of_matchweek": 0,
        "continuous_metrics": {
            name: {
                "mean": metric["mean"],
                "variance": metric["variance"],
                "effective_n": metric["pseudo_n"],
                "observation_variance": metric.get(
                    "observation_variance", metric["variance"] * metric["pseudo_n"]
                ),
            }
            for name, metric in prior["continuous_metrics"].items()
        },
        "formation_prior": prior["formation_prior"],
        "update_log": [],
    }


def observation_files(observations_dir):
    return sorted(
        path
        for path in observations_dir.glob("*.json")
        if not path.name.endswith(".template.json")
    )


def build_snapshots(
    prior_path=DEFAULT_PRIOR,
    observations_dir=DEFAULT_OBSERVATIONS,
    require_fixture_match=None,
):
    files = observation_files(observations_dir)
    if require_fixture_match is None:
        require_fixture_match = observations_dir.resolve() == DEFAULT_OBSERVATIONS.resolve()
    validate_observations(files, require_fixture_match=require_fixture_match)
    observations = sorted((load_json(path) for path in files), key=lambda item: item["matchweek"])
    state = initial_state(load_json(prior_path))
    snapshots = {}
    for observation in observations:
        state = apply_matchweek(state, observation)
        snapshots[f"matchweek_{observation['matchweek']:02d}.json"] = state
    return snapshots


def serialized_snapshots(snapshots):
    return {
        name: json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n"
        for name, snapshot in snapshots.items()
    }


def write_snapshots(snapshots, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    expected = set(snapshots)
    for path in output_dir.glob("*.json"):
        if path.name not in expected:
            path.unlink()
    for name, content in serialized_snapshots(snapshots).items():
        (output_dir / name).write_text(content, encoding="utf-8")


def check_snapshots(snapshots, output_dir):
    expected = serialized_snapshots(snapshots)
    actual_names = {path.name for path in output_dir.glob("*.json")} if output_dir.exists() else set()
    if actual_names != set(expected):
        raise ValidationError(
            f"posterior filenames are stale: expected {sorted(expected)}, found {sorted(actual_names)}"
        )
    for name, content in expected.items():
        if (output_dir / name).read_text(encoding="utf-8") != content:
            raise ValidationError(f"posterior snapshot is stale: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write rebuilt snapshots")
    mode.add_argument("--check", action="store_true", help="fail when committed snapshots are stale")
    parser.add_argument("--prior", type=Path, default=DEFAULT_PRIOR)
    parser.add_argument("--observations-dir", type=Path, default=DEFAULT_OBSERVATIONS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    snapshots = build_snapshots(args.prior, args.observations_dir)
    if args.write:
        write_snapshots(snapshots, args.output_dir)
        print(f"Wrote {len(snapshots)} posterior snapshot(s) to {args.output_dir}")
    else:
        check_snapshots(snapshots, args.output_dir)
        print(f"Posterior check passed: {len(snapshots)} snapshot(s) are current")


if __name__ == "__main__":
    main()
