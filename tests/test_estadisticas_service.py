from unittest.mock import Mock

from app.application.estadisticas_service import EstadisticasService
from app.domain.datos_institucionales.entities import ReporteEstadistico, ResultadoFuente
from app.domain.datos_institucionales.ports import (
    AnalizadorDatos,
    FuenteInstituciones,
    FuenteMunicipios,
)
from tests.datos_prueba import INSTITUCIONES, MUNICIPIOS


def crear_mocks(origen_ies="api", origen_mpios="api"):
    ies = Mock(spec=FuenteInstituciones)
    mpios = Mock(spec=FuenteMunicipios)
    analizador = Mock(spec=AnalizadorDatos)
    ies.obtener.return_value = ResultadoFuente(INSTITUCIONES, origen_ies)
    mpios.obtener.return_value = ResultadoFuente(MUNICIPIOS, origen_mpios)
    analizador.analizar.return_value = ReporteEstadistico({}, [], [], [])
    return ies, mpios, analizador


def test_pasa_los_datos_de_las_dos_fuentes_al_analizador():
    ies, mpios, analizador = crear_mocks()
    EstadisticasService(ies, mpios, analizador).generar_reporte()
    analizador.analizar.assert_called_once_with(INSTITUCIONES, MUNICIPIOS)


def test_reporte_indica_el_origen_de_cada_fuente():
    ies, mpios, analizador = crear_mocks("api", "cache")
    reporte = EstadisticasService(ies, mpios, analizador).generar_reporte()
    assert reporte.origen == {"instituciones": "api", "municipios": "cache"}


def test_estado_de_las_fuentes():
    ies, mpios, analizador = crear_mocks()
    ies.estado.return_value = {"estado": "CLOSED"}
    mpios.estado.return_value = {"estado": "OPEN"}
    estados = EstadisticasService(ies, mpios, analizador).estado_fuentes()
    assert [e["estado"] for e in estados] == ["CLOSED", "OPEN"]
