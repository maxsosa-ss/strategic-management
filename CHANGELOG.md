# Historial de cambios

Sigue el formato de [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [versionado semántico](https://semver.org/lang/es/): mientras la versión sea `0.x`, un cambio de minor (`0.2` a `0.3`) puede romper la interfaz.

## Sin publicar

Sin cambios todavía.

## 0.3.0 - 2026-10-23

### Agregado
- `dataframe_to_supercube`: sube un DataFrame a un super cube en una sola llamada, creándolo (`cube_name`) o actualizándolo (`cube_id`). Acepta una `conn` ya abierta para subir varios cubos con una sola conexión.
- Identidad visual con la paleta de marca: título "SMPY" en el README y en la portada del sitio, franjas separadoras en el README, ícono del sitio (`favicon.svg`) e imagen para compartir el repositorio (`docs/assets/social-preview.png`, para subir a mano en Settings > Social preview de GitHub).
- Paquete `smpy.transforms` para funciones de conversión y limpieza de datos que no dependen de ninguna conexión. Primera función: `filter_values`, que filtra un DataFrame por valores de columnas y valida los nombres con sugerencias.
- `report_prompts`: lista los prompts de un reporte (nombre, tipo, tipo de dato, clave).
- `report_to_df` acepta `prompts` (respuestas a los prompts, por nombre), `filters` y `exclude` (filtros por columna, en pandas sobre el reporte ya descargado) y `strict`. El filtro del lado del servidor es el prompt. `report_to_sheet` los acepta también.

### Cambiado
- **Cambio incompatible:** el paquete se llama ahora `smpy` (antes `sm-connectors` / `sm_connectors`) y el código se reorganizó en subpaquetes. Los imports pasan de `sm_connectors.mstr`, `sm_connectors.google` y `sm_connectors.pipeline` a `smpy.connectors.mstr`, `smpy.connectors.google` y `smpy.connectors.pipeline`. Se eliminaron los atajos de importación: ahora cada función se importa solo desde el módulo donde está definida, por ejemplo `from smpy.connectors.google import get_sheets_client` y `from smpy.config import get_env`, en lugar de `from sm_connectors import get_sheets_client`. El skill pasa de `sm-connectors` a `smpy`.
- `sheet_to_supercube` ahora reutiliza `dataframe_to_supercube` y también acepta `conn`.
- La instalación se documenta siempre desde GitHub (`pip install "smpy[all] @ git+https://..."`) en el README, el sitio y el skill, con una advertencia: en PyPI existe otro paquete llamado `smpy`, por lo que no hay que instalarlo con `pip install smpy` a secas.

### Corregido
- Al usar la librería desde otro proyecto, leía el `.env` de la propia librería en lugar del `.env` del proyecto. Ahora busca el `.env` desde la carpeta de trabajo hacia arriba, y una variable de entorno real tiene prioridad sobre el archivo.

## 0.2.0 - 2026-10-22

### Agregado
- `create_supercube` y `df_to_supercube`: crean y actualizan super cubes desde un DataFrame con las políticas `replace`, `add`, `update` y `upsert`.
- `MSTR_FOLDER_ID` (opcional) y parámetro `folder_id`: carpeta destino para los cubos nuevos.
- `report_to_df`: ejecuta un reporte de MicroStrategy y devuelve un DataFrame.
- `df_to_sheet` con `mode="replace"` y `mode="append"`; el modo `append` valida que las columnas coincidan con el encabezado.
- `sheet_to_df`: lee una pestaña de Google Sheets como DataFrame.
- `report_to_sheet` y `sheet_to_supercube`: flujos completos con transformación opcional.
- Documentación: README, sitio con MkDocs, recetas y ejemplos ejecutables.

### Cambiado
- El proyecto de MicroStrategy se identifica solo por ID (`MSTR_PROJECT_ID`); se eliminó `MSTR_PROJECT_NAME`.
- El usuario de MicroStrategy se lee de `MSTR_USER`.

### Corregido
- `df_to_sheet(mode="append")` pisaba filas en pestañas que tienen una tabla de Google Sheets definida, porque la tabla no crece al agregar filas. Ahora calcula la próxima fila libre.

## 0.1.0 - 2026-10-21

### Agregado
- Estructura inicial: conexión a MicroStrategy (`get_mstr_connection`, `mstr_session`) y a Google (`get_google_credentials`, `get_sheets_client`, `get_google_service`) con configuración por `.env`.
