import math
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class LimitadorPeticiones:
    """Limita cuantas peticiones puede hacer una misma IP en una ventana de tiempo.

    Se usa en login y registro para frenar ataques de fuerza bruta (OWASP API4:2023).
    El estado vive en memoria, sirve para una sola instancia del servidor.
    """

    def __init__(self, maximo, ventana_s, reloj=time.monotonic):
        self.maximo = maximo
        self.ventana_s = ventana_s
        self.reloj = reloj
        self._peticiones = defaultdict(deque)
        self._lock = threading.Lock()

    def registrar(self, clave):
        """Devuelve 0 si la peticion pasa, o los segundos que hay que esperar."""
        ahora = self.reloj()
        with self._lock:
            peticiones = self._peticiones[clave]
            while peticiones and ahora - peticiones[0] >= self.ventana_s:
                peticiones.popleft()
            if len(peticiones) >= self.maximo:
                return max(1, math.ceil(self.ventana_s - (ahora - peticiones[0])))
            peticiones.append(ahora)
            return 0

    def reiniciar(self):
        with self._lock:
            self._peticiones.clear()

    def __call__(self, request: Request):
        ip = request.client.host if request.client else "desconocida"
        espera = self.registrar(f"{request.url.path}:{ip}")
        if espera:
            raise HTTPException(status_code=429, detail="Too many requests, try again later",
                                headers={"Retry-After": str(espera)})
