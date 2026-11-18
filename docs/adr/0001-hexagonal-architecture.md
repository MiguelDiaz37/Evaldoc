# ADR 0001: Hexagonal architecture

- Status: Accepted
- Date: 2026-10-31 (updated 2026-11-18)
- Authors: Miguel Diaz, Jhonatan Ardila

## Context

EvalDoc started as a small FastAPI app. The first version kept HTTP handling, SQLAlchemy
queries and the business rules in the same router files. The rule "a professor with
evaluations cannot be deleted" lived inside an HTTP handler, so the only way to test it was
through the API and a database.

## Decision

We split the code into four layers following ports and adapters:

| Layer | Package | Depends on |
|---|---|---|
| Domain | `app/domain` | nothing (plain Python) |
| Application | `app/application` | domain |
| API (input adapters) | `app/api` | application, domain |
| Infrastructure (output adapters) | `app/infrastructure` | domain |

The domain defines the `DocenteRepository` port as an abstract class. Infrastructure
implements it with SQLAlchemy (`SqlAlchemyDocenteRepository`).

`DocenteService` receives the repository through its constructor. `app/container.py` is the
composition root: it is the only module that knows which adapter goes into the service.
FastAPI `Depends` calls it, and tests replace it with `app.dependency_overrides` or pass
mocks directly to the constructor.

The domain has one bounded context, professor evaluation (`evaluacion_docente`), with the
language professor, evaluation, score and comment (`Docente`, `Evaluacion`).

## Update 2026-11-18

Earlier lab guides added an AI assistant (Gemini) and open data statistics (datos.gov.co,
DuckDB, circuit breaker). They were not part of EvalDoc's purpose, so they were removed and
the project kept only the professor evaluation context.

## Consequences

Positive:

- Business rules are tested without a database (`unittest.mock`).
- `tests/test_arquitectura.py` reads the imports of each layer and fails if the domain or
  the application layer imports FastAPI, SQLAlchemy, Pydantic or dotenv.
- Changing SQLite to PostgreSQL only touches the database adapter and the container.

Negative:

- More files and mapping code: the repository converts between ORM rows and domain
  entities.

## Alternatives considered

- Keep the layered router code. Rejected because the business rules could only be tested
  through HTTP and a database.
