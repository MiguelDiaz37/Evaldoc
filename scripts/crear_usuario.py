"""Crea un usuario desde la terminal. Es la unica forma de crear cuentas ADMIN.

Uso: python -m scripts.crear_usuario correo@academia.umb.edu.co ADMIN
La contrasena se pide con getpass para que no quede en el historial de la terminal.
"""
import getpass
import sys

from app.container import get_auth_service
from app.domain.autenticacion.entities import Rol
from app.infrastructure.db import models
from app.infrastructure.db.database import SessionLocal, engine


def main(args):
    if len(args) != 2 or args[1] not in Rol.__members__:
        print("Uso: python -m scripts.crear_usuario <correo> <ADMIN|USER>")
        return 2
    models.Base.metadata.create_all(bind=engine)
    contrasena = getpass.getpass("Contrasena: ")
    with SessionLocal() as db:
        usuario = get_auth_service(db).registrar(args[0], contrasena, Rol[args[1]])
    print(f"Usuario creado: {usuario.correo} ({usuario.rol.value})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
