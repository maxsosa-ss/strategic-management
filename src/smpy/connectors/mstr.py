"""Conexión a MicroStrategy. Devuelve la `Connection` oficial de mstrio-py sin envolverla,
así cualquier función nueva del SDK queda disponible de inmediato."""

from contextlib import contextmanager

import pandas as pd
from mstrio.connection import Connection
from mstrio.helpers import IServerError
from mstrio.modeling.prompt import Prompt
from mstrio.project_objects import Report
from mstrio.project_objects.datasets import SuperCube

from ..config import get_env
from ..transforms.filters import filter_values


def get_mstr_connection(
    base_url: str | None = None,
    username: str | None = None,
    password: str | None = None,
    project_id: str | None = None,
    login_mode: int | None = None,
) -> Connection:
    """Crea una conexión. Los parámetros omitidos se leen de MSTR_* en el entorno.

    El proyecto se identifica siempre por ID (MSTR_PROJECT_ID), no por nombre.
    """
    return Connection(
        base_url=base_url or get_env("MSTR_BASE_URL"),
        username=username or get_env("MSTR_USER"),
        password=password or get_env("MSTR_PASSWORD"),
        project_id=project_id or get_env("MSTR_PROJECT_ID"),
        login_mode=login_mode or int(get_env("MSTR_LOGIN_MODE", "1")),
    )


def _definir_prompts(report: Report) -> list[dict]:
    """Prompts del reporte como diccionarios (nombre, título, tipo, clave...)."""
    return [p.to_dict() for p in report.prompts]


def _nombre_prompt(definicion: dict) -> str:
    return definicion.get("title") or definicion.get("name") or definicion["key"]


def report_prompts(conn: Connection, report_id: str) -> pd.DataFrame:
    """Lista los prompts de un reporte: es lo que hay que responder con `prompts=` en `report_to_df`.

    Columnas: `nombre` (el que se usa como clave en `prompts=`), `tipo` (VALUE, ELEMENTS,
    OBJECTS, EXPRESSION, LEVEL), `tipo_de_dato`, `obligatorio` y `clave`. Ojo: `obligatorio` no
    es confiable; MicroStrategy puede exigir responder un prompt marcado como no obligatorio.
    """
    filas = [
        {
            "nombre": _nombre_prompt(d),
            "tipo": d.get("type"),
            "tipo_de_dato": d.get("dataType"),
            "obligatorio": d.get("required"),
            "clave": d["key"],
        }
        for d in _definir_prompts(Report(conn, id=report_id))
    ]
    return pd.DataFrame(filas, columns=["nombre", "tipo", "tipo_de_dato", "obligatorio", "clave"])


def _buscar_prompt(definiciones: list[dict], pedido: str) -> dict:
    for d in definiciones:
        if pedido in (d.get("title"), d.get("name"), d["key"]):
            return d
    nombres = [_nombre_prompt(d) for d in definiciones]
    raise ValueError(f"El reporte no tiene un prompt {pedido!r}. Prompts disponibles: {nombres or 'ninguno'}")


def _armar_respuestas(report: Report, prompts: dict) -> list[Prompt]:
    definiciones = _definir_prompts(report)
    respuestas = []
    for pedido, valor in prompts.items():
        d = _buscar_prompt(definiciones, pedido)
        if d.get("type") == "VALUE" and isinstance(valor, (list, tuple, set, dict)):
            raise ValueError(
                f"El prompt {pedido!r} es de tipo VALUE y recibe un solo valor, no {type(valor).__name__}. "
                "Para varios valores, ejecutá el reporte una vez por cada uno."
            )
        # Se envía tal cual a la API: para tipos distintos de VALUE hay que pasar la estructura que
        # espera MicroStrategy (ver la receta de prompts en la documentación).
        respuestas.append(Prompt(key=d["key"], type=d["type"], answers=valor))
    return respuestas


