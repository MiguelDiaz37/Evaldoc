from fastapi import APIRouter, Depends

from app.api.schemas import PreguntaIA, RespuestaIA
from app.application.asistente_ia_service import AsistenteIAService
from app.container import get_asistente_service

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])


@router.post(
    "",
    response_model=RespuestaIA,
    summary="Ask the AI assistant",
    description="Sends a question to Gemini. `tecnica` can be `zero-shot`, `few-shot` or `cot`. "
    "If you send `id_docente`, the comments of that professor are added to the prompt (basic RAG). "
    "Returns 429 if the rate limit is reached and 504 if Gemini takes too long.",
    responses={
        404: {"description": "Professor not found"},
        429: {"description": "Rate limit reached, try again later"},
        502: {"description": "Error from Gemini"},
        503: {"description": "API key not configured"},
        504: {"description": "Gemini timeout"},
    },
)
def preguntar(datos: PreguntaIA, service: AsistenteIAService = Depends(get_asistente_service)):
    return service.preguntar(datos.pregunta, datos.tecnica, datos.id_docente)
