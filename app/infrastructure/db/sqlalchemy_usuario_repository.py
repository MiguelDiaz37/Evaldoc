from sqlalchemy.orm import Session

from app.domain.autenticacion.entities import Usuario
from app.domain.autenticacion.ports import UsuarioRepository
from app.infrastructure.db.models import UsuarioORM


def a_entidad(fila: UsuarioORM) -> Usuario:
    return Usuario(id_usuario=fila.id_usuario, correo=fila.correo,
                   hash_contrasena=fila.hash_contrasena, rol=fila.rol)


class SqlAlchemyUsuarioRepository(UsuarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_correo(self, correo):
        fila = self.db.query(UsuarioORM).filter(UsuarioORM.correo == correo).first()
        return a_entidad(fila) if fila else None

    def guardar(self, usuario):
        fila = UsuarioORM(correo=usuario.correo, hash_contrasena=usuario.hash_contrasena,
                          rol=usuario.rol.value)
        self.db.add(fila)
        self.db.commit()
        self.db.refresh(fila)
        return a_entidad(fila)
