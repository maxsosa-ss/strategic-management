# Historial de cambios

Sigue el formato de [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y [versionado semántico](https://semver.org/lang/es/): mientras la versión sea `0.x`, un cambio de minor (`0.2` a `0.3`) puede romper la interfaz.

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
