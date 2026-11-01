import json
import logging
from pathlib import Path

import httpx

from app.domain.exceptions import FuenteNoDisponible
from app.infrastructure.resiliencia.circuit_breaker import CircuitBreaker, CircuitoAbierto
from app.infrastructure.resiliencia.retry import reintentar

log = logging.getLogger("evaldoc.datos_abiertos")


def es_error_temporal(error):
    if isinstance(error, httpx.TransportError):
        return True
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code >= 500 or error.response.status_code == 429
    return False


class ClienteSocrata:
    def __init__(self, base_url, dataset, http: httpx.Client, breaker: CircuitBreaker,
                 carpeta_cache="data/cache", campos=None, intentos=3, espera_base=0.5,
                 limite=5000, dormir=None):
        self.base_url = base_url.rstrip("/")
        self.dataset = dataset
        self.http = http
        self.breaker = breaker
        self.ruta_cache = Path(carpeta_cache) / f"{dataset}.json"
        self.campos = campos
        self.intentos = intentos
        self.espera_base = espera_base
        self.limite = limite
        self.dormir = dormir
        self.ultimo_origen = None

    @property
    def url(self):
        return f"{self.base_url}/resource/{self.dataset}.json"

    def _pedir(self):
        params = {"$limit": self.limite}
        if self.campos:
            params["$select"] = ",".join(self.campos)
        res = self.http.get(self.url, params=params)
        res.raise_for_status()
        return res.json()

    def _pedir_con_reintentos(self):
        opciones = {"intentos": self.intentos, "espera_base": self.espera_base,
                    "es_reintentable": es_error_temporal,
                    "al_reintentar": lambda n, espera, e: log.warning(
                        "%s attempt %s failed (%s), retrying in %.1fs", self.dataset, n,
                        type(e).__name__, espera)}
        if self.dormir:
            opciones["dormir"] = self.dormir
        return reintentar(self._pedir, **opciones)

    def obtener(self):
        try:
            filas = self.breaker.llamar(self._pedir_con_reintentos)
        except (CircuitoAbierto, httpx.HTTPError, ValueError) as e:
            log.warning("%s not available (%s), using cache", self.dataset, type(e).__name__)
            return self._leer_cache(), "cache"
        self._guardar_cache(filas)
        return filas, "api"

    def _guardar_cache(self, filas):
        self.ruta_cache.parent.mkdir(parents=True, exist_ok=True)
        self.ruta_cache.write_text(json.dumps(filas, ensure_ascii=False, indent=1),
                                   encoding="utf-8")

    def _leer_cache(self):
        if not self.ruta_cache.exists():
            raise FuenteNoDisponible(f"Dataset {self.dataset} is not available and has no cache")
        return json.loads(self.ruta_cache.read_text(encoding="utf-8"))

    def estado(self):
        datos = self.breaker.resumen()
        datos["dataset"] = self.dataset
        datos["url"] = self.url
        return datos
