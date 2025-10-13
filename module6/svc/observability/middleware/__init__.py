"""Error tracking middleware for OpenTelemetry.

This package provides middleware for tracking errors in FastAPI applications
using OpenTelemetry for distributed tracing.
"""

from .error_tracking import (
    ErrorTrackingMiddleware,
    record_exception_to_span,
    is_retriable_error,
    get_http_context,
    extract_request_id,
    truncate_error_payload
)

__all__ = [
    "ErrorTrackingMiddleware",
    "record_exception_to_span",
    "is_retriable_error",
    "get_http_context",
    "extract_request_id",
    "truncate_error_payload"
]