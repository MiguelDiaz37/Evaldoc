from abc import ABC, abstractmethod

from app.domain.autenticacion.entities import Usuario


class UsuarioRepository(ABC):
    @abstractmethod
    def obtener_por_correo(self, correo: str) -> Usuario | None: ...

    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario: ...


class HasherContrasenas(ABC):
    @abstractmethod
    def hashear(self, contrasena: str) -> str: ...

    @abstractmethod
    def verificar(self, contrasena: str, hash_guardado: str) -> bool: ...


class EmisorTokens(ABC):
    @abstractmethod
    def emitir(self, usuario: Usuario) -> str: ...

    @abstractmethod
    def leer(self, token: str) -> dict:
        """Devuelve los claims del token o lanza TokenInvalido."""
