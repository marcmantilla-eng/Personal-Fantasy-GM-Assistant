"""Confirms app.data_source.get_provider() is safe by default: with no
settings file (or a settings file that doesn't request Yahoo), it must
return MockProvider so the dashboard always has something to show, even
before Yahoo is ever configured.
"""

import app.data_source as data_source
import app.user_settings as user_settings


def test_get_provider_defaults_to_mock_when_no_settings_file(tmp_path, monkeypatch):
    missing_path = tmp_path / "user_settings.json"
    monkeypatch.setattr(user_settings, "SETTINGS_PATH", str(missing_path))

    provider = data_source.get_provider()

    assert isinstance(provider, data_source.MockProvider)
    assert data_source.get_last_error() is None


def test_get_provider_falls_back_to_mock_when_yahoo_provider_fails(tmp_path, monkeypatch):
    settings_path = tmp_path / "user_settings.json"
    settings_path.write_text(
        '{"data_source": "yahoo", "league_key": null, "team_key": null}',
        encoding="utf-8",
    )
    monkeypatch.setattr(user_settings, "SETTINGS_PATH", str(settings_path))

    provider = data_source.get_provider()

    assert isinstance(provider, data_source.MockProvider)
    assert data_source.get_last_error() is not None
