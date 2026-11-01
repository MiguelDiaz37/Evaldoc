from functools import lru_cache

import httpx
from fastapi import Depends
from sqlalchemy.orm import Session

from app import config
from app.application.asistente_ia_service import AsistenteIAService
from app.application.docente_service import DocenteService
from app.application.estadisticas_service import EstadisticasService
from app.infrastructure.analitica.duckdb_analizador import DuckDBAnalizador
from app.infrastructure.datos_abiertos.fuentes import (
    CAMPOS_INSTITUCIONES,
    CAMPOS_MUNICIPIOS,
    InstitucionesDatosGov,
    MunicipiosDivipola,
)
from app.infrastructure.datos_abiertos.socrata_client import ClienteSocrata
from app.infrastructure.db.database import get_db
from app.infrastructure.db.sqlalchemy_docente_repository import SqlAlchemyDocenteRepository
from app.infrastructure.ia.csv_registro import CsvRegistroLlamadas
from app.infrastructure.ia.gemini_client import GeminiClient
from app.infrastructure.resiliencia.circuit_breaker import CircuitBreaker


def get_docente_repository(db: Session = Depends(get_db)):
    return SqlAlchemyDocenteRepository(db)


def get_modelo_ia():
    return GeminiClient(config.GEMINI_API_KEY, config.GEMINI_MODEL, config.GEMINI_TIMEOUT_MS)


def get_registro_llamadas():
    return CsvRegistroLlamadas(config.RUTA_LOG_IA)


def get_docente_service(repo=Depends(get_docente_repository)):
    return DocenteService(repo)


def get_asistente_service(
    repo=Depends(get_docente_repository),
    modelo=Depends(get_modelo_ia),
    registro=Depends(get_registro_llamadas),
):
    return AsistenteIAService(repo, modelo, registro)


@lru_cache
def get_http():
    return httpx.Client(timeout=config.HTTP_TIMEOUT_S, headers={"Accept": "application/json"})


def crear_cliente(dataset, nombre, campos):
    breaker = CircuitBreaker(nombre, config.UMBRAL_FALLOS, config.TIEMPO_RECUPERACION_S)
    return ClienteSocrata(config.DATOS_ABIERTOS_URL, dataset, get_http(), breaker,
                          config.CARPETA_CACHE, campos, config.REINTENTOS, config.ESPERA_BASE_S)


@lru_cache
def get_fuente_instituciones():
    cliente = crear_cliente(config.DATASET_INSTITUCIONES, "datos.gov.co-IES", CAMPOS_INSTITUCIONES)
    return InstitucionesDatosGov(cliente)


@lru_cache
def get_fuente_municipios():
    cliente = crear_cliente(config.DATASET_MUNICIPIOS, "DANE-DIVIPOLA", CAMPOS_MUNICIPIOS)
    return MunicipiosDivipola(cliente)


def get_estadisticas_service(
    instituciones=Depends(get_fuente_instituciones),
    municipios=Depends(get_fuente_municipios),
):
    return EstadisticasService(instituciones, municipios, DuckDBAnalizador())
