"""Conexión a MicroStrategy. Devuelve la `Connection` oficial de mstrio-py sin envolverla,
así cualquier función nueva del SDK queda disponible de inmediato."""

from contextlib import contextmanager

import pandas as pd
from mstrio.connection import Connection
from mstrio.project_objects import Report
from mstrio.project_objects.datasets import SuperCube

from .config import get_env


def get_mstr_connection(
    base_url: str | None = None,
    username: str | None = None,
    password: str | None = None,
    project_id: str | None = None,
    login_mode: int | None = None,
) -> Connection:
    """Crea una conexión. Los parámetros omitidos se leen de MSTR_* en el entorno.

    El proyecto se identifica siempre por ID (MSTR_PROJECT_ID), no por nombre.
    """
    return Connection(
        base_url=base_url or get_env("MSTR_BASE_URL"),
        username=username or get_env("MSTR_USER"),
        password=password or get_env("MSTR_PASSWORD"),
        project_id=project_id or get_env("MSTR_PROJECT_ID"),
        login_mode=login_mode or int(get_env("MSTR_LOGIN_MODE", "1")),
    )


def report_to_df(conn: Connection, report_id: str, **kwargs) -> pd.DataFrame:
    """Ejecuta un reporte y lo devuelve como DataFrame. kwargs van a `Report.to_dataframe`
    (por ejemplo `limit` o `prompt_answers`)."""
    return Report(conn, id=report_id).to_dataframe(**kwargs)


SUPERCUBE_POLICIES = ("replace", "add", "update", "upsert")


def create_supercube(
    conn: Connection,
    name: str,
    table_name: str,
    df: pd.DataFrame,
    folder_id: str | None = None,
    to_metric: list[str] | None = None,
    to_attribute: list[str] | None = None,
) -> SuperCube:
    """Crea un super cube nuevo con el DataFrame y lo publica.

    Carpeta destino: `folder_id` si se pasa; si no, MSTR_FOLDER_ID del entorno; si tampoco
    está, "My Reports" del usuario. Guardá `cube.id` para actualizarlo después con
    `df_to_supercube`.
    """
    folder_id = folder_id or get_env("MSTR_FOLDER_ID", required=False) or None
    cube = SuperCube(conn, name=name)
    cube.add_table(
        name=table_name,
        data_frame=df,
        update_policy="add",
        to_metric=to_metric,
        to_attribute=to_attribute,
    )
    cube.create(folder_id=folder_id)
    return cube


def df_to_supercube(
    conn: Connection,
    cube_id: str,
    table_name: str,
    df: pd.DataFrame,
    policy: str = "replace",
    to_metric: list[str] | None = None,
    to_attribute: list[str] | None = None,
) -> SuperCube:
    """Sube un DataFrame a un super cube existente y lo publica.

    policy: "replace" (reemplaza todo), "add" (inserta filas nuevas únicas),
            "update" (actualiza filas existentes) o "upsert" (actualiza e inserta).
    `table_name` es el nombre lógico de la tabla dentro del cubo.
    """
    if policy not in SUPERCUBE_POLICIES:
        raise ValueError(f"policy inválida: {policy!r} (usar una de {SUPERCUBE_POLICIES})")
    cube = SuperCube(conn, id=cube_id)
    cube.add_table(
        name=table_name,
        data_frame=df,
        update_policy=policy,
        to_metric=to_metric,
        to_attribute=to_attribute,
    )
    cube.update()
    return cube


@contextmanager
def mstr_session(**kwargs):
    """Context manager que cierra la sesión al salir.

    with mstr_session() as conn:
        df = Report(conn, id="...").to_dataframe()
    """
    conn = get_mstr_connection(**kwargs)
    try:
        yield conn
    finally:
        conn.close()
