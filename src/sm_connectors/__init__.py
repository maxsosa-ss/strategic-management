"""Conexiones reutilizables a MicroStrategy y Google.

Las dependencias pesadas se importan de forma perezosa: instalá solo los extras que uses
(`pip install -e .[mstr]`, `.[google]` o `.[all]`).
"""

from importlib.metadata import PackageNotFoundError, version

from .config import ConfigError, get_env

try:
    __version__ = version("sm-connectors")
except PackageNotFoundError:  # se usa el código sin instalarlo
    __version__ = "desconocida"

__all__ = ["__version__", "ConfigError", "get_env", "get_mstr_connection", "get_google_credentials", "get_sheets_client"]


def get_mstr_connection(*args, **kwargs):
    from .mstr import get_mstr_connection as _f

    return _f(*args, **kwargs)


def get_google_credentials(*args, **kwargs):
    from .google import get_google_credentials as _f

    return _f(*args, **kwargs)


def get_sheets_client(*args, **kwargs):
    from .google import get_sheets_client as _f

    return _f(*args, **kwargs)
