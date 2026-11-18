import pytest

from scripts import crear_usuario
from tests.conftest import CONTRASENA, TestSession, engine


@pytest.fixture
def sin_bd_real(monkeypatch):
    monkeypatch.setattr(crear_usuario, "SessionLocal", TestSession)
    monkeypatch.setattr(crear_usuario, "engine", engine)
    monkeypatch.setattr(crear_usuario.getpass, "getpass", lambda _: CONTRASENA)


def test_crea_un_admin(sin_bd_real, client, capsys):
    assert crear_usuario.main(["jefe@academia.umb.edu.co", "ADMIN"]) == 0
    assert "jefe@academia.umb.edu.co (ADMIN)" in capsys.readouterr().out
    res = client.post("/api/v1/auth/login",
                      json={"correo": "jefe@academia.umb.edu.co", "contrasena": CONTRASENA})
    token = {"Authorization": f"Bearer {res.json()['access_token']}"}
    assert client.get("/api/v1/admin/panel", headers=token).status_code == 200


@pytest.mark.parametrize("args", [[], ["jefe@academia.umb.edu.co"], ["a@academia.umb.edu.co", "ROOT"]])
def test_argumentos_invalidos(sin_bd_real, args):
    assert crear_usuario.main(args) == 2
