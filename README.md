# CareerFlow

CareerFlow is a job application management platform built using
FastAPI and Python. It enables users to manage job applications,
track their progress, and enforce application status workflows.

The project is being developed incrementally as part of a
90-day Software Engineering, AI Engineering, and Machine
Learning Engineering curriculum.

## Features

- Create, retrieve, update, and delete job applications
- Track application statuses
- Enforce valid status transitions
- Validate request data using Pydantic
- Generate unique application IDs
- Maintain timezone-aware creation and modification timestamps
- Layered architecture with separation of concerns
- Constructor-based dependency injection
- FastAPI dependency providers and nested dependencies
- Configurable dependency lifetimes
- Isolated automated testing

## Technology Stack

| Technology | Purpose                               |
| ---------- | ------------------------------------- |
| Python     | Backend programming language          |
| FastAPI    | REST API framework                    |
| Pydantic   | Data validation and serialization     |
| Uvicorn    | ASGI server                           |
| pytest     | Automated testing                     |
| pytest-cov | Code coverage measurement             |
| HTTPX      | HTTP integration testing              |
| uv         | Dependency and environment management |

## Project Structure

    careerflow/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── dependencies.py
    │   ├── exceptions.py
    │   ├── routers/
    │   │   └── applications.py
    │   ├── schemas/
    │   │   └── application.py
    │   ├── services/
    │   │   └── application_service.py
    │   └── repositories/
    │       └── application_repository.py
    ├── tests/
    │   ├── conftest.py
    │   ├── test_applications.py
    │   ├── test_application_service.py
    │   ├── test_application_repository.py
    │   └── test_dependencies.py
    ├── .gitignore
    ├── .python-version
    ├── pytest.ini
    ├── pyproject.toml
    ├── uv.lock
    └── README.md

## Getting Started

### Prerequisites

- Python compatible with the project's pyproject.toml
- uv package manager
- Git

### Installation

Clone the repository:

```bash
git clone https://github.com/mihirg42/CareerFlow.git
cd CareerFlow
```

Install the project dependencies:

```bash
uv sync
```

### Running the Application

```bash
uv run uvicorn app.main:app --reload
```

The application will be available at:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

| Method | Endpoint                  | Description                 | Success Code |
| ------ | ------------------------- | --------------------------- | ------------ |
| GET    | /health                   | Application health check    | 200          |
| GET    | /applications             | Retrieve all applications   | 200          |
| GET    | /applications/{id}        | Retrieve an application     | 200          |
| POST   | /applications             | Create an application       | 201          |
| PUT    | /applications/{id}        | Replace application details | 200          |
| PATCH  | /applications/{id}/status | Update application status   | 200          |
| DELETE | /applications/{id}        | Delete an application       | 204          |

### Error Responses

| Status Code | Description                           |
| ----------- | ------------------------------------- |
| 404         | Application not found                 |
| 409         | Invalid application status transition |
| 422         | Request validation failed             |

## Application Data Model

| Field           | Type     | Requirement            |
| --------------- | -------- | ---------------------- |
| id              | Integer  | Server-generated       |
| company_name    | String   | Required, non-blank    |
| job_title       | String   | Required, non-blank    |
| job_url         | URL      | Optional               |
| status          | Enum     | Initially APPLIED      |
| applied_date    | Date     | Required               |
| salary_expected | Integer  | Optional, non-negative |
| notes           | String   | Optional               |
| created_at      | Datetime | Server-generated       |
| updated_at      | Datetime | Server-generated       |

All server-generated timestamps are timezone-aware and use
Indian Standard Time (Asia/Kolkata, UTC+05:30).

## Example API Request

Create a new job application:

```json
{
  "company_name": "Microsoft",
  "job_title": "Software Engineer",
  "job_url": "https://example.com/jobs/123",
  "applied_date": "2026-11-26",
  "salary_expected": 1500000,
  "notes": "Applied through company website"
}
```

Send this request to:

    POST /applications

The server generates the application ID, initial status,
creation timestamp, and modification timestamp.

## Application Status Workflow

An application starts with the APPLIED status and can
transition according to the following rules:

| Current Status | Allowed Next Statuses            |
| -------------- | -------------------------------- |
| APPLIED        | SHORTLISTED, REJECTED, WITHDRAWN |
| SHORTLISTED    | INTERVIEW, REJECTED, WITHDRAWN   |
| INTERVIEW      | OFFERED, REJECTED, WITHDRAWN     |
| OFFERED        | WITHDRAWN                        |
| REJECTED       | None                             |
| WITHDRAWN      | None                             |

Retaining the current status is permitted.

Invalid status transitions return HTTP 409 Conflict.

Both PUT and PATCH operations enforce the same transition
rules to prevent bypassing business validation.

Invalid operations leave the stored application unchanged.

## Architecture

CareerFlow follows a layered architecture with dependency
injection and separation of concerns.

    HTTP Client
         |
         v
       Router
         |
         v
       Service
         |
         v
      Repository
         |
         v
    In-Memory Storage

### Router Layer

Responsibilities:

- Handling HTTP requests and responses
- Receiving injected service instances
- Validating requests through Pydantic schemas
- Translating application exceptions into HTTP responses
- Returning appropriate HTTP status codes

