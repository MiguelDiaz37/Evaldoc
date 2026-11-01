from dataclasses import dataclass, field

from app.domain.exceptions import DatoInvalido


@dataclass
class Evaluacion:
    puntaje: int
    comentario: str | None = None
    id_docente: int | None = None
    id_evaluacion: int | None = None

    def __post_init__(self):
        if self.puntaje is not None and not 1 <= self.puntaje <= 5:
            raise DatoInvalido("puntaje must be between 1 and 5")


@dataclass
class Docente:
    nombre: str
    foto_perfil: str | None = None
    id_docente: int | None = None
    evaluaciones: list[Evaluacion] = field(default_factory=list)

    def __post_init__(self):
        if not self.nombre or len(self.nombre.strip()) < 3:
            raise DatoInvalido("nombre must have at least 3 characters")

    def puede_eliminarse(self):
        return len(self.evaluaciones) == 0

    def comentarios(self, limite=10):
        con_texto = [e for e in self.evaluaciones if e.comentario]
        return con_texto[:limite]
