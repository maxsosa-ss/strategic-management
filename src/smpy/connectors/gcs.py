"""Lectura de archivos Parquet desde Google Cloud Storage."""

import io

import pandas as pd

from ..config import get_env
from .google import get_google_credentials

GCS_SCOPES = ["https://www.googleapis.com/auth/devstorage.read_only"]


def get_storage_client(scopes: list[str] | None = None):
    """Cliente de Google Cloud Storage con las credenciales según GOOGLE_AUTH_MODE.

    En Cloud Run usá `GOOGLE_AUTH_MODE=adc`: toma la cuenta de servicio del servicio, sin archivos.
    """
    from google.cloud import storage

    return storage.Client(credentials=get_google_credentials(scopes or GCS_SCOPES))


def read_parquet(
    path: str,
    bucket: str | None = None,
    columns: list[str] | None = None,
    client=None,
) -> pd.DataFrame:
    """Lee un archivo Parquet del bucket como DataFrame.

    `path` es la ruta del objeto dentro del bucket (por ejemplo `"crudos/ambulatorio.parquet"`).
    Si no se pasa `bucket`, usa la variable `GCS_BUCKET`. `columns` limita las columnas que se
    leen. `client` permite reutilizar un cliente ya creado (ver `get_storage_client`).

    Lanza FileNotFoundError, con el bucket y la ruta, si el objeto no existe.
    """
    from google.api_core.exceptions import NotFound

    bucket = bucket or get_env("GCS_BUCKET")
    client = client or get_storage_client()
    blob = client.bucket(bucket).blob(path)
    try:
        contenido = blob.download_as_bytes()
    except NotFound as e:
        raise FileNotFoundError(f"No existe gs://{bucket}/{path}") from e
    return pd.read_parquet(io.BytesIO(contenido), columns=columns)
