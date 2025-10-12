#!/usr/bin/env python
"""
Manual test cases for the retry logic.

This script creates traces with different error types and tests the should_retry function.
"""

import sys
import logging
import time
from typing import Dict, Any

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from ..trace_storage.file_span_processor import FileBasedSpanProcessor
from ..trace_storage.models import StoredSpan
from .retry_logic import should_retry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure OpenTelemetry
resource = Resource(attributes={
    SERVICE_NAME: "retry-logic-tester"
})

provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

# Create a file-based span processor for storing spans
file_processor = FileBasedSpanProcessor("traces/test_traces.jsonl")
provider.add_span_processor(file_processor)

# Create a tracer
tracer = trace.get_tracer("retry-logic-test")


def create_trace_with_error(error_type: str, retriable: bool = None) -> str:
    """
    Create a trace with a specified error type.

    Args:
        error_type: The error type to set in the span
        retriable: Optional override for error.retriable attribute

    Returns:
        The trace ID of the created trace
    """
    with tracer.start_as_current_span("root_operation") as root_span:
        # Create a child span with error
        with tracer.start_as_current_span("child_operation") as child_span:
            # Set span status to ERROR
            child_span.set_status(trace.StatusCode.ERROR)

            # Set error attributes
            child_span.set_attribute("error", True)
            child_span.set_attribute("error.type", error_type)
            child_span.set_attribute("error.message", f"Test {error_type}")

            # Set error.retriable if provided
            if retriable is not None:
                child_span.set_attribute("error.retriable", retriable)

    # Get the trace ID from the root span
    trace_id = format(root_span.get_span_context().trace_id, "032x")
    logger.info(f"Created trace with ID: {trace_id}, error type: {error_type}, retriable: {retriable}")

    # Give the processor time to process the spans
    time.sleep(0.1)

    return trace_id


def run_test_case(error_type: str, retriable: bool = None) -> Dict[str, Any]:
    """
    Run a test case with a specified error type.

    Args:
        error_type: The error type to test
        retriable: Optional override for error.retriable attribute

    Returns:
        The retry decision result
    """
    trace_id = create_trace_with_error(error_type, retriable)
    result = should_retry(trace_id)
    logger.info(f"Result: {result}")
    return result


def run_test_cases():
    """Run all test cases."""
    logger.info("=== Running test case 1: ValidationError (should return ABORT) ===")
    result1 = run_test_case("ValidationError")

    logger.info("\n=== Running test case 2: ConnectionError (should return RETRY) ===")
    result2 = run_test_case("ConnectionError")

    logger.info("\n=== Running test case 3: UnknownError (should return WAIT) ===")
    result3 = run_test_case("UnknownError")

    logger.info("\n=== Running test case 4: ValidationError with retriable=True override (should return RETRY) ===")
    result4 = run_test_case("ValidationError", retriable=True)

    logger.info("\n=== Results summary ===")
    logger.info(f"ValidationError: {result1['decision']} (expected ABORT)")
    logger.info(f"ConnectionError: {result2['decision']} (expected RETRY)")
    logger.info(f"UnknownError: {result3['decision']} (expected WAIT)")
    logger.info(f"ValidationError with retriable=True: {result4['decision']} (expected RETRY)")


if __name__ == "__main__":
    run_test_cases()