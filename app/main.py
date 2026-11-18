from fastapi import FastAPI

from app.api import docentes_router
from app.api.errores import registrar_manejadores
from app.infrastructure.db import models
from app.infrastructure.db.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EvalDoc API",
    version="0.4.0",
    description="API for EvalDoc, a web app where UMB students can rate and comment on "
    "their professors. Built with hexagonal architecture (domain, application, api, "
    "infrastructure).",
)

registrar_manejadores(app)
app.include_router(docentes_router.router)


@app.get("/", tags=["Health"], summary="Check the API is running")
def inicio():
    return {"mensaje": "EvalDoc API funcionando", "docs": "/docs"}
