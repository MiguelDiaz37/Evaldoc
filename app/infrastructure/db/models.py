from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.infrastructure.db.database import Base


class DocenteORM(Base):
    __tablename__ = "docente"
    id_docente = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    foto_perfil = Column(String(300), nullable=True)

    evaluaciones = relationship("EvaluacionORM", back_populates="docente")


class EvaluacionORM(Base):
    __tablename__ = "evaluacion"
    id_evaluacion = Column(Integer, primary_key=True)
    id_docente = Column(Integer, ForeignKey("docente.id_docente"), nullable=False)
    puntaje = Column(Integer)
    comentario = Column(String(500))

    docente = relationship("DocenteORM", back_populates="evaluaciones")