The router does not instantiate the service or directly
access application storage.

### Service Layer

Responsibilities:

- Implementing business logic
- Validating application status transitions
- Coordinating repository operations
- Raising business-level exceptions

The service receives its repository through constructor
dependency injection.

The service layer remains independent of FastAPI's
dependency resolution mechanism.

### Repository Layer

Responsibilities:

- Managing application storage
- Performing CRUD operations
- Generating unique application IDs
- Managing creation and modification timestamps
- Preventing unintended mutation of stored records
- Handling missing application records

The current repository uses an in-memory Python dictionary.

### Schema Layer

Responsibilities:

- Defining request and response models
- Validating incoming application data
- Defining application status enumerations
- Serializing outgoing application data

Separate schemas are used for creation, full updates,
status updates, and responses.

## Dependency Injection

CareerFlow uses constructor dependency injection together
with FastAPI's dependency resolution mechanism.

The service receives its repository externally instead of
constructing it internally.

```python
class ApplicationService:
    def __init__(self, repository: ApplicationRepository):
        self.repository = repository
```

Dependency provider functions are defined in:

    app/dependencies.py

FastAPI resolves the dependencies in the following order:

    get_repository()
           |
           v
    get_service(repository)
           |
           v
    API Endpoint

This approach provides:

- Reduced coupling between components
- Easier dependency substitution
- Improved testability
- Centralized dependency configuration
- Easier migration to database-backed repositories

## Dependency Lifetimes

Different components have different lifetimes according
to their responsibilities.

| Component                   | Lifetime                     |
| --------------------------- | ---------------------------- |
| Application repository      | Process-wide shared instance |
| Application service         | Request-scoped               |
| Test repository             | One instance per test        |
| Direct test service fixture | One instance per test        |

The repository is shared across HTTP requests within the
same application process, allowing application data to
persist between requests.

A new service instance is normally created for each request,
using the shared repository.

FastAPI caches resolved dependencies within an individual
request by default.

## Automated Testing

CareerFlow includes automated tests covering repository
operations, service-layer business rules, API integration,
and dependency injection.

### Repository Tests

- CRUD operations
- Independent repository instances
- Missing application handling
- Protection against unintended data mutation

### Service Tests

- Business rule validation
- Valid and invalid status transitions
- PUT and PATCH transition enforcement
- Missing application handling
- Preservation of data after invalid operations

### API Integration Tests

- HTTP endpoints and response codes
- Request validation
- Response serialization
- Unique ID generation
- Server-generated fields
- Timestamp management

### Dependency Injection Tests

- Correct constructor injection
- Shared repository state across services
- Isolated repository instances
- Data persistence across HTTP requests
- FastAPI dependency substitution

## Test Isolation

Pytest fixtures provide fresh repository instances for
individual tests.

API integration tests use FastAPI's dependency_overrides
mechanism to replace the application's shared repository
with an isolated test repository.

```python
app.dependency_overrides[get_repository] = lambda: repository
```

Dependency overrides are removed after each test to prevent
state leakage between tests.

A dedicated dependency lifetime test also exercises the
original application dependency chain without overrides.

## Running Tests

Run the complete test suite:

```bash
uv run pytest -v
```

Run tests with statement coverage:

```bash
uv run pytest --cov=app --cov-report=term-missing
```

Enforce a minimum coverage requirement of 90%:

```bash
uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```

Generate an HTML coverage report:

```bash
uv run pytest --cov=app --cov-report=html
```

The generated report is available at:

    htmlcov/index.html

## Test Results

Latest recorded local test run: November 26, 2026.

| Test Category        | Tests Passed |
| -------------------- | -----------: |
| Repository           |           10 |
| Service              |           79 |
| API integration      |           34 |
| Dependency injection |            5 |
| Total                |          128 |

### Statement Coverage

| Module                    | Statements | Missed | Coverage |
| ------------------------- | ---------: | -----: | -------: |
| dependencies.py           |          9 |      0 |     100% |
| exceptions.py             |          4 |      0 |     100% |
| main.py                   |          7 |      0 |     100% |
| application_repository.py |         46 |      0 |     100% |
| applications.py           |         42 |      0 |     100% |
| application.py            |         25 |      0 |     100% |
| application_service.py    |         28 |      0 |     100% |
| Total                     |        161 |      0 |     100% |

These results represent statement coverage, not exhaustive
branch coverage or proof that the application is bug-free.

## Current Limitations

- Data is stored in memory and is lost on application restart.
- Repository state is not shared between multiple worker processes.
- Authentication and authorization are not implemented.
- Concurrent updates are not protected by transactions or locks.
- Database persistence is not implemented.
- The service currently depends on a concrete repository type.
- Pagination, filtering, and search are not implemented.

## Planned Improvements

- Repository interfaces and Python protocols
- PostgreSQL integration
- SQLAlchemy ORM
- Alembic database migrations
- Database transactions
- Indexing and query optimization
- Pagination, filtering, and search
- JWT authentication
- User-level authorization
- Redis caching
- Background tasks and reminders
- React and TypeScript frontend
- Docker containerization
- CI/CD using GitHub Actions
- Logging and observability
- Performance testing
- Production deployment
