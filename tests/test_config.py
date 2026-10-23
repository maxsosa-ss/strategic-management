"""El .env que se lee es el del proyecto que usa la librería, no el de la librería."""

import subprocess
import sys

SCRIPT = "from smpy.config import get_env\nprint(get_env('SM_TEST_VAR', required=False))\n"


def _correr(carpeta, env_extra=None):
    import os

    env = {k: v for k, v in os.environ.items() if k != "SM_TEST_VAR"}
    env.update(env_extra or {})
    # Se ejecuta un archivo .py (no `-c`), porque python-dotenv se comporta distinto en modo interactivo.
    (carpeta / "mi_script.py").write_text(SCRIPT, encoding="utf-8")
    out = subprocess.run([sys.executable, "mi_script.py"], cwd=carpeta, env=env, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return out.stdout.strip()


def test_lee_el_env_del_proyecto(tmp_path):
    (tmp_path / ".env").write_text("SM_TEST_VAR=del_proyecto\n", encoding="utf-8")
    assert _correr(tmp_path) == "del_proyecto"


def test_busca_el_env_en_carpetas_superiores(tmp_path):
    (tmp_path / ".env").write_text("SM_TEST_VAR=del_proyecto\n", encoding="utf-8")
    sub = tmp_path / "scripts" / "diarios"
    sub.mkdir(parents=True)
    assert _correr(sub) == "del_proyecto"


def test_una_variable_de_entorno_real_tiene_prioridad(tmp_path):
    (tmp_path / ".env").write_text("SM_TEST_VAR=del_env\n", encoding="utf-8")
    assert _correr(tmp_path, {"SM_TEST_VAR": "del_sistema"}) == "del_sistema"


def test_sin_env_no_usa_el_de_la_libreria(tmp_path):
    assert _correr(tmp_path) == "None"
