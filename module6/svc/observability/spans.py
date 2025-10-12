"""Span utilities for observability.

This module provides utilities for working with OpenTelemetry spans,
including error tracking and context managers.
"""

from contextlib import contextmanager
from opentelemetry import trace, metrics
from .middleware.error_tracking import record_exception_to_span

# Tracer instance for manual instrumentation
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)


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