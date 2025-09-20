"""Test version of main.py that uses SQLite for demonstration."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database_sqlite import test_db_pool
from routers import applications, configurations
from repository_base import ApplicationRepository, ConfigurationRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events for testing."""
    # Startup
    logging.basicConfig(level=getattr(logging, settings.log_level))
    logger = logging.getLogger(__name__)

    logger.info("Starting Configuration Service (Test Mode)")
    test_db_pool.initialize()
    logger.info("SQLite test database initialized")

    yield

    # Shutdown
    logger.info("Shutting down Configuration Service (Test Mode)")
    test_db_pool.close()
    logger.info("SQLite test database closed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application for testing."""
    app = FastAPI(
        title="Configuration Service (Test Mode)",
        description="Centralized configuration management service - SQLite Test Version",
        version="0.1.0",
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create repository instances with test database
    test_app_repository = ApplicationRepository(test_db_pool)
    test_config_repository = ConfigurationRepository(test_db_pool)

    # Monkey patch the repositories in routers
    applications.app_repository = test_app_repository
    configurations.config_repository = test_config_repository

    # Include routers
    app.include_router(
        applications.router,
        prefix=f"{settings.api_prefix}/applications",
        tags=["applications"]
    )
    app.include_router(
        configurations.router,
        prefix=f"{settings.api_prefix}/configurations",
        tags=["configurations"]
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "configuration-service", "mode": "test"}

    return app


# Create the test application instance
app = create_app()