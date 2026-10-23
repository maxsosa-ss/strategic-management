"""Lectura de configuración desde variables de entorno / .env."""

import os

from dotenv import find_dotenv, load_dotenv

# usecwd=True busca el .env desde la carpeta de trabajo hacia arriba (el del proyecto que usa la
# librería). Sin esto, python-dotenv parte de la carpeta de este archivo y lee el .env de la librería.
load_dotenv(find_dotenv(usecwd=True))


class ConfigError(RuntimeError):
    """Falta una variable de entorno requerida."""


def get_env(name: str, default: str | None = None, required: bool = True) -> str | None:
    """Lee una variable de entorno (el `.env` se carga al importar la librería).

    Si `required` es True y la variable no existe o está vacía, lanza `ConfigError`.
    """
    value = os.getenv(name, default)
    if required and not value:
        raise ConfigError(f"Falta la variable de entorno {name} (ver .env.example)")
    return value
