from app.models import Player, Team, FreeAgent
from app.recommendations.waiver import recommend_waivers


def test_recommends_pickup_when_free_agent_projects_higher_than_weakest_bench():
    weak_bench = Player("1", "Weak Bench RB", "RB", "NYG", projected_points=3.0,
                         is_starter=False, roster_slot="BN")
    team = Team("t1", "Test", [weak_bench])
    agent = FreeAgent("f1", "Hot Waiver RB", "RB", "TEN", projected_points=10.0,
                       recent_avg_points=9.0, percent_owned=20.0, trending="up",
                       note="Test note.")

    recs = recommend_waivers(team, [agent])

    assert len(recs) == 1
    assert recs[0]["add_name"] == "Hot Waiver RB"
    assert recs[0]["drop_name"] == "Weak Bench RB"
    assert recs[0]["point_gain"] == 7.0


def test_no_recommendation_when_free_agent_is_worse_than_bench():
    strong_bench = Player("1", "Strong Bench RB", "RB", "NYG", projected_points=15.0,
                           is_starter=False, roster_slot="BN")
    team = Team("t1", "Test", [strong_bench])
    agent = FreeAgent("f1", "Mediocre RB", "RB", "TEN", projected_points=5.0,
                       recent_avg_points=4.0, percent_owned=10.0, trending="steady")

    recs = recommend_waivers(team, [agent])

    assert recs == []


def test_flex_eligible_position_compares_against_flex_pool_when_no_exact_match():
    bench_te = Player("1", "Bench TE", "TE", "NYG", projected_points=4.0,
                       is_starter=False, roster_slot="BN")
    team = Team("t1", "Test", [bench_te])
    agent = FreeAgent("f1", "Streaming WR", "WR", "TEN", projected_points=9.0,
                       recent_avg_points=8.0, percent_owned=15.0, trending="steady")

    recs = recommend_waivers(team, [agent])

    assert len(recs) == 1
    assert recs[0]["drop_name"] == "Bench TE"


def test_recommendations_sorted_by_point_gain_descending():
    bench1 = Player("1", "Bench RB1", "RB", "NYG", projected_points=5.0, is_starter=False, roster_slot="BN")
    bench2 = Player("2", "Bench WR1", "WR", "NYG", projected_points=5.0, is_starter=False, roster_slot="BN")
    team = Team("t1", "Test", [bench1, bench2])
    small_gain = FreeAgent("f1", "Small Gain RB", "RB", "TEN", projected_points=6.0,
                           recent_avg_points=5.0, percent_owned=10.0)
    big_gain = FreeAgent("f2", "Big Gain WR", "WR", "TEN", projected_points=15.0,
                         recent_avg_points=14.0, percent_owned=30.0)

    recs = recommend_waivers(team, [small_gain, big_gain])

    assert recs[0]["add_name"] == "Big Gain WR"
    assert recs[1]["add_name"] == "Small Gain RB"
