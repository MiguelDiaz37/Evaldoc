import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./evaldoc.db")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_MINUTOS = int(os.getenv("JWT_MINUTOS", "30"))
BCRYPT_RONDAS = int(os.getenv("BCRYPT_RONDAS", "12"))
