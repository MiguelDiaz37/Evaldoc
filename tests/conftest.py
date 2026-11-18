import os
import secrets

# La clave del JWT se genera al azar en cada corrida: no hay secretos escritos en el codigo.
os.environ.setdefault("JWT_SECRET", secrets.token_urlsafe(48))
os.environ.setdefault("BCRYPT_RONDAS", "4")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.container import get_auth_service  # noqa: E402
from app.domain.autenticacion.entities import Rol  # noqa: E402
from app.infrastructure.db.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestSession = sessionmaker(bind=engine)

CORREO_ADMIN = "admin@academia.umb.edu.co"
CORREO_USER = "estudiante@academia.umb.edu.co"
CONTRASENA = secrets.token_urlsafe(12)


def get_test_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def limpiar_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def crear_usuario(correo, rol):
    with TestSession() as db:
        return get_auth_service(db).registrar(correo, CONTRASENA, rol)


def cabecera(client, correo):
    res = client.post("/api/v1/auth/login", json={"correo": correo, "contrasena": CONTRASENA})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def admin(client):
    crear_usuario(CORREO_ADMIN, Rol.ADMIN)
    return cabecera(client, CORREO_ADMIN)


@pytest.fixture
def estudiante(client):
    crear_usuario(CORREO_USER, Rol.USER)
    return cabecera(client, CORREO_USER)
