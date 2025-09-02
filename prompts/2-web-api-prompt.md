Create a comprehensive implementation plan for a REST API service called the 'Config Service' based on the following specifications:

The Config Service is a Python application that will use the FastAPI web framework, Pydantic for data modeling and validation, and PostgreSQL as the database. The key requirements are:

- Implement two data models: Application and Configuration, with the specified database table structures and column types.

- Expose the following API endpoints, all prefixed with '/api/v1':

  - Applications: POST, PUT, GET (single), GET (list)
  - Configurations: POST, PUT, GET (single)

- Use psycopg2 directly for database connection pooling and query execution, without an ORM.

- Implement a migration system with a 'migrations' table and SQL migration files.

- Manage service configuration using environment variables parsed by Pydantic-settings.

- Use Pipenv for virtual environment and dependency management.

- Strictly adhere to the specified technology stack versions.

The plan should cover the overall architecture, file/folder structure, API implementation details, database management, configuration handling, and a testing approach. It should not introduce any additional dependencies without approval.

If you need any clarification or have additional questions, please ask. The goal is to create a plan that precisely matches the provided specifications.
