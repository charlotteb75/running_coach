"""Shared test resources. Each test gets fresh resources and automatic cleanup."""

from unittest.mock import MagicMock

import pytest
from flask import Flask

from app.extensions import db


@pytest.fixture
def db_session():
    """Create an isolated SQLite database."""
    app = Flask(__name__)
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
            yield db.session
        finally:
            db.session.remove()
            db.drop_all()
            db.engine.dispose()


@pytest.fixture
def openrouter_client(monkeypatch, tmp_path):
    """Fake the SDK and supply temporary prompts."""
    from app.services import openrouter

    monkeypatch.setenv("OPENROUTER_KEY", "fake")
    monkeypatch.setenv("OPENROUTER_MODEL", "fake")
    (tmp_path / "running_coach.md").write_text("Test instructions", encoding="utf-8")
    (tmp_path / "daily_training_day.md").write_text("Generate a test plan", encoding="utf-8")
    monkeypatch.setattr(openrouter, "PROMPT_PATH", tmp_path)
    sdk = MagicMock()
    monkeypatch.setattr(openrouter, "OpenAI", sdk)
    return sdk.return_value.__enter__.return_value
