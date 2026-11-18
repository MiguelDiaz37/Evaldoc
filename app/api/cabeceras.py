from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

RUTAS_DOCS = ("/docs", "/redoc", "/openapi.json")

CABECERAS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Cache-Control": "no-store",
}
# Swagger necesita cargar scripts, asi que la politica estricta va solo en la API
CSP_API = "default-src 'none'; frame-ancestors 'none'"


def configurar_seguridad_http(app: FastAPI, origenes_cors):
    if origenes_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origenes_cors,
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["Authorization", "Content-Type"],
            allow_credentials=False,
        )

    @app.middleware("http")
    async def cabeceras_seguridad(request: Request, call_next):
        respuesta = await call_next(request)
        respuesta.headers.update(CABECERAS)
        if not request.url.path.startswith(RUTAS_DOCS):
            respuesta.headers["Content-Security-Policy"] = CSP_API
        return respuesta
