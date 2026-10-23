# Recetas

Cada receta tiene su script en la carpeta `examples/` del repositorio, listo para ejecutar. Completá los IDs y ejecutalo desde la raíz del proyecto, donde está el `.env`.

## Llevar un reporte a una hoja, acumulando filas

Usá `mode="append"` cuando la hoja es un historial que crece con cada ejecución, y `mode="replace"` cuando la hoja tiene que reflejar el estado actual del reporte.

```python
--8<-- "examples/reporte_a_sheet.py"
```

Con `append`, la función exige que las columnas del DataFrame coincidan con el encabezado de la hoja. Si no coinciden, no escribe nada y explica la diferencia. Una hoja vacía recibe el encabezado y las filas.

!!! warning "Ejecutar dos veces suma las filas dos veces"
    `append` no detecta duplicados. Si el reporte devuelve siempre el período completo, usá `replace`.

## Crear un cubo desde una hoja y mantenerlo actualizado

`sheet_to_supercube` crea el cubo cuando le pasás `cube_name` y lo actualiza cuando le pasás `cube_id`. Guardá el ID que devuelve la primera vez.

```python
--8<-- "examples/sheet_a_cubo.py"
```

El cubo se crea en la carpeta que indiques con `folder_id`. Si no lo pasás, usa `MSTR_FOLDER_ID` del `.env`, y si tampoco está, "My Reports".

!!! warning "Los cubos importados desde la web quedan conectados a su origen"
    Un cubo que creaste en la interfaz de Strategy importando un Google Sheet se actualiza leyendo de nuevo el Sheet (`SuperCube(conn, id=...).refresh()`). Subirle un DataFrame desde Python no cambia sus datos. Para cubos que se alimentan desde Python, creálos con `create_supercube` o `sheet_to_supercube`.

## Alimentar un cubo con un DataFrame propio

Sirve cuando los datos vienen de un CSV, una API o un cálculo, o cuando armás el DataFrame uniendo varias fuentes. `dataframe_to_supercube` lo crea o lo actualiza en una sola llamada:

```python
from smpy.connectors.pipeline import dataframe_to_supercube

cube_id = dataframe_to_supercube(df, "Tabla", cube_name="Mi cubo", to_attribute=["Periodo"])  # crea
dataframe_to_supercube(df, "Tabla", cube_id=cube_id, policy="upsert")                         # actualiza
```

Para subir varios cubos seguidos con una sola conexión, abrí la sesión vos y pasala con `conn=`.

!!! tip "Los períodos numéricos"
    Una columna como `Periodo` (202510) llega como número y el cubo la trata como métrica. Si querés que sea un atributo, indicá `to_attribute=["Periodo"]`.

Las columnas de texto y fecha son atributos y funcionan como la clave de cada fila; las numéricas son métricas y son lo que `update` y `upsert` modifican. Este script muestra las cuatro políticas con las funciones de más bajo nivel:

```python
--8<-- "examples/dataframe_a_cubo.py"
```

| Política | Qué hace con las filas existentes | Qué hace con las filas nuevas |
|---|---|---|
| `replace` | Las borra: el cubo queda con lo que enviás | Las inserta |
| `add` | Las deja como están | Las inserta |
| `update` | Modifica las métricas | Las ignora |
| `upsert` | Modifica las métricas | Las inserta |

Si un número llega como texto (por ejemplo un código como `"001"`) y querés controlar cómo se clasifica, usá `to_metric=[...]` o `to_attribute=[...]` para forzar la columna.

## Transformar los datos antes de subirlos

Los flujos `report_to_sheet` y `sheet_to_supercube` aceptan `transform`: una función que recibe el DataFrame y devuelve el que se sube.

```python
def mi_transformacion(df):
    df = df.rename(columns={"País": "Pais"})
    df["Pais"] = df["Pais"].str.strip()
    return df
```

Escribí la transformación como una función de DataFrame a DataFrame, sin conexiones adentro. Así la probás con datos de ejemplo, sin tocar MicroStrategy ni Google. Las transformaciones propias de un proyecto viven en ese proyecto; si se repiten en dos o más, conviene subirlas a la librería.

Si necesitás controlar cada paso por separado, por ejemplo para reintentar solo la subida, usá las funciones sueltas:

```python
from smpy.connectors.google import df_to_sheet, get_sheets_client
from smpy.connectors.mstr import mstr_session, report_to_df

with mstr_session() as conn:
    df = report_to_df(conn, "ID_REPORTE")
df = mi_transformacion(df)
df_to_sheet(get_sheets_client(), "ID_SHEET", "Hoja 1", df, mode="replace")
```

## Bajar un reporte con prompts y filtros

Primero mirá qué prompts tiene el reporte y de qué tipo son:

```python
from smpy.connectors.mstr import mstr_session, report_prompts, report_to_df

with mstr_session() as conn:
    print(report_prompts(conn, "ID_REPORTE"))
```

Después respondelos por nombre con `prompts=`. Es el filtro dinámico del reporte y el más eficiente, porque lo aplica MicroStrategy antes de enviar los datos. Para filtrar además por los valores de un atributo, usá `filters` (dejar solo esos valores) y `exclude` (sacarlos):

