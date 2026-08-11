"""Figures out which players need the manager's attention this week.

This module only looks at player status fields — it doesn't know
anything about Flask, mock data, or Yahoo. That separation is what
lets it be tested on its own (see tests/test_alerts.py).
"""

from app.models import (
    STATUS_QUESTIONABLE, STATUS_INJURED, STATUS_OUT, STATUS_SUSPENDED, STATUS_BYE,
)

SEVERITY_ORDER = {"Out": 3, "Suspended": 3, "Injured": 2, "Bye Week": 2, "Questionable": 1}


def build_alerts(team, current_week: int):
    """Return a list of alert dicts for any starter that needs attention.

    Each alert explains, in plain language, what is wrong and how
    confident we are that it affects this week's lineup.
    """
    alerts = []
    for player in team.starters():
        if player.bye_week == current_week:
            alerts.append(_alert(player, STATUS_BYE,
                f"{player.name} is on a bye week and will score zero points. "
                f"You must replace them in your starting lineup.",
                confidence="High"))
        elif player.status == STATUS_OUT:
            alerts.append(_alert(player, STATUS_OUT,
                f"{player.name} is ruled OUT for this week and should be benched.",
                confidence="High"))
        elif player.status == STATUS_SUSPENDED:
            alerts.append(_alert(player, STATUS_SUSPENDED,
                f"{player.name} is suspended and cannot play this week.",
                confidence="High"))
        elif player.status == STATUS_INJURED:
            alerts.append(_alert(player, STATUS_INJURED,
                f"{player.name} is dealing with an injury. Their current projection "
                f"({player.projected_points} pts) is already reduced to reflect this, "
                f"but there is a real chance they are inactive on game day.",
                confidence="Medium"))
        elif player.status == STATUS_QUESTIONABLE:
            alerts.append(_alert(player, STATUS_QUESTIONABLE,
                f"{player.name} is listed as Questionable. They may play a limited role "
                f"or be a late scratch — consider your bench options as insurance.",
                confidence="Low-Medium"))

    alerts.sort(key=lambda a: SEVERITY_ORDER.get(a["status"], 0), reverse=True)
    return alerts


def _alert(player, status, message, confidence):
    return {
        "player_id": player.player_id,
        "player_name": player.name,
        "position": player.position,
        "status": status,
        "message": message,
        "confidence": confidence,
    }
