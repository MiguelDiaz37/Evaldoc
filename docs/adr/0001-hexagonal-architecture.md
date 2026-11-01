# ADR 0001: Hexagonal architecture with three bounded contexts

- Status: Accepted
- Date: 2026-10-31
- Authors: Miguel Diaz, Jhonatan Ardila

## Context

EvalDoc started as a small FastAPI app. The first version kept HTTP handling, SQLAlchemy
queries, the Gemini call and the business rules in the same router files. That caused three
problems:

1. The rule "a professor with evaluations cannot be deleted" lived inside an HTTP handler, so
   the only way to test it was through the API and a database.
2. The AI endpoint created the Gemini client inside the handler, so tests could not replace
   it and every change to the prompt meant touching HTTP code.
3. Lab guide 6 asks us to consume two Colombian open data APIs (datos.gov.co and DANE). These
   services can be slow or down, and we did not want network failures to leak into the
   business logic.

## Decision

We split the code into four layers following ports and adapters:

| Layer | Package | Depends on |
|---|---|---|
| Domain | `app/domain` | nothing (plain Python) |
| Application | `app/application` | domain |
| API (input adapters) | `app/api` | application, domain |
| Infrastructure (output adapters) | `app/infrastructure` | domain |

The domain defines ports as abstract classes (`DocenteRepository`, `ModeloIA`,
`RegistroLlamadas`, `FuenteInstituciones`, `FuenteMunicipios`, `AnalizadorDatos`).
Infrastructure implements them with SQLAlchemy, Gemini, a CSV file, httpx and DuckDB.

Services receive their ports through the constructor:

- `DocenteService(repo)`
- `AsistenteIAService(repo, modelo, registro)`
- `EstadisticasService(instituciones, municipios, analizador)`

`app/container.py` is the composition root: it is the only module that knows which adapter
goes into each service. FastAPI `Depends` calls it, and tests replace it with
`app.dependency_overrides` or pass mocks directly to the constructors.

### Bounded contexts

| Context | Language | Main objects |
|---|---|---|
| Professor evaluation (`evaluacion_docente`) | professor, evaluation, score, comment | `Docente`, `Evaluacion`, `DocenteRepository` |
| AI assistant (`asistente_ia`) | prompt, technique, tokens, call log | `ModeloIA`, `RegistroLlamadas`, `RespuestaModelo` |
| Institutional data (`datos_institucionales`) | institution, sector, accreditation, municipality | `Institucion`, `Municipio`, `ReporteEstadistico` |

The AI assistant reads professors through the `DocenteRepository` port; it does not touch
the evaluation tables. The institutional data context does not know about professors yet;
it gives students context about the higher education system.

### External APIs

- MEN higher education institutions, datos.gov.co dataset `n5yy-8nav`.
- DANE DIVIPOLA municipalities, datos.gov.co dataset `gdxc-w37w`.

Each one goes through `ClienteSocrata`, which wraps the HTTP call in:

1. Retry with exponential backoff (3 attempts, 0.5 s and 1 s waits by default). Only
   temporary errors are retried: network errors, HTTP 5xx and 429.
2. A circuit breaker per API with three states. After 3 failed requests it goes from CLOSED
   to OPEN and rejects calls without touching the network. After 30 s it goes to HALF_OPEN
   and lets one call through. Success closes it; failure opens it again.
3. A local JSON cache. Every successful response is saved, and when the API fails or the
   circuit is open the last copy is used. The response says if the data came from `api` or
   `cache`.

The JSON is loaded into an in-memory DuckDB database, where four SQL queries compute
institutions per department, institutions by academic type, municipal coverage (a join
between both APIs) and descriptive statistics.

## Consequences

Positive:

- Business rules are tested without a database or network (`unittest.mock`). The suite has
  55 tests and runs in under one second.
- `tests/test_arquitectura.py` reads the imports of each layer and fails if the domain or
  the application layer imports FastAPI, SQLAlchemy, httpx, DuckDB or Google libraries.
- Changing SQLite to PostgreSQL, or Gemini to another model, only touches one adapter and
  the container.
- If datos.gov.co is down the statistics page still works with cached data and says so.

Negative:

- More files and more mapping code: the repository converts between ORM rows and domain
  entities, and the open data adapters convert raw JSON into `Institucion` and `Municipio`.
- The circuit breaker state lives in memory, so each server process has its own state and
  it resets on restart. That is acceptable for one instance; several instances would need
  a shared store.
- The cache can be old. The UI shows the origin of each source so users know.
- Department and municipality names come written differently in each dataset (accents,
  commas, "Cali" vs "Santiago de Cali"). We normalize them in SQL and keep a small alias
  table, which has to be updated if new mismatches appear.

## Alternatives considered

- Keep the layered router code and add the APIs inside the routers. Rejected because the
  new resilience logic would be mixed with HTTP code and hard to test.
- Use a library for the circuit breaker (for example `pybreaker`). We wrote a small one
  (about 80 lines) to understand the three states and to control the clock in tests.
- Process the data with pandas. DuckDB lets us write the analysis as SQL, reads JSON
  directly and is the tool requested by the guide.
