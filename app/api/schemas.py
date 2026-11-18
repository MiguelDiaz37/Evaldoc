from pydantic import BaseModel, ConfigDict, Field


class DocenteIn(BaseModel):
    nombre: str = Field(min_length=3, max_length=150, examples=["Carlos Perez"])
    foto_perfil: str | None = None


class DocenteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_docente: int
    nombre: str
    foto_perfil: str | None = None


class LoginIn(BaseModel):
    correo: str = Field(max_length=150, examples=["estudiante@academia.umb.edu.co"])
    contrasena: str = Field(max_length=72, examples=["unaClaveSegura123"])


class RegistroIn(LoginIn):
    model_config = ConfigDict(extra="forbid")


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_usuario: int
    correo: str
    rol: str
