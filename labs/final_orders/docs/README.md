# Proyecto Final: Final Orders Service - Clean & Hexagonal Architecture

Servicio de gestión de órdenes implementado en Python con FastAPI, arquitectura limpia/hexagonal, SQLAlchemy, Alembic, JWT y Docker.

El proyecto integra:

- Dominio y reglas de negocio.
- Casos de uso independientes.
- Puertos definidos mediante `Protocol`.
- Adaptadores en memoria y SQLAlchemy.
- API REST segura con JWT.
- Unit of Work.
- Eventos de dominio.
- Pruebas unitarias, de contrato, integración y E2E.
- Migraciones independientes con Alembic.
- Docker multistage.
- CI/CD con GitHub Actions.
- Auditoría de dependencias.
- Observabilidad básica.

---

## Tabla de contenidos

1. Visión general
2. Arquitectura
3. Stack tecnológico
4. Estructura del proyecto
5. Requisitos previos
6. Instalación local
7. Configuración
8. Migraciones
9. Ejecución de la API
10. Uso de la API
11. Pruebas y cobertura
12. Calidad del código
13. Seguridad y auditoría
14. Observabilidad
15. Docker
16. CI/CD
17. Documentación técnica

---

## Visión general

Final Orders Service es un servicio backend para gestionar órdenes de compra.

La aplicación permite:

- Registrar usuarios.
- Autenticar usuarios mediante JWT.
- Crear órdenes.
- Listar únicamente las órdenes del usuario autenticado.
- Consultar una orden propia.
- Cancelar órdenes pendientes.
- Eliminar órdenes.
- Publicar eventos de dominio.
- Ejecutar migraciones versionadas.
- Exponer documentación OpenAPI.

Las reglas de negocio están separadas de FastAPI, SQLAlchemy, SQLite y cualquier otro detalle de infraestructura.

---

## Arquitectura

El proyecto sigue principios de Arquitectura Limpia y Arquitectura Hexagonal:

                    ┌─────────────────────────┐
                    │       Cliente HTTP      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Presentation / FastAPI  │
                    │ Routers, schemas, JWT   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Application             │
                    │ Use cases, DTOs, ports  │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Domain                  │
                    │ Entities, events, rules │
                    └────────────┬────────────┘
                                 ▲
                                 │
                    ┌────────────┴────────────┐
                    │ Infrastructure          │
                    │ SQLAlchemy, UoW, config │
                    │ security, migrations    │
                    └─────────────────────────┘

Reglas de dependencia

Presentation ───────► Application ───────► Domain
Infrastructure ─────► Application
Infrastructure ─────► Domain
Domain ──────────────► Sin dependencias externas

Flujo de creación de una orden

Cliente
  │
  ▼
FastAPI Router
  │
  ▼
Validación Pydantic + JWT
  │
  ▼
Caso de uso CreateOrder
  │
  ▼
Puerto UnitOfWork / OrderRepository
  │
  ▼
Adaptador SQLAlchemy
  │
  ▼
Base de datos
  │
  ▼
Commit
  │
  ▼
Evento OrderCreated

Capas del sistema

`domain´: entidades (Order y OrderItem), estados de la orden, cálculo de subtotales y totales, reglas para confirmar y cancelar, excepciones de dominio, evento OrderCreated.
El dominio no depende de FastAPI ni SQLAlchemy.

`application´: casos de uso, DTOs, puertos definidos con Protocol, orquestación de transacciones y publicación de eventos.

`infraestructure´: configuración mediante pydantic-settings, conexión a SQLAlchemy, modelos ORM, repositorio SQLAlchemy, Unit ofWork, seguridad JWT, publicador de eventos y migraciones Alembic.

`presentation´: routers FastAPI, Schemas Pydantic, dependencias de autenticación, presenters, wiring de los casos de uso.

---

## Stack Tecnológico

