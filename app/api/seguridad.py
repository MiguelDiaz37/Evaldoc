from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.auth_service import AuthService
from app.container import get_auth_service
from app.domain.autenticacion.entities import Rol
from app.domain.exceptions import TokenInvalido

bearer = HTTPBearer(auto_error=False, description="JWT returned by POST /api/v1/auth/login")


def usuario_actual(credenciales: HTTPAuthorizationCredentials | None = Depends(bearer),
                   auth: AuthService = Depends(get_auth_service)):
    if credenciales is None or credenciales.scheme.lower() != "bearer":
        raise TokenInvalido("Not authenticated")
    return auth.usuario_desde_token(credenciales.credentials)


def requiere_rol(*roles: Rol):
    def verificar(usuario=Depends(usuario_actual)):
        return AuthService.exigir_rol(usuario, *roles)

    return verificar


solo_admin = requiere_rol(Rol.ADMIN)
cualquier_usuario = requiere_rol(Rol.ADMIN, Rol.USER)
