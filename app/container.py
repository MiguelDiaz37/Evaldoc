from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from app import config
from app.application.auth_service import AuthService
from app.application.docente_service import DocenteService
from app.infrastructure.db.database import get_db
from app.infrastructure.db.sqlalchemy_docente_repository import SqlAlchemyDocenteRepository
from app.infrastructure.db.sqlalchemy_usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.seguridad.bcrypt_hasher import BcryptHasher
from app.infrastructure.seguridad.jwt_tokens import JwtTokens


def get_docente_repository(db: Session = Depends(get_db)):
    return SqlAlchemyDocenteRepository(db)


def get_docente_service(repo=Depends(get_docente_repository)):
    return DocenteService(repo)


@lru_cache
def get_hasher():
    return BcryptHasher(config.BCRYPT_RONDAS)


@lru_cache
def get_tokens():
    return JwtTokens(config.JWT_SECRET, config.JWT_MINUTOS)


def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(SqlAlchemyUsuarioRepository(db), get_hasher(), get_tokens())
