from pydantic import BaseModel, ConfigDict, Field


class DocenteIn(BaseModel):
    nombre: str = Field(min_length=3, max_length=150, examples=["Carlos Perez"])
    foto_perfil: str | None = None


class DocenteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_docente: int
    nombre: str
    foto_perfil: str | None = None
