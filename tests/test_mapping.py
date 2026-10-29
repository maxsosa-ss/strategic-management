"""Tests de las funciones de mapeo de rubros y subrubros (sin red)."""

import warnings

import pandas as pd
import pytest

from smpy.transforms.mapping import amb_rubros_subrubros, disc_rubros_subrubros, int_rubros_subrubros


@pytest.fixture
def aux_rubros():
    return pd.DataFrame(
        {
            "Rubro GE": ["Cirugia", "Consulta", "F/D", "Resto"],
            "Rubro PPTO": ["Cirugia", "Consulta", "Resto", "Resto"],
            "Subrubro PPTO NAN": ["Cir. Otras", "Con. Programada", "Resto", "Resto"],
        }
    )


@pytest.fixture
def aux_amb_subrubros():
    return pd.DataFrame(
        {
            "Rubro GE": ["Cirugia", "Cirugia", "Consulta"],
            "Subrubro GE": ["Cir. Cardiovasculares", "Cir. Urinario", "Guardia"],
            "Rubro&Subrubro GE": ["CirugiaCir. Cardiovasculares", "CirugiaCir. Urinario", "ConsultaGuardia"],
            "Subrubro PPTO": ["Cir. Cardiovascular", "Cir. Otras", "Con. Guardia"],
        }
    )


@pytest.fixture
def aux_int_subrubros():
    return pd.DataFrame(
        {
            "Prestacion ID": ["NM1", "NM2"],
            "Prestacion DESC": ["a", "b"],
            "Subrubro PPTO": ["3- Media B", "6- Alta A"],
        }
    )


@pytest.fixture
def aux_disc():
    return pd.DataFrame(
        {
            "Prestacion ID": ["DI1", "DI2"],
            "Prestacion DESC": ["a", "b"],
            "Rubro PPTO": ["Educativo", "Asistencial"],
            "Subrubro PPTO": ["Acompañante", ""],
        }
    )


def test_amb_mapea_rubro_y_subrubro(aux_rubros, aux_amb_subrubros):
    df = pd.DataFrame(
        {"Rubro GE": ["Cirugia", "Consulta"], "Subrubro GE": ["Cir. Cardiovasculares", "Guardia"], "v": [1, 2]}
    )
    out = amb_rubros_subrubros(df, aux_rubros, aux_amb_subrubros)
    assert out["Rubro PPTO"].tolist() == ["Cirugia", "Consulta"]
    assert out["Subrubro PPTO"].tolist() == ["Cir. Cardiovascular", "Con. Guardia"]
    assert out["v"].tolist() == [1, 2]


def test_amb_subrubro_faltante_o_no_encontrado_usa_el_del_rubro(aux_rubros, aux_amb_subrubros):
    df = pd.DataFrame(
        {"Rubro GE": ["Cirugia", "Consulta", "F/D"], "Subrubro GE": ["", "No existe", None]}
    )
    out = amb_rubros_subrubros(df, aux_rubros, aux_amb_subrubros)
    assert out["Rubro PPTO"].tolist() == ["Cirugia", "Consulta", "Resto"]
    assert out["Subrubro PPTO"].tolist() == ["Cir. Otras", "Con. Programada", "Resto"]


def test_amb_no_modifica_el_original_y_acepta_otros_nombres_de_columna(aux_rubros, aux_amb_subrubros):
    df = pd.DataFrame({"rubro": ["Cirugia"], "sub": ["Cir. Urinario"]})
    out = amb_rubros_subrubros(df, aux_rubros, aux_amb_subrubros, col_rubro="rubro", col_subrubro="sub")
    assert out["Subrubro PPTO"].tolist() == ["Cir. Otras"]
    assert list(df.columns) == ["rubro", "sub"]


def test_amb_usa_la_pareja_y_no_el_texto_concatenado(aux_rubros):
    # "A"+"BC" y "AB"+"C" darían la misma clave concatenada, pero son parejas distintas.
    aux_sub = pd.DataFrame(
        {"Rubro GE": ["A", "AB"], "Subrubro GE": ["BC", "C"], "Subrubro PPTO": ["x", "y"]}
    )
    aux_r = pd.DataFrame({"Rubro GE": ["A", "AB"], "Rubro PPTO": ["A", "AB"], "Subrubro PPTO NAN": ["", ""]})
    df = pd.DataFrame({"Rubro GE": ["A", "AB"], "Subrubro GE": ["BC", "C"]})
    assert amb_rubros_subrubros(df, aux_r, aux_sub)["Subrubro PPTO"].tolist() == ["x", "y"]


