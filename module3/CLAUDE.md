# CLAUDE

## MANDATORY INSTRUCTIONS

**CRITICAL**: If not already done, you MUST read the `AGENTS.md` file NOW during this session BEFORE proceeding with any tasks. This file and other referenced files contain very important context when working with the codebase.

## Project Overview

Configuration Service - A centralized configuration management system built with FastAPI and PostgreSQL. Provides dynamic, flexible configuration handling for software applications with runtime updates without requiring redeployment.

**Current Status**: Working baseline implementation with basic CRUD operations for applications and configurations.

## Project Structure

```
module3/
├── svc/                          # Service code directory
│   ├── main.py                   # FastAPI application entry point
│   ├── config.py                 # Settings management
│   ├── database.py               # Connection pool & utilities
│   ├── models.py                 # Pydantic data models
│   ├── repository.py             # Data access layer (Repository pattern)
│   ├── migrations.py             # Database migration system
│   ├── routers/                  # API endpoint modules
│   │   ├── applications.py       # Application CRUD endpoints
│   │   └── configurations.py     # Configuration CRUD endpoints
│   ├── migrations/               # SQL migration files
│   ├── docker-compose.yml        # Database services
│   ├── pyproject.toml            # Python dependencies
│   └── test_integration.py       # API integration tests
├── memory/                       # Context files for AI assistance
│   ├── ABOUT.md                  # Project overview and vision
│   ├── ARCHITECTURE.md           # Technical architecture details
│   ├── IMPLEMENTATION.md         # Implementation specifics
│   ├── ENV_SCRIPTS.md            # Environment setup and scripts
│   └── WORKFLOW_STATUS.md        # Four-stage development process
├── changes/                      # Working documents for development
└── Makefile                      # Development commands
```

## Common Commands

```bash
# Setup and installation
make install              # Install dependencies with uv

# Database management
make db-up               # Start PostgreSQL with Docker
make db-down             # Stop PostgreSQL
make migrate             # Run database migrations
make db-reset            # Reset database with fresh data

# Development
make run                 # Start FastAPI development server
make test                # Run tests with coverage
make test-integration    # Run integration tests only

# API Testing
curl http://localhost:8000/health                    # Health check
curl http://localhost:8000/docs                      # API documentation
curl http://localhost:8000/api/v1/applications/      # List applications
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

## Quick Reference

### Essential Files
- **Agent instructions**: `AGENTS.md`
- **Memory files**: `memory/` directory (ABOUT, ARCHITECTURE, IMPLEMENTATION, ENV_SCRIPTS, WORKFLOW_STATUS)
- **Settings**: `.claude/settings.local.json`
- **Environment**: `svc/.env` (copy from `svc/.env.example`)
- **Dependencies**: `svc/pyproject.toml`

### API Endpoints
- **Health**: `GET /health`
- **API Docs**: `GET /docs` (Swagger UI)
- **Applications**: `GET|POST|PUT|DELETE /api/v1/applications/`
- **Configurations**: `GET|POST|PUT|DELETE /api/v1/configurations/`

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