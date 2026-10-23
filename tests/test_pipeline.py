"""Tests de los flujos de pipeline con MicroStrategy y Google simulados (sin red)."""

from contextlib import contextmanager
from types import SimpleNamespace

import pandas as pd
import pytest

from smpy.connectors import pipeline


@pytest.fixture
def llamadas(monkeypatch):
    registro = {"sesiones": 0, "crear": [], "actualizar": []}

    @contextmanager
    def sesion_falsa():
        registro["sesiones"] += 1
        yield "CONN_PROPIA"

    def crear(conn, name, table_name, df, **kw):
        registro["crear"].append((conn, name, table_name, len(df), kw))
        return SimpleNamespace(id="ID_NUEVO")

    def actualizar(conn, cube_id, table_name, df, **kw):
        registro["actualizar"].append((conn, cube_id, table_name, len(df), kw))

    monkeypatch.setattr(pipeline, "mstr_session", sesion_falsa)
    monkeypatch.setattr(pipeline, "create_supercube", crear)
    monkeypatch.setattr(pipeline, "df_to_supercube", actualizar)
    return registro


@pytest.fixture
def df():
    return pd.DataFrame({"Periodo": [202510, 202511], "Valor": [1.5, 2.5]})


def test_dataframe_to_supercube_crea_y_devuelve_id(llamadas, df):
    assert pipeline.dataframe_to_supercube(df, "T", cube_name="Mi cubo", folder_id="F", to_attribute=["Periodo"]) == "ID_NUEVO"
    conn, name, tabla, filas, kw = llamadas["crear"][0]
    assert (conn, name, tabla, filas) == ("CONN_PROPIA", "Mi cubo", "T", 2)
    assert kw == {"folder_id": "F", "to_metric": None, "to_attribute": ["Periodo"]}
    assert not llamadas["actualizar"]


def test_dataframe_to_supercube_actualiza_con_la_politica(llamadas, df):
    assert pipeline.dataframe_to_supercube(df, "T", cube_id="CUBO", policy="upsert") == "CUBO"
    conn, cube_id, tabla, filas, kw = llamadas["actualizar"][0]
    assert (cube_id, tabla, filas, kw["policy"]) == ("CUBO", "T", 2, "upsert")
    assert not llamadas["crear"]


def test_dataframe_to_supercube_reusa_la_conexion_recibida(llamadas, df):
    pipeline.dataframe_to_supercube(df, "T", cube_id="A", conn="MI_CONN")
    pipeline.dataframe_to_supercube(df, "T", cube_name="B", conn="MI_CONN")
    assert llamadas["sesiones"] == 0
    assert llamadas["actualizar"][0][0] == "MI_CONN" and llamadas["crear"][0][0] == "MI_CONN"


def test_dataframe_to_supercube_exige_id_o_nombre(llamadas, df):
    with pytest.raises(ValueError, match="cube_id"):
        pipeline.dataframe_to_supercube(df, "T")


def test_sheet_to_supercube_lee_transforma_y_sube(llamadas, df, monkeypatch):
    monkeypatch.setattr(pipeline, "get_sheets_client", lambda: "GC")
    monkeypatch.setattr(pipeline, "sheet_to_df", lambda gc, sid, ws: df if (gc, sid, ws) == ("GC", "S", "H") else None)
    pipeline.sheet_to_supercube("S", "H", "T", cube_id="CUBO", transform=lambda d: d.head(1))
    assert llamadas["actualizar"][0][3] == 1  # se subió el DataFrame transformado


def test_sheet_to_supercube_valida_antes_de_leer(llamadas, monkeypatch):
    monkeypatch.setattr(pipeline, "get_sheets_client", lambda: pytest.fail("no debe tocar Google"))
    with pytest.raises(ValueError, match="cube_id"):
        pipeline.sheet_to_supercube("S", "H", "T")
