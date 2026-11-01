import pytest

from app.infrastructure.resiliencia.circuit_breaker import (
    CircuitBreaker,
    CircuitoAbierto,
    EstadoCircuito,
)


class Reloj:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def falla():
    raise ConnectionError("API down")


@pytest.fixture
def reloj():
    return Reloj()


@pytest.fixture
def breaker(reloj):
    return CircuitBreaker("prueba", umbral_fallos=3, tiempo_recuperacion=30, reloj=reloj)


def provocar_fallos(breaker, n):
    for _ in range(n):
        with pytest.raises(ConnectionError):
            breaker.llamar(falla)


def test_empieza_cerrado_y_deja_pasar(breaker):
    assert breaker.estado == EstadoCircuito.CLOSED
    assert breaker.llamar(lambda: "ok") == "ok"


def test_se_abre_al_llegar_al_umbral(breaker):
    provocar_fallos(breaker, 2)
    assert breaker.estado == EstadoCircuito.CLOSED
    provocar_fallos(breaker, 1)
    assert breaker.estado == EstadoCircuito.OPEN


def test_abierto_rechaza_sin_llamar(breaker):
    provocar_fallos(breaker, 3)
    llamadas = []
    with pytest.raises(CircuitoAbierto):
        breaker.llamar(lambda: llamadas.append(1))
    assert llamadas == []


def test_pasa_a_half_open_despues_del_tiempo(breaker, reloj):
    provocar_fallos(breaker, 3)
    reloj.t = 29
    assert breaker.estado == EstadoCircuito.OPEN
    reloj.t = 30
    assert breaker.estado == EstadoCircuito.HALF_OPEN


def test_half_open_con_exito_se_cierra(breaker, reloj):
    provocar_fallos(breaker, 3)
    reloj.t = 31
    assert breaker.llamar(lambda: "ok") == "ok"
    assert breaker.estado == EstadoCircuito.CLOSED
    assert breaker.fallos_seguidos == 0


def test_half_open_con_fallo_vuelve_a_abrir(breaker, reloj):
    provocar_fallos(breaker, 3)
    reloj.t = 31
    provocar_fallos(breaker, 1)
    assert breaker.estado == EstadoCircuito.OPEN
    reloj.t = 50
    assert breaker.estado == EstadoCircuito.OPEN


def test_exito_reinicia_contador(breaker):
    provocar_fallos(breaker, 2)
    breaker.llamar(lambda: "ok")
    provocar_fallos(breaker, 2)
    assert breaker.estado == EstadoCircuito.CLOSED


def test_historial_guarda_transiciones(breaker, reloj):
    provocar_fallos(breaker, 3)
    reloj.t = 31
    breaker.llamar(lambda: "ok")
    pasos = [(h["de"], h["a"]) for h in breaker.historial]
    assert pasos == [("CLOSED", "OPEN"), ("OPEN", "HALF_OPEN"), ("HALF_OPEN", "CLOSED")]
