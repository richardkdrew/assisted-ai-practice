"""Main FastAPI application module."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from .config import settings
    from .database import db_pool
    from .routers import applications, configurations
    from .observability import setup_observability
except ImportError:
    from config import settings
    from database import db_pool
    from routers import applications, configurations
    from observability import setup_observability


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logging.basicConfig(level=getattr(logging, settings.log_level))
    logger = logging.getLogger(__name__)

    logger.info("Starting Configuration Service")
    db_pool.initialize()
    logger.info("Database pool initialized")

    yield

    # Shutdown
    logger.info("Shutting down Configuration Service")
    db_pool.close()
    logger.info("Database pool closed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Configuration Service",
        description="Centralized configuration management service",
        version="0.1.0",
        lifespan=lifespan
    )

    # Setup observability
    setup_observability(app)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
        return {"status": "healthy", "service": "configuration-service"}


    return app


# Create the application instance
app = create_app()