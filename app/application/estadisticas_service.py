from app.domain.datos_institucionales.ports import (
    AnalizadorDatos,
    FuenteInstituciones,
    FuenteMunicipios,
)


class EstadisticasService:
    def __init__(self, instituciones: FuenteInstituciones, municipios: FuenteMunicipios,
                 analizador: AnalizadorDatos):
        self.instituciones = instituciones
        self.municipios = municipios
        self.analizador = analizador

    def generar_reporte(self):
        ies = self.instituciones.obtener()
        mpios = self.municipios.obtener()
        reporte = self.analizador.analizar(ies.datos, mpios.datos)
        reporte.origen = {"instituciones": ies.origen, "municipios": mpios.origen}
        return reporte

    def estado_fuentes(self):
        return [self.instituciones.estado(), self.municipios.estado()]
