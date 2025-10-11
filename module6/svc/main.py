"""Main FastAPI application module."""

import logging
import traceback
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Union

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from opentelemetry import trace

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


def get_trace_id_for_response() -> Dict[str, str]:
    """Extract trace context information for error responses.

    Returns:
        Dictionary with trace_id and request_id
    """
    current_span = trace.get_current_span()
    span_context = current_span.get_span_context()

    if span_context.is_valid:
        trace_id = f"{span_context.trace_id:032x}"
        return {"trace_id": trace_id, "request_id": f"req_{trace_id[:8]}"}

    # Fallback if no valid span context
    return {"trace_id": "unknown", "request_id": "unknown"}


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions with structured error response format.

    Args:
        request: FastAPI request object
        exc: Validation exception

    Returns:
        JSON response with error details and trace information
    """
    # Get current span
    current_span = trace.get_current_span()

    # Record error details to span
    current_span.set_attribute("error", True)
    current_span.set_attribute("error.type", "ValidationError")
    current_span.set_attribute("error.message", str(exc))
    current_span.set_attribute("error.http.status_code", status.HTTP_422_UNPROCESSABLE_ENTITY)
    current_span.set_attribute("http.request.path", request.url.path)
    current_span.set_attribute("http.request.method", request.method)

    # Extract validation error details
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })

    # Get trace context for response
    trace_context = get_trace_id_for_response()

    # Create structured error response
    error_response = {
        "error": {
            "message": "Validation error",
            "type": "ValidationError",
            "details": errors,
            "trace_id": trace_context["trace_id"],
            "request_id": trace_context["request_id"]
        },
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
    }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions with structured error response format.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSON response with error details and trace information
    """
    # Get current span
    current_span = trace.get_current_span()

    # Determine appropriate status code
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if hasattr(exc, "status_code"):
        status_code = exc.status_code

    # Record error details to span
    current_span.set_attribute("error", True)
    current_span.set_attribute("error.type", exc.__class__.__name__)
    current_span.set_attribute("error.message", str(exc))
    current_span.set_attribute("error.http.status_code", status_code)
    current_span.set_attribute("http.request.path", request.url.path)
    current_span.set_attribute("http.request.method", request.method)

    # Record stack trace to span
    stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    current_span.set_attribute("error.stack", stack_trace[:4096])  # Limit to 4KB

    # Get trace context for response
    trace_context = get_trace_id_for_response()

    # Create structured error response
    error_response = {
        "error": {
            "message": str(exc),
            "type": exc.__class__.__name__,
            "trace_id": trace_context["trace_id"],
            "request_id": trace_context["request_id"]
        },
        "status_code": status_code
    }

    # Log the error
    logger = logging.getLogger(__name__)
    logger.error(f"Exception: {exc.__class__.__name__}, Message: {str(exc)}, Trace ID: {trace_context['trace_id']}")

    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


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

    # Register exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

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

    @app.get("/error-test")
    async def test_error():
        """Test error endpoint that raises an exception."""
        raise ValueError("This is a test error to check structured error tracing")

    @app.get("/span-test")
    async def test_span_attributes():
        """Test endpoint that creates a span with custom attributes for testing."""
        try:
            from observability import error_span, tracer
        except ImportError:
            from .observability import error_span, tracer

        # Create a test span with various attributes
        with tracer.start_as_current_span("test_span_attributes") as span:
            # Set standard attributes
            span.set_attribute("test.attribute", "test_value")
            span.set_attribute("test.number", 42)
            span.set_attribute("test.boolean", True)

            # Set error-related attributes
            span.set_attribute("error", True)
            span.set_attribute("error.type", "TestErrorType")
            span.set_attribute("error.message", "Test error message")
            span.set_attribute("error.retriable", False)

            # Add context attributes
            span.set_attribute("http.request.method", "GET")
            span.set_attribute("http.request.path", "/span-test")

            # Return information about the span
            return {
                "message": "Test span created with attributes",
                "span_id": f"{span.get_span_context().span_id:016x}",
                "trace_id": f"{span.get_span_context().trace_id:032x}",
                "attributes": {
                    "test.attribute": "test_value",
                    "test.number": 42,
                    "test.boolean": True,
                    "error": True,
                    "error.type": "TestErrorType",
                    "error.message": "Test error message",
                    "error.retriable": False,
                }
            }

    @app.get("/error-span-test")
    async def test_error_span():
        """Test endpoint that uses the error_span context manager."""
        try:
            from observability import error_span
        except ImportError:
            from .observability import error_span

        try:
            with error_span("test_error_span_operation", test_attribute="test_value"):
                # Simulate an operation that fails
                raise ValueError("Simulated error for testing error_span")
        except Exception as e:
            # Catch the exception but return details about what happened
            return {
                "message": "Error span test completed",
                "exception_caught": str(e),
                "exception_type": e.__class__.__name__,
                "note": "The error was caught but the span should have error attributes"
            }

            # Set error-related attributes
            span.set_attribute("error", True)
            span.set_attribute("error.type", "TestErrorType")
            span.set_attribute("error.message", "Test error message")
            span.set_attribute("error.retriable", False)

            # Add context attributes
            span.set_attribute("http.request.method", "GET")
            span.set_attribute("http.request.path", "/span-test")

            # Return information about the span
            return {
                "message": "Test span created with attributes",
                "span_id": f"{span.get_span_context().span_id:016x}",
                "trace_id": f"{span.get_span_context().trace_id:032x}",
                "attributes": {
                    "test.attribute": "test_value",
                    "test.number": 42,
                    "test.boolean": True,
                    "error": True,
                    "error.type": "TestErrorType",
                    "error.message": "Test error message",
                    "error.retriable": False,
                }
            }

    @app.get("/error-test/{error_type}")
    async def test_error_by_type(error_type: str):
        """Test endpoint that raises different types of errors for testing error categorization.

        Valid error types:
        - validation: ValidationError (permanent)
        - connection: ConnectionError (retriable)
        - timeout: TimeoutError (retriable)
        - notfound: HTTPException 404 (permanent)
        - unavailable: HTTPException 503 (retriable)
        """
        if error_type == "validation":
            from pydantic import ValidationError, BaseModel, Field
            # Create a validation error by actually validating an invalid model
            class TestModel(BaseModel):
                value: int = Field(gt=0)

            # This will raise a ValidationError when we try to validate -1
            TestModel.model_validate({"value": -1})

        elif error_type == "connection":
            raise ConnectionError("Test connection error (retriable)")

        elif error_type == "timeout":
            raise TimeoutError("Test timeout error (retriable)")

        elif error_type == "notfound":
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Resource not found (permanent)")

        elif error_type == "unavailable":
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Service temporarily unavailable (retriable)")

        else:
            return {"message": f"Unknown error type '{error_type}'. Valid types are: validation, connection, timeout, notfound, unavailable"}


    return app


# Create the application instance
app = create_app()