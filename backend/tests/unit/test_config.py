from app.core.config import get_settings


def test_applitools_env_maps_from_standard_names(monkeypatch):
    monkeypatch.setenv("APPLITOOLS_ENABLED", "true")
    monkeypatch.setenv("APPLITOOLS_API_KEY", "demo-key")
    monkeypatch.setenv("APPLITOOLS_SERVER_URL", "https://eyes.example")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.applitools_enabled is True
    assert settings.applitools_api_key == "demo-key"
    assert settings.applitools_server_url == "https://eyes.example"
    get_settings.cache_clear()
