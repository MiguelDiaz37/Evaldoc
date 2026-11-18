"""Pruebas de regresion de los issues de seguridad que reporto SonarCloud en el pipeline.

Si alguien vuelve a escribir el workflow sin estas protecciones, las pruebas fallan.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WORKFLOW = (RAIZ / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
REQUIREMENTS = (RAIZ / "requirements.txt").read_text(encoding="utf-8")


def lineas_pip_install():
    return [linea for linea in WORKFLOW.splitlines() if "pip install" in linea]


def test_acciones_fijadas_con_sha_completo():
    # Issue High: "Use full commit SHA hash for this dependency"
    acciones = re.findall(r"uses:\s*([^\s#]+)", WORKFLOW)
    assert acciones
    for accion in acciones:
        assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", accion), accion


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
