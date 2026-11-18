class ErrorDominio(Exception):
    pass


class DatoInvalido(ErrorDominio):
    pass


class DocenteNoEncontrado(ErrorDominio):
    pass


class DocenteConEvaluaciones(ErrorDominio):
    pass


class CredencialesInvalidas(ErrorDominio):
    pass


class TokenInvalido(ErrorDominio):
    pass


class AccesoDenegado(ErrorDominio):
    pass


class CorreoYaRegistrado(ErrorDominio):
    pass
