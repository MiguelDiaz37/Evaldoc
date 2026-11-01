from app.infrastructure.db.models import EvaluacionORM
from tests.conftest import TestSession


def test_crud_docente(client):
    res = client.post("/api/v1/docentes", json={"nombre": "Carlos Perez"})
    assert res.status_code == 201
    id_docente = res.json()["id_docente"]

    res = client.get(f"/api/v1/docentes/{id_docente}")
    assert res.status_code == 200
    assert res.json()["nombre"] == "Carlos Perez"

    res = client.put(f"/api/v1/docentes/{id_docente}", json={"nombre": "Carlos A Perez"})
    assert res.status_code == 200
    assert res.json()["nombre"] == "Carlos A Perez"

    res = client.get("/api/v1/docentes")
    assert len(res.json()) == 1

    res = client.delete(f"/api/v1/docentes/{id_docente}")
    assert res.status_code == 204
    assert client.get(f"/api/v1/docentes/{id_docente}").status_code == 404


def test_errores(client):
    res = client.post("/api/v1/docentes", json={"nombre": "A"})
    assert res.status_code == 422

    assert client.get("/api/v1/docentes/999").status_code == 404
    assert client.put("/api/v1/docentes/999", json={"nombre": "Nadie"}).status_code == 404
    assert client.delete("/api/v1/docentes/999").status_code == 404


def test_no_borrar_docente_con_evaluaciones(client):
    res = client.post("/api/v1/docentes", json={"nombre": "Laura Gomez"})
    id_docente = res.json()["id_docente"]

    db = TestSession()
    db.add(EvaluacionORM(id_docente=id_docente, puntaje=4, comentario="buen profe"))
    db.commit()
    db.close()

    res = client.delete(f"/api/v1/docentes/{id_docente}")
    assert res.status_code == 409
