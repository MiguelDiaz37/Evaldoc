from fastapi import APIRouter, Depends

from app.api.schemas import LoginIn, RegistroIn, TokenOut, UsuarioOut
from app.api.seguridad import cualquier_usuario, solo_admin
from app.application.auth_service import AuthService
from app.container import get_auth_service

router = APIRouter(prefix="/api/v1", tags=["Authentication"])

ERROR_401 = {401: {"description": "Missing, invalid or expired token"}}
ERROR_403 = {403: {"description": "The user role is not allowed"}}


@router.post(
    "/auth/registro",
    response_model=UsuarioOut,
    status_code=201,
    summary="Register a student",
    description="Creates a USER account. Only @academia.umb.edu.co emails are accepted. "
    "The role can't be chosen here, ADMIN accounts are created with scripts/crear_usuario.py.",
    responses={409: {"description": "Email already registered"}},
)
def registrar(datos: RegistroIn, auth: AuthService = Depends(get_auth_service)):
    return auth.registrar(datos.correo, datos.contrasena)


@router.post(
    "/auth/login",
    response_model=TokenOut,
    summary="Log in",
    description="Checks email and password and returns a JWT (HS256) that expires in 30 minutes.",
    responses={401: {"description": "Invalid email or password"}},
)
def login(datos: LoginIn, auth: AuthService = Depends(get_auth_service)):
    return {"access_token": auth.login(datos.correo, datos.contrasena), "token_type": "bearer"}


@router.get(
    "/usuarios/me",
    response_model=UsuarioOut,
    summary="Current user (USER or ADMIN)",
    description="Returns the user of the token. Any authenticated role can call it.",
    responses=ERROR_401,
)
def mi_usuario(usuario=Depends(cualquier_usuario)):
    return usuario


@router.get(
    "/admin/panel",
    summary="Admin panel (ADMIN only)",
    description="Test endpoint for role based access. Returns 403 for USER accounts.",
    responses={**ERROR_401, **ERROR_403},
)
def panel_admin(usuario=Depends(solo_admin)):
    return {"mensaje": "Welcome to the admin panel", "admin": usuario.correo}
