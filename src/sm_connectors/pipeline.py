"""Flujos completos que combinan MicroStrategy y Google."""

from typing import Callable

import pandas as pd

from .google import df_to_sheet, get_sheets_client, sheet_to_df
from .mstr import create_supercube, df_to_supercube, mstr_session, report_to_df


def report_to_sheet(
    report_id: str,
    sheet_id: str,
    worksheet: str,
    mode: str = "replace",
    transform: Callable[[pd.DataFrame], pd.DataFrame] | None = None,
) -> int:
    """Reporte de MicroStrategy -> (transformación opcional) -> hoja de Google.

    `transform` recibe el DataFrame del reporte y devuelve el que se sube.
    `mode` es "replace" o "append" (ver `df_to_sheet`). Devuelve las filas escritas.
    """
    with mstr_session() as conn:
        df = report_to_df(conn, report_id)
    if transform:
        df = transform(df)
    return df_to_sheet(get_sheets_client(), sheet_id, worksheet, df, mode=mode)


def sheet_to_supercube(
    sheet_id: str,
    worksheet: str,
    table_name: str,
    cube_id: str | None = None,
    cube_name: str | None = None,
    policy: str = "replace",
    folder_id: str | None = None,
    transform: Callable[[pd.DataFrame], pd.DataFrame] | None = None,
    to_metric: list[str] | None = None,
    to_attribute: list[str] | None = None,
) -> str:
    """Hoja de Google -> (transformación opcional) -> super cube de MicroStrategy.

    - Sin `cube_id`: crea un cubo nuevo llamado `cube_name` (en `folder_id`, o MSTR_FOLDER_ID,
      o "My Reports") y devuelve su ID. **Guardá ese ID**: llamar de nuevo con `cube_name`
      en vez de `cube_id` intenta crear otro cubo.
    - Con `cube_id`: actualiza ese cubo con `policy` (replace | add | update | upsert).

    `table_name` es el nombre lógico de la tabla dentro del cubo y debe ser el mismo en las
    actualizaciones. Devuelve el ID del cubo.
    """
    if not cube_id and not cube_name:
        raise ValueError("Indicá cube_id (para actualizar) o cube_name (para crear)")
    df = sheet_to_df(get_sheets_client(), sheet_id, worksheet)
    if transform:
        df = transform(df)
    with mstr_session() as conn:
        if cube_id:
            df_to_supercube(conn, cube_id, table_name, df, policy=policy, to_metric=to_metric, to_attribute=to_attribute)
            return cube_id
        return create_supercube(
            conn, cube_name, table_name, df, folder_id=folder_id, to_metric=to_metric, to_attribute=to_attribute
        ).id
