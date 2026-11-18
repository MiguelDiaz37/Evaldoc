import secrets

from app.domain.autenticacion.entities import (
    Rol,
    Usuario,
    normalizar_correo,
    validar_contrasena,
)
from app.domain.autenticacion.ports import EmisorTokens, HasherContrasenas, UsuarioRepository
from app.domain.exceptions import (
    AccesoDenegado,
    CorreoYaRegistrado,
    CredencialesInvalidas,
    DatoInvalido,
    TokenInvalido,
)

MENSAJE_CREDENCIALES = "Invalid email or password"


class AuthService:
    def __init__(self, repo: UsuarioRepository, hasher: HasherContrasenas, tokens: EmisorTokens):
        self.repo = repo
        self.hasher = hasher
        self.tokens = tokens
        # Hash de relleno para gastar el mismo tiempo cuando el correo no existe
        self._hash_relleno = None

    def registrar(self, correo, contrasena, rol=Rol.USER):
        correo = normalizar_correo(correo)
        validar_contrasena(contrasena)
        if self.repo.obtener_por_correo(correo) is not None:
            raise CorreoYaRegistrado("Email already registered")
        usuario = Usuario(correo=correo, hash_contrasena=self.hasher.hashear(contrasena), rol=rol)
        return self.repo.guardar(usuario)

    def login(self, correo, contrasena):
        try:
            correo = normalizar_correo(correo)
        except DatoInvalido:
            raise CredencialesInvalidas(MENSAJE_CREDENCIALES) from None

        usuario = self.repo.obtener_por_correo(correo)
        if usuario is None:
            # Se verifica contra un hash falso para que la respuesta tarde lo mismo
            # y no se pueda saber que correos estan registrados.
            self.hasher.verificar(contrasena or "", self._relleno())
            raise CredencialesInvalidas(MENSAJE_CREDENCIALES)
        if not self.hasher.verificar(contrasena or "", usuario.hash_contrasena):
            raise CredencialesInvalidas(MENSAJE_CREDENCIALES)
        return self.tokens.emitir(usuario)

    def usuario_desde_token(self, token):
        claims = self.tokens.leer(token)
        usuario = self.repo.obtener_por_correo(claims.get("sub", ""))
        if usuario is None or usuario.rol.value != claims.get("rol"):
            raise TokenInvalido("Invalid token")
        return usuario

    @staticmethod
    def exigir_rol(usuario, *roles):
        if not usuario.tiene_rol(*roles):
            raise AccesoDenegado("You don't have permission for this action")
        return usuario

    def _relleno(self):
        if self._hash_relleno is None:
            self._hash_relleno = self.hasher.hashear(secrets.token_urlsafe(16))
        return self._hash_relleno
