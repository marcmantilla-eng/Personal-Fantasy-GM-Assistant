"""Reads and writes user_settings.json — small, non-secret preferences
like which data source, league, and team to use.

This file is separate from .env on purpose: .env holds secrets (Client
ID/Secret) that must never be touched by app code at runtime beyond
reading them once; this file holds ordinary settings the app itself
updates as you use the Setup screen, and is safe to inspect or delete.
"""

import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "user_settings.json")

DEFAULTS = {
    "data_source": "mock",   # "mock" or "yahoo"
    "league_key": None,
    "team_key": None,
    "game_code": "nfl",
}


def load_settings() -> dict:
    if not os.path.exists(SETTINGS_PATH):
        return dict(DEFAULTS)
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULTS)
    merged = dict(DEFAULTS)
    merged.update(data)
    return merged


def save_settings(settings: dict) -> None:
    merged = load_settings()
    merged.update(settings)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
