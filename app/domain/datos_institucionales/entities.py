from dataclasses import dataclass, field


@dataclass(frozen=True)
class Institucion:
    codigo: str
    nombre: str
    tipo: str
    sector: str
    caracter: str
    departamento: str
    municipio: str
    acreditada: bool


@dataclass(frozen=True)
class Municipio:
    codigo: str
    nombre: str
    codigo_departamento: str
    departamento: str
    tipo: str


@dataclass
class ResultadoFuente:
    datos: list
    origen: str


@dataclass
class ReporteEstadistico:
    resumen: dict
    por_departamento: list[dict]
    por_caracter: list[dict]
    cobertura_municipal: list[dict]
    origen: dict = field(default_factory=dict)
