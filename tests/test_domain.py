import pytest

from app.domain.evaluacion_docente.entities import Docente, Evaluacion
from app.domain.exceptions import DatoInvalido


def test_docente_sin_evaluaciones_se_puede_eliminar():
    assert Docente(nombre="Carlos Perez").puede_eliminarse()


def test_docente_con_evaluaciones_no_se_puede_eliminar():
    docente = Docente(nombre="Carlos Perez", evaluaciones=[Evaluacion(puntaje=4)])
    assert not docente.puede_eliminarse()


def test_nombre_muy_corto():
    with pytest.raises(DatoInvalido):
        Docente(nombre="A")


def test_puntaje_fuera_de_rango():
    with pytest.raises(DatoInvalido):
        Evaluacion(puntaje=6)


def test_comentarios_ignora_vacios_y_respeta_limite():
    evaluaciones = [Evaluacion(puntaje=5, comentario=f"comentario {i}") for i in range(12)]
    evaluaciones.append(Evaluacion(puntaje=3, comentario=None))
    docente = Docente(nombre="Carlos Perez", evaluaciones=evaluaciones)
    assert len(docente.comentarios()) == 10
