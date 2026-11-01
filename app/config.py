import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./evaldoc.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_TIMEOUT_MS = 20000
RUTA_LOG_IA = "llamadas_ia.csv"

DATOS_ABIERTOS_URL = os.getenv("DATOS_ABIERTOS_URL", "https://www.datos.gov.co")
DATASET_INSTITUCIONES = "n5yy-8nav"
DATASET_MUNICIPIOS = "gdxc-w37w"
CARPETA_CACHE = os.getenv("CARPETA_CACHE", "data/cache")
HTTP_TIMEOUT_S = float(os.getenv("HTTP_TIMEOUT_S", "10"))
REINTENTOS = int(os.getenv("REINTENTOS", "3"))
ESPERA_BASE_S = float(os.getenv("ESPERA_BASE_S", "0.5"))
UMBRAL_FALLOS = int(os.getenv("UMBRAL_FALLOS", "3"))
TIEMPO_RECUPERACION_S = float(os.getenv("TIEMPO_RECUPERACION_S", "30"))
