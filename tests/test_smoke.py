"""Smoke tests. Los `live` usan credenciales reales: pytest -m live"""

import pytest

from smpy.config import ConfigError, get_env


def test_get_env_required_missing(monkeypatch):
    monkeypatch.delenv("NO_EXISTE", raising=False)
    with pytest.raises(ConfigError):
        get_env("NO_EXISTE")


def test_get_env_default(monkeypatch):
    monkeypatch.delenv("NO_EXISTE", raising=False)
    assert get_env("NO_EXISTE", "x") == "x"


def test_el_paquete_raiz_no_reexporta_funciones():
    """Cada función se importa desde su módulo, para ver siempre de dónde viene."""
    import smpy

    publicos = {n for n in dir(smpy) if not n.startswith("_")}
    assert publicos <= {"config", "connectors", "transforms"}, publicos


@pytest.mark.live
def test_mstr_connection():
    from smpy.connectors.mstr import mstr_session

    with mstr_session() as conn:
        assert conn.status()


@pytest.mark.live
def test_google_credentials():
    from smpy.connectors.google import get_google_credentials

    assert get_google_credentials() is not None