def test_amb_rubro_sin_mapeo_avisa_y_deja_vacio(aux_rubros, aux_amb_subrubros):
    df = pd.DataFrame({"Rubro GE": ["Cirugia", "Inventado", ""], "Subrubro GE": ["", "", ""]})
    with pytest.warns(UserWarning, match="Inventado"):
        out = amb_rubros_subrubros(df, aux_rubros, aux_amb_subrubros)
    assert pd.isna(out.loc[1, "Rubro PPTO"]) and pd.isna(out.loc[1, "Subrubro PPTO"])


def test_amb_sin_avisos_si_todo_mapea_o_viene_vacio(aux_rubros, aux_amb_subrubros):
    df = pd.DataFrame({"Rubro GE": ["Cirugia", None], "Subrubro GE": ["", ""]})
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        amb_rubros_subrubros(df, aux_rubros, aux_amb_subrubros)


def test_columna_inexistente_en_df(aux_rubros, aux_amb_subrubros):
    with pytest.raises(ValueError, match="faltan las columnas \\['Subrubro GE'\\]"):
        amb_rubros_subrubros(pd.DataFrame({"Rubro GE": ["Cirugia"]}), aux_rubros, aux_amb_subrubros)


def test_columna_inexistente_en_tabla_auxiliar(aux_rubros, aux_amb_subrubros):
    df = pd.DataFrame({"Rubro GE": ["Cirugia"], "Subrubro GE": [""]})
    with pytest.raises(ValueError, match="aux_subrubros"):
        amb_rubros_subrubros(df, aux_rubros, aux_amb_subrubros.drop(columns="Subrubro PPTO"))


def test_clave_repetida_con_valores_distintos_falla_pero_con_el_mismo_valor_no(aux_rubros, aux_amb_subrubros):
    df = pd.DataFrame({"Rubro GE": ["Cirugia"], "Subrubro GE": ["Cir. Urinario"]})
    repetida = pd.concat([aux_amb_subrubros, aux_amb_subrubros.iloc[[1]].assign(**{"Subrubro PPTO": "Otro"})])
    with pytest.raises(ValueError, match="valores distintos"):
        amb_rubros_subrubros(df, aux_rubros, repetida)
    igual = pd.concat([aux_amb_subrubros, aux_amb_subrubros.iloc[[1]]])
    assert amb_rubros_subrubros(df, aux_rubros, igual)["Subrubro PPTO"].tolist() == ["Cir. Otras"]


def test_int_subrubro_por_prestacion_y_por_defecto(aux_rubros, aux_int_subrubros):
    df = pd.DataFrame({"Rubro GE": ["Cirugia", "Cirugia", "Consulta"], "Prestacion ID": ["NM1", "NM9", "NM2"]})
    out = int_rubros_subrubros(df, aux_rubros, aux_int_subrubros)
    assert out["Rubro PPTO"].tolist() == ["Cirugia", "Cirugia", "Consulta"]
    assert out["Subrubro PPTO"].tolist() == ["3- Media B", "Cir. Otras", "6- Alta A"]


def test_int_compara_ids_como_texto(aux_rubros):
    aux_sub = pd.DataFrame({"Prestacion ID": [1393], "Subrubro PPTO": ["x"]})
    df = pd.DataFrame({"Rubro GE": ["Cirugia"], "Prestacion ID": ["1393"]})
    assert int_rubros_subrubros(df, aux_rubros, aux_sub)["Subrubro PPTO"].tolist() == ["x"]


def test_disc_mapea_ambos_y_deja_vacio_sin_mapeo(aux_disc):
    df = pd.DataFrame({"Prestacion ID": ["DI1", "DI2", "DI9"]})
    with pytest.warns(UserWarning, match="DI9"):
        out = disc_rubros_subrubros(df, aux_disc)
    assert out["Rubro PPTO"].tolist()[:2] == ["Educativo", "Asistencial"]
    assert out["Subrubro PPTO"].tolist()[0] == "Acompañante"
    assert out["Subrubro PPTO"].isna().tolist() == [False, True, True]  # "" del sheet cuenta como vacío


def test_disc_nombre_de_columna_por_parametro(aux_disc):
    out = disc_rubros_subrubros(pd.DataFrame({"id": ["DI1"]}), aux_disc, col_prestacion="id")
    assert out["Rubro PPTO"].tolist() == ["Educativo"]
