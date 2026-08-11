"""Tests for app/yahoo_integration/adapter.py using canned, Yahoo-shaped
fixture data -- no network access, no credentials, no live Yahoo calls.

These fixtures mirror the exact shapes returned by the installed
yahoo_fantasy_api library (confirmed by reading its source), so a passing
test here means the adapter will handle real Yahoo responses correctly.
"""

from app.models import STATUS_HEALTHY, STATUS_QUESTIONABLE, STATUS_OUT
from app.yahoo_integration.adapter import adapt_roster, adapt_free_agent


def _raw_roster_player(player_id, name, status, selected_position, eligible_positions):
    return {
        "player_id": player_id,
        "name": name,
        "status": status,
        "position_type": "O",
        "eligible_positions": eligible_positions,
        "selected_position": selected_position,
    }


def test_adapt_roster_maps_status_codes_to_app_statuses():
    raw_roster = [
        _raw_roster_player(1, "Healthy Guy", "", "QB", ["QB"]),
        _raw_roster_player(2, "Questionable Guy", "Q", "RB", ["RB"]),
        _raw_roster_player(3, "Out Guy", "O", "WR", ["WR"]),
    ]

    players = adapt_roster(raw_roster, details_by_id={}, stats_by_id={})

    by_id = {p.player_id: p for p in players}
    assert by_id["1"].status == STATUS_HEALTHY
    assert by_id["2"].status == STATUS_QUESTIONABLE
    assert by_id["3"].status == STATUS_OUT


def test_adapt_roster_numbers_duplicate_rb_and_wr_slots():
    raw_roster = [
        _raw_roster_player(1, "RB One", "", "RB", ["RB"]),
        _raw_roster_player(2, "RB Two", "", "RB", ["RB"]),
        _raw_roster_player(3, "WR One", "", "WR", ["WR"]),
        _raw_roster_player(4, "WR Two", "", "WR", ["WR"]),
    ]

    players = adapt_roster(raw_roster, details_by_id={}, stats_by_id={})

    slots = {p.name: p.roster_slot for p in players}
    assert slots["RB One"] == "RB1"
    assert slots["RB Two"] == "RB2"
    assert slots["WR One"] == "WR1"
    assert slots["WR Two"] == "WR2"


def test_adapt_roster_maps_bench_and_flex_slots():
    raw_roster = [
        _raw_roster_player(1, "Bench Guy", "", "BN", ["RB", "BN"]),
        _raw_roster_player(2, "Flex Guy", "", "W/R/T", ["RB", "WR", "TE", "W/R/T"]),
    ]

    players = adapt_roster(raw_roster, details_by_id={}, stats_by_id={})

    by_name = {p.name: p for p in players}
    assert by_name["Bench Guy"].roster_slot == "BN"
    assert by_name["Bench Guy"].is_starter is False
    assert by_name["Flex Guy"].roster_slot == "FLEX"
    assert by_name["Flex Guy"].is_starter is True


def test_adapt_roster_uses_real_bye_week_when_available_and_zero_otherwise():
    raw_roster = [
        _raw_roster_player(1, "Bye Week Known", "", "QB", ["QB"]),
        _raw_roster_player(2, "Bye Week Unknown", "", "QB", ["QB"]),
    ]
    details_by_id = {
        1: {"editorial_team_abbr": "kc", "bye_weeks": {"week": "10"}, "primary_position": "QB"},
        2: {"editorial_team_abbr": "buf", "primary_position": "QB"},
    }

    players = adapt_roster(raw_roster, details_by_id=details_by_id, stats_by_id={})

    by_name = {p.name: p for p in players}
    assert by_name["Bye Week Known"].bye_week == 10
    assert by_name["Bye Week Known"].nfl_team == "KC"
    assert by_name["Bye Week Unknown"].bye_week == 0


def test_adapt_roster_marks_estimated_points_and_uses_stat_total():
    raw_roster = [_raw_roster_player(1, "Stat Guy", "", "RB", ["RB"])]
    stats_by_id = {1: {"player_id": 1, "total_points": "14.3"}}

    players = adapt_roster(raw_roster, details_by_id={}, stats_by_id=stats_by_id)

    player = players[0]
    assert player.projection_is_estimate is True
    assert player.projected_points == 14.3
    assert player.recent_avg_points == 14.3


def test_adapt_roster_defaults_to_zero_points_when_no_stats_available():
    raw_roster = [_raw_roster_player(1, "No Stats Guy", "", "RB", ["RB"])]

    players = adapt_roster(raw_roster, details_by_id={}, stats_by_id={})

    assert players[0].projected_points == 0.0
    assert players[0].projection_is_estimate is True


def test_adapt_free_agent_builds_estimate_from_stat_row():
    raw = {"player_id": 42, "name": "Free Agent Guy", "eligible_positions": ["WR"], "percent_owned": 35}
    detail = {"editorial_team_abbr": "nyg", "primary_position": "WR"}
    stat_row = {"player_id": 42, "total_points": "9.8"}

    agent = adapt_free_agent(raw, detail, stat_row)

    assert agent.player_id == "42"
    assert agent.name == "Free Agent Guy"
    assert agent.position == "WR"
    assert agent.nfl_team == "NYG"
    assert agent.projected_points == 9.8
    assert agent.percent_owned == 35.0
    assert agent.projection_is_estimate is True
