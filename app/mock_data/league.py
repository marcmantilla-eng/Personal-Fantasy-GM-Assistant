"""Fake league data standing in for real Yahoo data during Phase 2.

Nothing in this file talks to the internet. It exists so the dashboard
and recommendation logic can be built and tested before Yahoo credentials
are ever involved. Numbers (projections, matchup quality, etc.) are made
up for demonstration purposes.
"""

from app.models import (
    Player, Team, Matchup, FreeAgent, DraftProspect,
    STATUS_HEALTHY, STATUS_QUESTIONABLE, STATUS_INJURED, STATUS_OUT, STATUS_BYE,
)

CURRENT_WEEK = 7
LEAGUE_NAME = "Mock Dynasty Legends"
MY_TEAM_NAME = "Paper Tigers"
OPPONENT_TEAM_NAME = "Waiver Wire Warriors"

SCORING_SUMMARY = {
    "type": "Points Per Reception (PPR)",
    "passing_td": 4,
    "rushing_td": 6,
    "receiving_td": 6,
    "reception": 1,
    "notes": "Standard PPR scoring, 0.5 point per completion is NOT used.",
}


def _my_players():
    return [
        Player("p1", "Josh Allen", "QB", "BUF", STATUS_HEALTHY, 0, 24.8, 22.1, "Good", "vs NYJ", True, "QB"),
        Player("p2", "Bijan Robinson", "RB", "ATL", STATUS_HEALTHY, 0, 18.2, 16.9, "Great", "vs CAR", True, "RB1"),
        Player("p3", "Jonathan Taylor", "RB", "IND", STATUS_QUESTIONABLE, 0, 11.5, 15.4, "Tough", "@ BAL", True, "RB2"),
        Player("p4", "Justin Jefferson", "WR", "MIN", STATUS_HEALTHY, 0, 19.4, 18.0, "Good", "vs CHI", True, "WR1"),
        Player("p5", "Tee Higgins", "WR", "CIN", STATUS_INJURED, 0, 6.0, 14.2, "Average", "@ CLE", True, "WR2"),
        Player("p6", "Travis Kelce", "TE", "KC", STATUS_HEALTHY, 10, 13.1, 12.5, "Average", "BYE", True, "TE"),
        Player("p7", "Kenneth Walker III", "RB", "SEA", STATUS_HEALTHY, 0, 12.9, 10.8, "Good", "vs ARI", True, "FLEX"),
        Player("p8", "Harrison Butker", "K", "KC", STATUS_HEALTHY, 10, 7.5, 8.0, "Average", "BYE", True, "K"),
        Player("p9", "Cowboys DEF", "DEF", "DAL", STATUS_HEALTHY, 0, 8.2, 6.5, "Good", "vs NYG", True, "DEF"),
        # Bench
        Player("p10", "Gus Edwards", "RB", "LAC", STATUS_HEALTHY, 0, 9.8, 8.5, "Good", "vs DEN", False, "BN"),
        Player("p11", "Rome Odunze", "WR", "CHI", STATUS_HEALTHY, 0, 10.6, 9.1, "Tough", "@ MIN", False, "BN"),
        Player("p12", "Sam LaPorta", "TE", "DET", STATUS_HEALTHY, 0, 11.9, 11.0, "Great", "vs GB", False, "BN"),
        Player("p13", "Jayden Daniels", "QB", "WAS", STATUS_HEALTHY, 0, 20.1, 19.5, "Average", "@ PHI", False, "BN"),
        Player("p14", "Rashid Shaheed", "WR", "NO", STATUS_OUT, 0, 0.0, 7.2, "Average", "vs TB", False, "BN"),
        Player("p15", "Cade Otton", "TE", "TB", STATUS_HEALTHY, 0, 6.4, 5.8, "Average", "@ NO", False, "BN"),
    ]


def _opponent_players():
    return [
        Player("o1", "Patrick Mahomes", "QB", "KC", STATUS_HEALTHY, 10, 23.0, 21.8, "Average", "BYE", True, "QB"),
        Player("o2", "Breece Hall", "RB", "NYJ", STATUS_HEALTHY, 0, 16.4, 14.0, "Tough", "@ BUF", True, "RB1"),
        Player("o3", "De'Von Achane", "RB", "MIA", STATUS_HEALTHY, 0, 15.8, 17.2, "Good", "vs NE", True, "RB2"),
        Player("o4", "Amon-Ra St. Brown", "WR", "DET", STATUS_HEALTHY, 0, 17.9, 16.4, "Great", "vs GB", True, "WR1"),
        Player("o5", "DK Metcalf", "WR", "SEA", STATUS_QUESTIONABLE, 0, 10.2, 13.7, "Average", "vs ARI", True, "WR2"),
        Player("o6", "Mark Andrews", "TE", "BAL", STATUS_HEALTHY, 0, 10.8, 9.9, "Average", "vs IND", True, "TE"),
        Player("o7", "James Cook", "RB", "BUF", STATUS_HEALTHY, 0, 11.7, 10.5, "Good", "vs NYJ", True, "FLEX"),
        Player("o8", "Justin Tucker", "K", "BAL", STATUS_HEALTHY, 0, 8.1, 7.9, "Average", "vs IND", True, "K"),
        Player("o9", "49ers DEF", "DEF", "SF", STATUS_HEALTHY, 0, 7.6, 8.8, "Good", "vs SEA", True, "DEF"),
    ]


