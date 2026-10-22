"""Un DataFrame propio (de un CSV, una API, un cálculo) -> super cube, con las 4 políticas.

Ejecutar desde la raíz del proyecto (el .env se lee desde ahí).
"""

import pandas as pd

from sm_connectors.mstr import create_supercube, df_to_supercube, mstr_session

TABLA = "Paises"

# Las columnas de texto son atributos (identifican la fila); las numéricas son métricas.
base = pd.DataFrame(
    {"País": ["Argentina", "Chile"], "Capital": ["Buenos Aires", "Santiago"], "Población_M": [46, 19]}
)

with mstr_session() as conn:
    cubo = create_supercube(conn, "Paises_demo", TABLA, base)  # carpeta: folder_id > MSTR_FOLDER_ID > My Reports
    cubo_id = cubo.id

    # add: inserta solo filas nuevas (ignora las que ya existen)
    df_to_supercube(conn, cubo_id, TABLA, pd.DataFrame(
        {"País": ["Perú"], "Capital": ["Lima"], "Población_M": [34]}), policy="add")

    # update: modifica filas existentes (ignora las que no existen)
    df_to_supercube(conn, cubo_id, TABLA, pd.DataFrame(
        {"País": ["Chile"], "Capital": ["Santiago"], "Población_M": [20]}), policy="update")

    # upsert: modifica las existentes e inserta las nuevas
    df_to_supercube(conn, cubo_id, TABLA, pd.DataFrame(
        {"País": ["Chile", "Bolivia"], "Capital": ["Santiago", "Sucre"], "Población_M": [20, 12]}), policy="upsert")

    # replace: el cubo queda con exactamente lo que enviás
    df_to_supercube(conn, cubo_id, TABLA, base, policy="replace")
