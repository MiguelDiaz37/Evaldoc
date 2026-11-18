from unittest.mock import Mock

import pytest

from app.application.auth_service import MENSAJE_CREDENCIALES, AuthService
from app.domain.autenticacion.entities import Rol, Usuario
from app.domain.autenticacion.ports import EmisorTokens, HasherContrasenas, UsuarioRepository
from app.domain.exceptions import (
    AccesoDenegado,
    CorreoYaRegistrado,
    CredencialesInvalidas,
    DatoInvalido,
    TokenInvalido,
)

CORREO = "laura@academia.umb.edu.co"


@pytest.fixture
def piezas():
    repo = Mock(spec=UsuarioRepository)
    hasher = Mock(spec=HasherContrasenas)
    tokens = Mock(spec=EmisorTokens)
    hasher.hashear.side_effect = lambda c: "hash-de-" + c
    hasher.verificar.side_effect = lambda c, h: h == "hash-de-" + c
    repo.guardar.side_effect = lambda u: u
    tokens.emitir.return_value = "token"
    return repo, hasher, tokens


def usuario(rol=Rol.USER):
    return Usuario(correo=CORREO, hash_contrasena="hash-de-clave1234", rol=rol)


def test_registrar_guarda_el_hash_y_no_la_contrasena(piezas):
    repo, hasher, tokens = piezas
    repo.obtener_por_correo.return_value = None
    creado = AuthService(repo, hasher, tokens).registrar(" Laura@Academia.umb.edu.co ", "clave1234")
    assert creado.correo == CORREO
    assert creado.hash_contrasena == "hash-de-clave1234"
    assert creado.rol == Rol.USER


def test_registrar_correo_repetido(piezas):
    repo, hasher, tokens = piezas
    repo.obtener_por_correo.return_value = usuario()
    with pytest.raises(CorreoYaRegistrado, match="^Email already registered$"):
        AuthService(repo, hasher, tokens).registrar(CORREO, "clave1234")
    repo.guardar.assert_not_called()


@pytest.mark.parametrize("contrasena", ["corta", "x" * 73])
def test_registrar_valida_el_largo_de_la_contrasena(piezas, contrasena):
    repo, hasher, tokens = piezas
    with pytest.raises(DatoInvalido):
        AuthService(repo, hasher, tokens).registrar(CORREO, contrasena)


def test_login_correcto_emite_token(piezas):
    repo, hasher, tokens = piezas
    repo.obtener_por_correo.return_value = usuario()
    assert AuthService(repo, hasher, tokens).login(CORREO, "clave1234") == "token"
    tokens.emitir.assert_called_once_with(repo.obtener_por_correo.return_value)


@pytest.mark.parametrize("correo,contrasena", [
    (CORREO, "otraClave"),
    ("nadie@academia.umb.edu.co", "clave1234"),
    ("no-es-correo", "clave1234"),
])
def test_login_fallido_da_el_mismo_mensaje(piezas, correo, contrasena):
    repo, hasher, tokens = piezas
    repo.obtener_por_correo.side_effect = lambda c: usuario() if c == CORREO else None
    with pytest.raises(CredencialesInvalidas, match=f"^{MENSAJE_CREDENCIALES}$"):
        AuthService(repo, hasher, tokens).login(correo, contrasena)
    tokens.emitir.assert_not_called()


def test_login_con_correo_inexistente_igual_verifica_un_hash(piezas):
    repo, hasher, tokens = piezas
    repo.obtener_por_correo.return_value = None
    with pytest.raises(CredencialesInvalidas):
        AuthService(repo, hasher, tokens).login("nadie@academia.umb.edu.co", "clave1234")
    hasher.verificar.assert_called_once()


def test_usuario_desde_token(piezas):
    repo, hasher, tokens = piezas
    repo.obtener_por_correo.return_value = usuario(Rol.ADMIN)
    tokens.leer.return_value = {"sub": CORREO, "rol": "ADMIN"}
    assert AuthService(repo, hasher, tokens).usuario_desde_token("t").rol == Rol.ADMIN


@pytest.mark.parametrize("claims,existe", [
    ({"sub": CORREO, "rol": "ADMIN"}, True),   # el token dice ADMIN pero la BD dice USER
    ({"sub": CORREO, "rol": "USER"}, False),   # el usuario ya no existe
])
def test_token_que_no_coincide_con_la_bd(piezas, claims, existe):
    repo, hasher, tokens = piezas
    repo.obtener_por_correo.return_value = usuario() if existe else None
    tokens.leer.return_value = claims
    with pytest.raises(TokenInvalido):
        AuthService(repo, hasher, tokens).usuario_desde_token("t")


def test_exigir_rol():
    assert AuthService.exigir_rol(usuario(Rol.ADMIN), Rol.ADMIN).rol == Rol.ADMIN
    with pytest.raises(AccesoDenegado, match="^You don't have permission for this action$"):
        AuthService.exigir_rol(usuario(Rol.USER), Rol.ADMIN)


@pytest.mark.parametrize("contrasena", ["x" * 8, "x" * 72])
def test_contrasenas_en_el_limite_son_validas(piezas, contrasena):
    repo, hasher, tokens = piezas
    repo.obtener_por_correo.return_value = None
    assert AuthService(repo, hasher, tokens).registrar(CORREO, contrasena).correo == CORREO


def test_contrasena_de_7_bytes_no_es_valida(piezas):
    repo, hasher, tokens = piezas
    with pytest.raises(DatoInvalido):
        AuthService(repo, hasher, tokens).registrar(CORREO, "x" * 7)
