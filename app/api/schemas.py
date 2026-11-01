from pydantic import BaseModel, ConfigDict, Field


class DocenteIn(BaseModel):
    nombre: str = Field(min_length=3, max_length=150, examples=["Carlos Perez"])
    foto_perfil: str | None = None


class DocenteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_docente: int
    nombre: str
    foto_perfil: str | None = None


class PreguntaIA(BaseModel):
    pregunta: str = Field(min_length=3, examples=["Is this professor good at explaining?"])
    tecnica: str = Field(default="zero-shot", examples=["zero-shot"])
    id_docente: int | None = Field(default=None, examples=[1])


class RespuestaIA(BaseModel):
    respuesta: str
    tecnica: str
    tokens_entrada: int
    tokens_salida: int
    tiempo_ms: int


class EstadoCircuitoOut(BaseModel):
    fuente: str
    dataset: str
    url: str
    nombre: str
    estado: str
    fallos_seguidos: int
    umbral_fallos: int
    tiempo_recuperacion_s: float
    historial: list[dict]


class ReporteOut(BaseModel):
    origen: dict
    resumen: dict
    por_departamento: list[dict]
    por_caracter: list[dict]
    cobertura_municipal: list[dict]
