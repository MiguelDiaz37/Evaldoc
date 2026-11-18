"""Revisa el mutation score que deja mutmut y falla si queda por debajo del umbral.

Uso: python -m scripts.verificar_mutacion [umbral]

La ruta del archivo de resultados es fija y no se recibe por linea de comandos, para que
nadie pueda hacer que el script lea otro archivo del sistema (path traversal, CWE-22).
"""
import json
import sys
from pathlib import Path

RUTA_STATS = Path("mutants") / "mutmut-cicd-stats.json"
UMBRAL = 50.0


def calcular_score(stats):
    if stats["total"] == 0:
        raise ValueError("mutmut no genero mutantes")
    return round(stats["killed"] * 100 / stats["total"], 1)


def leer_umbral(args):
    if not args:
        return UMBRAL
    umbral = float(args[0])
    if not 0 <= umbral <= 100:
        raise ValueError("el umbral debe estar entre 0 y 100")
    return umbral


def main(umbral=UMBRAL, ruta=RUTA_STATS):
    with open(ruta, encoding="utf-8") as archivo:
        stats = json.load(archivo)
    score = calcular_score(stats)
    print(f"Mutation score: {score}% ({stats['killed']}/{stats['total']} muertos, "
          f"{stats['survived']} sobrevivientes, {stats['no_tests']} sin pruebas)")
    if score < umbral:
        print(f"ERROR: el score esta por debajo del minimo de {umbral}%")
        return 1
    print(f"OK: el score cumple el minimo de {umbral}%")
    return 0


if __name__ == "__main__":
    sys.exit(main(leer_umbral(sys.argv[1:])))
