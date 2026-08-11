"""Thin, read-only wrapper around the yahoo-fantasy-api library.

Every method here only reads data from Yahoo. The underlying library also
offers methods to change a lineup, add/drop a player, claim a waiver, or
propose a trade -- this file never calls any of those, on purpose. Those
stay off-limits until a later phase, if Yahoo's rules ever permit them for
this app.
"""

import yahoo_fantasy_api as yfa

from app.yahoo_integration.auth import get_authenticated_session


class YahooClient:
    def __init__(self, game_code="nfl", session=None):
        self._sc = session or get_authenticated_session()
        self._game = yfa.Game(self._sc, game_code)
        # Constructing a League/Team object triggers a Yahoo API call, so
        # each one is built once per client and reused.
        self._leagues = {}
        self._teams = {}

    def _league(self, league_key):
        if league_key not in self._leagues:
            self._leagues[league_key] = yfa.League(self._sc, league_key)
        return self._leagues[league_key]

    def _team(self, team_key):
        if team_key not in self._teams:
            league_key = team_key[: team_key.find(".t.")]
            self._teams[team_key] = self._league(league_key).to_team(team_key)
        return self._teams[team_key]

    def list_leagues(self):
        """All of the logged-in user's leagues for this sport, across every
        season they've played -- season is included in the result so a
        setup screen can show the user which one is current."""
        leagues = []
        for league_key in self._game.league_ids():
            settings = self._league(league_key).settings()
            leagues.append({
                "league_key": settings.get("league_key", league_key),
                "name": settings.get("name", league_key),
                "season": settings.get("season", ""),
            })
        return leagues

    def list_teams(self, league_key):
        """Every team in a league, flagging which one belongs to the
        logged-in user."""
        league = self._league(league_key)
        my_team_key = league.team_key()
        teams = league.teams()
        return [
            {
                "team_key": key,
                "name": info.get("name", key),
                "is_my_team": key == my_team_key,
            }
            for key, info in teams.items()
        ]

    def league_settings(self, league_key):
        return self._league(league_key).settings()

    def current_week(self, league_key):
        return self._league(league_key).current_week()

    def roster(self, team_key, week=None):
        return self._team(team_key).roster(week=week)

    def team_name(self, team_key):
        return self._team(team_key).details().get("name", team_key)

    def opponent_team_key(self, team_key, week):
        return self._team(team_key).matchup(week)

    def free_agents(self, league_key, position):
        return self._league(league_key).free_agents(position)

    def player_details(self, league_key, player_ids):
        player_ids = list(player_ids)
        if not player_ids:
            return []
        return self._league(league_key).player_details(player_ids)

    def player_stats(self, league_key, player_ids, req_type):
        player_ids = list(player_ids)
        if not player_ids:
            return []
        return self._league(league_key).player_stats(player_ids, req_type)
