"""The local web dashboard. Runs only on this computer (127.0.0.1) —
nobody outside your machine can reach it.

Every route below asks app.data_source.get_provider() for data (mock or
real Yahoo, depending on your settings) and feeds it through the
recommendation engine (app/recommendations/) to produce plain-language
suggestions.
"""

import datetime
import os

from flask import Flask, render_template, request, redirect, url_for

from app.data_source import get_provider, get_last_error
from app.user_settings import load_settings, save_settings
from app.recommendations.alerts import build_alerts
from app.recommendations.lineup import optimal_lineup, starter_vs_bench_comparisons
from app.recommendations.waiver import recommend_waivers
from app.recommendations.matchup import compare_matchup
from app.recommendations.draft import build_draft_board
from app.audit_log import log_event

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


def _now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def _mode_context():
    settings = load_settings()
    return {
        "is_live": settings.get("data_source") == "yahoo",
    }


@app.route("/")
def home():
    return roster_view()


@app.route("/roster")
def roster_view():
    provider = get_provider()
    team = provider.get_my_team()
    week = provider.CURRENT_WEEK

    lineup, bench, swaps = optimal_lineup(team, week)
    alerts = build_alerts(team, week)
    comparisons = starter_vs_bench_comparisons(team, week)

    log_event(_now(), "viewed", "roster", f"Checked roster/lineup for week {week}.")

    return render_template(
        "roster.html",
        league_name=provider.LEAGUE_NAME,
        team_name=team.name,
        week=week,
        lineup=lineup,
        bench=bench,
        swaps=swaps,
        alerts=alerts,
        comparisons=comparisons,
        active_page="roster",
        **_mode_context(),
    )


@app.route("/waivers")
def waivers_view():
    provider = get_provider()
    team = provider.get_my_team()
    free_agents = provider.get_free_agents()
    recommendations = recommend_waivers(team, free_agents)

    log_event(_now(), "viewed", "waivers", f"Reviewed {len(free_agents)} free agents.")

    return render_template(
        "waivers.html",
        league_name=provider.LEAGUE_NAME,
        recommendations=recommendations,
        active_page="waivers",
        **_mode_context(),
    )


@app.route("/matchup")
def matchup_view():
    provider = get_provider()
    matchup = provider.get_current_matchup()
    result = compare_matchup(matchup, provider.CURRENT_WEEK)

    log_event(_now(), "viewed", "matchup",
              f"Compared week {provider.CURRENT_WEEK} matchup vs {matchup.opponent_team.name}.")

    return render_template(
        "matchup.html",
        league_name=provider.LEAGUE_NAME,
        result=result,
        active_page="matchup",
        **_mode_context(),
    )


@app.route("/draft")
def draft_view():
    provider = get_provider()
    prospects = provider.get_draft_prospects()
    # Mock "already drafted" state for demonstration: a few players taken, and
    # our team already has one RB and one WR. Real drafted-state tracking
    # arrives in a later phase alongside live draft support.
    drafted_ids = {"d1", "d3", "d5"}
    drafted_players_by_position = {"RB": 1, "WR": 1}

    board = build_draft_board(prospects, drafted_ids, drafted_players_by_position)

    log_event(_now(), "viewed", "draft", "Generated customized draft board.")

    return render_template(
        "draft.html",
        league_name=provider.LEAGUE_NAME,
        board=board,
        drafted_ids=drafted_ids,
        active_page="draft",
        **_mode_context(),
    )


@app.route("/setup", methods=["GET"])
def setup_view():
    settings = load_settings()
    connection_error = get_last_error()
    has_credentials = _has_yahoo_credentials()

    from app.yahoo_integration.auth import is_connected
    connected = is_connected()

    leagues = []
    teams = []
    connect_error = None
    selected_league_key = request.args.get("league_key") or settings.get("league_key")

    if connected:
        try:
            from app.yahoo_integration.client import YahooClient
            client = YahooClient(game_code=settings.get("game_code", "nfl"))
            leagues = client.list_leagues()
            if selected_league_key:
                teams = client.list_teams(selected_league_key)
        except Exception as exc:
            connect_error = str(exc)

    log_event(_now(), "viewed", "setup", "Opened connection settings.")

    return render_template(
        "setup.html",
        active_page="setup",
        settings=settings,
        has_credentials=has_credentials,
        connected=connected,
        leagues=leagues,
        teams=teams,
        selected_league_key=selected_league_key,
        connect_error=connect_error,
        connection_error=connection_error,
        **_mode_context(),
    )


@app.route("/setup/connect", methods=["POST"])
def setup_connect():
    """Kicks off the one-time Yahoo login. The actual browser/paste-code
    flow happens in the terminal window running this app, per yahoo_oauth's
    design -- this route just triggers it and reports success/failure."""
    try:
        from app.yahoo_integration.auth import get_authenticated_session
        get_authenticated_session()
        log_event(_now(), "connected", "setup", "Connected to Yahoo (read-only).")
    except Exception as exc:
        log_event(_now(), "connect_failed", "setup", f"Yahoo connection failed: {exc}")
    return redirect(url_for("setup_view"))


@app.route("/setup/select", methods=["POST"])
def setup_select():
    league_key = request.form.get("league_key") or None
    team_key = request.form.get("team_key") or None
    use_live = request.form.get("use_live") == "on"

    save_settings({
        "league_key": league_key,
        "team_key": team_key,
        "data_source": "yahoo" if (use_live and league_key and team_key) else "mock",
    })

    log_event(_now(), "settings_changed", "setup",
              f"Selected league={league_key}, team={team_key}, live={use_live}.")

    return redirect(url_for("setup_view"))


def _has_yahoo_credentials() -> bool:
    import os as _os
    return bool(_os.environ.get("YAHOO_CLIENT_ID")) and bool(_os.environ.get("YAHOO_CLIENT_SECRET"))


def create_app():
    from dotenv import load_dotenv
    load_dotenv()
    return app


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    app.run(host="127.0.0.1", port=5055, debug=True)
