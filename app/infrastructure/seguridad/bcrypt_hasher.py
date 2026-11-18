import bcrypt

from app.domain.autenticacion.ports import HasherContrasenas


class BcryptHasher(HasherContrasenas):
    def __init__(self, rondas=12):
        self.rondas = rondas

    def hashear(self, contrasena):
        return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt(self.rondas)).decode()

    def verificar(self, contrasena, hash_guardado):
        try:
            return bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8"))
        except ValueError:
            return False
