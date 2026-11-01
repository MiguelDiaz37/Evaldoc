import json
import tempfile
from dataclasses import asdict
from pathlib import Path

import duckdb

from app.domain.datos_institucionales.entities import ReporteEstadistico
from app.domain.datos_institucionales.ports import AnalizadorDatos

MACRO_CLAVE = (
    "CREATE MACRO clave(t) AS "
    "trim(regexp_replace(upper(strip_accents(t)), '[^A-Z]+', ' ', 'g'))"
)

ALIAS_MUNICIPIOS = [("CALI", "SANTIAGO DE CALI")]

SQL_POR_DEPARTAMENTO = """
SELECT departamento,
       COUNT(*) AS total,
       COUNT(*) FILTER (WHERE sector = 'Oficial') AS oficiales,
       COUNT(*) FILTER (WHERE sector = 'Privado') AS privadas,
       COUNT(*) FILTER (WHERE acreditada) AS acreditadas,
       ROUND(100.0 * COUNT(*) FILTER (WHERE acreditada) / COUNT(*), 1) AS pct_acreditadas
FROM ies
GROUP BY departamento
ORDER BY total DESC, departamento
"""

SQL_POR_CARACTER = """
SELECT caracter,
       COUNT(*) AS total,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS porcentaje,
       COUNT(*) FILTER (WHERE acreditada) AS acreditadas,
       ROUND(100.0 * COUNT(*) FILTER (WHERE acreditada) / COUNT(*), 1) AS pct_acreditadas
FROM ies
GROUP BY caracter
ORDER BY total DESC
"""

SQL_COBERTURA = """
WITH mpios AS (
    SELECT departamento, clave(departamento) AS k_dpto, clave(nombre) AS k_mpio
    FROM municipios
),
mpios_con_ies AS (
    SELECT DISTINCT clave(i.departamento) AS k_dpto,
           COALESCE(a.destino, clave(i.municipio)) AS k_mpio
    FROM ies i LEFT JOIN alias_municipio a ON a.origen = clave(i.municipio)
)
SELECT m.departamento,
       COUNT(*) AS municipios,
       COUNT(c.k_mpio) AS municipios_con_ies,
       ROUND(100.0 * COUNT(c.k_mpio) / COUNT(*), 1) AS pct_cobertura
FROM mpios m
LEFT JOIN mpios_con_ies c ON c.k_dpto = m.k_dpto AND c.k_mpio = m.k_mpio
GROUP BY m.departamento
ORDER BY pct_cobertura DESC, municipios_con_ies DESC, m.departamento
"""

SQL_RESUMEN = """
WITH dptos AS (SELECT DISTINCT clave(departamento) AS k FROM municipios),
conteo AS (SELECT clave(departamento) AS k, COUNT(*) AS n FROM ies GROUP BY 1),
por_dpto AS (SELECT COALESCE(c.n, 0) AS n FROM dptos d LEFT JOIN conteo c USING (k))
SELECT (SELECT COUNT(*) FROM ies) AS total_ies,
       (SELECT COUNT(*) FROM municipios) AS total_municipios,
       COUNT(*) AS departamentos,
       COUNT(*) FILTER (WHERE n = 0) AS departamentos_sin_ies,
       ROUND(AVG(n), 2) AS media_ies_por_departamento,
       MEDIAN(n) AS mediana_ies_por_departamento,
       ROUND(STDDEV_SAMP(n), 2) AS desviacion_estandar,
       MIN(n) AS minimo,
       MAX(n) AS maximo
FROM por_dpto
"""


def filas(con, sql):
    res = con.execute(sql)
    columnas = [c[0] for c in res.description]
    return [dict(zip(columnas, f)) for f in res.fetchall()]


class DuckDBAnalizador(AnalizadorDatos):
    def analizar(self, instituciones, municipios):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta_ies = Path(carpeta) / "ies.json"
            ruta_mpios = Path(carpeta) / "municipios.json"
            ruta_ies.write_text(json.dumps([asdict(i) for i in instituciones]), encoding="utf-8")
            ruta_mpios.write_text(json.dumps([asdict(m) for m in municipios]), encoding="utf-8")

            con = duckdb.connect()
            try:
                con.execute(MACRO_CLAVE)
                con.execute("CREATE TABLE alias_municipio(origen VARCHAR, destino VARCHAR)")
                con.executemany("INSERT INTO alias_municipio VALUES (?, ?)", ALIAS_MUNICIPIOS)
                con.execute("CREATE TABLE ies AS SELECT * FROM "
                            f"read_json_auto('{ruta_ies.as_posix()}')")
                con.execute("CREATE TABLE municipios AS SELECT * FROM "
                            f"read_json_auto('{ruta_mpios.as_posix()}')")
                resumen = filas(con, SQL_RESUMEN)[0]
                resumen["mediana_ies_por_departamento"] = float(
                    resumen["mediana_ies_por_departamento"])
                return ReporteEstadistico(
                    resumen=resumen,
                    por_departamento=filas(con, SQL_POR_DEPARTAMENTO),
                    por_caracter=filas(con, SQL_POR_CARACTER),
                    cobertura_municipal=filas(con, SQL_COBERTURA),
                )
            finally:
                con.close()
