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

## Project Structure

With exception to the README nd the .gitignore file, creaet all other files inside a top level svc folder of the config-service parent folder e.g. config-service/svc/

# Database Environment

Use Docker for the database dependencies

## Developer Experience

Use `pipenv` for managing virtual environments, external dependencies, and script running. Do NOT use `pip` or `uv` - only pipenv directly (e.g. `pipenv install` for each dependency). Make sure to run `pipenv install` for each dependency

Use an appropriate .gitignore file to make sure we're avoiding unnecessary files in version control.

## Notes

1. Focus on dynamic architecture
2. Clean interfaces
3. Optimal performance
4. Use design patterns
5. Follow clean code principles
6. Separation of concerns
7. Modular and testable code
8. Ensure scalability for future growth
9. Use comments when needed

