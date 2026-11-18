from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.docente_service import DocenteService
from app.infrastructure.db.database import get_db
from app.infrastructure.db.sqlalchemy_docente_repository import SqlAlchemyDocenteRepository


def get_docente_repository(db: Session = Depends(get_db)):
    return SqlAlchemyDocenteRepository(db)


def get_docente_service(repo=Depends(get_docente_repository)):
    return DocenteService(repo)
