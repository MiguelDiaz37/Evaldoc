import time

from app.domain.asistente_ia.ports import ModeloIA, RegistroLlamadas
from app.domain.evaluacion_docente.ports import DocenteRepository
from app.domain.exceptions import (
    DocenteNoEncontrado,
    IAError,
    IALimiteAlcanzado,
    IANoConfigurada,
    IATiempoAgotado,
    TecnicaInvalida,
)

TECNICAS = ["zero-shot", "few-shot", "cot"]

EJEMPLOS = """Comentario: "explica muy bien y responde dudas" -> Positivo
Comentario: "llega tarde y no devuelve notas" -> Negativo
Comentario: "normal, la clase es algo aburrida" -> Neutro
"""

ESTADOS_ERROR = {
    IANoConfigurada: "no_configurada",
    IALimiteAlcanzado: "limite",
    IATiempoAgotado: "timeout",
    IAError: "error",
}


class AsistenteIAService:
    def __init__(self, repo: DocenteRepository, modelo: ModeloIA, registro: RegistroLlamadas):
        self.repo = repo
        self.modelo = modelo
        self.registro = registro

    def armar_prompt(self, pregunta, tecnica, contexto):
        prompt = "Eres un asistente de EvalDoc, una pagina donde estudiantes evaluan docentes.\n"
        if contexto:
            prompt += "Responde SOLO con base en estos comentarios de estudiantes:\n" + contexto + "\n"

        if tecnica == "few-shot":
            prompt += "Ejemplos de como clasificar comentarios:\n" + EJEMPLOS
        elif tecnica == "cot":
            prompt += "Piensa paso a paso: primero analiza cada comentario y luego da la conclusion.\n"

        prompt += "Pregunta: " + pregunta
        return prompt

    def buscar_contexto(self, id_docente):
        docente = self.repo.obtener(id_docente)
        if docente is None:
            raise DocenteNoEncontrado("Professor not found")
        return "\n".join(f"- ({e.puntaje} estrellas) {e.comentario}" for e in docente.comentarios())

    def preguntar(self, pregunta, tecnica="zero-shot", id_docente=None):
        if tecnica not in TECNICAS:
            raise TecnicaInvalida("tecnica must be zero-shot, few-shot or cot")

        contexto = self.buscar_contexto(id_docente) if id_docente else ""
        prompt = self.armar_prompt(pregunta, tecnica, contexto)

        inicio = time.perf_counter()
        try:
            res = self.modelo.generar(prompt)
        except tuple(ESTADOS_ERROR) as e:
            tiempo = int((time.perf_counter() - inicio) * 1000)
            self.registro.registrar(pregunta, tecnica, "", 0, 0, tiempo, ESTADOS_ERROR[type(e)])
            raise
        tiempo = int((time.perf_counter() - inicio) * 1000)

        self.registro.registrar(pregunta, tecnica, res.texto, res.tokens_entrada,
                                res.tokens_salida, tiempo, "ok")
        return {
            "respuesta": res.texto,
            "tecnica": tecnica,
            "tokens_entrada": res.tokens_entrada,
            "tokens_salida": res.tokens_salida,
            "tiempo_ms": tiempo,
        }
