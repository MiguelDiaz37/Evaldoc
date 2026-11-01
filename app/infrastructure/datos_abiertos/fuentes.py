from app.domain.datos_institucionales.entities import Institucion, Municipio, ResultadoFuente
from app.domain.datos_institucionales.ports import FuenteInstituciones, FuenteMunicipios
from app.infrastructure.datos_abiertos.socrata_client import ClienteSocrata

CAMPOS_INSTITUCIONES = [
    "c_digo_instituci_n", "nombre_instituci_n", "principal_seccional", "sector",
    "car_cter_acad_mico", "departamento_domicilio", "municipio_domicilio",
    "acreditada_alta_calidad", "estado",
]

CAMPOS_MUNICIPIOS = ["cod_dpto", "dpto", "cod_mpio", "nom_mpio", "tipo_municipio"]


def a_institucion(fila):
    return Institucion(
        codigo=fila.get("c_digo_instituci_n", ""),
        nombre=fila.get("nombre_instituci_n", "").strip(),
        tipo=fila.get("principal_seccional", ""),
        sector=fila.get("sector", ""),
        caracter=fila.get("car_cter_acad_mico", ""),
        departamento=fila.get("departamento_domicilio", ""),
        municipio=fila.get("municipio_domicilio", ""),
        acreditada=fila.get("acreditada_alta_calidad", "").upper() == "SI",
    )


def a_municipio(fila):
    return Municipio(
        codigo=fila.get("cod_mpio", ""),
        nombre=fila.get("nom_mpio", ""),
        codigo_departamento=fila.get("cod_dpto", ""),
        departamento=fila.get("dpto", ""),
        tipo=fila.get("tipo_municipio", ""),
    )


class InstitucionesDatosGov(FuenteInstituciones):
    def __init__(self, cliente: ClienteSocrata):
        self.cliente = cliente

    def obtener(self):
        filas, origen = self.cliente.obtener()
        return ResultadoFuente(datos=[a_institucion(f) for f in filas], origen=origen)

    def estado(self):
        return self.cliente.estado() | {"fuente": "MEN - Instituciones de Educacion Superior"}


class MunicipiosDivipola(FuenteMunicipios):
    def __init__(self, cliente: ClienteSocrata):
        self.cliente = cliente

    def obtener(self):
        filas, origen = self.cliente.obtener()
        return ResultadoFuente(datos=[a_municipio(f) for f in filas], origen=origen)

    def estado(self):
        return self.cliente.estado() | {"fuente": "DANE - DIVIPOLA"}
