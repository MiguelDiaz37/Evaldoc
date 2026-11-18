"""Pruebas agregadas para matar mutantes que sobrevivian en el repositorio SQLAlchemy.

Revisan que al convertir filas en entidades se copien todos los campos, y que listar
filtre por nombre sin importar mayusculas y ordene alfabeticamente.
"""
import pytest

from app.infrastructure.db.models import DocenteORM, EvaluacionORM
from app.infrastructure.db.sqlalchemy_docente_repository import SqlAlchemyDocenteRepository
from app.domain.evaluacion_docente.entities import Docente
from tests.conftest import TestSession

FOTO = "https://umb.edu.co/fotos/laura.png"


@pytest.fixture
def db():
    sesion = TestSession()
    yield sesion
    sesion.close()


def test_obtener_copia_todos_los_campos(db):
    fila = DocenteORM(nombre="Laura Gomez", foto_perfil=FOTO)
    db.add(fila)
    db.flush()
    db.add(EvaluacionORM(id_docente=fila.id_docente, puntaje=4, comentario="explica bien"))
    db.commit()

    docente = SqlAlchemyDocenteRepository(db).obtener(fila.id_docente)

    assert docente.foto_perfil == FOTO
    evaluacion = docente.evaluaciones[0]
    assert evaluacion.id_evaluacion is not None
    assert evaluacion.id_docente == fila.id_docente
    assert evaluacion.puntaje == 4
    assert evaluacion.comentario == "explica bien"


def test_listar_filtra_sin_importar_mayusculas_y_ordena(db):
    repo = SqlAlchemyDocenteRepository(db)
    for nombre in ["Zoe Diaz", "Ana Ruiz", "Mariana Lopez", "Carlos Perez"]:
        repo.guardar(Docente(nombre=nombre))

    assert [d.nombre for d in repo.listar()] == [
        "Ana Ruiz", "Carlos Perez", "Mariana Lopez", "Zoe Diaz"]
    assert [d.nombre for d in repo.listar("ANA")] == ["Ana Ruiz", "Mariana Lopez"]


def test_guardar_actualiza_la_foto(db):
    repo = SqlAlchemyDocenteRepository(db)
    docente = repo.guardar(Docente(nombre="Laura Gomez"))
    docente.foto_perfil = FOTO
    assert repo.guardar(docente).foto_perfil == FOTO
