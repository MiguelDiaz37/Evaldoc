import ast
from pathlib import Path

APP = Path(__file__).resolve().parent.parent / "app"
LIBRERIAS = ("fastapi", "sqlalchemy", "google", "httpx", "duckdb", "jinja2")


def imports_de(capa):
    nombres = set()
    for archivo in (APP / capa).rglob("*.py"):
        for nodo in ast.walk(ast.parse(archivo.read_text(encoding="utf-8"))):
            if isinstance(nodo, ast.Import):
                nombres.update(a.name for a in nodo.names)
            elif isinstance(nodo, ast.ImportFrom) and nodo.module:
                nombres.add(nodo.module)
    return nombres


def test_dominio_no_depende_de_otras_capas_ni_librerias():
    prohibidos = ("app.application", "app.api", "app.infrastructure", "app.container") + LIBRERIAS
    assert [i for i in imports_de("domain") if i.startswith(prohibidos)] == []


def test_application_solo_depende_del_dominio():
    prohibidos = ("app.api", "app.infrastructure", "app.container") + LIBRERIAS
    assert [i for i in imports_de("application") if i.startswith(prohibidos)] == []


def test_infraestructura_no_depende_de_api():
    assert [i for i in imports_de("infrastructure") if i.startswith("app.api")] == []


def test_bounded_contexts_del_dominio():
    contextos = {p.name for p in (APP / "domain").iterdir() if p.is_dir() and p.name != "__pycache__"}
    assert contextos == {"evaluacion_docente", "asistente_ia", "datos_institucionales"}
