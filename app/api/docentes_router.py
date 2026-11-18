from fastapi import APIRouter, Depends

from app.api.schemas import DocenteIn, DocenteOut
from app.api.seguridad import cualquier_usuario, solo_admin
from app.application.docente_service import DocenteService
from app.container import get_docente_service

router = APIRouter(prefix="/api/v1/docentes", tags=["Professors"])

ERROR_401 = {401: {"description": "Missing, invalid or expired token"}}
ERROR_403 = {403: {"description": "Only ADMIN can do this"}}
ERROR_404 = {404: {"description": "Professor not found"}}


@router.get(
    "",
    response_model=list[DocenteOut],
    summary="List professors (USER or ADMIN)",
    description="Returns all professors. You can filter by name with `nombre`.",
    dependencies=[Depends(cualquier_usuario)],
    responses=ERROR_401,
)
def listar_docentes(nombre: str | None = None,
                    service: DocenteService = Depends(get_docente_service)):
    return service.listar(nombre)


@router.get(
    "/{id_docente}",
    response_model=DocenteOut,
    summary="Get a professor (USER or ADMIN)",
    description="Returns one professor by id. Returns 404 if it does not exist.",
    dependencies=[Depends(cualquier_usuario)],
    responses={**ERROR_401, **ERROR_404},
)
def obtener_docente(id_docente: int, service: DocenteService = Depends(get_docente_service)):
    return service.obtener(id_docente)


@router.post(
    "",
    response_model=DocenteOut,
    status_code=201,
    summary="Create a professor (ADMIN)",
    description="Creates a new professor. The name needs at least 3 characters.",
    dependencies=[Depends(solo_admin)],
    responses={**ERROR_401, **ERROR_403},
)
def crear_docente(datos: DocenteIn, service: DocenteService = Depends(get_docente_service)):
    return service.crear(datos.nombre, datos.foto_perfil)


@router.put(
    "/{id_docente}",
    response_model=DocenteOut,
    summary="Update a professor (ADMIN)",
    description="Updates the name and photo of a professor.",
    dependencies=[Depends(solo_admin)],
    responses={**ERROR_401, **ERROR_403, **ERROR_404},
)
def actualizar_docente(id_docente: int, datos: DocenteIn,
                       service: DocenteService = Depends(get_docente_service)):
    return service.actualizar(id_docente, datos.nombre, datos.foto_perfil)


@router.delete(
    "/{id_docente}",
    status_code=204,
    summary="Delete a professor (ADMIN)",
    description="Deletes a professor. If the professor already has evaluations "
    "it returns 409 so we don't lose them.",
    dependencies=[Depends(solo_admin)],
    responses={**ERROR_401, **ERROR_403, **ERROR_404, 409: {"description": "Has evaluations"}},
)
def eliminar_docente(id_docente: int, service: DocenteService = Depends(get_docente_service)):
    service.eliminar(id_docente)
