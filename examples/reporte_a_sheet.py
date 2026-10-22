"""Reporte de MicroStrategy -> transformación -> hoja de Google, acumulando filas.

Ejecutar desde la raíz del proyecto (el .env se lee desde ahí). Completá los IDs.
"""

import pandas as pd

from sm_connectors.pipeline import report_to_sheet

REPORT_ID = "ID_DEL_REPORTE"
SHEET_ID = "ID_DEL_SHEET"


def agregar_fecha_de_carga(df: pd.DataFrame) -> pd.DataFrame:
    """Ejemplo de transformación: recibe el DataFrame del reporte y devuelve el que se sube."""
    df = df.copy()
    df["Fecha de carga"] = pd.Timestamp.now().normalize()
    return df


if __name__ == "__main__":
    # mode="append" suma las filas al final; con mode="replace" se reescribe toda la pestaña.
    filas = report_to_sheet(REPORT_ID, SHEET_ID, "Historico", mode="append", transform=agregar_fecha_de_carga)
    print(f"Se escribieron {filas} filas")
