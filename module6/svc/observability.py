"""OpenTelemetry instrumentation for Configuration Service."""

import os
import traceback
import uuid
import json
import requests
import psycopg2
from typing import Optional, Dict, Any
from contextlib import contextmanager

from opentelemetry import trace, metrics, baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.status import Status, StatusCode
# Simplify to use only the trace context propagator that we know exists
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
DB_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')
CONFIG_COUNT = Gauge('configurations_total', 'Total number of configurations')
APP_COUNT = Gauge('applications_total', 'Total number of applications')


def setup_observability(app):
    """Set up OpenTelemetry and Prometheus metrics for the FastAPI application."""

    # Resource identification
    resource = Resource.create({
        "service.name": "configuration-service",
        "service.version": "1.0.0",
        "service.environment": os.getenv("ENVIRONMENT", "development"),
    })

    # Configure tracing
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()

    # Configure propagator for distributed tracing
    # Using only the TraceContextTextMapPropagator which is standard and should be available
    set_global_textmap(TraceContextTextMapPropagator())

    # OTLP exporter for traces
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"),
        insecure=True
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Configure metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317"),
            insecure=True
        ),
        export_interval_millis=5000,
    )
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument requests library
    RequestsInstrumentor().instrument()

    # Instrument psycopg2 for database monitoring
    Psycopg2Instrumentor().instrument()

    # Add Prometheus metrics endpoint
    @app.get("/metrics")
    async def metrics_endpoint():
        """Prometheus metrics endpoint."""
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # Add middleware for request metrics
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        method = request.method
        path = request.url.path

        # Start timing
        import time
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Record metrics
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=path, status_code=response.status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=path).observe(duration)

        return response

    # Add error tracking middleware
    app.add_middleware(ErrorTrackingMiddleware)


def update_business_metrics(applications_count: int, configurations_count: int, active_connections: int):
    """Update business and infrastructure metrics."""
    APP_COUNT.set(applications_count)
    CONFIG_COUNT.set(configurations_count)
    DB_CONNECTIONS.set(active_connections)


# Helper functions for error tracing
def truncate_error_payload(payload: str, max_size: int = 10240) -> str:
    """Truncate error payload to fit within the size limit (10KB by default).

    Args:
        payload: The string payload to truncate
        max_size: Maximum size in bytes (default: 10KB)

    Returns:
        Truncated string with indicator if truncation occurred
    """
    if len(payload) <= max_size:
        return payload

    truncated = payload[:max_size]
    return f"{truncated}... [truncated, original size: {len(payload)} bytes]"

def extract_request_id(request: Request) -> str:
    """Extract request ID from trace context or generate a new one.

    Args:
        request: FastAPI request object

    Returns:
        Request ID string
    """
    # Try to get from trace context first
    current_span = trace.get_current_span()
    span_context = current_span.get_span_context()

    if span_context.is_valid:
        # Use trace ID as request ID for correlation
        return f"{span_context.trace_id:032x}"

    # Generate a new ID if no valid context
    return f"req_{uuid.uuid4().hex}"

def get_http_context(request: Request) -> Dict[str, Any]:
    """Extract HTTP context information from the request.

    Args:
        request: FastAPI request object

    Returns:
        Dictionary with HTTP context attributes
    """
    return {
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "request_id": extract_request_id(request)
    }

