#!/usr/bin/env python
"""
Manual tests for retry logic that don't rely on OpenTelemetry SDK.

This script manually creates StoredSpan objects to test the retry logic.
"""

import logging
import uuid
from datetime import datetime

from observability.trace_storage.models import StoredSpan
from observability.trace_retry.retry_logic import should_retry
from observability.trace_storage.span_store import SpanStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a span store for testing
span_store = SpanStore()

# Global variable to store the span store instance
_GLOBAL_SPAN_STORE = span_store


# Mock the get_span_store function
def mock_get_span_store():
    return _GLOBAL_SPAN_STORE


# Patch the get_span_store function in retry_logic
import observability.trace_retry.retry_logic
observability.trace_retry.retry_logic.get_span_store = mock_get_span_store


def create_test_trace(error_type=None, retriable=None):
    """Create a test trace with specified error type and retriable attribute."""
    # Generate a random trace ID
    trace_id = uuid.uuid4().hex

    # Create timestamp
    timestamp = int(datetime.now().timestamp() * 1_000_000_000)

    # Create a root span
    root_span = StoredSpan(
        trace_id=trace_id,
        span_id=uuid.uuid4().hex[:16],
        name="root_operation",
        status="OK",
        start_time=timestamp,
        end_time=timestamp + 1_000_000_000,
        duration_ns=1_000_000_000,
        service_name="test-service"
    )

    # Add the root span to the store
    span_store.add_span(root_span)

    # Create a child span with error if specified
    if error_type:
        child_span_id = uuid.uuid4().hex[:16]
        attributes = {"error.type": error_type}
        if retriable is not None:
            attributes["error.retriable"] = retriable

        child_span = StoredSpan(
            trace_id=trace_id,
            span_id=child_span_id,
            parent_span_id=root_span.span_id,
            name="child_operation",
            status="ERROR",
            status_description=f"Test {error_type}",
            start_time=timestamp + 100_000_000,
            end_time=timestamp + 900_000_000,
            duration_ns=800_000_000,
            attributes=attributes,
            service_name="test-service"
        )

        # Add the child span to the store
        span_store.add_span(child_span)

    logger.info(f"Created trace with ID: {trace_id}, error type: {error_type}, retriable: {retriable}")
    return trace_id


def run_test_cases():
    """Run test cases to verify the retry logic."""
    # Test case 1: ValidationError (should return ABORT)
    logger.info("=== Test case 1: ValidationError (should return ABORT) ===")
    trace_id1 = create_test_trace(error_type="ValidationError")
    result1 = should_retry(trace_id1)
    logger.info(f"Result: {result1}")

    # Test case 2: ConnectionError (should return RETRY)
    logger.info("\n=== Test case 2: ConnectionError (should return RETRY) ===")
    trace_id2 = create_test_trace(error_type="ConnectionError")
    result2 = should_retry(trace_id2)
    logger.info(f"Result: {result2}")

    # Test case 3: UnknownError (should return WAIT)
    logger.info("\n=== Test case 3: UnknownError (should return WAIT) ===")
    trace_id3 = create_test_trace(error_type="UnknownError")
    result3 = should_retry(trace_id3)
    logger.info(f"Result: {result3}")

    # Test case 4: ValidationError with retriable=True (should return RETRY)
    logger.info("\n=== Test case 4: ValidationError with retriable=True (should return RETRY) ===")
    trace_id4 = create_test_trace(error_type="ValidationError", retriable=True)
    result4 = should_retry(trace_id4)
    logger.info(f"Result: {result4}")

    # Summary
    logger.info("\n=== Results summary ===")
    logger.info(f"1. ValidationError: {result1['decision']} (expected ABORT)")
    logger.info(f"2. ConnectionError: {result2['decision']} (expected RETRY)")
    logger.info(f"3. UnknownError: {result3['decision']} (expected WAIT)")
    logger.info(f"4. ValidationError with retriable=True: {result4['decision']} (expected RETRY)")


if __name__ == "__main__":
    run_test_cases()