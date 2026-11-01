from fastapi import APIRouter, Depends

from app.api.schemas import DocenteIn, DocenteOut
from app.application.docente_service import DocenteService
from app.container import get_docente_service

router = APIRouter(prefix="/api/v1/docentes", tags=["Professors"])


@router.get(
    "",
    response_model=list[DocenteOut],
    summary="List professors",
    description="Returns all professors. You can filter by name with `nombre`.",
)
def listar_docentes(nombre: str | None = None,
                    service: DocenteService = Depends(get_docente_service)):
    return service.listar(nombre)


@router.get(
    "/{id_docente}",
    response_model=DocenteOut,
    summary="Get a professor",
    description="Returns one professor by id. Returns 404 if it does not exist.",
    responses={404: {"description": "Professor not found"}},
)
def obtener_docente(id_docente: int, service: DocenteService = Depends(get_docente_service)):
    return service.obtener(id_docente)


@router.post(
    "",
    response_model=DocenteOut,
    status_code=201,
    summary="Create a professor",
    description="Creates a new professor. The name needs at least 3 characters.",
)
def crear_docente(datos: DocenteIn, service: DocenteService = Depends(get_docente_service)):
    return service.crear(datos.nombre, datos.foto_perfil)


@router.put(
    "/{id_docente}",
    response_model=DocenteOut,
    summary="Update a professor",
    description="Updates the name and photo of a professor.",
    responses={404: {"description": "Professor not found"}},
)
def actualizar_docente(id_docente: int, datos: DocenteIn,
                       service: DocenteService = Depends(get_docente_service)):
    return service.actualizar(id_docente, datos.nombre, datos.foto_perfil)


@router.delete(
    "/{id_docente}",
    status_code=204,
    summary="Delete a professor",
    description="Deletes a professor. If the professor already has evaluations "
    "it returns 409 so we don't lose them.",
    responses={404: {"description": "Professor not found"}, 409: {"description": "Has evaluations"}},
)
def eliminar_docente(id_docente: int, service: DocenteService = Depends(get_docente_service)):
    service.eliminar(id_docente)
