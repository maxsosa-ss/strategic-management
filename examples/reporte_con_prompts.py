"""Reporte con prompts y filtros: un período, varios períodos y varios períodos en paralelo.

Ejecutar desde la raíz del proyecto (el .env se lee desde ahí). Completá los IDs y el nombre del prompt.
"""

from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from smpy.connectors.mstr import mstr_session, report_prompts, report_to_df

REPORT_ID = "ID_DEL_REPORTE"
PROMPT = "Valor de Periodo"  # el nombre que muestra report_prompts
PERIODOS = [202607, 202608, 202609]

with mstr_session() as conn:  # una sola conexión para todo el script
    # 1. Qué prompts tiene el reporte
    print(report_prompts(conn, REPORT_ID))

    # 2. Un período; el resto de los filtros se aplican en pandas, con validación de los nombres
    df = report_to_df(
        conn,
        REPORT_ID,
        prompts={PROMPT: 202609},                         # lo filtra MicroStrategy
        filters={"Subzona Direccion Comercial Asociado": ["CABA", "GBA NORTE"]},
        exclude={"Zona Direccion Comercial Asociado": "F/D"},  # sacar las filas sin zona
    )

    # 3. Varios períodos, uno detrás de otro
    dfs = [report_to_df(conn, REPORT_ID, prompts={PROMPT: p}) for p in PERIODOS]
    historico = pd.concat(dfs, ignore_index=True)

    # 4. Varios períodos en paralelo (2 a 4 hilos; más carga al servidor, no más rápido sin límite)
    with ThreadPoolExecutor(max_workers=3) as pool:
        dfs = list(pool.map(lambda p: report_to_df(conn, REPORT_ID, prompts={PROMPT: p}), PERIODOS))
    historico = pd.concat(dfs, ignore_index=True)
