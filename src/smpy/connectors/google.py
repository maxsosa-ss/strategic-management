"""Credenciales y clientes de Google (service account u OAuth)."""

from pathlib import Path

import pandas as pd

from ..config import ConfigError, get_env

DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_google_credentials(scopes: list[str] | None = None, mode: str | None = None):
    """Devuelve credenciales de google-auth según GOOGLE_AUTH_MODE (service_account | oauth | adc).

    `adc` usa las credenciales del entorno (en Cloud Run, la cuenta de servicio del servicio; en
    local, las de `gcloud auth application-default login`), sin archivos ni variables.
    """
    scopes = scopes or DEFAULT_SCOPES
    mode = mode or get_env("GOOGLE_AUTH_MODE", "service_account")

    if mode == "adc":
        import google.auth

        credentials, _ = google.auth.default(scopes=scopes)
        return credentials

    if mode == "service_account":
        from google.oauth2.service_account import Credentials

        return Credentials.from_service_account_file(get_env("GOOGLE_SERVICE_ACCOUNT_FILE"), scopes=scopes)

    if mode == "oauth":
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        token_path = Path(get_env("GOOGLE_OAUTH_TOKEN_FILE", "token.json"))
        creds = Credentials.from_authorized_user_file(str(token_path), scopes) if token_path.exists() else None
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(get_env("GOOGLE_OAUTH_CLIENT_FILE"), scopes)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
        return creds

    raise ConfigError(f"GOOGLE_AUTH_MODE inválido: {mode!r} (usar 'service_account', 'oauth' o 'adc')")


def get_sheets_client(scopes: list[str] | None = None):
    """Cliente gspread autenticado."""
    import gspread

    return gspread.authorize(get_google_credentials(scopes))


def _to_cell(value):
    """Convierte un valor de pandas a algo que la API de Sheets acepta."""
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if hasattr(value, "item"):  # tipos de numpy -> tipos nativos de Python
        return value.item()
    return value


def df_to_values(df: pd.DataFrame, include_header: bool = True) -> list[list]:
    """Convierte un DataFrame en la lista de filas que acepta la API de Sheets.

    Los vacíos pasan a "", las fechas a texto y los tipos de numpy a tipos nativos.
    """
    rows = [[_to_cell(v) for v in row] for row in df.itertuples(index=False, name=None)]
    return ([[str(c) for c in df.columns]] if include_header else []) + rows


def df_to_sheet(
    gc,
    sheet_id: str,
    worksheet: str,
    df: pd.DataFrame,
    mode: str = "replace",
    create: bool = True,
) -> int:
    """Sube un DataFrame a una hoja. Devuelve la cantidad de filas de datos escritas.

    mode="replace": borra la hoja y escribe encabezado + datos desde A1.
    mode="append":  agrega las filas al final. Si la hoja está vacía escribe también el
                    encabezado; si no, exige que las columnas coincidan con las existentes.
    """
    if mode not in ("replace", "append"):
        raise ValueError(f"mode inválido: {mode!r} (usar 'replace' o 'append')")

    import gspread

    spreadsheet = gc.open_by_key(sheet_id)
    try:
        ws = spreadsheet.worksheet(worksheet)
    except gspread.WorksheetNotFound:
        if not create:
            raise
        ws = spreadsheet.add_worksheet(worksheet, rows=max(len(df) + 1, 100), cols=max(len(df.columns), 10))

    if mode == "replace":
        values = df_to_values(df)  # se arma antes de borrar para no vaciar la hoja si falla
        ws.clear()
        ws.update(values, "A1")
        return len(df)

    existing_header = ws.row_values(1)
    if existing_header:
        if existing_header != [str(c) for c in df.columns]:
            raise ValueError(
                f"Las columnas no coinciden con el encabezado de la hoja.\n"
                f"Hoja:      {existing_header}\nDataFrame: {list(df.columns)}"
            )
        values = df_to_values(df, include_header=False)
    else:
        values = df_to_values(df)
    if values:
        # La próxima fila se calcula acá y no con `append_rows`: si la hoja tiene una "tabla" de
        # Google Sheets, la API agrega según el rango de esa tabla (que no crece) y pisa filas.
        next_row = len(ws.get_all_values()) + 1
        missing = next_row + len(values) - 1 - ws.row_count
        if missing > 0:
            ws.add_rows(missing)
        ws.update(values, f"A{next_row}")
    return len(df)


def sheet_to_df(gc, sheet_id: str, worksheet: str, header_row: int = 1) -> pd.DataFrame:
    """Lee una pestaña como DataFrame. La fila `header_row` se usa como encabezado.

    Los números y booleanos llegan tipados; las celdas vacías llegan como "". Las columnas sin
    encabezado se ignoran (típicamente notas sueltas al costado de la tabla). Lanza ValueError si
    la pestaña no tiene filas de datos, para no propagar una carga vacía.
    """
    ws = gc.open_by_key(sheet_id).worksheet(worksheet)
    encabezados = [h for h in ws.row_values(header_row) if h != ""]
    records = ws.get_all_records(head=header_row, expected_headers=encabezados)
    df = pd.DataFrame(records).drop(columns="", errors="ignore")
    if df.empty:
        raise ValueError(f"La pestaña {worksheet!r} no tiene filas de datos debajo de la fila {header_row}")
    return df


def get_google_service(api: str, version: str, scopes: list[str] | None = None):
    """Cliente genérico de la API de Google, ej. get_google_service('drive', 'v3')."""
    from googleapiclient.discovery import build

    return build(api, version, credentials=get_google_credentials(scopes))
