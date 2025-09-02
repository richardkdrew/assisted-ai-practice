Project Structure:

- Create a new Python project directory called 'config-service'

- Within this directory, create the following folders and files:

  - `config-service/`

    - `__init__.py`

    - `main.py` (entry point)

    - `api/`

      - `__init__.py`
      - `applications.py`
      - `configurations.py`

    - `models/`

      - `__init__.py`
      - `application.py`
      - `configuration.py`

    - `db/`

      - `__init__.py`

      - `connection.py`

      - `migrations/`

        - `__init__.py`
        - `migrations.py`
        - `migrations_test.py`
        - `0001_initial.sql`

    - `settings.py`

    - `requirements.txt`

    - `Pipfile`

    - `Pipfile.lock`

Dependencies:

- Use Pipenv to manage the virtual environment and dependencies

- Install the following packages:

  - `fastapi==0.116.1`
  - `pydantic==2.11.7`
  - `pydantic-settings==2.0.0`
  - `psycopg2-binary==2.9.10`
  - `python-ulid==2.1.0`
  - `pytest==8.4.1`
  - `httpx==0.28.1`

Architecture:

- Use the FastAPI web framework to implement the REST API
- Utilize Pydantic for data modeling and validation
- Manage database connections and queries directly using psycopg2
- Implement a migration system using SQL files and a migrations management module

API Endpoints:

- Implement the following API endpoints as specified:

  - `/api/v1/applications`
    - POST, PUT, GET (single), GET (list)
  - `/api/v1/configurations`
    - POST, PUT, GET (single)

Database:

- Use PostgreSQL as the database engine
- Implement the Application and Configuration data models as specified
- Create a connection pool using `psycopg2.pool.ThreadedConnectionPool` and `concurrent.futures.ThreadPoolExecutor`
- Implement the migration system with a `migrations` table and SQL migration files

Configuration:

- Use a `.env` file and Pydantic-settings to manage environment variables
- Store variables such as the database connection string, logging level, etc.

Testing:

- Use pytest as the testing framework
- Implement unit tests for the API endpoints, data models, and database migration system
- Use httpx to test the API endpoints
