# Configuration Service Architecture

## Overview

The Configuration Service is built using a modern Python web stack with FastAPI and PostgreSQL, following a Repository pattern architecture that prioritizes direct SQL operations over ORM abstractions for performance and control.

## Technology Stack

### Core Components
- **Web Framework**: FastAPI 0.116.1 (async/await support, automatic OpenAPI documentation)
- **Database**: PostgreSQL 16 (JSONB support for flexible configuration storage)
- **Database Adapter**: psycopg2-binary 2.9.10 (PostgreSQL connectivity with connection pooling)
- **Validation**: Pydantic 2.11.7 (request/response validation and settings management)
- **Testing**: pytest 8.4.1 with pytest-cov 6.2.1 and httpx 0.28.1
- **Package Management**: uv (fast Python package management)

### Key Design Decisions
- **No ORM**: Direct SQL queries with Repository pattern for performance and SQL control
- **ULID Primary Keys**: Universally Unique Lexicographically Sortable Identifiers for better performance than UUIDs
- **Connection Pooling**: ThreadedConnectionPool for efficient database resource management
- **Async/Await**: Full async support throughout the application stack

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Repository    │    │   PostgreSQL    │
│                 │    │     Layer       │    │    Database     │
│  ┌───────────┐  │    │                 │    │                 │
│  │ Routers   │  │◄──►│  ┌───────────┐  │◄──►│  ┌───────────┐  │
│  └───────────┘  │    │  │Application│  │    │  │applications│  │
│  ┌───────────┐  │    │  │Repository │  │    │  │    table   │  │
│  │ Models    │  │    │  └───────────┘  │    │  └───────────┘  │
│  └───────────┘  │    │  ┌───────────┐  │    │  ┌───────────┐  │
│  ┌───────────┐  │    │  │Config     │  │    │  │configurations│  │
│  │ Database  │  │    │  │Repository │  │    │  │    table   │  │
│  │ Pool      │  │    │  └───────────┘  │    │  └───────────┘  │
│  └───────────┘  │    │                 │    │  ┌───────────┐  │
└─────────────────┘    └─────────────────┘    │  │migrations │  │
                                              │  │   table   │  │
                                              │  └───────────┘  │
                                              └─────────────────┘
