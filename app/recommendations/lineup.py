"""Works out the strongest legal starting lineup for a team.

"Legal" means it respects the roster slot rules (1 QB, 2 RB, 2 WR, 1 TE,
1 FLEX, 1 K, 1 DEF) and never starts a player who is on a bye or ruled
out. Within those rules, it picks the combination of players with the
highest total projected points.
"""

from app.models import ROSTER_SLOTS, FLEX_ELIGIBLE, STATUS_OUT, STATUS_SUSPENDED


def _eligible(players, current_week):
    """Players who could reasonably be started this week."""
    return [p for p in players
            if p.bye_week != current_week and p.status not in (STATUS_OUT, STATUS_SUSPENDED)]


def _base_position(slot: str) -> str:
    """Strip the trailing slot index, e.g. 'RB1' -> 'RB', 'QB' -> 'QB'."""
    return slot.rstrip("0123456789")


def optimal_lineup(team, current_week: int):
    """Return (lineup, bench, swaps) for the best legal starting lineup.

    lineup: dict of slot_name -> Player (or None if unfillable)
    bench: list of Players not in the lineup
    swaps: list of plain-language change descriptions vs. the team's
           current is_starter flags, so the dashboard can show
           "Start X instead of Y" recommendations.
    """
    pool = _eligible(team.players, current_week)
    pool_by_id = {p.player_id: p for p in pool}
    remaining = list(pool)
    remaining.sort(key=lambda p: p.projected_points, reverse=True)

    lineup = {}
    used_ids = set()

    # Fill fixed-position slots first (QB, RB, RB, WR, WR, TE, K, DEF),
    # then FLEX last so FLEX gets whichever eligible player is left over.
    fixed_slots = [s for s in ROSTER_SLOTS if s != "FLEX"]
    flex_slots = [s for s in ROSTER_SLOTS if s == "FLEX"]

    for slot in fixed_slots:
        candidates = [p for p in remaining
                      if p.position == _base_position(slot) and p.player_id not in used_ids]
        if candidates:
            best = max(candidates, key=lambda p: p.projected_points)
            lineup[slot] = best
            used_ids.add(best.player_id)
        else:
            lineup[slot] = None

    for slot in flex_slots:
        candidates = [p for p in remaining
                      if p.position in FLEX_ELIGIBLE and p.player_id not in used_ids]
        if candidates:
            best = max(candidates, key=lambda p: p.projected_points)
            lineup[slot] = best
            used_ids.add(best.player_id)
        else:
            lineup[slot] = None

    bench = [p for p in team.players if p.player_id not in used_ids]

    swaps = _describe_swaps(team, lineup, used_ids, pool_by_id)

    return lineup, bench, swaps


def _describe_swaps(team, lineup, used_ids, pool_by_id):
    """Plain-language explanations for any change vs. current starters."""
    current_starter_ids = {p.player_id for p in team.starters()}
    swaps = []

    for slot, player in lineup.items():
        if player is None:
            continue
        if player.player_id in current_starter_ids:
            continue
        # This player is newly recommended to start. Find who they likely replace:
        # whichever currently-starting player at a similar slot got benched.
        swaps.append({
            "action": "start",
            "player_name": player.name,
            "slot": slot,
            "reason": _reason_for_start(player, team),
        })

    for player in team.starters():
        if player.player_id not in used_ids:
            swaps.append({
                "action": "bench",
                "player_name": player.name,
                "slot": player.roster_slot,
                "reason": _reason_for_bench(player),
            })

    return swaps


def _reason_for_start(player, team):
    if player.matchup_quality in ("Great", "Good"):
        return (f"{player.name} has a favorable matchup ({player.matchup_quality.lower()} matchup "
                f"vs {player.opponent}) and a strong projection of {player.projected_points} points.")
    return f"{player.name} projects for {player.projected_points} points, the best available option for this slot."


def _reason_for_bench(player):
    if player.bye_week:
        return f"{player.name} is on a bye week and cannot score."
    if player.status in (STATUS_OUT, STATUS_SUSPENDED):
        return f"{player.name} is unavailable this week ({player.status})."
    return f"{player.name}'s projection ({player.projected_points} pts) is lower than other options this week."


def starter_vs_bench_comparisons(team, current_week: int):
    """For each starting slot, compare the current starter to the best bench alternative
    at a compatible position, with a plain-language explanation.
    """
    lineup, bench, _ = optimal_lineup(team, current_week)
    comparisons = []

    for slot, recommended in lineup.items():
        current = next((p for p in team.players if p.roster_slot == slot and p.is_starter), None)
        if current is None or recommended is None:
            continue
        if current.player_id == recommended.player_id:
            continue

        comparisons.append({
            "slot": slot,
            "current_starter": current.name,
            "current_points": current.projected_points,
            "recommended_starter": recommended.name,
            "recommended_points": recommended.projected_points,
            "point_difference": round(recommended.projected_points - current.projected_points, 1),
            "explanation": (
                f"Start {recommended.name} ({recommended.projected_points} pts, "
                f"{recommended.matchup_quality.lower()} matchup vs {recommended.opponent}) "
                f"over {current.name} ({current.projected_points} pts). "
                f"Recent form: {recommended.name} averaged {recommended.recent_avg_points} pts "
                f"over recent games vs {current.name}'s {current.recent_avg_points}."
            ),
        })

    return comparisons
