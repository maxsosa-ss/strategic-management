"""Mapeo de rubros y subrubros del presupuesto (PPTO) a partir de tablas auxiliares ya cargadas.

Las funciones no leen nada: reciben las tablas auxiliares como DataFrames (por ejemplo con
`smpy.connectors.google.sheet_to_df`) y devuelven una copia del DataFrame con las columnas
`Rubro PPTO` y `Subrubro PPTO`. Los nombres de las columnas del DataFrame de entrada se pasan por
parámetro; los de las tablas auxiliares son los del sheet de mapeos.
"""

import warnings
from collections import Counter

import pandas as pd

_MAX_VALORES_EN_MENSAJE = 15

# Columnas de las tablas auxiliares (las define el sheet de mapeos).
_RUBRO_GE = "Rubro GE"
_SUBRUBRO_GE = "Subrubro GE"
_RUBRO_PPTO = "Rubro PPTO"
_SUBRUBRO_PPTO = "Subrubro PPTO"
_SUBRUBRO_PPTO_NAN = "Subrubro PPTO NAN"
_PRESTACION_ID = "Prestacion ID"


def _texto(serie: pd.Series) -> pd.Series:
    """Pasa a texto conservando los nulos, así `1393` y `"1393"` coinciden como clave."""
    return serie.astype("string")


def _muestra(valores: list) -> str:
    recorte = valores[:_MAX_VALORES_EN_MENSAJE]
    resto = f" (y {len(valores) - len(recorte)} más)" if len(valores) > len(recorte) else ""
    return f"{recorte}{resto}"


def _validar_columnas(df: pd.DataFrame, columnas: list[str], nombre: str) -> None:
    faltan = [c for c in columnas if c not in df.columns]
    if faltan:
        raise ValueError(f"En {nombre} faltan las columnas {faltan}. Columnas disponibles: {list(df.columns)}")


def _diccionario(tabla: pd.DataFrame, col_claves: list[str], col_valor: str, nombre: str) -> dict:
    """Arma `{clave: valor}` desde una tabla auxiliar. La clave es una tupla de textos.

    Falla si una misma clave tiene valores distintos (el mapeo sería ambiguo). Las celdas vacías
    del valor cuentan como faltantes (`None`) para que se pueda aplicar el subrubro por defecto.
    """
    _validar_columnas(tabla, [*col_claves, col_valor], nombre)
    claves = list(zip(*(_texto(tabla[c]) for c in col_claves)))
    valores = [None if pd.isna(v) or v == "" else v for v in tabla[col_valor]]

    por_clave: dict[tuple, set] = {}
    for clave, valor in zip(claves, valores):
        por_clave.setdefault(clave, set()).add(valor)
    ambiguas = [" / ".join(map(str, k)) for k, vs in por_clave.items() if len(vs) > 1]
    if ambiguas:
        raise ValueError(
            f"En {nombre} la clave {col_claves} tiene valores distintos en {col_valor!r} para: "
            f"{_muestra(ambiguas)}. Revisá las filas repetidas."
        )
    return dict(zip(claves, valores))


def _buscar(claves: list[pd.Series], diccionario: dict) -> pd.Series:
    """Busca cada fila en el diccionario; lo que no está queda como nulo."""
    textos = zip(*(_texto(c) for c in claves))
    return pd.Series([diccionario.get(k) for k in textos], index=claves[0].index, dtype=object)


def _avisar_sin_mapeo(claves: pd.DataFrame, resultado: pd.Series, que: str) -> None:
    """Avisa de los valores no vacíos que no se pudieron mapear (los vacíos son esperables)."""
    sin_mapeo = claves[resultado.isna()]
    con_valor = sin_mapeo[sin_mapeo.notna().all(axis=1) & (sin_mapeo.astype(str) != "").all(axis=1)]
    valores = sorted({" / ".join(map(str, fila)) for fila in con_valor.itertuples(index=False)})
    if valores:
        warnings.warn(f"{que} sin mapeo ({len(valores)}): {_muestra(valores)}", stacklevel=3)


def _rubro_ppto(df: pd.DataFrame, col_rubro: str, aux_rubros: pd.DataFrame) -> pd.Series:
    dic = _diccionario(aux_rubros, [_RUBRO_GE], _RUBRO_PPTO, "aux_rubros")
    rubro = _buscar([df[col_rubro]], dic)
    _avisar_sin_mapeo(df[[col_rubro]], rubro, f"Valores de {col_rubro!r}")
    return rubro


def _con_subrubro_por_defecto(subrubro: pd.Series, rubro: pd.Series, aux_rubros: pd.DataFrame) -> pd.Series:
    """Donde no hay subrubro usa el `Subrubro PPTO NAN` de su rubro, tanto si falta como si no se encontró."""
    dic = _diccionario(aux_rubros, [_RUBRO_PPTO], _SUBRUBRO_PPTO_NAN, "aux_rubros")
    por_defecto = _buscar([rubro], dic)
    return subrubro.where(subrubro.notna(), por_defecto)


