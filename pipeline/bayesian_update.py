"""
Bayesian tactical identity model.

Two conjugate update mechanisms, chosen to match the data type rather than
forcing everything into one distribution:

1. Continuous metrics (possession%, PPDA, shots on target, etc.)
   -> Normal-Normal conjugate update, known-variance case.
      This is a simplification: possession% is technically bounded [0,100]
      and better modeled with a Beta distribution, but Normal is close enough
      given values cluster well away from the boundaries (40-65% range), and
      it keeps every continuous metric under one simple, explainable formula.

2. Formation choice (categorical: 4-2-3-1, 4-1-4-1, etc.)
   -> Dirichlet-Multinomial conjugate update. This one IS the textbook-correct
      model for categorical data -- no approximation needed.

Both mechanisms share the same qualitative behavior: the prior's influence
shrinks automatically as more matches are observed, with no manual decay
schedule required. That's the actual point of using conjugate priors instead
of a hand-rolled weighted average.
"""
import json
from datetime import date


def update_normal_normal(prior_mean, prior_variance, pseudo_n, observed_value, observation_variance=None):
    """
    Fold one new observed match value into a Normal-Normal conjugate prior.

    prior_mean, prior_variance : current belief, N(prior_mean, prior_variance)
    pseudo_n                   : the prior's weight in equivalent 'virtual matches'
    observed_value              : the new match's actual value for this metric
    observation_variance        : how noisy a single match's reading is.
                                   Defaults to prior_variance if not given --
                                   i.e. assume one match is about as
                                   informative as the prior's per-match unit.

    Returns (posterior_mean, posterior_variance, new_pseudo_n).
    new_pseudo_n increases by 1 each call -- this is what makes the prior's
    grip loosen automatically as the season goes on, with no decay schedule
    to hand-tune.
    """
    if observation_variance is None:
        observation_variance = prior_variance

    posterior_mean = (
        observation_variance * prior_mean + prior_variance * observed_value
    ) / (observation_variance + prior_variance)

    posterior_variance = (prior_variance * observation_variance) / (
        prior_variance + observation_variance
    )

    return posterior_mean, posterior_variance, pseudo_n + 1


def update_dirichlet(alpha_counts, observed_formation):
    """
    Fold one observed match's formation into a Dirichlet prior over formations.

    alpha_counts       : dict of {formation: pseudo_count}
    observed_formation : the formation string actually used this match

    Dirichlet-Multinomial conjugacy: the posterior is just prior counts + 1
    for whichever formation was observed. Formations never seen in the prior
    get an 'other' bucket rather than being impossible.
    """
    updated = dict(alpha_counts)
    key = observed_formation if observed_formation in updated else "other"
    updated[key] = updated.get(key, 0) + 1
    return updated


def formation_probabilities(alpha_counts):
    """Convert Dirichlet alpha counts into a normalized probability per formation."""
    total = sum(alpha_counts.values())
    return {k: round(v / total, 3) for k, v in alpha_counts.items()}


def apply_matchweek(prior_state, match_observation):
    """
    Apply one matchweek's observed data to the current posterior state,
    returning the new state plus a human-readable log entry.

    match_observation: {
        'matchweek': int, 'date': str, 'opponent': str, 'result': str,
        'metrics': {'possession_pct': 47.2, 'ppda': 8.1, ...},
        'formation': '4-2-3-1'
    }
    """
    new_metrics = {}
    shifts = []

    for name, dist in prior_state["continuous_metrics"].items():
        if name in match_observation.get("metrics", {}):
            observed = match_observation["metrics"][name]
            new_mean, new_var, new_n = update_normal_normal(
                dist["mean"], dist["variance"], dist.get("effective_n", dist.get("pseudo_n")), observed
            )
            shift = new_mean - dist["mean"]
            if abs(shift) > 0.01:
                direction = "up" if shift > 0 else "down"
                shifts.append(
                    f"{name}: {dist['mean']:.2f} -> {new_mean:.2f} ({direction} {abs(shift):.2f}, "
                    f"observed {observed})"
                )
            new_metrics[name] = {"mean": round(new_mean, 3), "variance": round(new_var, 4), "effective_n": new_n}
        else:
            new_metrics[name] = dist

    new_formation_alpha = prior_state["formation_prior"]["alpha"]
    if "formation" in match_observation:
        new_formation_alpha = update_dirichlet(new_formation_alpha, match_observation["formation"])

    log_entry = {
        "matchweek": match_observation["matchweek"],
        "date": match_observation["date"],
        "opponent": match_observation["opponent"],
        "result": match_observation["result"],
        "metrics_observed": match_observation.get("metrics", {}),
        "notable_shifts": shifts,
    }

    return {
        "as_of_matchweek": match_observation["matchweek"],
        "continuous_metrics": new_metrics,
        "formation_prior": {"alpha": new_formation_alpha},
        "update_log": prior_state.get("update_log", []) + [log_entry],
    }


if __name__ == "__main__":
    # Smoke test using the real Iraola prior + one hypothetical observed match
    with open("/home/claude/liverpool-analytics/data/manager_priors/iraola_2026.json") as f:
        prior = json.load(f)

    state = {
        "as_of_matchweek": 0,
        "continuous_metrics": {
            k: {"mean": v["mean"], "variance": v["variance"], "effective_n": v["pseudo_n"]}
            for k, v in prior["continuous_metrics"].items()
        },
        "formation_prior": prior["formation_prior"],
        "update_log": [],
    }

    hypothetical_match = {
        "matchweek": 1,
        "date": "2026-08-23",
        "opponent": "Newcastle United (A)",
        "result": "TBD",
        "metrics": {"possession_pct": 46.5, "ppda": 8.9, "goals_conceded_per_match": 1},
        "formation": "4-2-3-1",
    }

    new_state = apply_matchweek(state, hypothetical_match)
    print(json.dumps(new_state, indent=2))
