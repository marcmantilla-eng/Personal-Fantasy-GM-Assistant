from app.models import Player, Team
from app.recommendations.alerts import build_alerts


def make_team(players):
    return Team("t1", "Test Team", players)


def test_bye_week_starter_triggers_high_confidence_alert():
    p = Player("1", "Bye Guy", "TE", "KC", bye_week=7, is_starter=True, roster_slot="TE")
    team = make_team([p])

    alerts = build_alerts(team, current_week=7)

    assert len(alerts) == 1
    assert alerts[0]["status"] == "Bye Week"
    assert alerts[0]["confidence"] == "High"
    assert "Bye Guy" in alerts[0]["message"]


def test_out_status_triggers_alert():
    p = Player("1", "Hurt Guy", "RB", "SEA", status="Out", is_starter=True, roster_slot="RB")
    team = make_team([p])

    alerts = build_alerts(team, current_week=5)

    assert len(alerts) == 1
    assert alerts[0]["status"] == "Out"
    assert alerts[0]["confidence"] == "High"


def test_questionable_status_triggers_lower_confidence_alert():
    p = Player("1", "Maybe Guy", "WR", "MIA", status="Questionable", is_starter=True, roster_slot="WR")
    team = make_team([p])

    alerts = build_alerts(team, current_week=5)

    assert alerts[0]["status"] == "Questionable"
    assert "Low" in alerts[0]["confidence"]


def test_healthy_starter_produces_no_alert():
    p = Player("1", "Fine Guy", "QB", "BUF", status="Healthy", is_starter=True, roster_slot="QB")
    team = make_team([p])

    alerts = build_alerts(team, current_week=5)

    assert alerts == []


def test_bench_players_are_never_alerted():
    p = Player("1", "Benched Byer", "RB", "SEA", bye_week=5, is_starter=False, roster_slot="BN")
    team = make_team([p])

    alerts = build_alerts(team, current_week=5)

    assert alerts == []


def test_alerts_sorted_most_severe_first():
    questionable = Player("1", "Q Guy", "WR", "MIA", status="Questionable", is_starter=True, roster_slot="WR")
    out = Player("2", "Out Guy", "RB", "SEA", status="Out", is_starter=True, roster_slot="RB")
    team = make_team([questionable, out])

    alerts = build_alerts(team, current_week=5)

    assert alerts[0]["player_name"] == "Out Guy"
    assert alerts[1]["player_name"] == "Q Guy"
