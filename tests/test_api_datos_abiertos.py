from unittest.mock import Mock

from app.container import get_fuente_instituciones, get_fuente_municipios
from app.domain.datos_institucionales.entities import ResultadoFuente
from app.domain.datos_institucionales.ports import FuenteInstituciones, FuenteMunicipios
from app.domain.exceptions import FuenteNoDisponible
from app.main import app
from tests.datos_prueba import INSTITUCIONES, MUNICIPIOS

ESTADO = {"fuente": "x", "dataset": "d", "url": "u", "nombre": "n", "estado": "CLOSED",
          "fallos_seguidos": 0, "umbral_fallos": 3, "tiempo_recuperacion_s": 30.0, "historial": []}


def usar_fuentes(origen="api", error=None):
    ies = Mock(spec=FuenteInstituciones)
    mpios = Mock(spec=FuenteMunicipios)
    ies.obtener.return_value = ResultadoFuente(INSTITUCIONES, origen)
    mpios.obtener.return_value = ResultadoFuente(MUNICIPIOS, origen)
    if error:
        ies.obtener.side_effect = error
    ies.estado.return_value = ESTADO | {"fuente": "MEN"}
    mpios.estado.return_value = ESTADO | {"fuente": "DANE", "estado": "OPEN"}
    app.dependency_overrides[get_fuente_instituciones] = lambda: ies
    app.dependency_overrides[get_fuente_municipios] = lambda: mpios


def test_estadisticas_json(client):
    usar_fuentes()
    res = client.get("/api/v1/datos-abiertos/estadisticas")
    assert res.status_code == 200
    datos = res.json()
    assert datos["resumen"]["total_ies"] == 5
    assert datos["origen"] == {"instituciones": "api", "municipios": "api"}
    assert datos["por_departamento"][0]["departamento"] == "Bogotá D.C."


def test_circuitos(client):
    usar_fuentes()
    res = client.get("/api/v1/datos-abiertos/circuitos")
    assert res.status_code == 200
    assert [c["estado"] for c in res.json()] == ["CLOSED", "OPEN"]


def test_pagina_html(client):
    usar_fuentes("cache")
    res = client.get("/estadisticas")
    assert res.status_code == 200
    assert "IES por departamento" in res.text
    assert "Bogotá D.C." in res.text
    assert "cache" in res.text
    assert 'class="estado OPEN"' in res.text


def test_fuente_sin_cache_devuelve_503(client):
    usar_fuentes(error=FuenteNoDisponible("no cache"))
    res = client.get("/api/v1/datos-abiertos/estadisticas")
    assert res.status_code == 503
