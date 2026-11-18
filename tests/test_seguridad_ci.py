"""Pruebas de regresion de los issues de seguridad que reporto SonarCloud en el pipeline.

Si alguien vuelve a escribir el workflow sin estas protecciones, las pruebas fallan.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WORKFLOWS = sorted((RAIZ / ".github" / "workflows").glob("*.yml"))
WORKFLOW = (RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
REQUIREMENTS = (RAIZ / "requirements.txt").read_text(encoding="utf-8")


def lineas_pip_install():
    return [linea for linea in WORKFLOW.splitlines() if "pip install" in linea]


def test_acciones_fijadas_con_sha_completo():
    # Issue High: "Use full commit SHA hash for this dependency"
    assert len(WORKFLOWS) >= 2
    for workflow in WORKFLOWS:
        acciones = re.findall(r"uses:\s*([^\s#]+)", workflow.read_text(encoding="utf-8"))
        assert acciones, workflow.name
        for accion in acciones:
            assert re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", accion), (workflow.name, accion)


def test_workflows_con_permisos_minimos_por_defecto():
    for workflow in WORKFLOWS:
        texto = workflow.read_text(encoding="utf-8")
        assert re.search(r"^permissions:\s*\n\s+contents:\s*read", texto, re.M), workflow.name


def test_dependabot_vigila_pip_y_github_actions():
    config = (RAIZ / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    assert "package-ecosystem: pip" in config
    assert "package-ecosystem: github-actions" in config


def test_pip_solo_instala_binarios():
    # Issue Medium: omitir --only-binary :all: permite ejecutar setup.py de terceros
    assert lineas_pip_install()
    for linea in lineas_pip_install():
        assert "--only-binary :all:" in linea


def test_pip_exige_versiones_bloqueadas_con_hash():
    # Issue Medium: usar dependencias sin bloquear las versiones resueltas
    for linea in lineas_pip_install():
        assert "--require-hashes" in linea
    paquetes = [l for l in REQUIREMENTS.splitlines() if re.match(r"^[A-Za-z0-9]", l)]
    assert paquetes
    for paquete in paquetes:
        assert "==" in paquete, paquete
    assert REQUIREMENTS.count("--hash=sha256:") >= len(paquetes)


def test_workflow_con_permisos_minimos():
    assert re.search(r"^permissions:\s*\n\s+contents:\s*read", WORKFLOW, re.M)
