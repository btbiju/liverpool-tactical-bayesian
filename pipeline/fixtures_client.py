"""
football-data.org client for Liverpool fixtures/results.

Reads the API key from the FOOTBALL_DATA_API_KEY environment variable --
never hardcoded, never committed. Set it locally with:

    export FOOTBALL_DATA_API_KEY=your_key_here

In GitHub Actions, this comes from a repo secret (see BACKLOG.md).

NOTE: as of this writing, this has not been live-tested against the real
API from within the development sandbox, because that environment's network
allowlist doesn't include api.football-data.org (unrelated to the key
itself). It's structurally correct per the documented API and will run in
any environment with normal internet access (GitHub Actions, a local
machine, etc.). Flagged in BACKLOG.md until confirmed with a real response.
"""
import os
import json
import urllib.request
import urllib.error

BASE_URL = "https://api.football-data.org/v4"
LIVERPOOL_TEAM_ID = 64  # football-data.org's internal ID for Liverpool FC


def _get_api_key():
    key = os.environ.get("FOOTBALL_DATA_API_KEY")
    if not key:
        raise RuntimeError(
            "FOOTBALL_DATA_API_KEY environment variable not set. "
            "Set it with: export FOOTBALL_DATA_API_KEY=your_key_here"
        )
    return key


def _request(path, params=None):
    url = f"{BASE_URL}{path}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"

    req = urllib.request.Request(url, headers={"X-Auth-Token": _get_api_key()})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"football-data.org returned HTTP {e.code}: {body}") from e


def get_liverpool_fixtures(status=None, date_from=None, date_to=None):
    """
    Fetch Liverpool fixtures. status can be 'SCHEDULED', 'FINISHED', 'LIVE', etc.
    date_from/date_to are 'YYYY-MM-DD' strings.
    Returns the raw list of match dicts from the API.
    """
    params = {}
    if status:
        params["status"] = status
    if date_from:
        params["dateFrom"] = date_from
    if date_to:
        params["dateTo"] = date_to

    data = _request(f"/teams/{LIVERPOOL_TEAM_ID}/matches", params)
    return data.get("matches", [])


def get_match_result(match_id):
    """Fetch full detail for one finished match, including score."""
    return _request(f"/matches/{match_id}")


def extract_match_observation(match, matchweek):
    """
    Convert a raw football-data.org match object into the
    match_observation shape expected by pipeline/bayesian_update.py.

    NOTE: football-data.org's free tier does NOT include possession%, PPDA,
    or formation -- those need a stats-capable source (FotMob, manually
    assisted) layered on top. This function only fills what's actually
    available (score, opponent, date); metrics/formation must be added
    separately before calling apply_matchweek(). Flagged in BACKLOG.md.
    """
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]
    is_home = "Liverpool" in home
    opponent = away if is_home else home
    score = match.get("score", {}).get("fullTime", {})
    home_goals, away_goals = score.get("home"), score.get("away")

    if home_goals is not None and away_goals is not None:
        gf = home_goals if is_home else away_goals
        ga = away_goals if is_home else home_goals
        result = f"{'W' if gf > ga else 'D' if gf == ga else 'L'} {gf}-{ga}"
    else:
        result = "TBD"

    return {
        "matchweek": matchweek,
        "date": match.get("utcDate", "")[:10],
        "opponent": f"{opponent} ({'H' if is_home else 'A'})",
        "result": result,
        "metrics": {},  # to be filled from a stats source before updating
        "formation": None,  # to be filled from a stats source before updating
    }


if __name__ == "__main__":
    # Structural check only -- will raise RuntimeError with a clear message
    # if run somewhere without network access to api.football-data.org.
    try:
        fixtures = get_liverpool_fixtures(status="SCHEDULED")
        print(f"Fetched {len(fixtures)} upcoming fixtures")
        if fixtures:
            print(json.dumps(fixtures[0], indent=2)[:500])
    except RuntimeError as e:
        print(f"Could not complete live test: {e}")
