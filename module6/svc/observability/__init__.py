"""OpenTelemetry instrumentation for Configuration Service.

This package provides observability features including:
- Distributed tracing with OpenTelemetry
- Prometheus metrics collection
- Error tracking middleware
- Trace storage and querying
"""

from .setup import setup_observability
from .spans import error_span, tracer, meter
from .metrics import update_business_metrics
from .middleware import (
    ErrorTrackingMiddleware,
    record_exception_to_span,
    truncate_error_payload,
    get_http_context,
    extract_request_id,
    is_retriable_error
)

__all__ = [
    "setup_observability",
    "error_span",
    "tracer",
    "meter",
    "update_business_metrics",
    "ErrorTrackingMiddleware",
    "record_exception_to_span",
    "truncate_error_payload",
    "get_http_context",
    "extract_request_id",
    "is_retriable_error"
]