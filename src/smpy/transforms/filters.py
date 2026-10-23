"""Filtrado de DataFrames por valores de columnas, con validación."""

from difflib import get_close_matches

import pandas as pd

_MAX_VALORES_EN_ERROR = 15


def _lista(valores) -> list:
    """Acepta un valor suelto o una colección y devuelve siempre una lista."""
    if isinstance(valores, (list, tuple, set, frozenset, pd.Series)):
        return list(valores)
    return [valores]


def _sugerencia(texto: str, opciones: list[str]) -> str:
    # Primero por parecido (errores de tipeo) y, si no hay, por texto contenido ("Zona" en "Zona Direccion").
    candidatas = get_close_matches(texto, opciones, n=1) or [o for o in opciones if texto.lower() in o.lower()][:1]
    return f" ¿Quisiste decir {candidatas[0]!r}?" if candidatas else ""


def _validar_columna(df: pd.DataFrame, columna: str) -> None:
    if columna not in df.columns:
        columnas = [str(c) for c in df.columns]
        raise ValueError(
            f"La columna {columna!r} no existe.{_sugerencia(str(columna), columnas)} "
            f"Columnas disponibles: {columnas}"
        )


def _condicion(df: pd.DataFrame, columna: str, valores, incluir: bool, strict: bool) -> pd.Series:
    """Máscara de las filas que cumplen una condición, validada contra el DataFrame original."""
    _validar_columna(df, columna)
    pedidos = [str(v) for v in _lista(valores)]
    if not pedidos:
        raise ValueError(f"La lista de valores para {columna!r} está vacía.")

    # Se compara como texto para que 202609 y "202609" coincidan, sin tocar los tipos del DataFrame.
    en_columna = df[columna].astype(str)
    disponibles = sorted(en_columna.unique())
    faltan = [v for v in pedidos if v not in set(disponibles)]
    if faltan and strict:
        detalle = "; ".join(f"{v!r}.{_sugerencia(v, disponibles)}".rstrip() for v in faltan)
        muestra = disponibles[:_MAX_VALORES_EN_ERROR]
        resto = f" (y {len(disponibles) - len(muestra)} más)" if len(disponibles) > len(muestra) else ""
        raise ValueError(
            f"En la columna {columna!r} no existe: {detalle} "
            f"Valores disponibles: {muestra}{resto}. Pasá strict=False para ignorarlos."
        )

    coincide = en_columna.isin(pedidos)
    return coincide if incluir else ~coincide


def filter_values(
    df: pd.DataFrame,
    include: dict | None = None,
    exclude: dict | None = None,
    strict: bool = True,
) -> pd.DataFrame:
    """Filtra un DataFrame por los valores de sus columnas y devuelve una copia.

    `include` deja solo las filas cuyo valor está en la lista; `exclude` saca las filas cuyo
    valor está en la lista. Ambos son diccionarios `{columna: valor o lista de valores}`; las
    condiciones se combinan con "y" y cada una se valida contra el DataFrame original, no contra
    el ya filtrado. Los valores se comparan como texto, así `202609` y `"202609"` coinciden.

    Con `strict=True` (por defecto) falla con un mensaje claro, con sugerencias, si una columna
    o un valor no existe: un error de tipeo no devuelve un DataFrame vacío en silencio. Con
    `strict=False` los valores inexistentes se ignoran. Una columna inexistente falla siempre.
    """
    # Cada condición se valida contra el DataFrame original (no contra el ya filtrado) y después
    # se combinan: así un valor válido no falla porque otro filtro dejó la columna sin ese valor.
    mascara = pd.Series(True, index=df.index)
    for columna, valores in (include or {}).items():
        mascara &= _condicion(df, columna, valores, incluir=True, strict=strict)
    for columna, valores in (exclude or {}).items():
        mascara &= _condicion(df, columna, valores, incluir=False, strict=strict)
    return df[mascara].copy()