def amb_rubros_subrubros(
    df: pd.DataFrame,
    aux_rubros: pd.DataFrame,
    aux_subrubros: pd.DataFrame,
    col_rubro: str = "Rubro GE",
    col_subrubro: str = "Subrubro GE",
) -> pd.DataFrame:
    """Agrega `Rubro PPTO` y `Subrubro PPTO` a datos de Ambulatorio y devuelve una copia.

    `aux_rubros` (pestaña `amb_rubro`) tiene `Rubro GE`, `Rubro PPTO` y `Subrubro PPTO NAN`.
    `aux_subrubros` (pestaña `amb_subrubro`) tiene `Rubro GE`, `Subrubro GE` y `Subrubro PPTO`;
    el subrubro se busca por la pareja rubro + subrubro, sin concatenar textos. `col_rubro` y
    `col_subrubro` son las columnas de `df` a mapear.

    Si el subrubro no tiene mapeo (falta o no se encontró) se usa el `Subrubro PPTO NAN` de su
    rubro. Un rubro sin mapeo deja ambas columnas vacías y se informa con un aviso.
    """
    _validar_columnas(df, [col_rubro, col_subrubro], "df")
    rubro = _rubro_ppto(df, col_rubro, aux_rubros)
    dic = _diccionario(aux_subrubros, [_RUBRO_GE, _SUBRUBRO_GE], _SUBRUBRO_PPTO, "aux_subrubros")
    subrubro = _buscar([df[col_rubro], df[col_subrubro]], dic)

    out = df.copy()
    out[_RUBRO_PPTO] = rubro
    out[_SUBRUBRO_PPTO] = _con_subrubro_por_defecto(subrubro, rubro, aux_rubros)
    return out


def int_rubros_subrubros(
    df: pd.DataFrame,
    aux_rubros: pd.DataFrame,
    aux_subrubros: pd.DataFrame,
    col_rubro: str = "Rubro GE",
    col_prestacion: str = "Prestacion ID",
) -> pd.DataFrame:
    """Agrega `Rubro PPTO` y `Subrubro PPTO` a datos de Internaciones y devuelve una copia.

    `aux_rubros` (pestaña `int_rubro`) tiene `Rubro GE`, `Rubro PPTO` y `Subrubro PPTO NAN`.
    `aux_subrubros` (pestaña `int_subrubro`) tiene `Prestacion ID` y `Subrubro PPTO`: en
    Internaciones el subrubro depende de la prestación, no del subrubro de origen. `col_rubro` y
    `col_prestacion` son las columnas de `df` a mapear.

    Si la prestación no tiene subrubro (falta o no se encontró) se usa el `Subrubro PPTO NAN` de
    su rubro. Un rubro sin mapeo deja ambas columnas vacías y se informa con un aviso.
    """
    _validar_columnas(df, [col_rubro, col_prestacion], "df")
    rubro = _rubro_ppto(df, col_rubro, aux_rubros)
    dic = _diccionario(aux_subrubros, [_PRESTACION_ID], _SUBRUBRO_PPTO, "aux_subrubros")
    subrubro = _buscar([df[col_prestacion]], dic)

    out = df.copy()
    out[_RUBRO_PPTO] = rubro
    out[_SUBRUBRO_PPTO] = _con_subrubro_por_defecto(subrubro, rubro, aux_rubros)
    return out


def disc_rubros_subrubros(
    df: pd.DataFrame,
    aux_discapacidad: pd.DataFrame,
    col_prestacion: str = "Prestacion ID",
) -> pd.DataFrame:
    """Agrega `Rubro PPTO` y `Subrubro PPTO` a datos de Discapacidad y devuelve una copia.

    `aux_discapacidad` (pestaña `discapacidad`) tiene `Prestacion ID`, `Rubro PPTO` y
    `Subrubro PPTO`: ambos salen de la prestación, `col_prestacion` en `df`. Discapacidad no tiene
    subrubro por defecto: una prestación sin mapeo deja ambas columnas vacías y se informa con un aviso.
    """
    _validar_columnas(df, [col_prestacion], "df")
    rubros = _diccionario(aux_discapacidad, [_PRESTACION_ID], _RUBRO_PPTO, "aux_discapacidad")
    subrubros = _diccionario(aux_discapacidad, [_PRESTACION_ID], _SUBRUBRO_PPTO, "aux_discapacidad")
    rubro = _buscar([df[col_prestacion]], rubros)
    _avisar_sin_mapeo(df[[col_prestacion]], rubro, f"Valores de {col_prestacion!r}")

    out = df.copy()
    out[_RUBRO_PPTO] = rubro
    out[_SUBRUBRO_PPTO] = _buscar([df[col_prestacion]], subrubros)
    return out
