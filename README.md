# CareerFlow

CareerFlow is a job application management platform
built using FastAPI and Python.

The project is being developed incrementally as part
of a 90-day Software Engineering, AI Engineering,
and Machine Learning Engineering curriculum.

## Features

- Create and manage job applications
- Track application statuses
- Enforce status-transition rules
- Validate request data using Pydantic
- Generate unique application IDs
- Maintain creation and modification timestamps
- Automated API and service-layer testing

## Technology Stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- pytest
- uv

## Installation

Clone the repository and navigate to the project directory.

Install the dependencies:

    uv sync

## Running the Application

    uv run uvicorn app.main:app --reload

The application will be available at:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Running Tests

    uv run pytest

Run tests with statement coverage:

    uv run pytest --cov=app --cov-report=term-missing

Generate an HTML coverage report:

    uv run pytest --cov=app --cov-report=html

## API Endpoints

| Method | Endpoint                  | Description                 |
| ------ | ------------------------- | --------------------------- |
| GET    | /health                   | Application health check    |
| GET    | /applications             | Retrieve all applications   |
| GET    | /applications/{id}        | Retrieve an application     |
| POST   | /applications             | Create an application       |
| PUT    | /applications/{id}        | Replace application details |
| PATCH  | /applications/{id}/status | Update status               |
| DELETE | /applications/{id}        | Delete an application       |

## Architecture

CareerFlow follows a layered architecture:

    Client
      |
    Router
      |
    Service
      |
    Repository
      |
    Storage

### Router Layer

Handles HTTP requests, responses and status codes.

### Service Layer

Implements business rules and coordinates repository
operations.

### Repository Layer

Manages data access and storage.

### Schema Layer

Defines request and response models and validates
application data.

## Application Status Transitions

| Current Status | Allowed Next Statuses            |
| -------------- | -------------------------------- |
| APPLIED        | SHORTLISTED, REJECTED, WITHDRAWN |
| SHORTLISTED    | INTERVIEW, REJECTED, WITHDRAWN   |
| INTERVIEW      | OFFERED, REJECTED, WITHDRAWN     |
| OFFERED        | WITHDRAWN                        |
| REJECTED       | None                             |
| WITHDRAWN      | None                             |

Retaining the current status is permitted.
Invalid transitions return HTTP 409 Conflict.

## Current Limitations

- Data is stored in memory and is lost when the
  application restarts.
- Authentication and authorization are not implemented.
- Concurrent updates are not yet protected.
- The application is intended for single-process use.

## Planned Improvements

- Dependency injection
- Repository interfaces
- PostgreSQL integration
- SQLAlchemy ORM
- Database migrations
- Authentication and authorization
- Redis caching
- Background processing
- React frontend
- Docker deployment
- CI/CD pipeline
