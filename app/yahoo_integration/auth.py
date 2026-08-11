"""Handles the one-time Yahoo login and keeps the session refreshed.

How this works, in plain terms:
  1. Your Client ID and Client Secret live in .env (never printed, never
     committed to Git).
  2. The first time you connect, this opens your browser to a Yahoo
     sign-in/approval page. Yahoo then shows you a short code.
  3. You paste that code into the CONSOLE WINDOW running this app (the
     black window from the launcher) -- not into the web dashboard. This
     is how Yahoo's "installed application" login flow works for desktop
     apps: it has no public web address to send the code back to.
  4. After that, this module stores a refresh token in oauth2.json (also
     never committed) and renews your access automatically -- you should
     not need to repeat the browser step unless you revoke access or
     delete oauth2.json.

If Yahoo changes how their login works, only this file needs to change --
nothing else in the app talks to Yahoo's OAuth endpoints directly.
"""

import json
import os

OAUTH_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "oauth2.json"
)


class YahooAuthError(RuntimeError):
    """Raised when Yahoo credentials are missing or the login flow fails."""


def _ensure_oauth_file_seeded():
    """Write consumer_key/secret into oauth2.json if the file doesn't
    exist yet, so yahoo_oauth has something to start from. Never
    overwrites an existing file, since that would erase a saved
    refresh token.
    """
    if os.path.exists(OAUTH_FILE):
        return

    client_id = os.environ.get("YAHOO_CLIENT_ID")
    client_secret = os.environ.get("YAHOO_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise YahooAuthError(
            "Yahoo Client ID/Secret not found. Add them to your .env file "
            "before connecting (see .env.example)."
        )

    with open(OAUTH_FILE, "w", encoding="utf-8") as f:
        json.dump({"consumer_key": client_id, "consumer_secret": client_secret}, f)


def get_authenticated_session():
    """Return an authenticated yahoo_oauth.OAuth2 session, prompting for
    the one-time browser login if needed.

    The first call after a fresh setup will open a browser window and
    then WAIT for you to paste a verification code into this app's
    console window -- watch the console, not the web dashboard, at that
    moment.
    """
    _ensure_oauth_file_seeded()

    from yahoo_oauth import OAuth2

    session = OAuth2(None, None, from_file=OAUTH_FILE)

    if not session.token_is_valid():
        session.refresh_access_token()

    return session


def is_connected() -> bool:
    """True if a saved session exists and looks usable, without
    triggering a new browser login."""
    if not os.path.exists(OAUTH_FILE):
        return False
    try:
        with open(OAUTH_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    return bool(data.get("access_token")) and bool(data.get("refresh_token"))
