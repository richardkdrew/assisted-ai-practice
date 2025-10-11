# CLAUDE

## MANDATORY INSTRUCTIONS

> **MANDATORY**: All development MUST follow the constitutional requirements defined in `.specify/memory/constitution.md`. The constitution supersedes all other development practices and contains mandatory requirements for specification-first development, TDD, progress tracking with TodoWrite, and architectural consistency.

**CRITICAL**: Read the following context files at the start of each session:

- `memory/ARCHITECTURE.md` - Complete technical reference and implementation patterns

## Project Overview

Configuration Service - A centralized configuration management system built with FastAPI and PostgreSQL. Provides dynamic, flexible configuration handling for software applications with runtime updates without requiring redeployment.

**Current Status**: Working baseline implementation with basic CRUD operations for applications and configurations.

## Project Structure

```bash
module6/
├── svc/                          # Service code directory
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Settings management
│   ├── database.py               # Connection pool & utilities
│   ├── models.py                 # Pydantic data models
│   ├── repository.py             # Data access layer (Repository pattern)
│   ├── migrations.py             # Database migration system
│   ├── observability.py          # OpenTelemetry & error tracing implementation
│   ├── error_tracing_test.py     # Tests for error tracing functionality
│   ├── routers/                  # API endpoint modules
│   │   ├── applications.py       # Application CRUD endpoints
│   │   └── configurations.py     # Configuration CRUD endpoints
│   ├── migrations/               # SQL migration files
│   ├── observability/            # Observability configuration files
│   │   ├── otel-collector.yml    # OpenTelemetry collector config
│   │   ├── prometheus.yml        # Prometheus config
│   │   └── grafana/              # Grafana dashboards and datasources
│   ├── docker-compose.yml        # Services configuration (DB, OTEL, Jaeger, etc.)
│   ├── pyproject.toml            # Python dependencies
│   └── test_integration.py       # API integration tests
├── .specify/                     # Project specifications
│   └── memory/                   # Context files
│       └── constitution.md       # Development constitution
├── specs/                        # Feature specifications
│   └── 001-structured-error-tracing/ # Error tracing specification
└── Makefile                      # Development commands
```

## Common Commands

```bash
# Quick Start - Complete Development Stack
make dev                 # Start everything (DB + API + Observability + UI)
make dev-stop            # Stop all services

# Setup and installation
make install             # Install backend dependencies with uv
make ui-install          # Install frontend dependencies with npm

# Development (Individual Components)
make dev-backend         # Start backend stack only (DB + API + Observability)
make dev-ui-only         # Start UI only (assumes backend running)

# Testing
make test                # Run backend tests with coverage
make ui-test             # Run UI unit tests
make ui-test-e2e         # Run UI E2E tests (requires backend running)
make quality             # Run complete quality validation

# Database management
make migrate             # Run database migrations
make db-reset            # Reset database with fresh data
make db-shell            # Connect to PostgreSQL shell

# Observability
make grafana             # Open Grafana dashboards (http://localhost:3001)
make prometheus          # Open Prometheus (http://localhost:9090)

# Service URLs (after running 'make dev')
# - API:        http://localhost:8000
# - API Docs:   http://localhost:8000/docs
# - UI:         http://localhost:5173
# - Prometheus: http://localhost:9090
# - Grafana:    http://localhost:3001 (admin/admin)
```

## Architecture Overview

- **Web Framework**: FastAPI 0.116.1 (async/await, auto OpenAPI docs)
- **Database**: PostgreSQL 16 (JSONB for flexible config storage)
- **Data Access**: Repository pattern with direct SQL (no ORM)
- **Primary Keys**: ULID (Universally Unique Lexicographically Sortable)
- **Connection Pool**: psycopg2 ThreadedConnectionPool with RealDictCursor
- **Validation**: Pydantic 2.11.7 for request/response validation

**Key Design Decisions**:

