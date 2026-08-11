"""YahooProvider — the real-data equivalent of app.data_source.MockProvider.

Implements the exact same surface (LEAGUE_NAME, CURRENT_WEEK, get_my_team(),
get_opponent_team(), get_current_matchup(), get_free_agents(),
get_draft_prospects()) so the dashboard code never needs to know whether
it's looking at mock or real data.

Caching: results are kept in memory for a short time (CACHE_TTL_SECONDS)
and reused across page views. This exists ONLY to comply with Yahoo's
request that apps avoid hammering their API with repeat calls for data
that hasn't changed -- e.g. clicking between the Roster and Matchup tabs
a few times in a row shouldn't trigger a fresh Yahoo request every click.
It is not meant to hide requests or evade any kind of detection; a normal
page refresh after the cache expires will always show current data.
"""

import time

from app.models import Team, Matchup
from app.yahoo_integration.client import YahooClient
from app.yahoo_integration.adapter import adapt_roster, adapt_free_agent

CACHE_TTL_SECONDS = 300

# Module-level so the cache is shared across requests (each Flask request
# constructs a new YahooProvider, but the cache itself should outlive that).
_cache = {}


def _cached(key, fetch_fn):
    now = time.time()
    entry = _cache.get(key)
    if entry is not None and (now - entry[0]) < CACHE_TTL_SECONDS:
        return entry[1]
    value = fetch_fn()
    _cache[key] = (now, value)
    return value


# Standard offense/kicker/defense position codes used to page through
# Yahoo's free-agent list. DEF free agents come back under "DEF".
_FREE_AGENT_POSITIONS = ["QB", "RB", "WR", "TE", "K", "DEF"]

# How many free agents to keep per position, to keep this a short, readable
# waiver-wire list rather than a dump of every rostered-elsewhere player.
_FREE_AGENTS_PER_POSITION = 6


class YahooProvider:
    def __init__(self, settings):
        league_key = settings.get("league_key")
        team_key = settings.get("team_key")
        if not league_key or not team_key:
            raise RuntimeError(
                "No Yahoo league/team selected yet. Visit Setup to connect and choose one."
            )

        self.league_key = league_key
        self.team_key = team_key
        self._client = YahooClient(game_code=settings.get("game_code", "nfl"))

        league_settings = _cached(
            ("league_settings", league_key), lambda: self._client.league_settings(league_key)
        )
        self.LEAGUE_NAME = league_settings.get("name", "Your Yahoo League")
        self.CURRENT_WEEK = _cached(
            ("current_week", league_key), lambda: self._client.current_week(league_key)
        )

    def _roster_to_team(self, team_key, team_name):
        raw_roster = _cached(
            ("roster", team_key, self.CURRENT_WEEK),
            lambda: self._client.roster(team_key, week=self.CURRENT_WEEK),
        )
        player_ids = [r["player_id"] for r in raw_roster]

        details = _cached(
            ("player_details", team_key, self.CURRENT_WEEK),
            lambda: self._client.player_details(self.league_key, player_ids),
        )
        details_by_id = {int(d["player_id"]): d for d in details}

        stats = _cached(
            ("player_stats", team_key, self.CURRENT_WEEK),
            lambda: self._client.player_stats(self.league_key, player_ids, "lastweek"),
        )
        stats_by_id = {s["player_id"]: s for s in stats}

        players = adapt_roster(raw_roster, details_by_id, stats_by_id)
        return Team(team_key, team_name, players)

    def get_my_team(self):
        name = _cached(("team_name", self.team_key), lambda: self._client.team_name(self.team_key))
        return self._roster_to_team(self.team_key, name)

    def get_opponent_team(self):
        opponent_key = _cached(
            ("opponent_key", self.team_key, self.CURRENT_WEEK),
            lambda: self._client.opponent_team_key(self.team_key, self.CURRENT_WEEK),
        )
        name = _cached(("team_name", opponent_key), lambda: self._client.team_name(opponent_key))
        return self._roster_to_team(opponent_key, name)

    def get_current_matchup(self):
        return Matchup(self.CURRENT_WEEK, self.get_my_team(), self.get_opponent_team())

    def get_free_agents(self):
        agents = []
        for position in _FREE_AGENT_POSITIONS:
            raw_list = _cached(
                ("free_agents", self.league_key, position),
                lambda pos=position: self._client.free_agents(self.league_key, pos),
            )
            raw_list = raw_list[:_FREE_AGENTS_PER_POSITION]
            player_ids = [r["player_id"] for r in raw_list]

            details = _cached(
                ("fa_details", self.league_key, position),
                lambda ids=player_ids: self._client.player_details(self.league_key, ids),
            )
            details_by_id = {int(d["player_id"]): d for d in details}

            stats = _cached(
                ("fa_stats", self.league_key, position),
                lambda ids=player_ids: self._client.player_stats(self.league_key, ids, "lastweek"),
            )
            stats_by_id = {s["player_id"]: s for s in stats}

            for raw in raw_list:
                agents.append(adapt_free_agent(
                    raw,
                    details_by_id.get(raw["player_id"], {}),
                    stats_by_id.get(raw["player_id"], {}),
                ))
        return agents

    def get_draft_prospects(self):
        """Yahoo's free API has no generic pre-draft rankings/ADP feed to
        pull from, so the draft assistant stays on the same advisory mock
        prospect list even in live mode -- consistent with Phase 1's
        finding that there's no official live-draft data source."""
        from app.mock_data import league as mock_league
        return mock_league.get_draft_prospects()
