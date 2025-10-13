"""API router modules for the Configuration Service.

This package contains FastAPI router modules for different API endpoints.
"""

from .applications import router as applications_router
from .configurations import router as configurations_router

__all__ = ["applications_router", "configurations_router"]