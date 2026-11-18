import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.verificar_mutacion import calcular_score, leer_umbral, main

RAIZ = Path(__file__).resolve().parent.parent


def stats(killed, total):
    return {"killed": killed, "total": total, "survived": total - killed, "no_tests": 0}


def escribir(carpeta, datos):
    ruta = carpeta / "mutants" / "mutmut-cicd-stats.json"
    ruta.parent.mkdir()
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


def correr_script(carpeta, *args):
    return subprocess.run(
        [sys.executable, "-m", "scripts.verificar_mutacion", *args],
        cwd=carpeta, env={"PYTHONPATH": str(RAIZ)}, capture_output=True, text=True,
    )


def test_calcula_el_porcentaje_de_muertos():
    assert calcular_score(stats(63, 117)) == 53.8
    assert calcular_score(stats(117, 117)) == 100.0


def test_sin_mutantes_es_un_error():
    with pytest.raises(ValueError):
        calcular_score(stats(0, 0))


def test_pasa_cuando_cumple_el_umbral(tmp_path):
    assert main(50, escribir(tmp_path, stats(50, 100))) == 0


def test_falla_cuando_queda_por_debajo_del_umbral(tmp_path, capsys):
    assert main(50, escribir(tmp_path, stats(49, 100))) == 1
    assert "por debajo del minimo de 50" in capsys.readouterr().out


def test_umbral_por_defecto_y_validado():
    assert leer_umbral([]) == 50.0
    assert leer_umbral(["60"]) == 60.0
    with pytest.raises(ValueError):
        leer_umbral(["150"])


def test_regresion_path_traversal_no_acepta_rutas(tmp_path):
    # Issue High de SonarCloud: la ruta llegaba por linea de comandos sin validar,
    # asi que el script leia cualquier archivo que le pasaran.
    otro = tmp_path / "otro_archivo.json"
    otro.write_text(json.dumps(stats(100, 100)), encoding="utf-8")
    resultado = correr_script(tmp_path, str(otro))
    assert resultado.returncode != 0
    assert "Mutation score" not in resultado.stdout


def test_script_desde_linea_de_comandos(tmp_path):
    escribir(tmp_path, stats(40, 100))
    assert correr_script(tmp_path, "50").returncode == 1
    assert correr_script(tmp_path, "30").returncode == 0
