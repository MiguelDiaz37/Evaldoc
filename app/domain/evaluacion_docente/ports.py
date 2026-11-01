from abc import ABC, abstractmethod

from app.domain.evaluacion_docente.entities import Docente


class DocenteRepository(ABC):
    @abstractmethod
    def listar(self, nombre: str | None = None) -> list[Docente]: ...

    @abstractmethod
    def obtener(self, id_docente: int) -> Docente | None: ...

    @abstractmethod
    def guardar(self, docente: Docente) -> Docente: ...

    @abstractmethod
    def eliminar(self, id_docente: int) -> None: ...
