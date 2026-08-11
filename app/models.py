"""Plain data containers shared across the app.

These classes hold no logic — they are just labeled boxes for data,
so that mock data, recommendation logic, and the dashboard all agree
on what a "Player" or "Team" looks like. When real Yahoo data replaces
mock data later, it only needs to be translated into these same shapes.
"""

from dataclasses import dataclass, field


# Status a player can have going into a given week.
STATUS_HEALTHY = "Healthy"
STATUS_QUESTIONABLE = "Questionable"
STATUS_INJURED = "Injured"
STATUS_OUT = "Out"
STATUS_SUSPENDED = "Suspended"
STATUS_BYE = "Bye Week"

# Roster slot types used in this mock league (standard 10-team format).
# Duplicate positions (two RB, two WR) get a trailing number so each slot
# has a unique key; display code strips the digit to show "RB"/"WR".
ROSTER_SLOTS = ["QB", "RB1", "RB2", "WR1", "WR2", "TE", "FLEX", "K", "DEF"]
FLEX_ELIGIBLE = {"RB", "WR", "TE"}

BENCH_SIZE = 6


@dataclass
class Player:
    player_id: str
    name: str
    position: str          # primary position: QB, RB, WR, TE, K, DEF
    nfl_team: str
    status: str = STATUS_HEALTHY
    bye_week: int = 0
    projected_points: float = 0.0
    recent_avg_points: float = 0.0
    matchup_quality: str = "Average"   # "Great", "Good", "Average", "Tough", "Very Tough"
    opponent: str = ""
    is_starter: bool = False
    roster_slot: str = "BN"            # which slot they currently occupy: QB/RB/WR/TE/FLEX/K/DEF/BN
    projection_is_estimate: bool = False  # True when projected_points was inferred, not provided by the data source

    def is_available_this_week(self, current_week: int) -> bool:
        if self.bye_week == current_week:
            return False
        if self.status in (STATUS_OUT, STATUS_SUSPENDED):
            return False
        return True


@dataclass
class Team:
    team_id: str
    name: str
    players: list = field(default_factory=list)

    def starters(self):
        return [p for p in self.players if p.is_starter]

    def bench(self):
        return [p for p in self.players if not p.is_starter]

    def projected_total(self) -> float:
        return round(sum(p.projected_points for p in self.starters()), 1)


@dataclass
class Matchup:
    week: int
    my_team: Team
    opponent_team: Team


@dataclass
class FreeAgent:
    player_id: str
    name: str
    position: str
    nfl_team: str
    projected_points: float
    recent_avg_points: float
    percent_owned: float
    trending: str = "steady"   # "up", "down", "steady"
    note: str = ""
    projection_is_estimate: bool = False  # True when projected_points was inferred, not provided by the data source


@dataclass
class DraftProspect:
    player_id: str
    name: str
    position: str
    nfl_team: str
    bye_week: int
    base_rank: int
    projected_season_points: float
    adp: float          # average draft position across other drafts
    notes: str = ""
