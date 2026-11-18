import re
from dataclasses import dataclass
from enum import Enum

from app.domain.exceptions import DatoInvalido

DOMINIO_PERMITIDO = "@academia.umb.edu.co"
PATRON_CORREO = re.compile(r"^[a-z0-9._-]+" + re.escape(DOMINIO_PERMITIDO) + "$")
LARGO_MINIMO_CONTRASENA = 8
LARGO_MAXIMO_CONTRASENA = 72  # bcrypt solo usa los primeros 72 bytes


class Rol(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


def normalizar_correo(correo):
    correo = (correo or "").strip().lower()
    if not PATRON_CORREO.match(correo):
        raise DatoInvalido(f"correo must be an institutional address ending in {DOMINIO_PERMITIDO}")
    return correo


def validar_contrasena(contrasena):
    largo = len((contrasena or "").encode("utf-8"))
    if not LARGO_MINIMO_CONTRASENA <= largo <= LARGO_MAXIMO_CONTRASENA:
        raise DatoInvalido(
            f"contrasena must have between {LARGO_MINIMO_CONTRASENA} and "
            f"{LARGO_MAXIMO_CONTRASENA} bytes"
        )


@dataclass
class Usuario:
    correo: str
    hash_contrasena: str
    rol: Rol = Rol.USER
    id_usuario: int | None = None

    def __post_init__(self):
        self.correo = normalizar_correo(self.correo)
        self.rol = Rol(self.rol)

    def tiene_rol(self, *roles):
        return self.rol in roles
