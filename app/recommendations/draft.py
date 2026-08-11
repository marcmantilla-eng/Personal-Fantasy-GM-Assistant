"""Builds draft-day rankings adjusted for this league's needs.

Rankings start from a generic prospect list (base_rank / ADP) and then
get nudged based on:
  - roster positions this team still needs, and
  - how big a reach a pick would be versus typical draft position (ADP).

This never picks a player automatically — it only produces a sorted
list with explanations so the human drafter can decide.
"""

POSITION_TARGETS = {"QB": 1, "RB": 4, "WR": 4, "TE": 1, "K": 1, "DEF": 1}


def positional_needs(drafted_players_by_position: dict):
    """Given counts of already-drafted players per position, return remaining need per position."""
    needs = {}
    for position, target in POSITION_TARGETS.items():
        have = drafted_players_by_position.get(position, 0)
        needs[position] = max(target - have, 0)
    return needs


def build_draft_board(prospects, drafted_ids, drafted_players_by_position, weight_need: float = 1.0):
    """Return prospects sorted by adjusted rank, skipping already-drafted players.

    weight_need controls how strongly remaining positional need influences
    the ranking (0 = ignore need entirely, 1 = default, 2 = strongly prioritize need).
    """
    needs = positional_needs(drafted_players_by_position)
    available = [p for p in prospects if p.player_id not in drafted_ids]

    scored = []
    for prospect in available:
        need_at_position = needs.get(prospect.position, 0)
        need_bonus = need_at_position * 3.0 * weight_need
        reach_penalty = max(0.0, prospect.base_rank - prospect.adp) * 0.1
        adjusted_score = prospect.projected_season_points + need_bonus - reach_penalty

        scored.append({
            "player_id": prospect.player_id,
            "name": prospect.name,
            "position": prospect.position,
            "nfl_team": prospect.nfl_team,
            "bye_week": prospect.bye_week,
            "base_rank": prospect.base_rank,
            "adp": prospect.adp,
            "projected_season_points": prospect.projected_season_points,
            "adjusted_score": round(adjusted_score, 1),
            "team_need_level": need_at_position,
            "notes": prospect.notes,
            "explanation": _explain(prospect, need_at_position),
        })

    scored.sort(key=lambda s: s["adjusted_score"], reverse=True)
    for i, entry in enumerate(scored, start=1):
        entry["recommended_rank"] = i

    return scored


def _explain(prospect, need_at_position):
    if need_at_position >= 2:
        return (f"{prospect.name} ranks highly and fills a strong remaining need at "
                f"{prospect.position} (you still need {need_at_position}). {prospect.notes}")
    if need_at_position == 1:
        return (f"{prospect.name} fills your last remaining need at {prospect.position}. "
                f"{prospect.notes}")
    return f"{prospect.name} would be a depth/bench pick at {prospect.position} — no starting need remains. {prospect.notes}"
