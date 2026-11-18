from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain import exceptions as ex

CODIGOS = {
    ex.DatoInvalido: 422,
    ex.DocenteNoEncontrado: 404,
    ex.DocenteConEvaluaciones: 409,
    ex.CorreoYaRegistrado: 409,
    ex.CredencialesInvalidas: 401,
    ex.TokenInvalido: 401,
    ex.AccesoDenegado: 403,
}


def registrar_manejadores(app: FastAPI):
    async def manejar(request: Request, error: ex.ErrorDominio):
        codigo = CODIGOS.get(type(error), 400)
        cabeceras = {"WWW-Authenticate": "Bearer"} if codigo == 401 else None
        return JSONResponse(status_code=codigo, content={"detail": str(error)},
                            headers=cabeceras)

    app.add_exception_handler(ex.ErrorDominio, manejar)
