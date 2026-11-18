import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./evaldoc.db")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_MINUTOS = int(os.getenv("JWT_MINUTOS", "30"))
BCRYPT_RONDAS = int(os.getenv("BCRYPT_RONDAS", "12"))

# En produccion: DOCS_ACTIVOS=false para no publicar Swagger
DOCS_ACTIVOS = os.getenv("DOCS_ACTIVOS", "true").lower() == "true"
CORS_ORIGENES = [o.strip() for o in os.getenv("CORS_ORIGENES", "").split(",") if o.strip()]
LOGIN_MAX_INTENTOS = int(os.getenv("LOGIN_MAX_INTENTOS", "5"))
LOGIN_VENTANA_S = int(os.getenv("LOGIN_VENTANA_S", "60"))
