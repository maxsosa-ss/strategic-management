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

Sirve cuando los datos vienen de un CSV, una API o un cálculo. Las columnas de texto y fecha son atributos y funcionan como la clave de cada fila; las numéricas son métricas y son lo que `update` y `upsert` modifican.

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
from sm_connectors.google import df_to_sheet, get_sheets_client
from sm_connectors.mstr import mstr_session, report_to_df

with mstr_session() as conn:
    df = report_to_df(conn, "ID_REPORTE")
df = mi_transformacion(df)
df_to_sheet(get_sheets_client(), "ID_SHEET", "Hoja 1", df, mode="replace")
```

## Usar el SDK directamente

La librería no cubre todo el SDK a propósito. Cuando necesites algo que no está, pedí la conexión y usá mstrio-py como siempre:

```python
from sm_connectors.mstr import mstr_session
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