Lenguaje: Python 3.14
Gestión de dependencias: Poetry 2.4.3
API: FastAPI
Servidor: Uvicorn.
ORM: SQLAlchemy 2.
Migraciones: Alembic.
Base local: SQLite.
Autenticación: JWT con PyJWT.
Hash de contraseñas: pwdlib con Argon2.
Validación: Pydantic.
Configuración: pydantic-settings.
Pruebas: pytest, pytest-cov y pytest-asyncio.
Calidad: Ruff, Black, Isort y Mypy.
Contenedores: Docker multistage.
CI/CD: GitHub Actions.
Auditoría: pip-audit.

---

## Estructura del proyecto

.
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic/
│   └── versions/
├── docs/
│   └── README.md
├── labs/
│   ├── day01_tooling/
│   ├── day02_control_flow/
│   ├── ...
│   ├── day19_security/
│   └── final_orders/
│       ├── __init__.py
│       ├── main.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities.py
│       │   ├── events.py
│       │   └── exceptions.py
│       ├── application/
│       │   ├── __init__.py
│       │   ├── dto.py
│       │   ├── order_commands.py
│       │   ├── order_queries.py
│       │   ├── ports.py
│       │   └── use_cases.py
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── event_publisher.py
│       │   ├── memory.py
│       │   ├── models.py
│       │   ├── security.py
│       │   ├── sqlalchemy_repository.py
│       │   ├── sqlalchemy_uow.py
│       │   └── migrations/
│       │       ├── alembic.ini
│       │       ├── env.py
│       │       ├── script.py.mako
│       │       └── versions/
│       ├── presentation/
│       │   ├── __init__.py
│       │   ├── dependencies.py
│       │   ├── presenters.py
│       │   ├── schemas.py
│       │   └── routers/
│       │       ├── __init__.py
│       │       ├── auth.py
│       │       └── orders.py
│       └── tests/
│           ├── __init__.py
│           ├── conftest.py
│           ├── unit/
│           │   ├── test_create_order.py
│           │   ├── test_domain.py
│           │   ├── test_order_commands.py
│           │   └── test_order_queries.py
│           ├── contract/
│           │   ├── test_ports.py
│           │   └── test_repository.py
│           ├── integration/
│           │   └── test_api.py
│           └── e2e/
│               └── test_orders_flow.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── poetry.lock
├── pyproject.toml
└── README.md

---

## Requisitos previos

Instala:

- Python 3.14
- Poetry 2.4.3
- Docker Desktop
- Git

Verifica:

python --version
poetry --version
docker --version

---

## Instalación local

Clona el repositorio:
 git clone https://github.com/quiryat09S/python-mastery-capstone.git
cd python-mastery-capstone

Instala las dependencias:
poetry install

Verifica el proyecto:
poetry check

---

## Configuración

Copia el archivo de ejemplo:
Copy-Item .\.env.example .\.env

Configura .env:
DATABASE_URL=sqlite:///final_orders.db
ORDERS_API_URL=http://127.0.0.1:8000
ORDERS_API_TIMEOUT=10
ORDERS_JWT_SECRET=local-secret-with-at-least-32-characters
ORDERS_JWT_ALGORITHM=HS256
ORDERS_ENVIRONMENT=development

El archivo .env no debe subirse al repositorio.
El archivo .env.example sí debe versionarse y no debe contener secretos reales.

## Migraciones

Las migraciones del proyecto final están aisladas en:

`labs/final_orders/infrastructure/migrations/`

Aplicar migraciones:

    $env:DATABASE_URL = "sqlite:///final_orders.db"
    poetry run alembic -c .\labs\final_orders\infrastructure\migrations\alembic.ini upgrade head

Consultar versión actual:

    poetry run alembic -c .\labs\final_orders\infrastructure\migrations\alembic.ini current

Consultar el historial:

    poetry run alembic -c .\labs\final_orders\infrastructure\migrations\alembic.ini history

Crear una migración:

    poetry run alembic -c .\labs\final_orders\infrastructure\migrations\alembic.ini revision --autogenerate -m "describe schema change"

---

## Ejecución de la API

