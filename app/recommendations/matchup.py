"""Compares projected scores between two teams for the weekly matchup screen."""

from app.recommendations.lineup import optimal_lineup


def compare_matchup(matchup, current_week: int):
    my_lineup, _, _ = optimal_lineup(matchup.my_team, current_week)
    opp_lineup, _, _ = optimal_lineup(matchup.opponent_team, current_week)

    my_total = round(sum(p.projected_points for p in my_lineup.values() if p), 1)
    opp_total = round(sum(p.projected_points for p in opp_lineup.values() if p), 1)
    diff = round(my_total - opp_total, 1)

    if diff > 5:
        outlook = "Favored"
        summary = f"You are projected to win by {diff} points. Strong edge this week."
    elif diff > 0:
        outlook = "Slight Edge"
        summary = f"You are projected to win by a slim margin of {diff} points."
    elif diff == 0:
        outlook = "Toss-up"
        summary = "This matchup is projected to be a dead-even toss-up."
    elif diff > -5:
        outlook = "Slight Underdog"
        summary = f"You are projected to lose by a slim margin of {abs(diff)} points."
    else:
        outlook = "Underdog"
        summary = f"You are projected to lose by {abs(diff)} points. Consider all available upgrades."

    return {
        "week": current_week,
        "my_team_name": matchup.my_team.name,
        "opponent_team_name": matchup.opponent_team.name,
        "my_projected_total": my_total,
        "opponent_projected_total": opp_total,
        "point_difference": diff,
        "outlook": outlook,
        "summary": summary,
        "my_lineup": my_lineup,
        "opponent_lineup": opp_lineup,
    }