def report_to_df(
    conn: Connection,
    report_id: str,
    prompts: dict | None = None,
    filters: dict | None = None,
    exclude: dict | None = None,
    strict: bool = True,
    **kwargs,
) -> pd.DataFrame:
    """Ejecuta un reporte y lo devuelve como DataFrame, con prompts y filtros opcionales.

    Hay dos formas de filtrar y no se mezclan:

    - `prompts` filtra **en MicroStrategy**, antes de descargar. Son las respuestas a los prompts
      del reporte, `{nombre del prompt: valor}`. Es el filtro dinámico del reporte y el más
      eficiente. Para ver cuáles tiene un reporte, usá `report_prompts`. Un prompt `VALUE` recibe
      un solo valor; para otros tipos (ELEMENTS, OBJECTS...) se pasa la estructura que espera la
      API, sin traducir.
    - `filters` y `exclude` filtran **en pandas, sobre el reporte ya descargado**. Son
      `{columna: valor o lista}` con el nombre de la columna del DataFrame: `filters` deja solo
      esos valores y `exclude` los saca. Se pueden usar juntos y validan los nombres. Con
      `strict=True` (por defecto) un valor o columna inexistente da error con sugerencias; con
      `strict=False` los valores inexistentes se ignoran.

    El resto de los parámetros (`limit`, `prompt_answers` ya armados con `Prompt`, etc.) van a
    `Report.to_dataframe`. Crea un `Report` nuevo en cada llamada, porque el objeto del SDK
    conserva estado entre ejecuciones.
    """
    report = Report(conn, id=report_id)
    respuestas = list(kwargs.pop("prompt_answers", None) or [])
    if prompts:
        respuestas += _armar_respuestas(report, prompts)

    try:
        df = report.to_dataframe(prompt_answers=respuestas or None, **kwargs)
    except IServerError as e:
        if "required to be answered" not in str(e):
            raise
        raise ValueError(
            f"El reporte tiene prompts sin responder. Respondelos con `prompts=`. "
            f"Prompts del reporte: {[_nombre_prompt(d) for d in _definir_prompts(report)]}"
        ) from e

    if filters or exclude:
        df = filter_values(df, include=filters, exclude=exclude, strict=strict)
    return df


SUPERCUBE_POLICIES = ("replace", "add", "update", "upsert")


def create_supercube(
    conn: Connection,
    name: str,
    table_name: str,
    df: pd.DataFrame,
    folder_id: str | None = None,
    to_metric: list[str] | None = None,
    to_attribute: list[str] | None = None,
) -> SuperCube:
    """Crea un super cube nuevo con el DataFrame y lo publica.

    Carpeta destino: `folder_id` si se pasa; si no, MSTR_FOLDER_ID del entorno; si tampoco
    está, "My Reports" del usuario. Guardá `cube.id` para actualizarlo después con
    `df_to_supercube`.
    """
    folder_id = folder_id or get_env("MSTR_FOLDER_ID", required=False) or None
    cube = SuperCube(conn, name=name)
    cube.add_table(
        name=table_name,
        data_frame=df,
        update_policy="add",
        to_metric=to_metric,
        to_attribute=to_attribute,
    )
    cube.create(folder_id=folder_id)
    return cube


def df_to_supercube(
    conn: Connection,
    cube_id: str,
    table_name: str,
    df: pd.DataFrame,
    policy: str = "replace",
    to_metric: list[str] | None = None,
    to_attribute: list[str] | None = None,
) -> SuperCube:
    """Sube un DataFrame a un super cube existente y lo publica.

    policy: "replace" (reemplaza todo), "add" (inserta filas nuevas únicas),
            "update" (actualiza filas existentes) o "upsert" (actualiza e inserta).
    `table_name` es el nombre lógico de la tabla dentro del cubo.
    """
    if policy not in SUPERCUBE_POLICIES:
        raise ValueError(f"policy inválida: {policy!r} (usar una de {SUPERCUBE_POLICIES})")
    cube = SuperCube(conn, id=cube_id)
    cube.add_table(
        name=table_name,
        data_frame=df,
        update_policy=policy,
        to_metric=to_metric,
        to_attribute=to_attribute,
    )
    cube.update()
    return cube


@contextmanager
def mstr_session(**kwargs):
    """Context manager que cierra la sesión al salir.

    with mstr_session() as conn:
        df = Report(conn, id="...").to_dataframe()
    """
    conn = get_mstr_connection(**kwargs)
    try:
        yield conn
    finally:
        conn.close()
