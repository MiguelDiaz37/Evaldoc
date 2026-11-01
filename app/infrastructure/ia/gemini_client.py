import httpx
from google import genai
from google.genai import errors, types

from app.domain.asistente_ia.ports import ModeloIA, RespuestaModelo
from app.domain.exceptions import IAError, IALimiteAlcanzado, IANoConfigurada, IATiempoAgotado


class GeminiClient(ModeloIA):
    def __init__(self, api_key, modelo, timeout_ms=20000):
        self.api_key = api_key
        self.modelo = modelo
        self.timeout_ms = timeout_ms

    def generar(self, prompt):
        if not self.api_key:
            raise IANoConfigurada("GEMINI_API_KEY is not configured")

        client = genai.Client(api_key=self.api_key,
                              http_options=types.HttpOptions(timeout=self.timeout_ms))
        try:
            res = client.models.generate_content(model=self.modelo, contents=prompt)
        except httpx.TimeoutException:
            raise IATiempoAgotado("Gemini took too long to answer")
        except errors.APIError as e:
            if e.code == 429:
                raise IALimiteAlcanzado("Rate limit reached, try again later")
            raise IAError("Error from Gemini: " + str(e.message))

        entrada = 0
        salida = 0
        if res.usage_metadata:
            entrada = res.usage_metadata.prompt_token_count or 0
            salida = (res.usage_metadata.candidates_token_count or 0) + (
                res.usage_metadata.thoughts_token_count or 0
            )
        return RespuestaModelo(texto=res.text or "", tokens_entrada=entrada, tokens_salida=salida)
