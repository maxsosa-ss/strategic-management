"""Smoke tests. Los `live` usan credenciales reales: pytest -m live"""

import pytest

from sm_connectors import ConfigError, get_env


def test_get_env_required_missing(monkeypatch):
    monkeypatch.delenv("NO_EXISTE", raising=False)
    with pytest.raises(ConfigError):
        get_env("NO_EXISTE")


def test_get_env_default(monkeypatch):
    monkeypatch.delenv("NO_EXISTE", raising=False)
    assert get_env("NO_EXISTE", "x") == "x"


@pytest.mark.live
def test_mstr_connection():
    from sm_connectors.mstr import mstr_session

    with mstr_session() as conn:
        assert conn.status()


@pytest.mark.live
def test_google_credentials():
    from sm_connectors.google import get_google_credentials

    assert get_google_credentials() is not None
