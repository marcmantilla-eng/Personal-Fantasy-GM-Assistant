"""Picks which data source powers the dashboard: fake mock data, or your
real Yahoo league. The dashboard code never talks to mock_data or
yahoo_integration directly — it always goes through get_provider(), so
switching sources never requires touching dashboard/recommendation code.

Every provider exposes the same shape:
    LEAGUE_NAME: str
    CURRENT_WEEK: int
    get_my_team() -> Team
    get_opponent_team() -> Team
    get_current_matchup() -> Matchup
    get_free_agents() -> list[FreeAgent]
    get_draft_prospects() -> list[DraftProspect]

Defaults to mock data if settings are missing, invalid, or Yahoo isn't
connected yet -- the app should never crash just because Yahoo isn't
set up.
"""

from app.user_settings import load_settings

_last_error = None


def get_last_error():
    """Plain-language reason the last get_provider() call fell back to
    mock data, if any. Used by the Setup screen to explain what's wrong."""
    return _last_error


class MockProvider:
    """Thin wrapper around app.mock_data.league so it satisfies the
    provider interface explicitly, rather than callers reaching into
    the mock_data module directly."""

    def __init__(self):
        from app.mock_data import league as mock_league
        self._m = mock_league
        self.LEAGUE_NAME = mock_league.LEAGUE_NAME
        self.CURRENT_WEEK = mock_league.CURRENT_WEEK

    def get_my_team(self):
        return self._m.get_my_team()

    def get_opponent_team(self):
        return self._m.get_opponent_team()

    def get_current_matchup(self):
        return self._m.get_current_matchup()

    def get_free_agents(self):
        return self._m.get_free_agents()

    def get_draft_prospects(self):
        return self._m.get_draft_prospects()


def get_provider():
    """Return the active data provider based on saved settings.

    Falls back to MockProvider whenever Yahoo isn't configured/connected
    or fails to load, so the dashboard always has something to show.
    """
    global _last_error
    settings = load_settings()

    if settings.get("data_source") != "yahoo":
        _last_error = None
        return MockProvider()

    try:
        from app.yahoo_integration.provider import YahooProvider
        provider = YahooProvider(settings)
        _last_error = None
        return provider
    except Exception as exc:
        _last_error = str(exc)
        return MockProvider()