```

## Directory Structure

```
svc/                              # Service root directory
├── main.py                       # FastAPI application entry point
├── config.py                     # Settings and configuration management
├── database.py                   # Connection pool and database utilities
├── models.py                     # Pydantic data models
├── repository.py                 # Data access layer (Repository pattern)
├── migrations.py                 # Database migration system
├── docker-compose.yml            # Database services
├── pyproject.toml               # Python project configuration
├── .env.example                 # Environment template
├── routers/                     # API endpoint modules
│   ├── __init__.py
│   ├── applications.py          # Application CRUD endpoints
│   └── configurations.py       # Configuration CRUD endpoints
├── migrations/                  # SQL migration files
│   └── 001_initial_schema.sql   # Initial database schema
├── test_integration.py          # API integration tests
└── *_test.py                   # Unit test files
```

## Database Schema

### Applications Table
```sql
CREATE TABLE applications (
    id VARCHAR(26) PRIMARY KEY,           -- ULID string format
    name VARCHAR(256) UNIQUE NOT NULL,    -- Unique application name
    comments VARCHAR(1024),               -- Optional comments
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### Configurations Table
```sql
CREATE TABLE configurations (
    id VARCHAR(26) PRIMARY KEY,           -- ULID string format
    application_id VARCHAR(26) NOT NULL   -- Foreign key to applications
        REFERENCES applications(id) ON DELETE CASCADE,
    name VARCHAR(256) NOT NULL,           -- Configuration name
    comments VARCHAR(1024),               -- Optional comments
    config JSONB NOT NULL,                -- Configuration data as JSONB
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(application_id, name)          -- Unique name per application
);
```

### Indexes
```sql
CREATE INDEX idx_configurations_application_id ON configurations(application_id);
CREATE INDEX idx_configurations_name ON configurations(name);
CREATE INDEX idx_configurations_config ON configurations USING GIN(config);
```

## API Architecture

### Endpoint Structure
- **Base Path**: `/api/v1`
- **Applications**: `/api/v1/applications/`
- **Configurations**: `/api/v1/configurations/`
- **Health Check**: `/health`
- **Documentation**: `/docs` (automatic Swagger UI)

### Request/Response Flow
1. **Request Validation**: Pydantic models validate incoming JSON
2. **Router Processing**: FastAPI routers handle HTTP routing and parameter extraction
3. **ULID Validation**: String ULIDs validated for format correctness
4. **Repository Operations**: Repository layer executes SQL queries with connection pooling
5. **Response Serialization**: Pydantic models serialize responses to JSON

## Data Access Layer

### Repository Pattern Implementation
- **ApplicationRepository**: Handles all application-related database operations
- **ConfigurationRepository**: Handles all configuration-related database operations
- **Direct SQL**: No ORM - all database operations use direct SQL queries
- **Connection Management**: AsyncContextManager pattern for database connections
- **Transaction Handling**: Automatic commit/rollback with proper error handling

### Database Operations
- **execute_query()**: SELECT operations (read-only, no commit)
- **execute_command()**: INSERT/UPDATE/DELETE operations (with commit)
- **execute_returning()**: INSERT/UPDATE operations with RETURNING clause (with commit)

## Configuration Storage Model

### JSONB Storage
- **Flexible Schema**: Configurations stored as JSONB for arbitrary key-value structures
- **Query Capabilities**: GIN index enables efficient querying of configuration content
- **Type Safety**: Pydantic models ensure type validation at API boundaries
- **Serialization**: Automatic JSON serialization/deserialization in repository layer

### Configuration Relationships
- **One-to-Many**: Applications can have multiple configurations
- **Unique Names**: Configuration names must be unique within each application
- **Cascading Deletes**: Deleting an application removes all its configurations
- **Referential Integrity**: Foreign key constraints ensure data consistency

## Security & Validation

### Input Validation
- **Pydantic Models**: Type-safe request/response validation
- **ULID Format**: Strict ULID format validation for all ID parameters
- **SQL Injection Prevention**: Parameterized queries throughout
- **Length Limits**: String field length constraints (names: 256 chars, comments: 1024 chars)

### Error Handling
- **HTTP Status Codes**: Proper status codes for different error conditions
- **Validation Errors**: Detailed validation error messages via Pydantic
- **Database Errors**: Constraint violation handling with user-friendly messages
- **404 Handling**: Not found responses for missing resources

## Performance Considerations

### Database Performance
- **Connection Pooling**: ThreadedConnectionPool (configurable min/max connections)
- **Index Strategy**: Strategic indexes on foreign keys, names, and JSONB content
- **Direct SQL**: No ORM overhead for better query performance
- **ULID Benefits**: Lexicographically sortable, better than UUIDs for database performance

### API Performance
- **Async/Await**: Full async support for non-blocking I/O
- **Pagination**: Built-in pagination for list endpoints
- **Minimal Serialization**: Direct dict-to-JSON conversion where possible
- **Health Checks**: Lightweight health endpoint for monitoring

## Monitoring & Observability

### Health Monitoring
- **Health Endpoint**: `/health` provides service status
- **Database Pool Status**: Connection pool health monitoring
- **Application Lifecycle**: Startup/shutdown event handling

### Logging
- **Structured Logging**: Python logging with configurable levels
- **Database Operations**: Query logging and error tracking
- **Request/Response**: FastAPI automatic request logging
- **Error Tracking**: Comprehensive exception logging with context

## Deployment Architecture

### Container Strategy
- **Database Service**: PostgreSQL 16 via Docker Compose
- **Application Service**: FastAPI application (development server)
- **Environment Configuration**: `.env` file based configuration
- **Package Management**: uv for fast, reliable dependency management

### Environment Management
- **Settings**: Pydantic Settings for environment-based configuration
- **Database URL**: Configurable database connection parameters
- **Development Mode**: Hot reload with uvicorn for development

## Extension Points

### Future Architecture Considerations
- **Authentication**: JWT/OAuth integration points identified
- **Caching**: Redis integration for configuration caching
- **Message Queue**: Event-driven configuration updates
- **Multi-tenancy**: Tenant isolation patterns
- **Configuration Versioning**: Historical configuration tracking
- **Configuration Templates**: Template-based configuration generation

### API Versioning Strategy
- **URL Versioning**: `/api/v1/` prefix for version management
- **Backward Compatibility**: Strategy for maintaining older API versions
- **Migration Paths**: Clear upgrade paths for API consumers

---

*This architecture document reflects the current implementation state and serves as a reference for understanding the system design and technical decisions made during development.*