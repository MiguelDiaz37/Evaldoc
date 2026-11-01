from abc import ABC, abstractmethod

from app.domain.datos_institucionales.entities import (
    Institucion,
    Municipio,
    ReporteEstadistico,
    ResultadoFuente,
)


class FuenteInstituciones(ABC):
    @abstractmethod
    def obtener(self) -> ResultadoFuente: ...

    @abstractmethod
    def estado(self) -> dict: ...


class FuenteMunicipios(ABC):
    @abstractmethod
    def obtener(self) -> ResultadoFuente: ...

    @abstractmethod
    def estado(self) -> dict: ...


class AnalizadorDatos(ABC):
    @abstractmethod
    def analizar(self, instituciones: list[Institucion],
                 municipios: list[Municipio]) -> ReporteEstadistico: ...
