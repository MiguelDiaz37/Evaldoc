from unittest.mock import Mock

from app.container import get_modelo_ia, get_registro_llamadas
from app.domain.asistente_ia.ports import ModeloIA, RegistroLlamadas, RespuestaModelo
from app.domain.exceptions import IALimiteAlcanzado
from app.main import app


def usar_modelo_falso(modelo):
    app.dependency_overrides[get_modelo_ia] = lambda: modelo
    app.dependency_overrides[get_registro_llamadas] = lambda: Mock(spec=RegistroLlamadas)


def test_preguntar_ok(client):
    modelo = Mock(spec=ModeloIA)
    modelo.generar.return_value = RespuestaModelo("Negativo", 40, 5)
    usar_modelo_falso(modelo)

    res = client.post("/api/v1/ai", json={"pregunta": "Clasifica: 'no explica nada'"})

    assert res.status_code == 200
    assert res.json()["respuesta"] == "Negativo"
    assert res.json()["tokens_salida"] == 5


def test_tecnica_invalida(client):
    usar_modelo_falso(Mock(spec=ModeloIA))
    res = client.post("/api/v1/ai", json={"pregunta": "hola", "tecnica": "magia"})
    assert res.status_code == 422


def test_limite_devuelve_429(client):
    modelo = Mock(spec=ModeloIA)
    modelo.generar.side_effect = IALimiteAlcanzado("Rate limit reached, try again later")
    usar_modelo_falso(modelo)

    res = client.post("/api/v1/ai", json={"pregunta": "hola"})
    assert res.status_code == 429


def test_docente_no_existe_404(client):
    usar_modelo_falso(Mock(spec=ModeloIA))
    res = client.post("/api/v1/ai", json={"pregunta": "Que opinan?", "id_docente": 999})
    assert res.status_code == 404
