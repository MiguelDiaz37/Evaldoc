from unittest.mock import Mock

import pytest

from app.application.docente_service import DocenteService
from app.domain.evaluacion_docente.entities import Docente, Evaluacion
from app.domain.evaluacion_docente.ports import DocenteRepository
from app.domain.exceptions import DocenteConEvaluaciones, DocenteNoEncontrado


@pytest.fixture
def repo():
    return Mock(spec=DocenteRepository)


def test_crear_llama_a_guardar(repo):
    repo.guardar.return_value = Docente(id_docente=1, nombre="Carlos Perez")
    service = DocenteService(repo)

    docente = service.crear("Carlos Perez")

    assert docente.id_docente == 1
    repo.guardar.assert_called_once()
    assert repo.guardar.call_args.args[0].nombre == "Carlos Perez"


def test_obtener_no_existe(repo):
    repo.obtener.return_value = None
    with pytest.raises(DocenteNoEncontrado):
        DocenteService(repo).obtener(99)


def test_actualizar_cambia_nombre(repo):
    repo.obtener.return_value = Docente(id_docente=1, nombre="Carlos Perez")
    repo.guardar.side_effect = lambda d: d

    docente = DocenteService(repo).actualizar(1, "Carlos A Perez")

    assert docente.nombre == "Carlos A Perez"


def test_eliminar_con_evaluaciones_no_borra(repo):
    repo.obtener.return_value = Docente(
        id_docente=1, nombre="Laura Gomez", evaluaciones=[Evaluacion(puntaje=4)]
    )
    with pytest.raises(DocenteConEvaluaciones):
        DocenteService(repo).eliminar(1)
    repo.eliminar.assert_not_called()


def test_eliminar_sin_evaluaciones(repo):
    repo.obtener.return_value = Docente(id_docente=1, nombre="Laura Gomez")
    DocenteService(repo).eliminar(1)
    repo.eliminar.assert_called_once_with(1)
