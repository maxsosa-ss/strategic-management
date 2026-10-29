"""Tests de read_parquet y del modo adc con un cliente falso (sin red)."""

import io
import sys
import types

import pandas as pd
import pytest

from smpy.connectors import gcs
from smpy.connectors.google import get_google_credentials


class NotFound(Exception):
    pass


@pytest.fixture(autouse=True)
def api_core_falso(monkeypatch):
    # read_parquet importa NotFound de google.api_core; se reemplaza para no depender de la red ni del extra.
    exceptions = types.ModuleType("google.api_core.exceptions")
    exceptions.NotFound = NotFound
    monkeypatch.setitem(sys.modules, "google.api_core.exceptions", exceptions)


class FakeBlob:
    def __init__(self, contenido):
        self.contenido = contenido

    def download_as_bytes(self):
        if self.contenido is None:
            raise NotFound("404")
        return self.contenido


class FakeClient:
    def __init__(self, objetos):
        self.objetos = objetos  # {(bucket, ruta): bytes}

    def bucket(self, nombre):
        self.nombre = nombre
        return self

    def blob(self, ruta):
        return FakeBlob(self.objetos.get((self.nombre, ruta)))


@pytest.fixture
def parquet():
    pytest.importorskip("pyarrow")
    df = pd.DataFrame({"Prestacion ID": ["NM1", "NM2"], "Valor": [1.5, 2.5], "Otra": ["a", "b"]})
    buffer = io.BytesIO()
    df.to_parquet(buffer)
    return df, buffer.getvalue()


def test_read_parquet(parquet):
    df, contenido = parquet
    out = gcs.read_parquet("crudos/amb.parquet", "mi-bucket", client=FakeClient({("mi-bucket", "crudos/amb.parquet"): contenido}))
    pd.testing.assert_frame_equal(out, df)


def test_read_parquet_columnas(parquet):
    _, contenido = parquet
    out = gcs.read_parquet("a.parquet", "b", columns=["Valor"], client=FakeClient({("b", "a.parquet"): contenido}))
    assert list(out.columns) == ["Valor"]


def test_read_parquet_bucket_desde_el_entorno(parquet, monkeypatch):
    _, contenido = parquet
    monkeypatch.setenv("GCS_BUCKET", "del-entorno")
    out = gcs.read_parquet("a.parquet", client=FakeClient({("del-entorno", "a.parquet"): contenido}))
    assert len(out) == 2


def test_read_parquet_sin_bucket_falla_claro(monkeypatch):
    from smpy.config import ConfigError

    monkeypatch.delenv("GCS_BUCKET", raising=False)
    with pytest.raises(ConfigError, match="GCS_BUCKET"):
        gcs.read_parquet("a.parquet", client=FakeClient({}))


def test_read_parquet_inexistente(monkeypatch):
    with pytest.raises(FileNotFoundError, match="gs://b/falta.parquet"):
        gcs.read_parquet("falta.parquet", "b", client=FakeClient({}))


def test_modo_adc(monkeypatch):
    llamadas = []
    google_auth = pytest.importorskip("google.auth")
    monkeypatch.setattr(google_auth, "default", lambda scopes=None: (llamadas.append(scopes) or "CREDS", "proyecto"))

    assert get_google_credentials(scopes=["s"], mode="adc") == "CREDS"
    assert llamadas == [["s"]]


def test_modo_invalido_menciona_adc():
    from smpy.config import ConfigError

    with pytest.raises(ConfigError, match="adc"):
        get_google_credentials(mode="otro")
