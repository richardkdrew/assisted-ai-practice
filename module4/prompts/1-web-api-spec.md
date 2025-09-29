# Config Service spec

This document contains details necessary to create a prompt, which will later be used to create an implementation plan for a REST Web API. Please review the contents of this file and recommend a PROMPT that can be sent to an AI coding assistant for help with creating a plan for this service. 

The prompt should:
- ask the assistant to create a comprehensive plan that includes dependencies, file/folder structure, and architectural patterns.
- recommend strict adherence to ALL of the details in this document.
- strongly encourage the assistant to not add any additional dependencies without approval.
- encourage the assistant to ask for more information if they need it.

## Tech Stack

| Area                 | Choice     | Version |
|----------------------|------------|---------|
| Language             | Python     | 3.13.5  |
| Web framework        | Fast API   | 0.116.1 |
| Validation           | Pydantic   | 2.11.7  |
| Service config       | Pydantic   | 2.11.7  |
| Testing framework    | pytest     | 8.4.1   |
| Test Coverage helper | pytest-cov | 6.2.1.  |
| Testing HTTP helper  | httpx      | 0.28.1  |
| Database engine      | PostgreSQL | v16     |
| Python DB adapter    | psycopg2   | 2.9.10  |

It is very IMPORTANT the prompt stress the importance of including these SPECIFIC version numbers.

## Data Models

**Application**
DB Table: applications
Columns:
  - id: (primary key) datatype: string/ULID
  - name: unique datatype: string(256)
  - comments: datatype: string(1024)

**Configuations**
DB Table: configurations
Columns:
    - id: (primary key) datatype: string/ULID
    - application_id: (foreign key) datatype: string/ULID
    - name: datatype: string(256) expected to be unique per application
    - comments: datatype: string(1024)
    - config: Dictionary with name/value pairs datatype: JSONB 

## API Endpoints

Should be prefixed with `/api/v1`

**Applications**
  - POST `/applications`
  - PUT `/applications/{id}`
  - GET `/applications/{id}` (includes list of all related configuration.ids)
  - GET `/applications`

**Configurations**
  - POST `/configurations`
  - PUT `/configurations/{id}`
  - GET `/configurations/{id}`

## Data Persistence

This project will NOT be using an ORM. Rather, it will manage and issue SQL statements. Use the Repository for data access.

The connection pool should use the following components:
- psycopg2.pool.ThreadedConnectionPool
- concurrent.futures.ThreadPoolExecutor
- contextlib.asynccontextmanager
- psycopg2.extras.RealDictCursor as the cursor_factory
- pydantic_extra_types.ulid.ULID as the primary key for applications
  - python-ulid>=2.0.0,<3.0.0 wrapped by Pydantic ULID

## Data Schema

Implement a migration system that includes:
- A `migrations` database table with appropriate fields
- A `migrations/` folder to hold the `*.sql` migration files
- A `migrations.py` file to implement the migration system
- A `migrations_test.py` file to test the migration system

## Dates and times

Use the most up-to-date Python documentation for date and time operations to ensure we don't use deprecated APIs. Use the web to validate code with these docs: https://docs.python.org/3/library/time.html

## Automated Testing

- ALL code files MUST have an associated unit test (NOT `__init__.py` files) that focuses on 80% of the most important scenarios in the file it is testing.
- ALL unit tests will have a `_test.py` suffix and be located in the same folder as the unit under test.
- If we must have a `test/` folder, it should only contain test helpers, widely used mocks, and/or integration tests. Do not create this folder until it is needed.

## Service Configuration

Use a `.env` file to store environment variables, such as the database configuration string, logging level, etc. Use pydantic-settings (>=2.0.0,<3.0.0) to parse/validate the environment variables.

## Project Structure Requirements

**CRITICAL**: All build and configuration files MUST be located in the `svc/` directory:

```
module3/
├── svc/                          # Service root - ALL code and config here
│   ├── pyproject.toml           # Python dependencies (MUST be in svc/)
│   ├── .env.example             # Environment template (MUST be in svc/)
│   ├── docker-compose.yml       # Database services (MUST be in svc/)
│   ├── main.py                  # Application entry point
│   ├── config.py                # Settings management
│   ├── database.py              # Connection pool & utilities
│   ├── models.py                # Pydantic data models
│   ├── repository.py            # Data access layer
│   ├── migrations.py            # Migration runner
│   ├── routers/                 # API endpoint modules
│   │   ├── __init__.py
│   │   ├── applications.py      # Application CRUD endpoints
│   │   └── configurations.py    # Configuration CRUD endpoints
│   ├── migrations/              # SQL migration files
│   │   └── 001_initial_schema.sql
│   ├── test_integration.py      # API integration tests (MANDATORY)
│   └── *_test.py               # Unit tests
├── Makefile                     # Development commands (root level)
├── README.md                    # Documentation (root level)
└── .gitignore                   # Git ignore (root level)
```

