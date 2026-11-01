from app.domain.evaluacion_docente.entities import Docente
from app.domain.evaluacion_docente.ports import DocenteRepository
from app.domain.exceptions import DocenteConEvaluaciones, DocenteNoEncontrado


class DocenteService:
    def __init__(self, repo: DocenteRepository):
        self.repo = repo

    def listar(self, nombre=None):
        return self.repo.listar(nombre)

    def obtener(self, id_docente):
        docente = self.repo.obtener(id_docente)
        if docente is None:
            raise DocenteNoEncontrado("Professor not found")
        return docente

    def crear(self, nombre, foto_perfil=None):
        return self.repo.guardar(Docente(nombre=nombre, foto_perfil=foto_perfil))

    def actualizar(self, id_docente, nombre, foto_perfil=None):
        docente = self.obtener(id_docente)
        docente.nombre = nombre
        docente.foto_perfil = foto_perfil
        return self.repo.guardar(docente)

    def eliminar(self, id_docente):
        docente = self.obtener(id_docente)
        if not docente.puede_eliminarse():
            raise DocenteConEvaluaciones("Professor has evaluations, can't delete")
        self.repo.eliminar(id_docente)
