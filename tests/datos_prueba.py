from app.domain.datos_institucionales.entities import Institucion, Municipio


def ies(nombre, sector, caracter, departamento, municipio, acreditada):
    return Institucion("1", nombre, "Principal", sector, caracter, departamento, municipio,
                       acreditada)


def mpio(nombre, departamento):
    return Municipio("0", nombre, "0", departamento, "Municipio")


INSTITUCIONES = [
    ies("UMB", "Privado", "Universidad", "Bogotá D.C.", "Bogotá D.C.", False),
    ies("UNAL", "Oficial", "Universidad", "Bogotá D.C.", "Bogotá D.C.", True),
    ies("SENA Tec", "Oficial", "Institución Tecnológica", "Bogotá D.C.", "Bogotá D.C.", False),
    ies("UdeA", "Oficial", "Universidad", "Antioquia", "Medellín", True),
    ies("Univalle", "Oficial", "Universidad", "Valle del Cauca", "Cali", True),
]

MUNICIPIOS = [
    mpio("BOGOTÁ, D.C.", "BOGOTÁ, D.C."),
    mpio("MEDELLÍN", "ANTIOQUIA"),
    mpio("ABEJORRAL", "ANTIOQUIA"),
    mpio("SANTIAGO DE CALI", "VALLE DEL CAUCA"),
    mpio("MITÚ", "VAUPÉS"),
]