**Validation Requirements**:
- The `uv` commands must work from within the `svc/` directory
- Docker Compose commands must work from within the `svc/` directory
- All build files (pyproject.toml, docker-compose.yml, .env.example) MUST be in `svc/`

## Infrastructure and Deployment Requirements

**MANDATORY**: Must include all of the following:

### Database Service Configuration
- `docker-compose.yml` in `svc/` directory with PostgreSQL 16 service
- Health checks for database readiness
- Volume persistence configuration
- Port mapping (5432:5432)
- Environment variables for database credentials

### Environment Management
- `.env.example` template with all required variables in `svc/` directory
- Environment variable documentation with default values
- Default values that work for local development without modification

### Migration System (Enhanced Requirements)
- SQL-based migration files in `svc/migrations/` subdirectory
- Migration runner (`migrations.py`) with execution tracking
- Migrations table for tracking applied migrations
- `make migrate` command for applying migrations

## Integration Testing Requirements

**MANDATORY**: Must include comprehensive integration tests that validate complete API-to-database workflows:

### Required Integration Test Coverage
1. **Complete API-to-Database Flow Testing**:
   - Create application → verify database persistence → retrieve via API
   - Create configuration → verify foreign key relationship → retrieve via API
   - Update operations with database persistence verification
   - Delete operations with cascade behavior verification

2. **Integration Test Implementation**:
   - File: `test_integration.py` in `svc/` directory
   - Database cleanup fixtures (before/after each test)
   - Use actual PostgreSQL database (via Docker Compose), not mocks
   - Test all CRUD operations for both applications and configurations
   - Validate constraint enforcement (unique names, foreign keys)
   - Test error scenarios with proper HTTP status codes (404, 400, 409)

3. **Test Database Management**:
   - Tests must clean database state between test runs
   - Tests must verify actual database record creation/modification
   - Tests must validate relationship integrity (application ↔ configurations)

### Testing Commands Required
- `make test` - run all tests including integration tests
- `make test-integration` - run integration tests only
- Integration tests must be runnable independently from unit tests

## Quality Validation Requirements

**MANDATORY**: Implementation must pass these validation checkpoints:

### Structural Validation Checklist
- [ ] All build files (`pyproject.toml`, `docker-compose.yml`, `.env.example`) are in `svc/` directory
- [ ] `uv sync` works from `svc/` directory
- [ ] `docker-compose up -d` works from `svc/` directory
- [ ] Application files are properly organized in `svc/` directory structure

### Integration Test Validation Checklist
- [ ] Complete API-to-database integration tests exist in `test_integration.py`
- [ ] Tests create actual database records and verify persistence
- [ ] Tests validate constraint enforcement (foreign keys, unique constraints)
- [ ] Tests cover error scenarios and return proper HTTP status codes
- [ ] Tests clean database state between runs

### Deployment Validation Checklist
- [ ] Database starts successfully with `make db-up`
- [ ] Migrations apply successfully with `make migrate`
- [ ] Application starts successfully with `make run`
- [ ] Health endpoint responds at `/health`
- [ ] API documentation is accessible at `/docs`
- [ ] Basic CRUD operations work via curl/HTTP clients

**Acceptance Criteria**: ALL validation checkpoints must pass before implementation is considered complete.

## Development Workflow Requirements

**MANDATORY**: Implementation must support this exact workflow sequence:

```bash
# Initial setup (must work exactly as specified)
cd module3
make install           # Install dependencies with uv
make db-up            # Start PostgreSQL database
make migrate          # Apply database migrations
make run              # Start FastAPI development server

# Validation commands (must work exactly as specified)
curl http://localhost:8000/health                     # Health check
curl http://localhost:8000/docs                       # API documentation
curl http://localhost:8000/api/v1/applications/       # List applications

# Testing commands (must work exactly as specified)
make test             # Run all tests including integration tests
make test-integration # Run integration tests only
```

### Required Makefile Targets
All commands must use `uv` module calling syntax from `svc/` directory:

```makefile
install:          # uv sync
db-up:           # Start database with Docker Compose
db-down:         # Stop database
db-reset:        # Reset database with fresh data
migrate:         # Apply database migrations
run:             # Start development server
test:            # Run all tests with coverage
test-integration: # Run integration tests only
clean:           # Clean temporary files
```

### File Location Validation
These commands must work correctly from the `svc/` directory:
- `uv sync` (dependency installation)
- `docker-compose up -d` (database startup)
- `uv run python -m uvicorn main:app --reload` (application startup)
- `uv run python -m migrations` (migration execution)

## Environment Setup

Use Docker for database dependencies with docker-compose.yml in svc/ directory.

## Developer Experience

Use `uv` for managing virtual environments, external dependencies, and script running. Do NOT use `pip` or `uv pip` - only uv directly (e.g. `uv add` and `uv sync`).

A `Makefile` with targets for all common tasks (`test`, `run`, etc). When calling these tools, use the uv module calling syntax. Example: `uv run python -m pytest` (notice the call through python)

Use an appropriate .gitignore file to make sure we're avoiding unnecessary files in version control.
