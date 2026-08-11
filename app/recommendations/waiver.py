"""Suggests free-agent pickups and which current bench player to drop.

The logic is intentionally simple and explainable: a free agent is
worth recommending if they project higher than a team's weakest bench
player at a compatible position. This keeps the reasoning inspectable
rather than hiding behind a black-box score.
"""

FLEX_COMPATIBLE = {"RB", "WR", "TE"}


def recommend_waivers(team, free_agents):
    """Return a list of pickup recommendations, each with a suggested drop."""
    bench = team.bench()
    recommendations = []

    for agent in free_agents:
        drop_candidate = _weakest_compatible_bench_player(bench, agent.position)
        if drop_candidate is None:
            continue

        point_gain = round(agent.projected_points - drop_candidate.projected_points, 1)
        if point_gain <= 0:
            continue

        recommendations.append({
            "add_name": agent.name,
            "add_position": agent.position,
            "add_team": agent.nfl_team,
            "add_projection": agent.projected_points,
            "percent_owned": agent.percent_owned,
            "trending": agent.trending,
            "drop_name": drop_candidate.name,
            "drop_projection": drop_candidate.projected_points,
            "point_gain": point_gain,
            "confidence": _confidence_for_gain(point_gain, agent),
            "projection_is_estimate": agent.projection_is_estimate,
            "explanation": (
                f"Add {agent.name} ({agent.nfl_team}, {agent.position}) and drop "
                f"{drop_candidate.name}. {agent.name} projects {point_gain} points higher "
                f"per week. {agent.note}"
            ),
        })

    recommendations.sort(key=lambda r: r["point_gain"], reverse=True)
    return recommendations


def _weakest_compatible_bench_player(bench, position):
    same_position = [p for p in bench if p.position == position]
    candidates = same_position

    if position in FLEX_COMPATIBLE and not candidates:
        candidates = [p for p in bench if p.position in FLEX_COMPATIBLE]

    if not candidates:
        return None

    return min(candidates, key=lambda p: p.projected_points)


def _confidence_for_gain(point_gain, agent):
    if point_gain >= 4 and agent.trending == "up":
        return "High"
    if point_gain >= 2:
        return "Medium"
    return "Low"
