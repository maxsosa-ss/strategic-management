---
name: smpy
description: Usar al iniciar o modificar cualquier proyecto que necesite conectarse a MicroStrategy o Google (Sheets/Drive). Indica cómo usar la librería smpy en vez de reescribir la conexión.
---

# smpy

Librería `smpy` con las conexiones comunes. **No reimplementar** autenticación ni conexión en cada proyecto: importarla.

## Instalación en un proyecto nuevo

Siempre desde GitHub, dentro del entorno virtual del proyecto:

    pip install "smpy[all] @ git+https://github.com/maxsosa-ss/strategic-management.git"   # o [mstr] / [google] / [gcs]

**Nunca instalar con `pip install smpy` a secas**: en PyPI existe otro paquete con ese nombre (un front-end de SurveyMan, sin relación) y pip lo descargaría sin avisar. Comprobar con `pip show smpy` que la versión es `0.x` y no `1.0.3`.

Para fijar una versión, agregar `@vX.Y.Z` (una etiqueta existente) al final de la URL. Si el repositorio es privado, git debe estar autenticado.

Paquetes: `smpy.connectors` (mstr, google, gcs, pipeline) y `smpy.transforms` (conversión y limpieza de datos sin conexiones; `filters.filter_values` y `mapping.{amb,int,disc}_rubros_subrubros`).

Copiar `.env.example` a `.env` y completar. Nunca commitear `.env` ni JSON de credenciales.

## Uso

MicroStrategy (devuelve la `Connection` oficial de mstrio-py; usar el SDK directo para todo lo demás):

    from smpy.connectors.mstr import mstr_session
    from mstrio.project_objects import Report

    with mstr_session() as conn:
        df = Report(conn, id="REPORT_ID").to_dataframe()

Google:

    from smpy.connectors.google import get_sheets_client
    gc = get_sheets_client()
    ws = gc.open_by_key("SHEET_ID").worksheet("Hoja1")

    from smpy.connectors.google import get_google_service
    drive = get_google_service("drive", "v3")

Reporte -> transformación -> Sheet (`mode` = `"replace"` borra y reescribe, `"append"` agrega al final y exige las mismas columnas):

    from smpy.connectors.pipeline import report_to_sheet
    report_to_sheet(REPORT_ID, SHEET_ID, "Hoja1", mode="append", transform=mi_funcion)

Las tres rutas principales: DataFrame a hoja `df_to_sheet`, hoja a cubo `sheet_to_supercube`, DataFrame a cubo `dataframe_to_supercube` (todas en `smpy.connectors.pipeline` salvo `df_to_sheet`, que está en `smpy.connectors.google`).

    from smpy.connectors.pipeline import dataframe_to_supercube
    cube_id = dataframe_to_supercube(df, "Tabla", cube_name="Mi_cubo", to_attribute=["Periodo"])  # crea; guardar el ID
    dataframe_to_supercube(df, "Tabla", cube_id=cube_id, policy="upsert")                         # actualiza

Con más control, DataFrame -> super cube (alimenta tableros). `policy` = `replace` | `add` | `update` | `upsert`:

    from smpy.connectors.mstr import mstr_session, create_supercube, df_to_supercube
    with mstr_session() as conn:
        # carpeta: folder_id=... > MSTR_FOLDER_ID del .env > "My Reports"
        cube = create_supercube(conn, "Mi_cubo", "TablaLogica", df)       # una vez; guardar cube.id
        df_to_supercube(conn, cube.id, "TablaLogica", df2, policy="upsert")

## Qué aprendimos (no repetir estas pruebas)

- Policies del super cube, verificados en un cubo creado por API: `add` inserta solo filas nuevas (ignora repetidas); `update` modifica filas existentes e ignora las inexistentes; `upsert` hace ambas; `replace` deja solo lo enviado. Las columnas de texto/fecha son atributos y funcionan como clave; las numéricas son métricas y son lo que `update`/`upsert` modifican.
- Un cubo creado desde la interfaz web importando un Google Sheet queda **conectado al Sheet**: subirle DataFrames por API no cambia sus datos. Se actualiza con `SuperCube(conn, id=...).refresh()` (asíncrono). Para cubos que se alimentan desde Python, crearlos con `create_supercube`.
- Los `OlapCube` se actualizan con `refresh()`/`publish()` (asíncrono, devuelve un `Job`); los super cube solo se pueden publicar una vez, después se usa `update`.
- Si una hoja de Google Sheets tiene una "tabla" definida, `append_rows` de gspread pisa filas porque la tabla no crece. `df_to_sheet` ya lo evita calculando la próxima fila.
- El `.env` se busca desde la carpeta de trabajo hacia arriba (cada proyecto usa el suyo). Las rutas relativas del `.env` (por ejemplo `credentials.json`) también se resuelven desde la carpeta de trabajo: ejecutar desde la raíz del proyecto o usar rutas absolutas.

- Reportes con prompts: `report_prompts` los lista; se responden por nombre con `report_to_df(prompts={...})`. Verificado solo para tipo `VALUE` (acepta número o texto). El flag `required` no es confiable (el servidor exige responder un prompt marcado como no obligatorio). Valor inválido da `IServerError`; un período sin datos devuelve 0 filas sin error.
- El único filtro del lado del servidor es el prompt (`prompts=`). `filters`/`exclude` de `report_to_df` filtran siempre en pandas, después de descargar, y validan los nombres. Se descartó `Report.apply_filters` del SDK: se ignora en silencio en reportes con prompts (y falla en modo async), con atributos de varias formas (código y descripción) requiere IDs `idAtributo:código` que no se resuelven por nombre, `attr_elements` falla en reportes con prompts y se cuelga en reportes grandes (256 mil filas), y un elemento inexistente devuelve un DataFrame vacío sin error.
- No reutilizar un objeto `Report` entre ejecuciones: con otro prompt falla (`ERR006`) y después de `clear_filters()` devolvió un DataFrame vacío. `report_to_df` crea uno nuevo cada vez.
- Varios períodos: una conexión, una llamada por período y `pd.concat`. En paralelo (4 hilos, conexión compartida) dio los mismos resultados en 12 s contra 33 s secuenciales; usar 2 a 4 hilos.

## Reglas

- Si falta una función del SDK de MicroStrategy/Google, usar el SDK directo sobre la conexión devuelta; no agregar wrappers 1:1 a la librería.
- Solo agregar a la librería lo que se repite en 2+ proyectos (helpers de negocio, auth, reintentos).
- Variables de entorno: ver `.env.example`. Los errores de config lanzan `ConfigError`.
- Tras actualizar `mstrio-py`, correr `pytest -m live` (la versión debe ser compatible con el Intelligence Server).