def get_my_team() -> Team:
    return Team("t1", MY_TEAM_NAME, _my_players())


def get_opponent_team() -> Team:
    return Team("t2", OPPONENT_TEAM_NAME, _opponent_players())


def get_current_matchup() -> Matchup:
    return Matchup(CURRENT_WEEK, get_my_team(), get_opponent_team())


def get_free_agents():
    return [
        FreeAgent("f1", "Tyjae Spears", "RB", "TEN", 10.5, 8.9, 42.0, "up",
                  "Seeing more snaps with starter banged up — could pay off soon."),
        FreeAgent("f2", "Jaylen Wright", "RB", "MIA", 7.2, 5.5, 18.0, "up",
                  "Speculative add if you need running back depth."),
        FreeAgent("f3", "Wan'Dale Robinson", "WR", "NYG", 9.8, 8.2, 35.0, "steady",
                  "Consistent target share in a struggling offense."),
        FreeAgent("f4", "Tyler Conklin", "TE", "NYJ", 8.0, 6.8, 22.0, "steady",
                  "Streamable tight end while Kelce is on bye."),
        FreeAgent("f5", "Chargers DEF", "DEF", "LAC", 8.5, 7.0, 15.0, "up",
                  "Favorable matchup this week against a weak offense."),
        FreeAgent("f6", "Younghoe Koo", "K", "ATL", 8.3, 7.5, 30.0, "steady",
                  "Reliable kicker if you want an upgrade."),
    ]


def get_draft_prospects():
    """A generic draft board, not tied to any specific real season."""
    return [
        DraftProspect("d1", "Christian McCaffrey", "RB", "SF", 9, 1, 320.5, 1.2, "Elite floor and ceiling when healthy."),
        DraftProspect("d2", "Tyreek Hill", "WR", "MIA", 6, 2, 298.0, 2.5, "Explosive weekly upside."),
        DraftProspect("d3", "Ja'Marr Chase", "WR", "CIN", 12, 3, 291.4, 3.1, "Target monster, low bust risk."),
        DraftProspect("d4", "Bijan Robinson", "RB", "ATL", 5, 4, 285.7, 4.8, "Workload trending up."),
        DraftProspect("d5", "Josh Allen", "QB", "BUF", 12, 5, 380.2, 8.0, "Rushing upside separates him from other QBs."),
        DraftProspect("d6", "Justin Jefferson", "WR", "MIN", 6, 6, 279.9, 6.4, "Locked-in target share."),
        DraftProspect("d7", "Travis Kelce", "TE", "KC", 10, 7, 240.1, 9.5, "Ageing but still elite in scoring range."),
        DraftProspect("d8", "Jahmyr Gibbs", "RB", "DET", 5, 8, 270.3, 7.9, "Explosive but shares work in a good offense."),
        DraftProspect("d9", "Amon-Ra St. Brown", "WR", "DET", 5, 9, 268.5, 10.2, "High floor PPR machine."),
        DraftProspect("d10", "CeeDee Lamb", "WR", "DAL", 7, 10, 265.0, 11.0, "Elite target volume."),
        DraftProspect("d11", "Puka Nacua", "WR", "LAR", 6, 11, 255.8, 12.7, "Big target share if healthy all year."),
        DraftProspect("d12", "Jonathan Taylor", "RB", "IND", 14, 12, 250.4, 13.5, "Injury history is the main risk."),
        DraftProspect("d13", "Kenneth Walker III", "RB", "SEA", 5, 13, 232.6, 18.0, "Solid RB2 with upside."),
        DraftProspect("d14", "Sam LaPorta", "TE", "DET", 5, 14, 210.9, 22.0, "Best tight end value outside the top tier."),
        DraftProspect("d15", "Patrick Mahomes", "QB", "KC", 10, 15, 355.0, 20.5, "Elite ceiling, slightly lower rushing floor."),
    ]
