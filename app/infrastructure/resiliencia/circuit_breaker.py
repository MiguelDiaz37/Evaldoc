import threading
import time
from datetime import datetime
from enum import Enum


class EstadoCircuito(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitoAbierto(Exception):
    pass


class CircuitBreaker:
    def __init__(self, nombre, umbral_fallos=3, tiempo_recuperacion=30.0, reloj=time.monotonic):
        self.nombre = nombre
        self.umbral_fallos = umbral_fallos
        self.tiempo_recuperacion = tiempo_recuperacion
        self.reloj = reloj
        self._estado = EstadoCircuito.CLOSED
        self.fallos_seguidos = 0
        self.abierto_desde = None
        self.historial = []
        self._lock = threading.Lock()

    def _cambiar(self, nuevo):
        if nuevo != self._estado:
            self.historial.append({
                "fecha": datetime.now().isoformat(timespec="seconds"),
                "de": self._estado.value,
                "a": nuevo.value,
            })
            self.historial = self.historial[-20:]
            self._estado = nuevo

    @property
    def estado(self):
        with self._lock:
            if (self._estado == EstadoCircuito.OPEN
                    and self.reloj() - self.abierto_desde >= self.tiempo_recuperacion):
                self._cambiar(EstadoCircuito.HALF_OPEN)
            return self._estado

    def llamar(self, funcion):
        if self.estado == EstadoCircuito.OPEN:
            raise CircuitoAbierto(f"Circuit {self.nombre} is OPEN")
        try:
            resultado = funcion()
        except Exception:
            self._registrar_fallo()
            raise
        self._registrar_exito()
        return resultado

    def _registrar_exito(self):
        with self._lock:
            self.fallos_seguidos = 0
            self._cambiar(EstadoCircuito.CLOSED)

    def _registrar_fallo(self):
        with self._lock:
            self.fallos_seguidos += 1
            if (self._estado == EstadoCircuito.HALF_OPEN
                    or self.fallos_seguidos >= self.umbral_fallos):
                self.abierto_desde = self.reloj()
                self._cambiar(EstadoCircuito.OPEN)

    def resumen(self):
        return {
            "nombre": self.nombre,
            "estado": self.estado.value,
            "fallos_seguidos": self.fallos_seguidos,
            "umbral_fallos": self.umbral_fallos,
            "tiempo_recuperacion_s": self.tiempo_recuperacion,
            "historial": list(self.historial),
        }
