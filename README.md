# EvalDoc

Proyecto de Taller de Programacion - UMB. Pagina para que los estudiantes califiquen y comenten a sus docentes.

Backend con FastAPI organizado con arquitectura hexagonal. Incluye el CRUD de docentes, un asistente de IA con Gemini y estadisticas de educacion superior con dos APIs de datos abiertos de Colombia procesadas con DuckDB.

## Arquitectura hexagonal

```
app/
  domain/                         nucleo, Python puro
    evaluacion_docente/           Docente, Evaluacion, DocenteRepository
    asistente_ia/                 ModeloIA, RegistroLlamadas
    datos_institucionales/        Institucion, Municipio, FuenteInstituciones, FuenteMunicipios, AnalizadorDatos
    exceptions.py
  application/                    casos de uso (reciben los puertos por constructor)
    docente_service.py
    asistente_ia_service.py
    estadisticas_service.py
  api/                            adaptadores de entrada (FastAPI y pagina Jinja2)
  infrastructure/                 adaptadores de salida
    db/                           SQLAlchemy
    ia/                           Gemini y log CSV
    datos_abiertos/               cliente de datos.gov.co (Socrata)
    resiliencia/                  circuit breaker y retry con backoff exponencial
    analitica/                    DuckDB
  container.py                    arma las dependencias
  config.py
  main.py
docs/adr/                         decisiones de arquitectura (ADR)
data/cache/                       ultima copia de los datasets
```

Reglas: `domain` no importa nada de las otras capas ni librerias externas, `application` solo usa `domain` y `infrastructure` no conoce a `api`. Lo revisa `tests/test_arquitectura.py`.

La decision esta documentada en [docs/adr/0001-hexagonal-architecture.md](docs/adr/0001-hexagonal-architecture.md).

## APIs de datos abiertos

| API | Dataset | Uso |
|---|---|---|
| MEN - Instituciones de Educacion Superior (datos.gov.co) | `n5yy-8nav` | IES por departamento, sector, caracter y acreditacion |
| DANE - DIVIPOLA (datos.gov.co) | `gdxc-w37w` | municipios por departamento |

Cada API tiene:

- **Retry con backoff exponencial**: 3 intentos, esperas de 0.5 s y 1 s. Solo reintenta errores de red, 5xx y 429.
- **Circuit breaker**: CLOSED, OPEN despues de 3 fallos seguidos, HALF_OPEN despues de 30 s, y vuelve a CLOSED si la llamada de prueba funciona.
- **Cache**: si la API falla o el circuito esta abierto se usa la ultima copia en `data/cache/`. La respuesta dice si los datos vienen de `api` o de `cache`.

Consultas en DuckDB (`app/infrastructure/analitica/duckdb_analizador.py`):

1. IES por departamento: total, oficiales, privadas y porcentaje de acreditadas.
2. IES por caracter academico con porcentaje del total.
3. Cobertura municipal: cruce entre las dos APIs para saber que porcentaje de municipios de cada departamento tiene al menos una IES.
4. Resumen descriptivo: media, mediana, desviacion estandar, minimo y maximo de IES por departamento.

## Como correrlo

```
python -m venv venv
venv\Scripts\activate        (en mac/linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env       (en mac/linux: cp)
uvicorn app.main:app --reload
```

En el `.env` hay que poner la API key de Gemini (se saca en aistudio.google.com). Las estadisticas no necesitan API key.

- Pagina de estadisticas: http://localhost:8000/estadisticas
- Swagger: http://localhost:8000/docs

## Endpoints

- GET /api/v1/docentes
- GET /api/v1/docentes/{id}
- POST /api/v1/docentes
- PUT /api/v1/docentes/{id}
- DELETE /api/v1/docentes/{id}
- POST /api/v1/ai (tecnicas: zero-shot, few-shot, cot)
- GET /api/v1/datos-abiertos/estadisticas
- GET /api/v1/datos-abiertos/circuitos
- GET /estadisticas (pagina HTML)

## Demo del circuit breaker

```
python demo_circuit_breaker.py
```

Simula que la API de DIVIPOLA esta caida (HTTP 503), muestra los reintentos, como el circuito pasa a OPEN, luego a HALF_OPEN y vuelve a CLOSED cuando la API responde. Con `--sin-red` el ultimo paso usa la copia local en vez de internet.

## Probar la IA

Con el servidor corriendo, en otra terminal:

```
python probar_ia.py
```

Hace 12 llamadas (4 por tecnica) y las guarda en `llamadas_ia.csv`.

## Pruebas

```
pytest -v
```

55 pruebas: dominio, servicios con mocks (`unittest.mock`), circuit breaker, retry, cliente HTTP con `httpx.MockTransport`, consultas DuckDB, endpoints y reglas de arquitectura. Ninguna prueba usa internet.

## Integrantes

- Miguel Diaz
- Nicolas Sanchez
- Jhonatan Ardila
