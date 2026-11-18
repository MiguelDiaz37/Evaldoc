"""Pruebas de los controles OWASP API Security Top 10 2023 que no cubren otros archivos."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.cabeceras import configurar_seguridad_http
from app.api.errores import registrar_manejadores
from app.api.limite_peticiones import LimitadorPeticiones
from tests.conftest import CONTRASENA, CORREO_USER, crear_usuario
from app.domain.autenticacion.entities import Rol


class Reloj:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


# API4:2023 Unrestricted Resource Consumption -------------------------------------------

def test_limitador_bloquea_despues_del_maximo_y_libera_al_pasar_la_ventana():
    reloj = Reloj()
    limitador = LimitadorPeticiones(maximo=3, ventana_s=60, reloj=reloj)
    assert [limitador.registrar("ip") for _ in range(3)] == [0, 0, 0]
    reloj.t = 10
    assert limitador.registrar("ip") == 50
    assert limitador.registrar("otra-ip") == 0
    reloj.t = 60
    assert limitador.registrar("ip") == 0


def test_login_por_fuerza_bruta_recibe_429(client):
    crear_usuario(CORREO_USER, Rol.USER)
    intento = {"correo": CORREO_USER, "contrasena": "adivinando1"}
    codigos = [client.post("/api/v1/auth/login", json=intento).status_code for _ in range(6)]
    assert codigos == [401] * 5 + [429]
    res = client.post("/api/v1/auth/login", json={"correo": CORREO_USER, "contrasena": CONTRASENA})
    assert res.status_code == 429
    assert int(res.headers["Retry-After"]) > 0


def test_listado_paginado_con_maximo_de_100(client, admin):
    for i in range(3):
        client.post("/api/v1/docentes", json={"nombre": f"Docente {i}"}, headers=admin)
    res = client.get("/api/v1/docentes?limite=2&desde=1", headers=admin)
    assert [d["nombre"] for d in res.json()] == ["Docente 1", "Docente 2"]
    assert client.get("/api/v1/docentes?limite=101", headers=admin).status_code == 422
    assert client.get("/api/v1/docentes?nombre=" + "x" * 151, headers=admin).status_code == 422


def test_campos_con_largo_maximo(client):
    res = client.post("/api/v1/auth/login",
                      json={"correo": "a" * 200 + "@academia.umb.edu.co", "contrasena": "x"})
    assert res.status_code == 422


# API7:2023 SSRF y API8:2023 Security Misconfiguration ----------------------------------

@pytest.mark.parametrize("foto", ["http://umb.edu.co/a.png", "javascript:alert(1)",
                                  "file:///etc/passwd", "https://a b.png"])
def test_foto_solo_acepta_https(client, admin, foto):
    res = client.post("/api/v1/docentes", json={"nombre": "Carlos Perez", "foto_perfil": foto},
                      headers=admin)
    assert res.status_code == 422


def test_cabeceras_de_seguridad(client):
    res = client.get("/")
    assert res.headers["X-Content-Type-Options"] == "nosniff"
    assert res.headers["X-Frame-Options"] == "DENY"
    assert res.headers["Referrer-Policy"] == "no-referrer"
    assert res.headers["Cache-Control"] == "no-store"
    assert "max-age=31536000" in res.headers["Strict-Transport-Security"]
    assert res.headers["Content-Security-Policy"] == "default-src 'none'; frame-ancestors 'none'"
    assert "Content-Security-Policy" not in client.get("/docs").headers


def app_de_prueba(origenes):
    app = FastAPI()
    registrar_manejadores(app)
    configurar_seguridad_http(app, origenes)

    @app.get("/falla")
    def falla():
        raise RuntimeError("detalle interno con la ruta C:/secreto/config.py")

    return app


def test_cors_solo_permite_los_origenes_configurados():
    client = TestClient(app_de_prueba(["https://evaldoc.umb.edu.co"]))
    permitido = client.options("/falla", headers={"Origin": "https://evaldoc.umb.edu.co",
                                                  "Access-Control-Request-Method": "GET"})
    assert permitido.headers["access-control-allow-origin"] == "https://evaldoc.umb.edu.co"
    otro = client.options("/falla", headers={"Origin": "https://atacante.com",
                                             "Access-Control-Request-Method": "GET"})
    assert "access-control-allow-origin" not in otro.headers


def test_sin_origenes_no_hay_cors():
    client = TestClient(app_de_prueba([]))
    res = client.get("/", headers={"Origin": "https://atacante.com"})
    assert "access-control-allow-origin" not in res.headers


def test_error_inesperado_no_muestra_detalles():
    client = TestClient(app_de_prueba([]), raise_server_exceptions=False)
    res = client.get("/falla")
    assert res.status_code == 500
    assert res.json() == {"detail": "Internal server error"}
    assert "secreto" not in res.text


# API9:2023 Improper Inventory Management -----------------------------------------------

def test_docs_se_pueden_apagar_en_produccion(monkeypatch):
    import importlib

    from app import config, main
    monkeypatch.setattr(config, "DOCS_ACTIVOS", False)
    try:
        sin_docs = TestClient(importlib.reload(main).app)
        assert sin_docs.get("/docs").status_code == 404
        assert sin_docs.get("/openapi.json").status_code == 404
    finally:
        monkeypatch.setattr(config, "DOCS_ACTIVOS", True)
        importlib.reload(main)


def test_todas_las_rutas_estan_versionadas(client):
    rutas = client.get("/openapi.json").json()["paths"]
    assert all(r == "/" or r.startswith("/api/v1/") for r in rutas)
