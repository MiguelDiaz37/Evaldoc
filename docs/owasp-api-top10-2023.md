# OWASP API Security Top 10 2023 - EvalDoc controls

EvalDoc is a REST API, so we used the [OWASP API Security Top 10 2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
(the general OWASP Top 10 has no 2023 edition). The table lists every category, what EvalDoc
does about it and where the evidence is. Every implemented control has at least one automated
test that runs in the CI pipeline.

| # | Risk | Control implemented in EvalDoc | Code | Test |
|---|---|---|---|---|
| API1 | Broken Object Level Authorization | `/usuarios/me` takes the user from the JWT, never from an id in the URL, so a user can't read another account. Professors are public resources, but only ADMIN can change them. | `app/api/auth_router.py`, `app/api/seguridad.py` | `test_api_auth.py::test_endpoint_user_acepta_cualquier_rol` |
| API2 | Broken Authentication | Passwords hashed with bcrypt (cost 12). JWT HS256 signed with a secret of 32+ characters read from `JWT_SECRET`, expires in 30 min, `exp`, `iat`, `sub` and `iss` are required, `alg: none` is rejected. Same message and same work (a fake bcrypt check) when the email does not exist, so accounts can't be enumerated. | `app/application/auth_service.py`, `app/infrastructure/seguridad/` | `test_seguridad_tokens.py`, `test_auth_service.py::test_login_fallido_da_el_mismo_mensaje` |
| API3 | Broken Object Property Level Authorization | Response schemas only expose `id_usuario`, `correo` and `rol`, never the password hash. The register schema uses `extra="forbid"`, so sending `"rol": "ADMIN"` is rejected (no mass assignment). | `app/api/schemas.py` | `test_api_auth.py::test_registro_no_deja_elegir_el_rol` |
| API4 | Unrestricted Resource Consumption | Login and register allow 5 requests per minute per IP and answer 429 with `Retry-After`. The professor list is paginated (50 by default, 100 max). Every text field has a maximum length. | `app/api/limite_peticiones.py`, `app/api/docentes_router.py` | `test_owasp_controles.py::test_login_por_fuerza_bruta_recibe_429`, `test_listado_paginado_con_maximo_de_100` |
| API5 | Broken Function Level Authorization | Role based access control: create, update and delete professors and `/admin/panel` need ADMIN; USER gets 403. ADMIN accounts can only be created from the server terminal. | `app/api/seguridad.py`, `scripts/crear_usuario.py` | `test_api_auth.py::test_user_puede_leer_docentes_pero_no_modificarlos` |
| API6 | Unrestricted Access to Sensitive Business Flows | Only institutional emails (`@academia.umb.edu.co`) can register, one account per email, and registration has the same rate limit as login. | `app/domain/autenticacion/entities.py` | `test_api_auth.py::test_registro_rechaza_correo_externo_y_repetido` |
| API7 | Server Side Request Forgery | The server never downloads URLs sent by users. `foto_perfil` only accepts `https://` URLs without spaces, so `file://`, `javascript:` or `http://` values are rejected. | `app/api/schemas.py` | `test_owasp_controles.py::test_foto_solo_acepta_https` |
| API8 | Security Misconfiguration | Security headers on every response (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Strict-Transport-Security`, `Cache-Control: no-store`, CSP). CORS closed by default and only opened to origins in `CORS_ORIGENES`. Unexpected errors return a generic 500 without stack traces. Secrets live in `.env`, not in the code. | `app/api/cabeceras.py`, `app/api/errores.py`, `app/config.py` | `test_owasp_controles.py::test_cabeceras_de_seguridad`, `test_cors_*`, `test_error_inesperado_no_muestra_detalles` |
| API9 | Improper Inventory Management | All routes are versioned under `/api/v1`, the README lists every endpoint with its role, and Swagger can be turned off in production with `DOCS_ACTIVOS=false`. The unused AI and open data endpoints were removed. | `app/main.py`, `README.md` | `test_owasp_controles.py::test_docs_se_pueden_apagar_en_produccion`, `test_todas_las_rutas_estan_versionadas` |
| API10 | Unsafe Consumption of APIs | EvalDoc does not call third-party APIs anymore. For third-party code, dependencies are pinned with SHA-256 hashes, installed only from wheels, and watched by Dependabot. CI actions are pinned to commit SHAs. | `requirements.txt`, `.github/workflows/ci.yml` | `test_seguridad_ci.py` |

## Summary

All 10 categories are covered. Seven of them have controls written in EvalDoc's own code
(API1 to API5, API7 and API8); API6 and API9 combine code with configuration and
documentation, and API10 is handled through the supply chain because the project no
longer consumes external APIs.

## Known limitations

- The rate limiter keeps its counters in memory, so each server process has its own and they
  reset when the server restarts. Several instances would need a shared store such as Redis.
- JWTs can't be revoked before they expire, so a stolen token works until its 30 minutes
  end. Role changes do take effect at once, because the role in the token is compared with
  the database on every request and a mismatch returns 401.
- HSTS only has effect when the API is served over HTTPS.