- No ORM for performance and SQL control
- ULID strings for better database performance than UUIDs
- Async/await throughout the stack
- JSONB storage for flexible configuration schemas

## Environment Setup

1. **Prerequisites**: Python 3.13.5, Docker, uv package manager
2. **Setup**: `make install` → `make db-up` → `make migrate` → `make run`
3. **Configuration**: Copy `svc/.env.example` to `svc/.env` (defaults work for development)
4. **Verification**: `curl http://localhost:8000/health` should return `{"status":"healthy"}`

## Technology Stack

- **Language**: Python 3.13.5
- **Web Framework**: FastAPI 0.116.1
- **Database**: PostgreSQL 16
- **Database Adapter**: psycopg2-binary 2.9.10
- **Validation**: Pydantic 2.11.7 + pydantic-settings 2.6.1
- **Testing**: pytest 8.4.1, pytest-cov 6.2.1, httpx 0.28.1
- **Package Management**: uv (fast Python package management)
- **Primary Keys**: ULID via pydantic-extra-types 2.10.1 + ulid-py 1.1.0
- **Observability**:
  - OpenTelemetry 1.37.0 (distributed tracing)
  - Prometheus (metrics collection)
  - Jaeger (trace visualization)
  - OpenTelemetry Collector (trace processing)

## Quick Reference

### Essential Files

- **Context files**: `memory/ARCHITECTURE.md` and `memory/WORKFLOW_STATUS.md`
- **Engineering principles**: `PRINCIPLES.md`
- **Settings**: `.claude/settings.local.json`
- **Environment**: `svc/.env` (copy from `svc/.env.example`)
- **Dependencies**: `svc/pyproject.toml`

### API Endpoints

- **Health**: `GET /health`
- **API Docs**: `GET /docs` (Swagger UI)
- **Applications**: `GET|POST|PUT|DELETE /api/v1/applications/`
- **Configurations**: `GET|POST|PUT|DELETE /api/v1/configurations/`
- **Metrics**: `GET /metrics` (Prometheus metrics)
- **Test Endpoints**:
  - `GET /error-test` (Test error tracing)
  - `GET /error-test/{error_type}` (Test specific error types)
  - `GET /error-span-test` (Test error_span context manager)
  - `GET /span-test` (Test custom span attributes)

### Development Workflow

1. **Planning**: Create working document in `changes/` directory
2. **Implementation**: Follow four-stage process (PLAN → BUILD & ASSESS → REFLECT & ADAPT → COMMIT & PICK NEXT)
3. **Testing**: Run `make test` for comprehensive testing including integration tests
4. **Quality**: All operations must pass quality validation cleanly

### Important Context

- **Current Stage**: Stage 2: BUILD & ASSESS (working baseline achieved)
- **Test Coverage**: 80%+ target with comprehensive integration tests
- **No ORM**: Direct SQL with Repository pattern for performance
- **ULID Format**: String representations throughout API (validated at boundaries)
- **Configuration Storage**: JSONB in PostgreSQL for flexible schemas
- **Error Tracing**: Structured error responses with OpenTelemetry integration

### Observability Features

The service includes robust observability features for production monitoring and debugging:

- **Structured Error Tracing**: All errors include trace IDs and structured details
- **OpenTelemetry Integration**: Distributed tracing with spans and attributes
- **Error Categorization**: Errors are classified as retriable or permanent
- **Jaeger Integration**: Visualize traces and errors in Jaeger UI
- **Prometheus Metrics**: Service metrics exposed for monitoring

#### Error Response Format

Error responses follow a consistent format:

```json
{
  "error": {
    "message": "Error message",
    "type": "ErrorType",
    "trace_id": "trace_id_for_correlation",
    "request_id": "request_id_for_tracking"
  },
  "status_code": 400
}
```

Trace context is also included in response headers:
- `X-Request-ID`: Request identifier for correlation
- `traceparent`: W3C Trace Context for distributed tracing
