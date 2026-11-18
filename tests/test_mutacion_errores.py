"""Pruebas agregadas para matar mutantes que sobrevivian en el manejador de errores.

La app de app.main se arma una sola vez al importarla, asi que estas pruebas registran los
manejadores en una app nueva para comprobar el codigo HTTP y el cuerpo de cada error.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.errores import registrar_manejadores
from app.domain import exceptions as ex


class OtroError(ex.ErrorDominio):
    pass


ERRORES = {
    "dato": (ex.DatoInvalido("dato malo"), 422),
    "no-encontrado": (ex.DocenteNoEncontrado("Professor not found"), 404),
    "con-evaluaciones": (ex.DocenteConEvaluaciones("Professor has evaluations"), 409),
    "otro": (OtroError("error sin codigo propio"), 400),
}


@pytest.fixture
def client():
    app = FastAPI()
    registrar_manejadores(app)

    @app.get("/error/{nombre}")
    def lanzar(nombre: str):
        raise ERRORES[nombre][0]

    return TestClient(app)


@pytest.mark.parametrize("nombre", ERRORES)
def test_cada_error_tiene_su_codigo_y_mensaje(client, nombre):
    error, codigo = ERRORES[nombre]
    res = client.get(f"/error/{nombre}")
    assert res.status_code == codigo
    assert res.json() == {"detail": str(error)}
