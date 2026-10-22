---
name: sm-connectors
description: Usar al iniciar o modificar cualquier proyecto que necesite conectarse a MicroStrategy o Google (Sheets/Drive). Indica cómo usar la librería sm_connectors en vez de reescribir la conexión.
---

# sm-connectors

Librería local (`src/sm_connectors`) con las conexiones comunes. **No reimplementar** autenticación ni conexión en cada proyecto: importarla.

## Instalación en un proyecto nuevo

    pip install -e <ruta>/strategic-management[all]   # o [mstr] / [google]

Copiar `.env.example` a `.env` y completar. Nunca commitear `.env` ni JSON de credenciales.

## Uso

MicroStrategy (devuelve la `Connection` oficial de mstrio-py; usar el SDK directo para todo lo demás):

    from sm_connectors.mstr import mstr_session
    from mstrio.project_objects import Report

    with mstr_session() as conn:
        df = Report(conn, id="REPORT_ID").to_dataframe()

Google:

    from sm_connectors import get_sheets_client
    gc = get_sheets_client()
    ws = gc.open_by_key("SHEET_ID").worksheet("Hoja1")

    from sm_connectors.google import get_google_service
    drive = get_google_service("drive", "v3")

Reporte -> transformación -> Sheet (`mode` = `"replace"` borra y reescribe, `"append"` agrega al final y exige las mismas columnas):

    from sm_connectors.pipeline import report_to_sheet
    report_to_sheet(REPORT_ID, SHEET_ID, "Hoja1", mode="append", transform=mi_funcion)

DataFrame -> super cube (alimenta tableros). `policy` = `replace` | `add` | `update` | `upsert`:

    from sm_connectors.mstr import mstr_session, create_supercube, df_to_supercube
    with mstr_session() as conn:
        # carpeta: folder_id=... > MSTR_FOLDER_ID del .env > "My Reports"
        cube = create_supercube(conn, "Mi_cubo", "TablaLogica", df)       # una vez; guardar cube.id
        df_to_supercube(conn, cube.id, "TablaLogica", df2, policy="upsert")

## Qué aprendimos (no repetir estas pruebas)

- Policies del super cube, verificados en un cubo creado por API: `add` inserta solo filas nuevas (ignora repetidas); `update` modifica filas existentes e ignora las inexistentes; `upsert` hace ambas; `replace` deja solo lo enviado. Las columnas de texto/fecha son atributos y funcionan como clave; las numéricas son métricas y son lo que `update`/`upsert` modifican.
- Un cubo creado desde la interfaz web importando un Google Sheet queda **conectado al Sheet**: subirle DataFrames por API no cambia sus datos. Se actualiza con `SuperCube(conn, id=...).refresh()` (asíncrono). Para cubos que se alimentan desde Python, crearlos con `create_supercube`.
- Los `OlapCube` se actualizan con `refresh()`/`publish()` (asíncrono, devuelve un `Job`); los super cube solo se pueden publicar una vez, después se usa `update`.
- Si una hoja de Google Sheets tiene una "tabla" definida, `append_rows` de gspread pisa filas porque la tabla no crece. `df_to_sheet` ya lo evita calculando la próxima fila.
- Las rutas relativas del `.env` (por ejemplo `credentials.json`) se resuelven desde el directorio de trabajo: ejecutar desde la raíz del proyecto.

## Reglas

- Si falta una función del SDK de MicroStrategy/Google, usar el SDK directo sobre la conexión devuelta; no agregar wrappers 1:1 a la librería.
- Solo agregar a la librería lo que se repite en 2+ proyectos (helpers de negocio, auth, reintentos).
- Variables de entorno: ver `.env.example`. Los errores de config lanzan `ConfigError`.
- Tras actualizar `mstrio-py`, correr `pytest -m live` (la versión debe ser compatible con el Intelligence Server).
