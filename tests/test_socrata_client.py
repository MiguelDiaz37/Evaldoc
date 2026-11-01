import json

import httpx
import pytest

from app.domain.exceptions import FuenteNoDisponible
from app.infrastructure.datos_abiertos.socrata_client import ClienteSocrata
from app.infrastructure.resiliencia.circuit_breaker import CircuitBreaker, EstadoCircuito

FILAS = [{"cod_dpto": "11", "dpto": "BOGOTÁ, D.C.", "cod_mpio": "11001", "nom_mpio": "BOGOTÁ, D.C.",
          "tipo_municipio": "Municipio"}]


def crear(tmp_path, respuestas, umbral=3):
    pedidos = []

    def manejar(request):
        pedidos.append(request)
        codigo = respuestas[min(len(pedidos), len(respuestas)) - 1]
        if codigo == 200:
            return httpx.Response(200, json=FILAS)
        return httpx.Response(codigo, json={"error": "x"})

    http = httpx.Client(transport=httpx.MockTransport(manejar))
    breaker = CircuitBreaker("test", umbral_fallos=umbral, tiempo_recuperacion=60)
    cliente = ClienteSocrata("https://www.datos.gov.co", "gdxc-w37w", http, breaker,
                             tmp_path, ["cod_dpto", "dpto"], intentos=3, espera_base=0,
                             dormir=lambda s: None)
    return cliente, pedidos


def test_respuesta_ok_guarda_cache(tmp_path):
    cliente, pedidos = crear(tmp_path, [200])
    filas, origen = cliente.obtener()
    assert origen == "api"
    assert filas == FILAS
    assert pedidos[0].url.params["$select"] == "cod_dpto,dpto"
    assert json.loads((tmp_path / "gdxc-w37w.json").read_text(encoding="utf-8")) == FILAS


def test_reintenta_y_se_recupera(tmp_path):
    cliente, pedidos = crear(tmp_path, [503, 503, 200])
    filas, origen = cliente.obtener()
    assert origen == "api"
    assert len(pedidos) == 3


def test_falla_y_usa_cache(tmp_path):
    (tmp_path / "gdxc-w37w.json").write_text(json.dumps(FILAS), encoding="utf-8")
    cliente, pedidos = crear(tmp_path, [503])
    filas, origen = cliente.obtener()
    assert origen == "cache"
    assert filas == FILAS
    assert len(pedidos) == 3


def test_error_404_no_se_reintenta(tmp_path):
    (tmp_path / "gdxc-w37w.json").write_text(json.dumps(FILAS), encoding="utf-8")
    cliente, pedidos = crear(tmp_path, [404])
    _, origen = cliente.obtener()
    assert origen == "cache"
    assert len(pedidos) == 1


def test_circuito_abierto_no_llama_a_la_api(tmp_path):
    (tmp_path / "gdxc-w37w.json").write_text(json.dumps(FILAS), encoding="utf-8")
    cliente, pedidos = crear(tmp_path, [503], umbral=2)
    cliente.obtener()
    cliente.obtener()
    assert cliente.breaker.estado == EstadoCircuito.OPEN
    antes = len(pedidos)
    _, origen = cliente.obtener()
    assert origen == "cache"
    assert len(pedidos) == antes


def test_sin_cache_lanza_error(tmp_path):
    cliente, _ = crear(tmp_path, [503])
    with pytest.raises(FuenteNoDisponible):
        cliente.obtener()
