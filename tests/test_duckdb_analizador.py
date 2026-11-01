from app.infrastructure.analitica.duckdb_analizador import DuckDBAnalizador
from tests.datos_prueba import INSTITUCIONES, MUNICIPIOS


def reporte():
    return DuckDBAnalizador().analizar(INSTITUCIONES, MUNICIPIOS)


def test_por_departamento():
    bogota = reporte().por_departamento[0]
    assert bogota["departamento"] == "Bogotá D.C."
    assert bogota["total"] == 3
    assert bogota["oficiales"] == 2
    assert bogota["privadas"] == 1
    assert bogota["pct_acreditadas"] == 33.3


def test_por_caracter():
    caracter = {c["caracter"]: c for c in reporte().por_caracter}
    assert caracter["Universidad"]["total"] == 4
    assert caracter["Universidad"]["porcentaje"] == 80.0
    assert caracter["Institución Tecnológica"]["acreditadas"] == 0


def test_cobertura_cruza_nombres_con_tildes_y_alias():
    cobertura = {c["departamento"]: c for c in reporte().cobertura_municipal}
    assert cobertura["BOGOTÁ, D.C."]["municipios_con_ies"] == 1
    assert cobertura["ANTIOQUIA"]["pct_cobertura"] == 50.0
    assert cobertura["VALLE DEL CAUCA"]["municipios_con_ies"] == 1
    assert cobertura["VAUPÉS"]["municipios_con_ies"] == 0


def test_resumen_descriptivo():
    resumen = reporte().resumen
    assert resumen["total_ies"] == 5
    assert resumen["departamentos"] == 4
    assert resumen["departamentos_sin_ies"] == 1
    assert resumen["media_ies_por_departamento"] == 1.25
    assert resumen["mediana_ies_por_departamento"] == 1.0
    assert resumen["maximo"] == 3
    assert resumen["minimo"] == 0
