from fastapi import FastAPI

from app import config
from app.api import auth_router, docentes_router
from app.api.cabeceras import configurar_seguridad_http
from app.api.errores import registrar_manejadores
from app.infrastructure.db import models
from app.infrastructure.db.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EvalDoc API",
    version="0.5.0",
    description="API for EvalDoc, a web app where UMB students can rate and comment on "
    "their professors. Built with hexagonal architecture (domain, application, api, "
    "infrastructure). Protected endpoints need a JWT from POST /api/v1/auth/login: "
    "ADMIN can create, update and delete professors, USER can read them.",
    docs_url="/docs" if config.DOCS_ACTIVOS else None,
    redoc_url="/redoc" if config.DOCS_ACTIVOS else None,
    openapi_url="/openapi.json" if config.DOCS_ACTIVOS else None,
)

registrar_manejadores(app)
configurar_seguridad_http(app, config.CORS_ORIGENES)
app.include_router(auth_router.router)
app.include_router(docentes_router.router)


@app.get("/", tags=["Health"], summary="Check the API is running")
def inicio():
    return {"mensaje": "EvalDoc API funcionando", "docs": "/docs"}
