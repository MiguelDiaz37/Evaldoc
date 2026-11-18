# EvalDoc

Proyecto de Taller de Programacion - UMB. Pagina para que los estudiantes califiquen y comenten a sus docentes.

Backend con FastAPI organizado con arquitectura hexagonal. Esta version contiene el CRUD de docentes y las reglas de negocio de la evaluacion docente.

## Arquitectura hexagonal

```
app/
  domain/                         nucleo, Python puro
    evaluacion_docente/           Docente, Evaluacion, DocenteRepository
    exceptions.py
  application/                    casos de uso (reciben los puertos por constructor)
    docente_service.py
  api/                            adaptadores de entrada (FastAPI)
  infrastructure/                 adaptadores de salida
    db/                           SQLAlchemy
  container.py                    arma las dependencias
  config.py
  main.py
docs/adr/                         decisiones de arquitectura (ADR)
```

Reglas: `domain` no importa nada de las otras capas ni librerias externas, `application` solo usa `domain` y `infrastructure` no conoce a `api`. Lo revisa `tests/test_arquitectura.py`.

La decision esta documentada en [docs/adr/0001-hexagonal-architecture.md](docs/adr/0001-hexagonal-architecture.md).

## Como correrlo

```
python -m venv venv
venv\Scripts\activate        (en mac/linux: source venv/bin/activate)
pip install --require-hashes --only-binary :all: -r requirements.txt
copy .env.example .env       (en mac/linux: cp)
uvicorn app.main:app --reload
```

- Swagger: http://localhost:8000/docs

## Endpoints

- GET /api/v1/docentes
- GET /api/v1/docentes/{id}
- POST /api/v1/docentes
- PUT /api/v1/docentes/{id}
- DELETE /api/v1/docentes/{id}

## Dependencias

`requirements.in` tiene las librerias que usa el proyecto. `requirements.txt` se genera a partir de el con las versiones exactas y el hash de cada paquete:

```
uv pip compile requirements.in --python-version 3.12 --generate-hashes -o requirements.txt
```

## Pruebas

```
pytest -v
```

Pruebas de dominio, servicio con mocks (`unittest.mock`), endpoints, reglas de arquitectura y seguridad del pipeline. El CI corre las pruebas con cobertura y el analisis de SonarCloud en cada push.

## Integrantes

- Miguel Diaz
- Jhonatan Ardila
