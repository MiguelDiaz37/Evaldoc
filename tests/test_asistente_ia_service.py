from unittest.mock import Mock

import pytest

from app.application.asistente_ia_service import AsistenteIAService
from app.domain.asistente_ia.ports import ModeloIA, RegistroLlamadas, RespuestaModelo
from app.domain.evaluacion_docente.entities import Docente, Evaluacion
from app.domain.evaluacion_docente.ports import DocenteRepository
from app.domain.exceptions import DocenteNoEncontrado, IALimiteAlcanzado, TecnicaInvalida


@pytest.fixture
def mocks():
    repo = Mock(spec=DocenteRepository)
    modelo = Mock(spec=ModeloIA)
    registro = Mock(spec=RegistroLlamadas)
    modelo.generar.return_value = RespuestaModelo(texto="Positivo", tokens_entrada=50,
                                                  tokens_salida=10)
    return repo, modelo, registro


def test_respuesta_ok(mocks):
    repo, modelo, registro = mocks
    service = AsistenteIAService(repo, modelo, registro)

    res = service.preguntar("Clasifica: 'explica muy bien'")

    assert res["respuesta"] == "Positivo"
    assert res["tokens_entrada"] == 50
    assert registro.registrar.call_args.args[-1] == "ok"


def test_tecnica_invalida_no_llama_al_modelo(mocks):
    repo, modelo, registro = mocks
    with pytest.raises(TecnicaInvalida):
        AsistenteIAService(repo, modelo, registro).preguntar("hola", tecnica="otra")
    modelo.generar.assert_not_called()


def test_rag_agrega_comentarios_al_prompt(mocks):
    repo, modelo, registro = mocks
    repo.obtener.return_value = Docente(
        id_docente=1, nombre="Laura Gomez",
        evaluaciones=[Evaluacion(puntaje=5, comentario="explica muy bien")],
    )
    AsistenteIAService(repo, modelo, registro).preguntar("Que opinan?", id_docente=1)

    prompt = modelo.generar.call_args.args[0]
    assert "(5 estrellas) explica muy bien" in prompt


def test_few_shot_incluye_ejemplos(mocks):
    repo, modelo, registro = mocks
    AsistenteIAService(repo, modelo, registro).preguntar("Clasifica: 'ok'", tecnica="few-shot")
    assert "Ejemplos de como clasificar" in modelo.generar.call_args.args[0]


def test_docente_no_existe(mocks):
    repo, modelo, registro = mocks
    repo.obtener.return_value = None
    with pytest.raises(DocenteNoEncontrado):
        AsistenteIAService(repo, modelo, registro).preguntar("Que opinan?", id_docente=99)


def test_error_del_modelo_se_registra(mocks):
    repo, modelo, registro = mocks
    modelo.generar.side_effect = IALimiteAlcanzado("Rate limit reached, try again later")

    with pytest.raises(IALimiteAlcanzado):
        AsistenteIAService(repo, modelo, registro).preguntar("hola")
    assert registro.registrar.call_args.args[-1] == "limite"
