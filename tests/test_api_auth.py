"""Pruebas de los 3 endpoints que pide la guia: login, uno de ADMIN y uno de USER."""
from tests.conftest import CONTRASENA, CORREO_ADMIN, CORREO_USER, crear_usuario
from app.domain.autenticacion.entities import Rol


def login(client, correo, contrasena=CONTRASENA):
    return client.post("/api/v1/auth/login", json={"correo": correo, "contrasena": contrasena})


def test_registro_crea_usuario_con_rol_user(client):
    res = client.post("/api/v1/auth/registro",
                      json={"correo": "Nuevo@Academia.UMB.edu.co", "contrasena": CONTRASENA})
    assert res.status_code == 201
    assert res.json()["correo"] == "nuevo@academia.umb.edu.co"
    assert res.json()["rol"] == "USER"
    assert "contrasena" not in res.json() and "hash_contrasena" not in res.json()


def test_registro_no_deja_elegir_el_rol(client):
    res = client.post("/api/v1/auth/registro", json={
        "correo": "colado@academia.umb.edu.co", "contrasena": CONTRASENA, "rol": "ADMIN"})
    assert res.status_code == 422


def test_registro_rechaza_correo_externo_y_repetido(client):
    res = client.post("/api/v1/auth/registro",
                      json={"correo": "alguien@gmail.com", "contrasena": CONTRASENA})
    assert res.status_code == 422
    crear_usuario(CORREO_USER, Rol.USER)
    res = client.post("/api/v1/auth/registro",
                      json={"correo": CORREO_USER, "contrasena": CONTRASENA})
    assert res.status_code == 409


def test_login_devuelve_jwt(client):
    crear_usuario(CORREO_USER, Rol.USER)
    res = login(client, CORREO_USER)
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"
    assert res.json()["access_token"].count(".") == 2


def test_login_mismo_error_para_correo_y_contrasena(client):
    crear_usuario(CORREO_USER, Rol.USER)
    mala_contrasena = login(client, CORREO_USER, "otraClave123")
    correo_inexistente = login(client, "nadie@academia.umb.edu.co")
    assert mala_contrasena.status_code == correo_inexistente.status_code == 401
    assert mala_contrasena.json() == correo_inexistente.json()
    assert mala_contrasena.headers["WWW-Authenticate"] == "Bearer"


def test_endpoint_user_acepta_cualquier_rol(client, estudiante, admin):
    assert client.get("/api/v1/usuarios/me", headers=estudiante).json()["rol"] == "USER"
    assert client.get("/api/v1/usuarios/me", headers=admin).json()["correo"] == CORREO_ADMIN


def test_endpoint_admin_rechaza_user_con_403(client, estudiante, admin):
    assert client.get("/api/v1/admin/panel", headers=estudiante).status_code == 403
    res = client.get("/api/v1/admin/panel", headers=admin)
    assert res.status_code == 200
    assert res.json()["admin"] == CORREO_ADMIN


def test_sin_token_o_token_falso_da_401(client):
    assert client.get("/api/v1/usuarios/me").status_code == 401
    falso = {"Authorization": "Bearer esto.no.sirve"}
    assert client.get("/api/v1/admin/panel", headers=falso).status_code == 401


def test_user_puede_leer_docentes_pero_no_modificarlos(client, estudiante, admin):
    creado = client.post("/api/v1/docentes", json={"nombre": "Carlos Perez"}, headers=admin)
    id_docente = creado.json()["id_docente"]

    assert client.get("/api/v1/docentes", headers=estudiante).status_code == 200
    assert client.get(f"/api/v1/docentes/{id_docente}", headers=estudiante).status_code == 200
    assert client.post("/api/v1/docentes", json={"nombre": "Otro Profe"},
                       headers=estudiante).status_code == 403
    assert client.put(f"/api/v1/docentes/{id_docente}", json={"nombre": "Cambio"},
                      headers=estudiante).status_code == 403
    assert client.delete(f"/api/v1/docentes/{id_docente}",
                         headers=estudiante).status_code == 403
    assert client.get("/api/v1/docentes").status_code == 401
