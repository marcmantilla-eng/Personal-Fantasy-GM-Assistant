from app.models import Player, Team
from app.recommendations.lineup import optimal_lineup, starter_vs_bench_comparisons


def test_bye_week_starter_is_replaced_by_bench_player():
    starter = Player("1", "Bye TE", "TE", "KC", bye_week=7, projected_points=15.0,
                      is_starter=True, roster_slot="TE")
    bench_te = Player("2", "Backup TE", "TE", "DET", bye_week=0, projected_points=8.0,
                       is_starter=False, roster_slot="BN")
    team = Team("t1", "Test", [starter, bench_te])

    lineup, bench, swaps = optimal_lineup(team, current_week=7)

    assert lineup["TE"].player_id == "2"
    assert starter not in [p for p in lineup.values() if p]


def test_out_player_never_appears_in_lineup():
    starter = Player("1", "Out Guy", "RB", "SEA", status="Out", projected_points=20.0,
                      is_starter=True, roster_slot="RB")
    bench = Player("2", "Healthy Guy", "RB", "LAC", status="Healthy", projected_points=5.0,
                    is_starter=False, roster_slot="BN")
    team = Team("t1", "Test", [starter, bench])

    lineup, _, _ = optimal_lineup(team, current_week=5)

    all_ids = [p.player_id for p in lineup.values() if p]
    assert "1" not in all_ids
    assert "2" in all_ids


def test_flex_slot_filled_by_highest_remaining_eligible_player():
    rb1 = Player("1", "RB One", "RB", "SEA", projected_points=20.0, is_starter=True, roster_slot="RB1")
    rb2 = Player("2", "RB Two", "RB", "ATL", projected_points=18.0, is_starter=True, roster_slot="RB2")
    rb3 = Player("3", "RB3 Flex Candidate", "RB", "DAL", projected_points=12.0, is_starter=False, roster_slot="BN")
    wr_flex_candidate = Player("4", "WR Flex Candidate", "WR", "MIA", projected_points=9.0, is_starter=False, roster_slot="BN")
    team = Team("t1", "Test", [rb1, rb2, rb3, wr_flex_candidate])

    lineup, _, _ = optimal_lineup(team, current_week=5)

    assert lineup["FLEX"].player_id == "3"


def test_two_rb_slots_both_filled_without_overwriting():
    rb1 = Player("1", "RB One", "RB", "SEA", projected_points=20.0, is_starter=True, roster_slot="RB1")
    rb2 = Player("2", "RB Two", "RB", "ATL", projected_points=18.0, is_starter=True, roster_slot="RB2")
    team = Team("t1", "Test", [rb1, rb2])

    lineup, _, _ = optimal_lineup(team, current_week=5)

    assert lineup["RB1"] is not None
    assert lineup["RB2"] is not None
    assert {lineup["RB1"].player_id, lineup["RB2"].player_id} == {"1", "2"}


def test_starter_vs_bench_comparison_explains_point_difference():
    weak_starter = Player("1", "Weak Starter", "WR", "MIA", projected_points=5.0,
                           is_starter=True, roster_slot="WR1")
    strong_bench = Player("2", "Strong Bench", "WR", "DAL", projected_points=15.0,
                           is_starter=False, roster_slot="BN")
    filler_starters = [
        Player("q", "QBFiller", "QB", "BUF", projected_points=20, is_starter=True, roster_slot="QB"),
        Player("r1", "RBFillerOne", "RB", "SEA", projected_points=10, is_starter=True, roster_slot="RB1"),
        Player("r2", "RBFillerTwo", "RB", "ATL", projected_points=10, is_starter=True, roster_slot="RB2"),
        Player("w2", "WRFillerTwo", "WR", "DET", projected_points=10, is_starter=True, roster_slot="WR2"),
        Player("t", "TEFiller", "TE", "KC", projected_points=10, is_starter=True, roster_slot="TE"),
        Player("k", "KFiller", "K", "KC", projected_points=8, is_starter=True, roster_slot="K"),
        Player("d", "DEFFiller", "DEF", "DAL", projected_points=8, is_starter=True, roster_slot="DEF"),
    ]
    team = Team("t1", "Test", [weak_starter, strong_bench] + filler_starters)

    comparisons = starter_vs_bench_comparisons(team, current_week=5)

    wr_comparison = next(c for c in comparisons if c["current_starter"] == "Weak Starter")
    assert wr_comparison["recommended_starter"] == "Strong Bench"
    assert wr_comparison["point_difference"] == 10.0
