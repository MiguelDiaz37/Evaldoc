class ErrorDominio(Exception):
    pass


class DatoInvalido(ErrorDominio):
    pass


class DocenteNoEncontrado(ErrorDominio):
    pass


class DocenteConEvaluaciones(ErrorDominio):
    pass
