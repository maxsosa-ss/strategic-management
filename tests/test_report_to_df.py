"""Tests de report_prompts y report_to_df con un Report simulado (sin red)."""

import pandas as pd
import pytest
from mstrio.helpers import IServerError

from smpy.connectors import mstr

KEY = "ABC@0@10"
PROMPT = {"id": "ABC", "name": "Valor de Periodo", "title": "Valor de Periodo", "type": "VALUE",
          "dataType": "NUMERIC", "required": False, "key": KEY}


class FakePrompt:
    def __init__(self, d):
        self.d = d

    def to_dict(self):
        return dict(self.d)


class FakeReport:
    """Imita lo mínimo de mstrio.Report. `ultimo` guarda la instancia usada en la última llamada."""

    prompts_def = [PROMPT]
    attributes_def = [{"name": "Zona", "id": "Z1"}, {"name": "Periodo", "id": "P1"}]
    datos = pd.DataFrame({"Zona": ["AMBA", "CUYO", "NEA"], "Periodo": [202609, 202609, 202609], "Valor": [1, 2, 3]})
    ultimo = None
    exigir_prompts = False

    def __init__(self, conn, id):
        FakeReport.ultimo = self
        self.id = id
        self.prompts = [FakePrompt(d) for d in self.prompts_def]
        self.attributes = self.attributes_def
        self.filtros = None
        self.respuestas = "no se llamó"

    def apply_filters(self, attr_elements, operator):
        self.filtros = (attr_elements, operator)

    def to_dataframe(self, prompt_answers=None, **kw):
        self.respuestas, self.kw = prompt_answers, kw
        if self.exigir_prompts and not prompt_answers:
            raise IServerError("This report has prompts that are required to be answered.", 400)
        return self.datos.copy()


@pytest.fixture(autouse=True)
def report_falso(monkeypatch):
    monkeypatch.setattr(mstr, "Report", FakeReport)
    FakeReport.prompts_def, FakeReport.exigir_prompts, FakeReport.ultimo = [PROMPT], False, None


def test_report_prompts_lista_los_prompts():
    out = mstr.report_prompts("conn", "R1")
    assert out.to_dict("records") == [
        {"nombre": "Valor de Periodo", "tipo": "VALUE", "tipo_de_dato": "NUMERIC", "obligatorio": False, "clave": KEY}
    ]


def test_report_prompts_sin_prompts_devuelve_tabla_vacia_con_columnas():
    FakeReport.prompts_def = []
    out = mstr.report_prompts("conn", "R1")
    assert out.empty and list(out.columns) == ["nombre", "tipo", "tipo_de_dato", "obligatorio", "clave"]


def test_prompts_se_responden_por_nombre_con_clave_y_tipo():
    mstr.report_to_df("conn", "R1", prompts={"Valor de Periodo": 202609})
    (resp,) = FakeReport.ultimo.respuestas
    assert resp.to_dict()["key"] == KEY and resp.to_dict()["type"] == "VALUE" and resp.to_dict()["answers"] == 202609


def test_prompt_inexistente_lista_los_disponibles():
    with pytest.raises(ValueError, match="Valor de Periodo"):
        mstr.report_to_df("conn", "R1", prompts={"Periodo": 1})


def test_prompt_value_con_lista_es_un_error_claro():
    with pytest.raises(ValueError, match="un solo valor"):
        mstr.report_to_df("conn", "R1", prompts={"Valor de Periodo": [202609, 202610]})


def test_prompts_sin_responder_da_error_claro_con_los_prompts_del_reporte():
    FakeReport.exigir_prompts = True
    with pytest.raises(ValueError, match="sin responder.*Valor de Periodo"):
        mstr.report_to_df("conn", "R1")


def test_otros_errores_del_servidor_no_se_tapan():
    class Otro(FakeReport):
        def to_dataframe(self, **kw):
            raise IServerError("Numerical values required.", 400)

    mstr.Report = Otro
    with pytest.raises(IServerError, match="Numerical"):
        mstr.report_to_df("conn", "R1", prompts={"Valor de Periodo": "abc"})


def test_prompt_answers_ya_armados_se_suman_a_los_de_prompts():
    propio = mstr.Prompt(key="OTRO@0@10", type="VALUE", answers=1)
    mstr.report_to_df("conn", "R1", prompts={"Valor de Periodo": 202609}, prompt_answers=[propio])
    assert len(FakeReport.ultimo.respuestas) == 2


def test_filters_y_exclude_filtran_en_pandas_y_nunca_tocan_el_servidor():
    out = mstr.report_to_df("conn", "R1", filters={"Zona": ["AMBA", "CUYO"]}, exclude={"Zona": "CUYO"})
    assert out["Zona"].tolist() == ["AMBA"] and FakeReport.ultimo.filtros is None


def test_filtro_con_valor_inexistente_valida_y_strict_false_lo_ignora():
    with pytest.raises(ValueError, match="no existe"):
        mstr.report_to_df("conn", "R1", filters={"Zona": ["AMBBA"]})
    assert len(mstr.report_to_df("conn", "R1", filters={"Zona": ["AMBA", "X"]}, strict=False)) == 1


def test_funciona_con_filtros_y_prompts_a_la_vez():
    out = mstr.report_to_df("conn", "R1", prompts={"Valor de Periodo": 202609}, filters={"Zona": "NEA"})
    assert out["Valor"].tolist() == [3]


def test_kwargs_extra_van_a_to_dataframe():
    mstr.report_to_df("conn", "R1", limit=500)
    assert FakeReport.ultimo.kw == {"limit": 500}
