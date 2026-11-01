import pytest

from app.infrastructure.resiliencia.retry import reintentar


class Falla:
    def __init__(self, veces, error=ConnectionError):
        self.veces = veces
        self.error = error
        self.llamadas = 0

    def __call__(self):
        self.llamadas += 1
        if self.llamadas <= self.veces:
            raise self.error("fallo")
        return "ok"


def test_backoff_exponencial():
    esperas = []
    funcion = Falla(3)
    with pytest.raises(ConnectionError):
        reintentar(funcion, intentos=3, espera_base=0.5, dormir=esperas.append)
    assert esperas == [0.5, 1.0]
    assert funcion.llamadas == 3


def test_exito_despues_de_fallos():
    esperas = []
    funcion = Falla(2)
    assert reintentar(funcion, intentos=4, espera_base=1, dormir=esperas.append) == "ok"
    assert esperas == [1, 2]


def test_no_reintenta_errores_permanentes():
    esperas = []
    funcion = Falla(5, error=ValueError)
    with pytest.raises(ValueError):
        reintentar(funcion, intentos=3, dormir=esperas.append,
                   es_reintentable=lambda e: isinstance(e, ConnectionError))
    assert funcion.llamadas == 1
    assert esperas == []
