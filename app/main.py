from fastapi import FastAPI

from app.api import ai_router, datos_abiertos_router, docentes_router
from app.api.errores import registrar_manejadores
from app.infrastructure.db import models
from app.infrastructure.db.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EvalDoc API",
    version="0.3.0",
    description="API for EvalDoc, a web app where UMB students can rate and comment on "
    "their professors. Built with hexagonal architecture (domain, application, api, "
    "infrastructure). It also consumes two Colombian open data APIs (datos.gov.co and "
    "DANE DIVIPOLA) protected with a circuit breaker and retry with exponential backoff.",
)

registrar_manejadores(app)
app.include_router(docentes_router.router)
app.include_router(ai_router.router)
app.include_router(datos_abiertos_router.router)
app.include_router(datos_abiertos_router.paginas)


@app.get("/", tags=["Health"], summary="Check the API is running")
def inicio():
    return {"mensaje": "EvalDoc API funcionando", "estadisticas": "/estadisticas", "docs": "/docs"}
