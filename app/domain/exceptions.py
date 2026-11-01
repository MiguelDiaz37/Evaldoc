class ErrorDominio(Exception):
    pass


class DatoInvalido(ErrorDominio):
    pass


class DocenteNoEncontrado(ErrorDominio):
    pass


class DocenteConEvaluaciones(ErrorDominio):
    pass


class TecnicaInvalida(ErrorDominio):
    pass


class IANoConfigurada(ErrorDominio):
    pass


class IALimiteAlcanzado(ErrorDominio):
    pass


class IATiempoAgotado(ErrorDominio):
    pass


class IAError(ErrorDominio):
    pass


class FuenteNoDisponible(ErrorDominio):
    pass
