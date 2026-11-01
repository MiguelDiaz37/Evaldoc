from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RespuestaModelo:
    texto: str
    tokens_entrada: int
    tokens_salida: int


class ModeloIA(ABC):
    @abstractmethod
    def generar(self, prompt: str) -> RespuestaModelo: ...


class RegistroLlamadas(ABC):
    @abstractmethod
    def registrar(self, pregunta: str, tecnica: str, respuesta: str, tokens_entrada: int,
                  tokens_salida: int, tiempo_ms: int, estado: str) -> None: ...
