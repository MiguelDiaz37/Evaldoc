import secrets
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.domain.autenticacion.entities import Rol, Usuario
from app.domain.exceptions import DatoInvalido, TokenInvalido
from app.infrastructure.seguridad.bcrypt_hasher import BcryptHasher
from app.infrastructure.seguridad.jwt_tokens import JwtTokens

CLAVE = secrets.token_urlsafe(48)
USUARIO = Usuario(correo="laura@academia.umb.edu.co", hash_contrasena="x", rol=Rol.ADMIN)


def test_bcrypt_hashea_y_verifica():
    hasher = BcryptHasher(rondas=4)
    hash_guardado = hasher.hashear("clave1234")
    assert hash_guardado.startswith("$2b$04$")
    assert "clave1234" not in hash_guardado
    assert hasher.verificar("clave1234", hash_guardado)
    assert not hasher.verificar("otraClave", hash_guardado)
    assert not hasher.verificar("clave1234", "no-es-un-hash")


def test_token_lleva_correo_rol_y_vencimiento():
    ahora = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)
    tokens = JwtTokens(CLAVE, minutos=30, reloj=lambda: ahora)
    claims = jwt.decode(tokens.emitir(USUARIO), CLAVE, algorithms=["HS256"],
                        options={"verify_exp": False}, issuer="evaldoc")
    assert claims["sub"] == "laura@academia.umb.edu.co"
    assert claims["rol"] == "ADMIN"
    assert claims["exp"] - claims["iat"] == 30 * 60


def test_token_vencido():
    hace_una_hora = datetime.now(timezone.utc) - timedelta(hours=1)
    tokens = JwtTokens(CLAVE, minutos=30, reloj=lambda: hace_una_hora)
    with pytest.raises(TokenInvalido, match="^Token expired$"):
        tokens.leer(tokens.emitir(USUARIO))


def test_token_firmado_con_otra_clave_o_alterado():
    tokens = JwtTokens(CLAVE)
    otro = JwtTokens(secrets.token_urlsafe(48)).emitir(USUARIO)
    with pytest.raises(TokenInvalido, match="^Invalid token$"):
        tokens.leer(otro)
    cabecera, cuerpo, firma = tokens.emitir(USUARIO).split(".")
    with pytest.raises(TokenInvalido):
        tokens.leer(f"{cabecera}.{cuerpo}x.{firma}")


def test_token_con_algoritmo_none_es_rechazado():
    sin_firma = jwt.encode({"sub": USUARIO.correo, "rol": "ADMIN", "iss": "evaldoc"},
                           key=None, algorithm="none")
    with pytest.raises(TokenInvalido):
        JwtTokens(CLAVE).leer(sin_firma)


def test_clave_corta_no_se_acepta():
    with pytest.raises(ValueError):
        JwtTokens("corta")


@pytest.mark.parametrize("correo", ["a@gmail.com", "a@academia.umb.edu.co.evil.com", ""])
def test_usuario_solo_con_correo_institucional(correo):
    with pytest.raises(DatoInvalido):
        Usuario(correo=correo, hash_contrasena="x")


@pytest.mark.parametrize("falta", ["exp", "iat", "sub", "iss"])
def test_token_sin_un_claim_obligatorio_es_rechazado(falta):
    # Sin "exp" un token valdria para siempre; sin "iss" se aceptaria uno de otro sistema.
    ahora = datetime.now(timezone.utc)
    claims = {"sub": USUARIO.correo, "rol": "ADMIN", "iss": "evaldoc",
              "iat": ahora, "exp": ahora + timedelta(minutes=5)}
    del claims[falta]
    with pytest.raises(TokenInvalido):
        JwtTokens(CLAVE).leer(jwt.encode(claims, CLAVE, algorithm="HS256"))


def test_token_de_otro_emisor_es_rechazado():
    otro_sistema = JwtTokens(CLAVE, emisor="otra-app").emitir(USUARIO)
    with pytest.raises(TokenInvalido):
        JwtTokens(CLAVE).leer(otro_sistema)


def test_token_usa_hs256():
    assert jwt.get_unverified_header(JwtTokens(CLAVE).emitir(USUARIO))["alg"] == "HS256"


def test_clave_de_32_caracteres_es_el_minimo():
    JwtTokens("x" * 32)
    with pytest.raises(ValueError):
        JwtTokens("x" * 31)
