from sqlalchemy.orm import Session

from app.domain.evaluacion_docente.entities import Docente, Evaluacion
from app.domain.evaluacion_docente.ports import DocenteRepository
from app.infrastructure.db.models import DocenteORM


def a_entidad(fila: DocenteORM) -> Docente:
    evaluaciones = [
        Evaluacion(id_evaluacion=e.id_evaluacion, id_docente=e.id_docente,
                   puntaje=e.puntaje, comentario=e.comentario)
        for e in fila.evaluaciones
    ]
    return Docente(id_docente=fila.id_docente, nombre=fila.nombre,
                   foto_perfil=fila.foto_perfil, evaluaciones=evaluaciones)


class SqlAlchemyDocenteRepository(DocenteRepository):
    def __init__(self, db: Session):
        self.db = db

    def listar(self, nombre=None):
        query = self.db.query(DocenteORM)
        if nombre:
            query = query.filter(DocenteORM.nombre.ilike(f"%{nombre}%"))
        return [a_entidad(f) for f in query.order_by(DocenteORM.nombre).all()]

    def obtener(self, id_docente):
        fila = self.db.get(DocenteORM, id_docente)
        return a_entidad(fila) if fila else None

    def guardar(self, docente):
        if docente.id_docente is None:
            fila = DocenteORM()
            self.db.add(fila)
        else:
            fila = self.db.get(DocenteORM, docente.id_docente)
        fila.nombre = docente.nombre
        fila.foto_perfil = docente.foto_perfil
        self.db.commit()
        self.db.refresh(fila)
        return a_entidad(fila)

    def eliminar(self, id_docente):
        fila = self.db.get(DocenteORM, id_docente)
        if fila:
            self.db.delete(fila)
            self.db.commit()
