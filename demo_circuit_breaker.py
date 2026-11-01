import argparse
import json
import logging
import time
from pathlib import Path

import httpx

from app import config
from app.infrastructure.datos_abiertos.fuentes import CAMPOS_MUNICIPIOS
from app.infrastructure.datos_abiertos.socrata_client import ClienteSocrata
from app.infrastructure.resiliencia.circuit_breaker import CircuitBreaker


class TransporteDemo(httpx.BaseTransport):
    def __init__(self, sin_red):
        self.modo = "caida"
        self.sin_red = sin_red
        self.real = httpx.HTTPTransport()
        self.peticiones = 0

    def handle_request(self, request):
        self.peticiones += 1
        if self.modo == "caida":
            return httpx.Response(503, json={"error": "service unavailable"}, request=request)
        if self.sin_red:
            ruta = Path(config.CARPETA_CACHE) / f"{config.DATASET_MUNICIPIOS}.json"
            return httpx.Response(200, content=ruta.read_bytes(), request=request)
        return self.real.handle_request(request)


def mostrar(paso, breaker, origen, transporte):
    print(f"{paso:<38} estado={breaker.estado.value:<10} fallos={breaker.fallos_seguidos} "
          f"origen={origen:<6} peticiones_http={transporte.peticiones}")


def main():
    parser = argparse.ArgumentParser(description="Circuit breaker demo with DANE DIVIPOLA")
    parser.add_argument("--sin-red", action="store_true",
                        help="the recovery step uses the local cache instead of datos.gov.co")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="  [%(levelname)s] %(message)s")
    transporte = TransporteDemo(args.sin_red)
    breaker = CircuitBreaker("DANE-DIVIPOLA", umbral_fallos=3, tiempo_recuperacion=5)
    cliente = ClienteSocrata(config.DATOS_ABIERTOS_URL, config.DATASET_MUNICIPIOS,
                             httpx.Client(transport=transporte, timeout=10), breaker,
                             config.CARPETA_CACHE, CAMPOS_MUNICIPIOS, intentos=3,
                             espera_base=0.2)

    print("== 1. The API is down (HTTP 503): retry with backoff 0.2s, 0.4s ==")
    for i in range(1, 4):
        _, origen = cliente.obtener()
        mostrar(f"call {i}", breaker, origen, transporte)

    print("\n== 2. Circuit OPEN: calls are rejected without touching the API ==")
    _, origen = cliente.obtener()
    mostrar("call 4", breaker, origen, transporte)

    print("\n== 3. Waiting 5s (recovery time) ==")
    time.sleep(5.1)
    print(f"{'after waiting':<38} estado={breaker.estado.value}")

    print("\n== 4. The API is back: test call in HALF_OPEN ==")
    transporte.modo = "ok"
    filas, origen = cliente.obtener()
    mostrar("call 5", breaker, origen, transporte)
    print(f"{'municipalities received':<38} {len(filas)}")
    if args.sin_red:
        print("(--sin-red: the recovered API was simulated with the local copy of the dataset)")

    print("\nTransitions:")
    print(json.dumps(breaker.historial, indent=2))


if __name__ == "__main__":
    main()