def is_retriable_error(exception: Exception) -> bool:
    """Determine if an error is retriable (transient) or permanent.

    Categorizes exceptions as retriable (temporary) or permanent to help with
    retry decision-making and observability.

    Args:
        exception: The exception to categorize

    Returns:
        True if the error is retriable, False if it's permanent
    """
    # Common retriable error types (connection, timeout, and similar transient errors)
    retriable_error_types = (
        ConnectionError,
        TimeoutError,
        # Request-related errors
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.RetryError,
        # Database connection issues
        psycopg2.OperationalError,
        # Include any custom service unavailable errors
        # ServiceUnavailableError,
    )

    # Explicitly define permanent (non-retriable) error types for clarity
    permanent_error_types = (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        # Validation errors
        "ValidationError",  # Check by name since imports might vary
        "RequestValidationError",
        # Authentication errors
        "AuthenticationError",
        "NotAuthenticatedError",
        # Permission errors
        "PermissionDeniedError",
        "ForbiddenError",
    )

    # Check if error type is explicitly listed as permanent
    if exception.__class__.__name__ in permanent_error_types:
        return False

    # For HTTP errors, some status codes indicate retriable errors
    if hasattr(exception, "status_code"):
        retriable_status_codes = {408, 425, 429, 500, 502, 503, 504}
        if exception.status_code in retriable_status_codes:
            return True

        # Non-retriable HTTP status codes
        permanent_status_codes = {400, 401, 403, 404, 405, 422}
        if exception.status_code in permanent_status_codes:
            return False

    # Check if the exception is an instance of any retriable error types
    if isinstance(exception, retriable_error_types):
        return True

    # By default, errors are not retriable
    return False

def record_exception_to_span(span, exception: Exception, http_context: Optional[Dict[str, Any]] = None) -> None:
    """Record exception details to the current span.

    Args:
        span: OpenTelemetry span object
        exception: The exception that occurred
        http_context: Optional HTTP context dictionary
    """
    # Set span status to ERROR
    span.set_status(Status(StatusCode.ERROR))

    # Basic error attributes
    span.set_attribute("error", True)
    span.set_attribute("error.type", exception.__class__.__name__)
    span.set_attribute("error.message", str(exception))

    # Determine if error is retriable
    is_retriable = is_retriable_error(exception)
    span.set_attribute("error.retriable", is_retriable)

    # Add stack trace (truncated)
    stack_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    span.set_attribute("error.stack", truncate_error_payload(stack_trace, 4096))  # 4KB max for stack trace

    # Add HTTP context if available
    if http_context:
        for key, value in http_context.items():
            span.set_attribute(f"http.request.{key}", value)

    # Record the exception for OpenTelemetry
    span.record_exception(exception)


class ErrorTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking errors and attaching trace context to responses."""

    async def dispatch(self, request: Request, call_next):
        """Process the request and capture any errors that occur.

        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in the chain

        Returns:
            Response object
        """
        # Get current span for this request
        current_span = trace.get_current_span()

        # Extract request context for error reporting
        http_context = get_http_context(request)
        request_id = http_context["request_id"]

        try:
            # Process the request
            response = await call_next(request)

            # Add trace context to all responses
            response.headers["X-Request-ID"] = request_id
            response.headers["traceparent"] = f"00-{current_span.get_span_context().trace_id:032x}-{current_span.get_span_context().span_id:016x}-01"

            # If error status code, record error details
            if response.status_code >= 400:
                current_span.set_attribute("error", True)
                current_span.set_attribute("error.http.status_code", response.status_code)
                for key, value in http_context.items():
                    current_span.set_attribute(f"http.request.{key}", value)

            return response

        except Exception as e:
            # Record exception details to span
            record_exception_to_span(current_span, e, http_context)

            # Create JSON error response with trace information
            error_response = {
                "error": {
                    "message": str(e),
                    "type": e.__class__.__name__,
                    "trace_id": f"{current_span.get_span_context().trace_id:032x}",
                    "request_id": request_id
                },
                "status_code": 500
            }

            response = JSONResponse(
                status_code=500,
                content=error_response
            )

            # Add trace context to error response
            response.headers["X-Request-ID"] = request_id
            response.headers["traceparent"] = f"00-{current_span.get_span_context().trace_id:032x}-{current_span.get_span_context().span_id:016x}-01"

            return response


# Tracer instance for manual instrumentation
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Context manager for error spans
@contextmanager
def error_span(operation_name, **attributes):
    """Context manager for creating spans that automatically track errors.

    Args:
        operation_name: Name of the operation being performed
        **attributes: Additional span attributes

    Yields:
        The active span
    """
    with tracer.start_as_current_span(operation_name) as span:
        # Set initial span attributes
        for key, value in attributes.items():
            span.set_attribute(key, value)

        try:
            yield span
        except Exception as e:
            # Record error to span
            record_exception_to_span(span, e)
            raise