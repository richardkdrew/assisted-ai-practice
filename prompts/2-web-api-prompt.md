# Config Service Implementation Plan Request

Please create a comprehensive implementation plan for a Config Service REST Web API with the following critical requirements. **STRICT ADHERENCE TO ALL DETAILS IN THIS SPECIFICATION IS MANDATORY.**

## Mandatory Tech Stack (MUST use EXACT versions)
- **Language**: Python 3.13.5
- **Web Framework**: Fast API 0.116.1
- **Validation**: Pydantic 2.11.7
- **Service Config**: Pydantic 2.11.7
- **Testing Framework**: pytest 8.4.1
- **Test Coverage**: pytest-cov 6.2.1
- **HTTP Testing**: httpx 0.28.1
- **Database**: PostgreSQL v16
- **Python DB Adapter**: psycopg2 2.9.10
- **Additional Dependencies**:
  - pydantic-settings (>=2.0.0,<3.0.0)
  - python-ulid (>=2.0.0,<3.0.0)

**CRITICAL**: These specific version numbers must be used exactly as specified. Do not add any additional dependencies without explicit approval.

## Project Architecture Requirements

### Project Structure Requirements
**CRITICAL**: With the exception of README and .gitignore files, create ALL other files inside a top-level `svc/` folder of the `config-service` parent folder (e.g., `config-service/svc/`).

### Core Principles
1. **NO ORM**: Implement direct SQL statement management via Repository pattern
2. Create modular, scalable architecture with clear separation of concerns
3. Implement clean, testable code following SOLID principles
4. Focus on dynamic architecture with optimal performance
5. Use design patterns appropriately
6. Follow clean code principles
7. Ensure modular and testable code structure
8. Design for scalability and future growth

### Data Models

#### Applications Table (`applications`)
- **id**: string/ULID (primary key) - use pydantic_extra_types.ulid.ULID
- **name**: unique string(256)
- **comments**: string(1024)

#### Configurations Table (`configurations`)
- **id**: string/ULID (primary key) - use pydantic_extra_types.ulid.ULID
- **application_id**: string/ULID (foreign key to applications.id)
- **name**: string(256) - must be unique per application
- **comments**: string(1024)
- **config**: JSONB dictionary containing name/value pairs

### API Endpoints (All prefixed with `/api/v1`)

#### Applications Endpoints
- `POST /applications` - Create new application
- `PUT /applications/{id}` - Update existing application
- `GET /applications/{id}` - Get application by ID (must include list of all related configuration IDs)
- `GET /applications` - List all applications

#### Configurations Endpoints
- `POST /configurations` - Create new configuration
- `PUT /configurations/{id}` - Update existing configuration
- `GET /configurations/{id}` - Get configuration by ID

### Database Connection Requirements
Implement connection pooling using these specific components:
- `psycopg2.pool.ThreadedConnectionPool`
- `concurrent.futures.ThreadPoolExecutor`
- `contextlib.asynccontextmanager`
- `psycopg2.extras.RealDictCursor` as the cursor_factory

### Migration System Implementation
Create a complete migration system including:
- **migrations** database table with appropriate fields for tracking applied migrations
- **migrations/** folder to contain `*.sql` migration files
- **migrations.py** file implementing the migration system logic
- **migrations_test.py** file with comprehensive tests for the migration system

### Date and Time Handling
- Use the most current Python documentation for date/time operations
- Avoid deprecated APIs
- Reference: https://docs.python.org/3/library/time.html

### Testing Requirements (MANDATORY)
- **ALL code files** MUST have associated unit tests (excluding `__init__.py` files)
- Focus on 80% coverage of the most important scenarios for each file
- Unit tests must use `_test.py` suffix and be located in the same folder as the code being tested
- Only create a `test/` folder if needed for test helpers, mocks, or integration tests

### Configuration Management
- Use `.env` file for environment variables (database connection, logging level, etc.)
- Use `pydantic-settings` (>=2.0.0,<3.0.0) for parsing and validating environment variables

### Developer Experience Requirements
- **Use pipenv exclusively** for:
  - Virtual environment management
  - External dependency installation (`pipenv install` for each dependency)
  - Script running
- **DO NOT use pip or uv** - only pipenv directly
- Create appropriate `.gitignore` file for Python projects

## Implementation Plan Requirements

Your comprehensive plan should include:

1. **Complete project directory structure** with all files and folders
2. **Detailed architectural patterns** and design decisions
3. **Step-by-step implementation approach**
4. **Database schema design** and migration strategy
5. **API endpoint specifications** with request/response models
6. **Testing strategy** and coverage approach
7. **Configuration management** setup
8. **Development workflow** and best practices

## Important Guidelines

- **Ask for clarification** if any requirements are unclear or if you need additional information
- **Do not assume** any requirements not explicitly stated
- **Prioritize** clean interfaces, optimal performance, and maintainability
- **Ensure** all code is modular, testable, and follows separation of concerns
- **Plan for** scalability and future growth
- **Include comments** in code when necessary for clarity

Please provide a detailed implementation plan that addresses all these requirements comprehensively.
