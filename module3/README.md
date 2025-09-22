# Configuration Service

A centralized configuration management system that provides dynamic, flexible configuration handling for software applications. Enables runtime configuration updates without requiring application redeployment.

## Features

- **Centralized Configuration Management**: Single source of truth for application configurations
- **Dynamic Updates**: Runtime configuration changes without service interruption
- **Multi-Application Support**: Manage configurations for multiple applications
- **RESTful API**: Complete CRUD operations via REST endpoints
- **ULID Primary Keys**: Universally unique, lexicographically sortable identifiers
- **Repository Pattern**: Direct SQL queries without ORM overhead
- **Comprehensive Testing**: 80%+ test coverage with pytest

## Tech Stack

- **Language**: Python 3.13.5
- **Web Framework**: FastAPI 0.116.1
- **Validation**: Pydantic 2.11.7
- **Database**: PostgreSQL v16
- **Database Adapter**: psycopg2 2.9.10
- **Testing**: pytest 8.4.1, pytest-cov 6.2.1, httpx 0.28.1
- **Package Management**: uv

## Quick Start

### Prerequisites

- Python 3.13.5
- PostgreSQL 16 (or Docker)
- uv package manager

### Setup

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd configuration-service
   make install
   ```

2. **Start PostgreSQL database**:
   ```bash
   make db-up
   ```

3. **Run database migrations**:
   ```bash
   make migrate
   ```

4. **Start the service**:
   ```bash
   make run
   ```

The service will be available at `http://localhost:8000`

### Development Commands

```bash
# Install dependencies
make install

# Run tests with coverage
make test

# Run integration tests only
make test-integration

# Run the development server
make run

# Database management
make db-up      # Start PostgreSQL with Docker Compose
make db-down    # Stop PostgreSQL
make db-reset   # Reset database with fresh data
make migrate    # Run migrations
make db-shell   # Connect to database shell

# Code quality
make format     # Format code
make lint       # Run linting
make coverage   # Generate coverage report

# Cleanup
make clean      # Remove temporary files
```

## API Documentation

Once running, visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### API Endpoints

**Applications** (`/api/v1/applications`):
- `POST /` - Create application
- `GET /{id}` - Get application (includes configuration IDs)
- `PUT /{id}` - Update application
- `GET /` - List applications (paginated)
- `DELETE /{id}` - Delete application

**Configurations** (`/api/v1/configurations`):
- `POST /` - Create configuration
- `GET /{id}` - Get configuration
- `PUT /{id}` - Update configuration
- `DELETE /{id}` - Delete configuration

## Data Models

### Application
```json
{
  "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "name": "my-web-app",
  "comments": "Main web application",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "configuration_ids": ["01ARZ3NDEKTSV4RRFFQ69G5FAV"]
}
```

### Configuration
```json
{
  "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "application_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "name": "database-config",
  "comments": "Database connection settings",
  "config": {
    "host": "localhost",
    "port": 5432,
    "ssl": true,
    "pool_size": 20
  },
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## Configuration

Copy `svc/.env.example` to `svc/.env` and adjust settings:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/configservice
DB_HOST=localhost
DB_PORT=5432
DB_NAME=configservice
DB_USER=user
DB_PASSWORD=password

# Application Configuration
LOG_LEVEL=INFO
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000
```

## Architecture

- **No ORM**: Direct SQL queries with Repository pattern
- **Connection Pooling**: ThreadedConnectionPool with RealDictCursor
- **Migration System**: SQL-based migrations with tracking
- **ULID Primary Keys**: Sortable, unique identifiers
- **Pydantic Validation**: Request/response validation and settings
- **Async/Await**: AsyncContextManager for database operations

## Testing

Run the complete test suite:

```bash
make test
```

Run only integration tests:

```bash
make test-integration
```

Generate coverage report:

```bash
make coverage
```

Tests include:
- **Unit tests**: All modules with 80%+ coverage target
- **Integration tests**: Complete API-to-database flow testing
- **Model validation tests**: Pydantic model validation
- **Migration system tests**: Database schema management
- **API endpoint tests**: FastAPI route testing
- **Configuration validation tests**: Settings and environment handling

## Project Structure

```
├── Makefile            # Development commands
├── README.md           # Project documentation
└── svc/                # Service code directory
    ├── docker-compose.yml # Database services
    ├── pyproject.toml     # Python project config
    ├── .env.example       # Environment template
    ├── __init__.py
    ├── main.py         # FastAPI application
    ├── config.py       # Settings management
    ├── database.py     # Connection pool
    ├── migrations.py   # Migration runner
    ├── models.py       # Pydantic models
    ├── repository.py   # Data access layer
    ├── routers/
    │   ├── __init__.py
    │   ├── applications.py     # Application endpoints
    │   └── configurations.py  # Configuration endpoints
    ├── migrations/
    │   └── 001_initial_schema.sql
    ├── test_integration.py     # API integration tests
    └── *_test.py              # Unit tests
```

## License

[License details here]