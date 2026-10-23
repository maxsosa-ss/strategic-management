"""smpy: conexiones y herramientas de datos reutilizables.

- `smpy.connectors`: conexiones a MicroStrategy y Google, y los flujos que mueven DataFrames
  entre un sistema y otro.
- `smpy.transforms`: funciones de conversión y limpieza de datos, independientes de las conexiones.
- `smpy.config`: lectura de la configuración (`.env` y variables de entorno).

Este paquete no reexporta funciones a propósito: cada una se importa desde el módulo donde está
definida (por ejemplo `from smpy.connectors.google import get_sheets_client`), así siempre se ve
de dónde viene. Las dependencias pesadas se instalan por extras: `[mstr]`, `[google]` o `[all]`
(ver el README para instalar desde GitHub).
"""

from importlib import metadata as _metadata

try:
    __version__ = _metadata.version("smpy")
except _metadata.PackageNotFoundError:  # se usa el código sin instalarlo
    __version__ = "desconocida"
