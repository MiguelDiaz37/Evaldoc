from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain import exceptions as ex

CODIGOS = {
    ex.DatoInvalido: 422,
    ex.TecnicaInvalida: 422,
    ex.DocenteNoEncontrado: 404,
    ex.DocenteConEvaluaciones: 409,
    ex.IALimiteAlcanzado: 429,
    ex.IAError: 502,
    ex.IANoConfigurada: 503,
    ex.FuenteNoDisponible: 503,
    ex.IATiempoAgotado: 504,
}


def registrar_manejadores(app: FastAPI):
    async def manejar(request: Request, error: ex.ErrorDominio):
        codigo = CODIGOS.get(type(error), 400)
        return JSONResponse(status_code=codigo, content={"detail": str(error)})

    app.add_exception_handler(ex.ErrorDominio, manejar)
