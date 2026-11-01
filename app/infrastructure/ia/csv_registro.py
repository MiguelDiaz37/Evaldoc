import csv
import os
from datetime import datetime

from app.domain.asistente_ia.ports import RegistroLlamadas


class CsvRegistroLlamadas(RegistroLlamadas):
    def __init__(self, ruta="llamadas_ia.csv"):
        self.ruta = ruta

    def registrar(self, pregunta, tecnica, respuesta, tokens_entrada, tokens_salida,
                  tiempo_ms, estado):
        nuevo = not os.path.exists(self.ruta)
        with open(self.ruta, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if nuevo:
                w.writerow(["fecha", "tecnica", "pregunta", "respuesta", "tokens_entrada",
                            "tokens_salida", "tiempo_ms", "estado"])
            w.writerow([datetime.now().isoformat(timespec="seconds"), tecnica, pregunta,
                        respuesta, tokens_entrada, tokens_salida, tiempo_ms, estado])
