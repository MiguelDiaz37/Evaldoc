from dataclasses import asdict
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.schemas import EstadoCircuitoOut, ReporteOut
from app.application.estadisticas_service import EstadisticasService
from app.container import get_estadisticas_service

router = APIRouter(prefix="/api/v1/datos-abiertos", tags=["Open data"])
paginas = APIRouter(tags=["UI"])
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


@router.get(
    "/estadisticas",
    response_model=ReporteOut,
    summary="Higher education statistics",
    description="Downloads the MEN higher education institutions dataset (datos.gov.co) and "
    "the DANE DIVIPOLA municipalities, processes them with DuckDB and returns descriptive "
    "statistics. `origen` says if each source came from the API or from the local cache.",
    responses={503: {"description": "Source not available and no cache"}},
)
def estadisticas(service: EstadisticasService = Depends(get_estadisticas_service)):
    return asdict(service.generar_reporte())


@router.get(
    "/circuitos",
    response_model=list[EstadoCircuitoOut],
    summary="Circuit breaker states",
    description="Shows the state (CLOSED, OPEN, HALF_OPEN) of the circuit breaker of each "
    "external API and its last transitions.",
)
def circuitos(service: EstadisticasService = Depends(get_estadisticas_service)):
    return service.estado_fuentes()


@paginas.get("/estadisticas", response_class=HTMLResponse, include_in_schema=False)
def pagina_estadisticas(request: Request,
                        service: EstadisticasService = Depends(get_estadisticas_service)):
    reporte = service.generar_reporte()
    maximo = max((d["total"] for d in reporte.por_departamento), default=1)
    return templates.TemplateResponse(request, "estadisticas.html", {
        "reporte": reporte,
        "circuitos": service.estado_fuentes(),
        "maximo": maximo,
    })
