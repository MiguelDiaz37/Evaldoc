"""Pruebas agregadas para matar mutantes que sobrevivian en DocenteService.

Las pruebas anteriores revisaban que se lanzara la excepcion, pero no el mensaje, y no
revisaban que la foto de perfil ni el filtro por nombre llegaran al repositorio.
"""
from unittest.mock import Mock

import pytest

from app.application.docente_service import DocenteService
from app.domain.evaluacion_docente.entities import Docente, Evaluacion
from app.domain.evaluacion_docente.ports import DocenteRepository
from app.domain.exceptions import DocenteConEvaluaciones, DocenteNoEncontrado

FOTO = "https://umb.edu.co/fotos/carlos.png"


@pytest.fixture
def repo():
    return Mock(spec=DocenteRepository)


def test_listar_pasa_el_filtro_al_repositorio(repo):
    repo.listar.return_value = []
    DocenteService(repo).listar("Carlos")
    repo.listar.assert_called_once_with("Carlos")


def test_obtener_no_existe_da_mensaje_exacto(repo):
    repo.obtener.return_value = None
    with pytest.raises(DocenteNoEncontrado, match=r"^Professor not found$"):
        DocenteService(repo).obtener(99)


def test_crear_guarda_la_foto(repo):
    repo.guardar.side_effect = lambda d: d
    docente = DocenteService(repo).crear("Carlos Perez", FOTO)
    assert docente.foto_perfil == FOTO


def test_actualizar_cambia_la_foto(repo):
    repo.obtener.return_value = Docente(id_docente=1, nombre="Carlos Perez")
    repo.guardar.side_effect = lambda d: d
    docente = DocenteService(repo).actualizar(1, "Carlos Perez", FOTO)
    assert docente.foto_perfil == FOTO


def test_eliminar_con_evaluaciones_da_mensaje_exacto(repo):
    repo.obtener.return_value = Docente(
        id_docente=1, nombre="Laura Gomez", evaluaciones=[Evaluacion(puntaje=4)]
    )
    with pytest.raises(DocenteConEvaluaciones,
                       match=r"^Professor has evaluations, can't delete$"):
        DocenteService(repo).eliminar(1)
