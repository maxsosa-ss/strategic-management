<h1 align="center"><img src="docs/assets/smpy.svg" alt="smpy" width="720"></h1>

Conexiones a MicroStrategy y Google listas para usar, para no reescribirlas en cada proyecto. La librería envuelve los SDK oficiales ([mstrio-py](https://github.com/MicroStrategy/mstrio-py), [gspread](https://github.com/burnash/gspread), google-auth) y suma solo lo que se repite: credenciales, conexión y los flujos que mueven DataFrames entre un sistema y otro.

Cuando el SDK de MicroStrategy agrega algo nuevo, ya lo tenés: la conexión que devuelve la librería es la `Connection` oficial, sin capas en el medio.

## Estructura

| Paquete | Para qué sirve |
|---|---|
| `smpy.connectors` | Conexiones a MicroStrategy y Google, y los flujos que mueven DataFrames entre reportes, hojas y cubos |
| `smpy.transforms` | Funciones de conversión y limpieza de datos que no dependen de ninguna conexión. Por ahora: filtrado de DataFrames por valores de columnas |
| `smpy.config` | Lectura de la configuración desde el `.env` y las variables de entorno |

Cada función se importa desde el módulo donde está definida; `smpy` no reexporta nada. Así siempre se ve de dónde viene: `from smpy.connectors.google import get_sheets_client`, `from smpy.connectors.mstr import mstr_session`, `from smpy.connectors.pipeline import dataframe_to_supercube`.

<!-- --8<-- [start:instalacion] -->
## Instalación

Requiere Python 3.10 o superior.

La librería se instala siempre desde GitHub, dentro del entorno virtual del proyecto que la usa:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install "smpy[all] @ git+https://github.com/maxsosa-ss/strategic-management.git"
```

> **Importante: instalá siempre con la URL de GitHub y nunca con `pip install smpy` a secas.** En PyPI ya existe otro paquete con el nombre `smpy` (un front-end de Python para el lenguaje de encuestas SurveyMan, sin mantenimiento desde 2015). Sin la URL, pip descarga ese paquete en lugar de este y no muestra ningún error.

Para comprobar que instalaste el correcto, ejecutá `pip show smpy`: tiene que figurar la versión `0.x` de esta librería y no la `1.0.3` del paquete de encuestas. Si instalaste el equivocado, corré `pip uninstall smpy` y volvé a instalar con el comando de arriba.

Si solo necesitás una parte, reemplazá `[all]` por `[mstr]` o `[google]`. Para actualizar a la última versión, agregá `--upgrade`.

Para fijar una versión concreta, agregá una etiqueta al final de la URL, por ejemplo `...strategic-management.git@v0.3.0`. Las etiquetas disponibles están en la sección Releases del repositorio.

Si el repositorio es privado, git tiene que estar autenticado con tu cuenta de GitHub antes de instalar (por ejemplo con `gh auth login`, un token personal o una clave SSH).
<!-- --8<-- [end:instalacion] -->

<!-- --8<-- [start:configuracion] -->
## Configuración

Copiá `.env.example` a `.env` en la raíz del proyecto desde el que ejecutás tus scripts y completalo. La librería busca el `.env` desde la carpeta de trabajo hacia arriba, así que cada proyecto usa el suyo, y una variable de entorno del sistema tiene prioridad sobre el archivo. Las rutas relativas, como `credentials.json`, también se resuelven desde la carpeta de trabajo; si ejecutás scripts desde otro lugar (por ejemplo con el Programador de tareas), usá rutas absolutas.

| Variable | Obligatoria | Qué es |
|---|---|---|
| `MSTR_BASE_URL` | Sí | URL de MicroStrategy Library, por ejemplo `https://servidor/MicroStrategyLibrary` |
| `MSTR_USER` | Sí | Usuario |
| `MSTR_PASSWORD` | Sí | Contraseña |
| `MSTR_PROJECT_ID` | Sí | ID del proyecto (32 caracteres). Se usa siempre el ID, nunca el nombre |
| `MSTR_LOGIN_MODE` | No | `1` estándar (por defecto) o `16` LDAP |
| `MSTR_FOLDER_ID` | No | Carpeta donde se crean los cubos nuevos. Si falta, van a "My Reports" |
| `GOOGLE_AUTH_MODE` | No | `service_account` (por defecto) u `oauth` |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Con `service_account` | Ruta al JSON de la service account |
| `GOOGLE_OAUTH_CLIENT_FILE` | Con `oauth` | Ruta al client secret de OAuth |
| `GOOGLE_OAUTH_TOKEN_FILE` | Con `oauth` | Dónde guardar el token (por defecto `token.json`) |

Para que la librería escriba en un Google Sheet con una service account, compartí el Sheet con el `client_email` que figura en el JSON.

El `.env` y los JSON de credenciales están en `.gitignore`. No los subas al repositorio.
<!-- --8<-- [end:configuracion] -->

<img src="docs/assets/franja.svg" alt="" width="100%" height="6">

## Uso

Llevar el resultado de un reporte a una hoja, agregando filas al final y transformando antes de subir:

```python
from smpy.connectors.pipeline import report_to_sheet

report_to_sheet("ID_REPORTE", "ID_SHEET", "Historico", mode="append", transform=mi_funcion)
```

Crear un super cube desde una hoja y después mantenerlo actualizado:

```python
from smpy.connectors.pipeline import sheet_to_supercube

cube_id = sheet_to_supercube("ID_SHEET", "Hoja 1", "Paises", cube_name="Paises")  # guardá cube_id
sheet_to_supercube("ID_SHEET", "Hoja 1", "Paises", cube_id=cube_id, policy="replace")
```

Subir un DataFrame propio a un cubo, sin pasar por una hoja:

```python
from smpy.connectors.pipeline import dataframe_to_supercube

cube_id = dataframe_to_supercube(df, "Paises", cube_name="Paises", to_attribute=["Periodo"])
dataframe_to_supercube(df, "Paises", cube_id=cube_id, policy="upsert")
```

Bajar un reporte con prompts y filtros (`report_prompts` te dice qué prompts tiene):

```python
from smpy.connectors.mstr import mstr_session, report_prompts, report_to_df

with mstr_session() as conn:
    print(report_prompts(conn, "ID_REPORTE"))
    df = report_to_df(conn, "ID_REPORTE",
                      prompts={"Valor de Periodo": 202609},          # lo filtra MicroStrategy
                      filters={"Zona": ["AMBA", "CUYO"]},            # se filtra en pandas, con validación
                      exclude={"Zona": "F/D"})
```

Usar el SDK de MicroStrategy directamente cuando la librería no tiene lo que necesitás:

```python
from smpy.connectors.mstr import mstr_session
from mstrio.project_objects import Report

with mstr_session() as conn:      # cierra la sesión al salir
    df = Report(conn, id="ID_REPORTE").to_dataframe()
```

Hay más ejemplos listos para ejecutar en [examples/](examples/) y recetas explicadas en la [documentación](docs/recetas.md).

## Qué incluye

| Quiero | Función | Módulo |
|---|---|---|
| Conectarme a MicroStrategy | `get_mstr_connection`, `mstr_session` | `smpy.connectors.mstr` |
| Traer un reporte como DataFrame, respondiendo sus prompts y filtrando | `report_to_df` | `smpy.connectors.mstr` |
| Ver qué prompts tiene un reporte | `report_prompts` | `smpy.connectors.mstr` |
| Crear un super cube desde un DataFrame | `create_supercube` | `smpy.connectors.mstr` |
| Actualizar un super cube (`replace`, `add`, `update`, `upsert`) | `df_to_supercube` | `smpy.connectors.mstr` |
| Obtener credenciales o clientes de Google | `get_google_credentials`, `get_sheets_client`, `get_google_service` | `smpy.connectors.google` |
| Leer una pestaña como DataFrame | `sheet_to_df` | `smpy.connectors.google` |
| Escribir un DataFrame en una pestaña (`replace` o `append`) | `df_to_sheet` | `smpy.connectors.google` |
| Reporte a hoja, con transformación opcional | `report_to_sheet` | `smpy.connectors.pipeline` |
| Hoja a super cube, con transformación opcional | `sheet_to_supercube` | `smpy.connectors.pipeline` |
| DataFrame a super cube, creando o actualizando, en una sola llamada | `dataframe_to_supercube` | `smpy.connectors.pipeline` |
| Filtrar un DataFrame por valores de columnas, con validación | `filter_values` | `smpy.transforms.filters` |

Las tres rutas que más se usan quedan así: DataFrame a hoja con `df_to_sheet`, hoja a cubo con `sheet_to_supercube` y DataFrame a cubo con `dataframe_to_supercube`.

La referencia completa, con parámetros y comportamiento de cada función, está en la documentación.

<img src="docs/assets/franja.svg" alt="" width="100%" height="6">

## Documentación

Para ver el sitio de documentación necesitás una copia del repositorio (`git clone`), porque los archivos de `docs/` no se instalan con `pip`. Desde la carpeta clonada:

```bash
pip install -e ".[docs]"
mkdocs serve
```

Abrí http://127.0.0.1:8000. El historial de versiones está en [CHANGELOG.md](CHANGELOG.md).

## Pruebas

```bash
pytest              # pruebas sin red
pytest -m live      # conexión real a MicroStrategy y Google; requiere el .env
```

Corré `pytest -m live` después de actualizar `mstrio-py` o `gspread`. La versión de `mstrio-py` tiene que ser compatible con tu Intelligence Server.

## Skills

La carpeta [skills/](skills/) contiene los skills asociados al repositorio. Son archivos `SKILL.md` en texto plano, así que sirven con cualquier asistente de IA que los soporte. `smpy` le indica al asistente que use esta librería al iniciar un proyecto, en lugar de reescribir las conexiones.