Inicia FastAPI:

    poetry run uvicorn labs.final_orders.main:app --reload

La API estará disponible en:

http://127.0.0.1:8000

Documentación:

http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc

Health check:

http://127.0.0.1:8000/health

Readiness:

http://127.0.0.1:8000/ready

---

## Uso de la API

Flujo de autenticación:

- registrar usuario: POST /auth/register
- Iniciar sesión: POST /auth/login

Endpoints de Orders:
POST   /orders/
GET    /orders/
GET    /orders/{order_id}
POST   /orders/{order_id}/cancel
DELETE /orders/{order_id}

- Crear una orden: Una orden solo pude cancelarse cuando está en estado PENDING. Los usuarios solo pueden consultar y modificar sus propias órdenes.

---

## Pruebas y cobertura

Ejecutar la suite final:

    poetry run pytest .\labs\final_orders\tests -q

Ejecutar pruebas por categoría:

    poetry run pytest .\labs\final_orders\tests\unit -q
    poetry run pytest .\labs\final_orders\tests\contract -q
    poetry run pytest .\labs\final_orders\tests\integration -q
    poetry run pytest .\labs\final_orders\tests\e2e -q

Ejecutar con cobertura:

    poetry run pytest .\labs\final_orders\tests `
    --cov=labs.final_orders `
    --cov-report=term-missing `
    --cov-report=html `
    --cov-fail-under=80

El reporte HTML se genera en:

htmlcov/index.html

La suite final incluye:

- Pruebas unitarias de dominio
- Pruebas unitarias de casos de uso
- Pruebas de contrato
- Pruebas de integración con base temporal
- Pruebas E2E de autenticación y órdenes

---

## Calidad del código

Ruff:
    poetry run ruff check .

Black:

    poetry run black --check .

Isort:

    poetry run isort --check-only .

Mypy:

    poetry run mypy .

## Seguridad y auditoría

La aplicación:

- Carga secretos mediante variables de entorno.
- Mantiene .env fuera del repositorio.
- Usa Argon2 para contraseñas.
- Usa JWT para autenticación.
- Ejecuta Docker sin root.
- Valida dependencias con pip-audit.

Ejecutar auditoría:

    poetry run pip-audit --local

Resultado esperado:

No known vulnerabilities found

---

## Observabilidad

La API proporciona:

- GET /health
- GET /ready

Cada respuesta incluye:

- X-Process-Time
- X-Correlation-ID

Estos headers permiten medir el tiempo de procesamiento y ratsrear una solicitud.

El servicio también registra:

- Método HTTP.
- Ruta.
- Código de respuesta.
- Correlation ID.
- Errores de dominio.
- Errores inesperados.

---

## Docker

Construir la imágen:

    docker build -t final-orders-api:local .

Verificar el usuario del contenedor:

    docker run --rm final-orders-api:local id

Debe mostrar:

uid=1000(appuser)

Ejecutar:

    docker run --rm `
    --name final-orders-api `
    -p 8000:8000 `
    -e DATABASE_URL=sqlite:///./final_orders.db `
    -e ORDERS_JWT_SECRET=local-secret-with-at-least-32-characters `
    final-orders-api:local

Probar:

http://localhost:8000/health
http://localhost:8000/docs

---

## CI/CD

El workflow se encuentra en:

.github/workflows/ci.yml

El job de calidad ejecuta:

- Instalación reproducible con Poetry.
- Auditoría de dependencias.
- Ruff.
- Black.
- Isort.
- Mypy.
- Pruebas.
- Cobertura.
- Construcción de wheel.
- Publicación del artefacto.

El job Docker:

- Espera a que quality finalice correctamente.
- Construye la imagen.
- Publica la imagen en GitHub Container Registry después del push a main.

Imagen publicada:

ghcr.io/quiryat09s/final-orders-api:main

## Documentación técnica

El diagrama de arquitectura está en:

docs/final-architecture.md

Incluye:

Diagrama de capas.
Flujo de creación de órdenes.
Dependencias entre capas.
Flujo de eventos.

---