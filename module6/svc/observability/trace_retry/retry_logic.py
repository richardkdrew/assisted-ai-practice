"""
Retry logic for analyzing OpenTelemetry traces to determine retry decisions.

This module provides functionality to analyze OpenTelemetry traces and determine
whether failed operations should be retried based on error types found in spans.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from opentelemetry import trace

from ..trace_storage.file_span_processor import get_span_store
from ..trace_storage.models import StoredSpan
from .models import create_retry_decision, RetryDecisionType

# Configure logging
logger = logging.getLogger(__name__)

# Constants
DEFAULT_WAIT_SECONDS = 5

# Error type classifications
PERMANENT_ERROR_TYPES = {
    "ValidationError",
    "AuthenticationError",
    "NotFoundError",
    "AuthorizationError",
    "ValueError",
    "TypeError",
    "KeyError",
    "AttributeError",
    "RequestValidationError",
    "NotAuthenticatedError",
    "PermissionDeniedError",
    "ForbiddenError"
}

TRANSIENT_ERROR_TYPES = {
    "ConnectionError",
    "TimeoutError",
    "ServiceUnavailableError",
    "RateLimitError"
}


def find_error_spans(spans: List[StoredSpan]) -> List[StoredSpan]:
    """
    Find spans with error status in the trace.

    Args:
        spans: List of StoredSpan objects from a trace

    Returns:
        List of spans with status="ERROR"
    """
    return [span for span in spans if span.status == "ERROR"]


def get_retry_decision_from_span(span: StoredSpan) -> Tuple[RetryDecisionType, str, int]:
    """
    Determine the retry decision based on a single error span.

    This function analyzes a span's attributes to determine whether a retry
    should be performed, aborted, or handled with caution.

    Args:
        span: The error span to analyze

    Returns:
        Tuple of (decision, reason, wait_seconds)
    """
    # Check if error.retriable attribute is present (highest priority)
    if "error.retriable" in span.attributes:
        is_retriable = span.attributes["error.retriable"]
        if is_retriable is True:
            return "RETRY", f"Operation marked as retriable in span", DEFAULT_WAIT_SECONDS
        elif is_retriable is False:
            return "ABORT", f"Operation marked as non-retriable in span", 0

    # Check if error.type is present
    if "error.type" in span.attributes:
        error_type = span.attributes["error.type"]

        # Check for permanent errors
        if error_type in PERMANENT_ERROR_TYPES:
            return "ABORT", f"{error_type} detected which is a permanent error", 0

        # Check for transient errors
        if error_type in TRANSIENT_ERROR_TYPES:
            return "RETRY", f"{error_type} detected which is a transient error", DEFAULT_WAIT_SECONDS

    # If we don't have enough info, return WAIT (cautious approach)
    return "WAIT", "Unknown error type detected, using cautious retry approach", DEFAULT_WAIT_SECONDS


def analyze_multiple_errors(error_spans: List[StoredSpan]) -> Tuple[RetryDecisionType, str, int, str]:
    """
    Determine the overall retry decision when multiple error spans exist.

    This function analyzes multiple error spans and prioritizes the decision,
    with permanent errors taking precedence over transient errors.

    Args:
        error_spans: List of error spans to analyze

    Returns:
        Tuple of (decision, reason, wait_seconds, span_id)
    """
    # Track decisions by priority (ABORT > RETRY > WAIT)
    abort_spans = []
    retry_spans = []
    wait_spans = []

    # Analyze each error span
    for span in error_spans:
        decision, reason, wait_seconds = get_retry_decision_from_span(span)

        if decision == "ABORT":
            abort_spans.append((span, reason, wait_seconds))
        elif decision == "RETRY":
            retry_spans.append((span, reason, wait_seconds))
        else:  # WAIT
            wait_spans.append((span, reason, wait_seconds))

    # Prioritize decisions (permanent errors take precedence)
    if abort_spans:
        span, reason, wait_seconds = abort_spans[0]
        return "ABORT", reason, wait_seconds, span.span_id

    if retry_spans:
        span, reason, wait_seconds = retry_spans[0]
        return "RETRY", reason, wait_seconds, span.span_id

    if wait_spans:
        span, reason, wait_seconds = wait_spans[0]
        return "WAIT", reason, wait_seconds, span.span_id

    # This should not happen as we should have at least one span
    # But as a fallback, return WAIT
    return "WAIT", "No specific error type could be determined", DEFAULT_WAIT_SECONDS, error_spans[0].span_id


def should_retry(trace_id: str) -> Dict[str, Any]:
    """
    Analyze a trace to determine whether the operation should be retried.

    This function examines the error spans in a trace to classify errors as
    permanent or transient, and returns a decision about whether the operation
    should be retried.

    Args:
        trace_id: The trace ID to analyze (32-character hex string)

    Returns:
        Dictionary with decision information:
        {
            "decision": "RETRY"|"ABORT"|"WAIT",
            "reason": "explanation",
            "wait_seconds": 5,  # if RETRY or WAIT
            "trace_id": "...",
            "span_id": "..."
        }

    Raises:
        ValueError: If trace_id is invalid or no trace found
    """
    # Input validation
    if not trace_id or len(trace_id) != 32:
        raise ValueError(f"Invalid trace_id: {trace_id}. Must be 32-character hex string.")

    # Get the span store
    span_store = get_span_store()
    if span_store is None:
        raise ValueError("Span store not initialized. Ensure the trace storage system is properly set up.")

    # Retrieve trace data
    try:
        spans = span_store.get_trace(trace_id)
        if not spans:
            raise ValueError(f"No trace found with trace_id: {trace_id}")
    except Exception as e:
        raise ValueError(f"Error retrieving trace data: {e}")

    # Find error spans
    error_spans = find_error_spans(spans)

    # If no error spans, return "no retry needed"
    if not error_spans:
        # Use the root span or first span as reference
        reference_span = next((s for s in spans if s.parent_span_id is None), spans[0])
        return create_retry_decision(
            decision="ABORT",
            reason="No errors found in trace",
            trace_id=trace_id,
            span_id=reference_span.span_id
        )

    # If multiple error spans, analyze them together
    if len(error_spans) > 1:
        decision, reason, wait_seconds, span_id = analyze_multiple_errors(error_spans)
        return create_retry_decision(
            decision=decision,
            reason=reason,
            trace_id=trace_id,
            span_id=span_id,
            wait_seconds=wait_seconds
        )

    # Single error span
    error_span = error_spans[0]
    decision, reason, wait_seconds = get_retry_decision_from_span(error_span)

    return create_retry_decision(
        decision=decision,
        reason=reason,
        trace_id=trace_id,
        span_id=error_span.span_id,
        wait_seconds=wait_seconds
    )