"""Defaults that keep the API process from repeating the daily GitHub Actions job."""

from app.config import Settings


def test_background_schedulers_are_off_by_default():
    assert Settings.model_fields["enable_background_schedulers"].default is False


def test_startup_cache_warm_stays_on_unless_opted_out():
    assert Settings.model_fields["skip_startup_warm"].default is False


def test_scheduler_and_warm_flags_follow_env(monkeypatch):
    monkeypatch.setenv("ENABLE_BACKGROUND_SCHEDULERS", "true")
    monkeypatch.setenv("SKIP_STARTUP_WARM", "true")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    fresh = Settings()
    assert fresh.enable_background_schedulers is True
    assert fresh.skip_startup_warm is True
