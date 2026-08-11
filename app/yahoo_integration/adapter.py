"""Translates Yahoo's raw data shapes into this app's own Player/Team/
FreeAgent objects (app/models.py), so the rest of the app never has to know
what Yahoo's API looks like.

Yahoo's free API does not give us everything our dashboard wants to show:
  - No per-week point projection for a player.
  - No "how tough is this matchup" rating.
  - No opponent-team-this-week field on the roster itself.
Where that's true, we fill in an honest estimate computed from the
player's own recent/season scoring average (via Yahoo's real stats, not
invented numbers) and set projection_is_estimate=True so the dashboard can
label it clearly, per your instruction to estimate-and-label rather than
guess silently.

Bye week is different: it's a fixed schedule fact, not something to
estimate. If Yahoo's player-details response includes it (as
`bye_weeks`), we use that real value. If it's missing, we leave it as 0
(unknown) rather than making one up.
"""

from app.models import (
    Player, FreeAgent,
    STATUS_HEALTHY, STATUS_QUESTIONABLE, STATUS_INJURED, STATUS_OUT, STATUS_SUSPENDED,
)

# Yahoo's short status codes/text seen on rosters, mapped onto our simpler
# 5-state model. Unrecognized/blank codes default to healthy so we never
# accidentally bench a player who is actually fine.
_STATUS_MAP = {
    "": STATUS_HEALTHY,
    "Q": STATUS_QUESTIONABLE,
    "DTD": STATUS_QUESTIONABLE,
    "D": STATUS_QUESTIONABLE,
    "O": STATUS_OUT,
    "IR": STATUS_OUT,
    "PUP": STATUS_OUT,
    "NFI": STATUS_OUT,
    "NA": STATUS_OUT,
    "SUSP": STATUS_SUSPENDED,
}

# Yahoo's selected_position codes that mean "not in the starting lineup".
_NON_STARTING_SLOTS = {"BN", "IR"}


def _map_status(raw_status: str) -> str:
    return _STATUS_MAP.get((raw_status or "").strip().upper(), STATUS_HEALTHY)


def _primary_position(detail: dict, eligible_positions: list) -> str:
    """Best-guess primary position, preferring Yahoo's own primary_position
    field and falling back to the first non-flex eligible position."""
    if detail and detail.get("primary_position"):
        return detail["primary_position"]
    for pos in eligible_positions:
        if pos not in ("W/R/T", "W/T", "FLEX", "BN", "IR", "Util"):
            return pos
    return eligible_positions[0] if eligible_positions else "FLEX"

def _bye_week_from_detail(detail: dict) -> int:
    """Read Yahoo's own bye-week field if present. Never estimated."""
    if not detail:
        return 0
    bye = detail.get("bye_weeks")
    if isinstance(bye, dict) and bye.get("week"):
        try:
            return int(bye["week"])
        except (TypeError, ValueError):
            return 0
    return 0


def _estimate_points(stat_row: dict) -> float:
    """Pull a recent-form point estimate out of a player_stats() row.
    Yahoo's stats API reports total_points for the requested range; if it's
    missing we simply have no basis for an estimate and return 0.0."""
    if not stat_row:
        return 0.0
    try:
        return round(float(stat_row.get("total_points", 0.0)), 1)
    except (TypeError, ValueError):
        return 0.0


def _slot_for_roster_position(selected_position: str, position: str, slot_counts: dict) -> str:
    """Map Yahoo's selected_position onto this app's slot names, numbering
    duplicate RB/WR starting slots (RB1/RB2, WR1/WR2) in the order they're
    encountered, matching app/models.py's ROSTER_SLOTS."""
    if selected_position in _NON_STARTING_SLOTS:
        return "BN"
    if selected_position in ("W/R/T", "W/T", "FLEX", "Util"):
        return "FLEX"
    if selected_position in ("RB", "WR"):
        slot_counts[selected_position] = slot_counts.get(selected_position, 0) + 1
        return f"{selected_position}{slot_counts[selected_position]}"
    return selected_position


def adapt_roster(raw_roster: list, details_by_id: dict, stats_by_id: dict) -> list:
    """Turn Team.roster()'s raw entries into a list of app.models.Player.

    details_by_id: player_id -> League.player_details() dict (for nfl_team,
        bye week, primary position).
    stats_by_id: player_id -> League.player_stats() row (for the recent-form
        point estimate).
    """
    players = []
    slot_counts = {}

    for raw in raw_roster:
        player_id = str(raw["player_id"])
        detail = details_by_id.get(raw["player_id"], {})
        stat_row = stats_by_id.get(raw["player_id"], {})

        position = _primary_position(detail, raw.get("eligible_positions", []))
        estimate = _estimate_points(stat_row)
        selected_position = raw.get("selected_position", "BN")
        slot = _slot_for_roster_position(selected_position, position, slot_counts)

        players.append(Player(
            player_id=player_id,
            name=raw["name"],
            position=position,
            nfl_team=detail.get("editorial_team_abbr", "").upper() or "FA",
            status=_map_status(raw.get("status", "")),
            bye_week=_bye_week_from_detail(detail),
            projected_points=estimate,
            recent_avg_points=estimate,
            matchup_quality="Unknown",
            opponent="",
            is_starter=selected_position not in _NON_STARTING_SLOTS,
            roster_slot=slot,
            projection_is_estimate=True,
        ))

    return players


def adapt_free_agent(raw: dict, detail: dict, stat_row: dict) -> FreeAgent:
    """Turn one League.free_agents() entry into an app.models.FreeAgent."""
    estimate = _estimate_points(stat_row)
    return FreeAgent(
        player_id=str(raw["player_id"]),
        name=raw["name"],
        position=_primary_position(detail, raw.get("eligible_positions", [])),
        nfl_team=detail.get("editorial_team_abbr", "").upper() or "FA",
        projected_points=estimate,
        recent_avg_points=estimate,
        percent_owned=float(raw.get("percent_owned", 0) or 0),
        trending="steady",
        note="Estimate based on recent scoring average (Yahoo doesn't publish free agent projections).",
        projection_is_estimate=True,
    )
