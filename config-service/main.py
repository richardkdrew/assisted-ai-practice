"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from database.connection import db_manager
from database.migrations import migration_manager
from api.v1.applications import router as applications_router
from api.v1.configurations import router as configurations_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Config Service")

    try:
        # Initialize database connection pool
        db_manager.initialize_pool()
        logger.info("Database connection pool initialized")

        # Run database migrations
        await migration_manager.run_migrations()
        logger.info("Database migrations completed")

        yield

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down Config Service")
        db_manager.close_pool()
        logger.info("Database connection pool closed")


# Create FastAPI application
app = FastAPI(
    title="Config Service",
    description="A REST API service for managing application configurations",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(applications_router, prefix="/api/v1", tags=["applications"])

app.include_router(configurations_router, prefix="/api/v1", tags=["configurations"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Config Service API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        migration_status = await migration_manager.get_migration_status()

        return {
            "status": "healthy",
            "database": "connected",
            "migrations": {
                "applied": migration_status["applied_count"],
                "pending": migration_status["pending_count"],
            },
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