```python
df = report_to_df(conn, "ID_REPORTE",
                  prompts={"Valor de Periodo": 202609},
                  filters={"Subzona Direccion Comercial Asociado": ["CABA", "GBA NORTE"]},
                  exclude={"Zona Direccion Comercial Asociado": "F/D"})
```

`filters` y `exclude` usan el nombre de la columna del DataFrame y se aplican en pandas, después de descargar. Funcionan en cualquier reporte, admiten incluir y excluir a la vez, y validan los valores: si escribís `"AMBBA"`, el error dice `¿Quisiste decir 'AMBA'?` y lista los valores disponibles. Con `strict=False` los valores inexistentes se ignoran en lugar de dar error.

!!! warning "Los prompts cambian de un reporte a otro"
    Cada reporte tiene los prompts que definió su autor, y pueden cambiar. Por eso `report_prompts` es el primer paso. Los prompts de tipo `VALUE` (un número, un texto o una fecha) reciben un solo valor y están probados. Para `ELEMENTS`, `OBJECTS` y `EXPRESSION`, el valor se envía tal cual a la API, así que tenés que pasar la estructura que espera MicroStrategy; esos tipos todavía no están verificados.

!!! note "Dos filtros, cada uno en su lugar"
    El **prompt** es el filtro dinámico del reporte y lo aplica MicroStrategy antes de descargar: es el único filtro que se hace del lado del servidor. `filters` y `exclude` se aplican siempre sobre el reporte **ya descargado**, así que no reducen lo que se descarga. Si necesitás bajar menos datos, hace falta un prompt (o pedirle al autor del reporte que agregue uno).

    Se probó filtrar del lado del servidor con `Report.apply_filters` del SDK y se descartó: en reportes con prompts MicroStrategy lo ignora sin avisar, no funciona con atributos que tienen varias formas (código y descripción), y resolver los nombres de los elementos ejecuta el reporte, que en uno grande puede colgarse.

## Descargar varios períodos

Abrí una sola conexión y llamá a `report_to_df` una vez por período; después unís los resultados:

```python
import pandas as pd

with mstr_session() as conn:
    dfs = [report_to_df(conn, "ID_REPORTE", prompts={"Valor de Periodo": p}) for p in periodos]
historico = pd.concat(dfs, ignore_index=True)
```

Con el reporte de ejemplo (farmacia, unas 1.150 filas por período), cada ejecución tardó entre 7 y 9 segundos, casi todo en la consulta de MicroStrategy. Así que 4 períodos tardaron unos 33 segundos en secuencia. Lo que se probó para ir más rápido:

| Forma | Tiempo (4 períodos) | Resultado |
|---|---|---|
| Secuencial, un `Report` nuevo por período (lo que hace `report_to_df`) | 33 s | Correcto |
| Paralelo, 4 hilos con una conexión compartida | 12 s | Mismos resultados que en secuencia |
| Reutilizar un solo objeto `Report` con distintos prompts | — | **Falla** desde el segundo período |

!!! warning "No reutilices el objeto `Report` del SDK"
    El objeto conserva el estado de la ejecución anterior y la segunda llamada falla (`No opened prompts need to be answered`). `report_to_df` ya crea uno nuevo en cada llamada; por eso conviene usarla en lugar de armar el loop con `Report` a mano.

Los hilos aceleran, pero cada uno es una consulta más sobre el servidor: usá 2 a 4, no más. Funcionó en la prueba, pero el SDK no garantiza que una conexión se pueda compartir entre hilos, así que probalo con tus datos antes de automatizarlo. El script completo está en `examples/reporte_con_prompts.py`.

Para bajar menos, antes que paralelizar:
- **No vuelvas a descargar los períodos cerrados.** Guardá el histórico (en una hoja con `mode="append"`, o en un cubo con `policy="upsert"`) y bajá solo el período actual.
- **Pedile al autor del reporte un prompt que acepte varios períodos o un rango.** Una sola consulta que trae todo suele ser más barata que N consultas.
- **Si lo necesitás seguido, volcalo a un cubo** y leé de ahí: leer un cubo es mucho más rápido que ejecutar el reporte.

## Usar el SDK directamente

La librería no cubre todo el SDK a propósito. Cuando necesites algo que no está, pedí la conexión y usá mstrio-py como siempre:

```python
from smpy.connectors.mstr import mstr_session
from mstrio.project_objects import Report

with mstr_session() as conn:
    df = Report(conn, id="ID_REPORTE").to_dataframe(limit=1000)
```

Para otras APIs de Google, `get_google_service("drive", "v3")` devuelve el cliente oficial ya autenticado.

## Actualizar un cubo OLAP

Los cubos OLAP se alimentan de una consulta a la base y no aceptan un DataFrame. Se actualizan pidiéndole a MicroStrategy que vuelva a ejecutar la consulta. La librería no tiene un helper para esto todavía; usá el SDK:

```python
from mstrio.project_objects.datasets import OlapCube

with mstr_session() as conn:
    job = OlapCube(conn, id="ID_CUBO").refresh()   # asíncrono: devuelve un Job
```
