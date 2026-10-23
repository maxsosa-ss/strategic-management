"""Tests de filter_values (sin red)."""

import pandas as pd
import pytest

from smpy.transforms.filters import filter_values


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "Zona": ["AMBA", "AMBA", "CUYO", "NEA", "F/D"],
            "Periodo": [202609, 202609, 202610, 202610, 202610],
            "Valor": [1, 2, 3, 4, 5],
        }
    )


def test_include_con_lista_y_con_valor_suelto(df):
    assert filter_values(df, include={"Zona": ["AMBA", "CUYO"]})["Valor"].tolist() == [1, 2, 3]
    assert filter_values(df, include={"Zona": "NEA"})["Valor"].tolist() == [4]


def test_exclude(df):
    assert filter_values(df, exclude={"Zona": ["F/D", "NEA"]})["Valor"].tolist() == [1, 2, 3]


def test_include_y_exclude_juntos_y_columnas_distintas_con_y(df):
    out = filter_values(df, include={"Periodo": 202610}, exclude={"Zona": "F/D"})
    assert out["Valor"].tolist() == [3, 4]


def test_cada_filtro_se_valida_contra_los_datos_originales_no_los_ya_filtrados(df):
    # Tras incluir solo el período 202609 ya no queda "F/D" (está en 202610), pero sigue siendo un
    # valor válido de la columna: no debe dar error.
    out = filter_values(df, include={"Periodo": 202609}, exclude={"Zona": "F/D"})
    assert out["Valor"].tolist() == [1, 2]
    # y el orden de los diccionarios no cambia el resultado
    out2 = filter_values(df, exclude={"Zona": "F/D"}, include={"Periodo": 202609})
    assert out2.equals(out)


def test_compara_como_texto_sin_cambiar_los_tipos(df):
    out = filter_values(df, include={"Periodo": ["202609"]})
    assert len(out) == 2 and out["Periodo"].dtype == df["Periodo"].dtype


def test_no_modifica_el_original(df):
    filter_values(df, include={"Zona": "AMBA"})
    assert len(df) == 5


def test_valor_inexistente_da_error_con_sugerencia_y_valores_disponibles(df):
    with pytest.raises(ValueError) as e:
        filter_values(df, include={"Zona": ["AMBBA"]})
    msg = str(e.value)
    assert "'AMBBA'" in msg and "¿Quisiste decir 'AMBA'?" in msg and "CUYO" in msg


def test_strict_false_ignora_los_inexistentes(df):
    assert filter_values(df, include={"Zona": ["AMBA", "Atlantis"]}, strict=False)["Valor"].tolist() == [1, 2]
    assert filter_values(df, exclude={"Zona": ["Atlantis"]}, strict=False).shape == df.shape


def test_columna_inexistente_falla_siempre_con_sugerencia(df):
    for strict in (True, False):
        with pytest.raises(ValueError, match="¿Quisiste decir 'Zona'"):
            filter_values(df, include={"Zon": "AMBA"}, strict=strict)


def test_sugiere_por_texto_contenido_cuando_no_hay_parecido():
    d = pd.DataFrame({"Zona Direccion Comercial": ["AMBA"]})
    with pytest.raises(ValueError, match="¿Quisiste decir 'Zona Direccion Comercial'"):
        filter_values(d, include={"Zona": "AMBA"})


def test_lista_vacia_es_un_error(df):
    with pytest.raises(ValueError, match="vacía"):
        filter_values(df, include={"Zona": []})


def test_sin_filtros_devuelve_una_copia(df):
    out = filter_values(df)
    assert out.equals(df) and out is not df
