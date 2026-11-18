"""Pruebas agregadas para matar mutantes que sobrevivian en las entidades del dominio.

Revisan los valores limite (puntaje 1 y 5, nombre de 3 caracteres) y el texto exacto de los
mensajes de error, que son los que la API le devuelve al usuario.
"""
import pytest

from app.domain.evaluacion_docente.entities import Docente, Evaluacion
from app.domain.exceptions import DatoInvalido

MENSAJE_PUNTAJE = r"^puntaje must be between 1 and 5$"
MENSAJE_NOMBRE = r"^nombre must have at least 3 characters$"


@pytest.mark.parametrize("puntaje", [1, 5])
def test_puntajes_limite_son_validos(puntaje):
    assert Evaluacion(puntaje=puntaje).puntaje == puntaje


@pytest.mark.parametrize("puntaje", [0, 6])
def test_puntajes_fuera_del_limite_dan_mensaje_exacto(puntaje):
    with pytest.raises(DatoInvalido, match=MENSAJE_PUNTAJE):
        Evaluacion(puntaje=puntaje)


def test_nombre_de_tres_caracteres_es_valido():
    assert Docente(nombre="Ana").nombre == "Ana"


@pytest.mark.parametrize("nombre", ["", "Al", "  Al  "])
def test_nombre_corto_da_mensaje_exacto(nombre):
    with pytest.raises(DatoInvalido, match=MENSAJE_NOMBRE):
        Docente(nombre=nombre)
