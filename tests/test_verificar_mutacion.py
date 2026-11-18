import json

import pytest

from scripts.verificar_mutacion import calcular_score, main


def stats(killed, total):
    return {"killed": killed, "total": total, "survived": total - killed, "no_tests": 0}


def escribir(tmp_path, datos):
    ruta = tmp_path / "stats.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


def test_calcula_el_porcentaje_de_muertos():
    assert calcular_score(stats(63, 117)) == 53.8
    assert calcular_score(stats(117, 117)) == 100.0


def test_sin_mutantes_es_un_error():
    with pytest.raises(ValueError):
        calcular_score(stats(0, 0))


def test_pasa_cuando_cumple_el_umbral(tmp_path):
    assert main(escribir(tmp_path, stats(50, 100)), 50) == 0


def test_falla_cuando_queda_por_debajo_del_umbral(tmp_path, capsys):
    assert main(escribir(tmp_path, stats(49, 100)), 50) == 1
    assert "por debajo del minimo de 50" in capsys.readouterr().out
