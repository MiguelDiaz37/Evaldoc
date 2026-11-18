from datetime import datetime, timedelta, timezone

import jwt

from app.domain.autenticacion.ports import EmisorTokens
from app.domain.exceptions import TokenInvalido

ALGORITMO = "HS256"
LARGO_MINIMO_CLAVE = 32


class JwtTokens(EmisorTokens):
    def __init__(self, clave, minutos=30, emisor="evaldoc", reloj=None):
        if not clave or len(clave) < LARGO_MINIMO_CLAVE:
            raise ValueError(f"JWT_SECRET must have at least {LARGO_MINIMO_CLAVE} characters")
        self.clave = clave
        self.minutos = minutos
        self.emisor = emisor
        self.reloj = reloj or (lambda: datetime.now(timezone.utc))

    def emitir(self, usuario):
        ahora = self.reloj()
        claims = {
            "sub": usuario.correo,
            "rol": usuario.rol.value,
            "iss": self.emisor,
            "iat": ahora,
            "exp": ahora + timedelta(minutes=self.minutos),
        }
        return jwt.encode(claims, self.clave, algorithm=ALGORITMO)

    def leer(self, token):
        try:
            return jwt.decode(
                token, self.clave, algorithms=[ALGORITMO], issuer=self.emisor,
                options={"require": ["exp", "iat", "sub", "iss"]},
            )
        except jwt.ExpiredSignatureError:
            raise TokenInvalido("Token expired") from None
        except jwt.InvalidTokenError:
            raise TokenInvalido("Invalid token") from None
