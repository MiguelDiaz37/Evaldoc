"""Revisa el mutation score que deja mutmut y falla si queda por debajo del umbral.

Uso: python -m scripts.verificar_mutacion [ruta_stats] [umbral]
"""
import json
import sys

RUTA_STATS = "mutants/mutmut-cicd-stats.json"
UMBRAL = 50.0


def calcular_score(stats):
    if stats["total"] == 0:
        raise ValueError("mutmut no genero mutantes")
    return round(stats["killed"] * 100 / stats["total"], 1)


def main(ruta=RUTA_STATS, umbral=UMBRAL):
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
    args = sys.argv[1:]
    ruta = args[0] if args else RUTA_STATS
    umbral = float(args[1]) if len(args) > 1 else UMBRAL
    sys.exit(main(ruta, umbral))
