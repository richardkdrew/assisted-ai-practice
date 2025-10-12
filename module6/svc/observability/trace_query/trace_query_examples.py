#!/usr/bin/env python3
"""
Example usage of the trace storage and query system.

This script demonstrates how to:
1. Set up a tracer with the FileBasedSpanProcessor
2. Create traces with spans and errors
3. Query and analyze the stored traces

Usage:
    python3 trace_query_examples.py [--create-traces | --query-traces]
"""

import argparse
import os
import sys
import time
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import SpanKind, StatusCode

from observability.trace_storage.file_span_processor import FileBasedSpanProcessor
from observability.trace_query import (
    get_trace,
    recent_failures,
    filter_by_error_type,
    filter_by_attribute,
    filter_by_status,
    filter_by_time,
)


def setup_tracer():
    """Set up a tracer with the FileBasedSpanProcessor."""
    # Create a trace file in the examples directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    trace_file = os.path.join(script_dir, "example_traces.jsonl")

    # Set up the tracer with our file-based span processor
    provider = TracerProvider()
    processor = FileBasedSpanProcessor(trace_file, max_spans=1000)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Get a tracer for creating spans
    tracer = trace.get_tracer("trace_query_examples")
    return tracer, processor


def create_example_traces(tracer):
    """Create example traces with different patterns."""
    traces = []

    # Example 1: Successful web request with database query
    with tracer.start_as_current_span(
        name="GET /api/users",
        kind=SpanKind.SERVER,
        attributes={
            "http.method": "GET",
            "http.url": "/api/users",
            "http.route": "/api/users",
        }
    ) as root_span:
        # Store the trace ID for later querying
        trace_id = format(root_span.get_span_context().trace_id, "032x")
        traces.append({"name": "Successful API Request", "trace_id": trace_id})

        # Add request received event
        root_span.add_event("request_received", {"client_ip": "127.0.0.1"})

        # Database query span
        with tracer.start_as_current_span(
            name="SELECT users",
            kind=SpanKind.CLIENT,
            attributes={
                "db.system": "postgresql",
                "db.statement": "SELECT * FROM users LIMIT 100",
                "db.operation": "SELECT",
            }
        ):
            # Simulate database query
            time.sleep(0.05)

        # Process results span
        with tracer.start_as_current_span(
            name="process_results",
            kind=SpanKind.INTERNAL,
            attributes={
                "users.count": 42,
            }
        ):
            # Simulate processing
            time.sleep(0.02)

        # Add request completed event
        root_span.add_event("request_completed", {"status_code": 200, "duration_ms": 75})
        root_span.set_attributes({"http.status_code": 200})

    # Example 2: Failed payment with nested operations
    with tracer.start_as_current_span(
        name="POST /api/payments",
        kind=SpanKind.SERVER,
        attributes={
            "http.method": "POST",
            "http.url": "/api/payments",
            "http.route": "/api/payments",
        }
    ) as root_span:
        # Store the trace ID for later querying
        trace_id = format(root_span.get_span_context().trace_id, "032x")
        traces.append({"name": "Failed Payment", "trace_id": trace_id})

        # Add request received event
        root_span.add_event("request_received", {"client_ip": "192.168.1.42"})

        # Validate payment span (OK)
        with tracer.start_as_current_span(
            name="validate_payment",
            kind=SpanKind.INTERNAL,
            attributes={
                "payment.amount": 129.99,
                "payment.currency": "USD",
                "payment.method": "credit_card",
                "user.id": "user_12345",
            }
        ):
            # Simulate validation
            time.sleep(0.03)

        # Process payment span (ERROR)
        with tracer.start_as_current_span(
            name="process_payment",
            kind=SpanKind.CLIENT,
            attributes={
                "payment.provider": "stripe",
                "payment.gateway": "stripe_api",
                "payment.amount": 129.99,
            }
        ) as payment_span:
            # Simulate error
            time.sleep(0.04)

            # Set error status
            payment_span.set_status(
                StatusCode.ERROR,
                "Payment authorization failed"
            )

            # Add error details
            payment_span.set_attributes({
                "error.type": "PaymentError",
                "error.message": "Insufficient funds",
                "error.code": "insufficient_funds",
            })

        # Set error status on the parent span
        root_span.set_status(StatusCode.ERROR, "Payment processing failed")
        root_span.add_event("request_completed", {"status_code": 400})
        root_span.set_attributes({
            "http.status_code": 400,
            "error.type": "TransactionError",
            "error.message": "Could not complete payment transaction",
        })

    # Example 3: Database connection error
    with tracer.start_as_current_span(
        name="GET /api/products",
        kind=SpanKind.SERVER,
        attributes={
            "http.method": "GET",
            "http.url": "/api/products",
            "http.route": "/api/products",
        }
    ) as root_span:
        # Store the trace ID for later querying
        trace_id = format(root_span.get_span_context().trace_id, "032x")
        traces.append({"name": "Database Connection Error", "trace_id": trace_id})

        # Database query span with error
        with tracer.start_as_current_span(
            name="SELECT products",
            kind=SpanKind.CLIENT,
            attributes={
                "db.system": "postgresql",
                "db.statement": "SELECT * FROM products WHERE category = 'electronics'",
                "db.operation": "SELECT",
            }
        ) as db_span:
            # Simulate database error
            time.sleep(0.02)

            # Set error status
            db_span.set_status(
                StatusCode.ERROR,
                "Database connection failed"
            )

            # Add error details
            db_span.set_attributes({
                "error.type": "ConnectionError",
                "error.message": "Connection refused",
                "error.code": "connection_refused",
            })

        # Error handling span
        with tracer.start_as_current_span(
            name="handle_db_error",
            kind=SpanKind.INTERNAL,
            attributes={
                "error.handled": True,
            }
        ):
            # Simulate error handling
            time.sleep(0.01)

        # Set error status on the parent span
        root_span.set_status(StatusCode.ERROR, "Failed to retrieve products")
        root_span.add_event("request_completed", {"status_code": 503})
        root_span.set_attributes({
            "http.status_code": 503,
            "error.type": "ServiceUnavailableError",
            "error.message": "Database is currently unavailable",
        })

    # Ensure all spans are processed
    time.sleep(0.1)
    return traces


def query_example_traces(traces, processor):
    """Demonstrate querying the traces we created."""
    print("\n=== Trace Query Examples ===\n")

    # Example 1: Get a trace by ID
    print(f"Example 1: Get trace by ID ({traces[0]['name']})")
    print("-" * 50)
    spans = get_trace(traces[0]['trace_id'])
    print(f"Found {len(spans)} spans:")
    for span in spans:
        print(f"  - {span.name} ({span.status})")
    print()

    # Example 2: Get recent failures
    print("Example 2: Recent failures (last hour)")
    print("-" * 50)
    failures = recent_failures(hours=1)
    print(f"Found {len(failures)} failure spans:")
    for span in failures:
        print(f"  - {span.name} ({span.status}): {span.status_description}")
        if 'error.type' in span.attributes:
            print(f"    Error: {span.attributes['error.type']} - {span.attributes.get('error.message', '')}")
    print()

    # Example 3: Filter by error type
    print("Example 3: Filter by error type (ConnectionError)")
    print("-" * 50)
    connection_errors = filter_by_error_type("ConnectionError")
    print(f"Found {len(connection_errors)} ConnectionError spans:")
    for span in connection_errors:
        print(f"  - {span.name} ({span.status}): {span.attributes.get('error.message', '')}")
    print()

    # Example 4: Filter by attribute
    print("Example 4: Filter by attribute (http.method=POST)")
    print("-" * 50)
    post_requests = filter_by_attribute("http.method", "POST")
    print(f"Found {len(post_requests)} POST request spans:")
    for span in post_requests:
        print(f"  - {span.name} ({span.status}): {span.attributes['http.url']}")
    print()

    # Example 5: Filter by time range
    print("Example 5: Filter by time range (last 5 minutes)")
    print("-" * 50)
    recent_spans = filter_by_time(duration="5m")
    print(f"Found {len(recent_spans)} spans in the last 5 minutes:")
    for span in recent_spans[:5]:  # Show only first 5 spans
        print(f"  - {span.name} ({span.status})")
    if len(recent_spans) > 5:
        print(f"  ... and {len(recent_spans) - 5} more")
    print()

    # Example 6: Filter by status and time
    print("Example 6: Filter by status (ERROR) and time (last 10 minutes)")
    print("-" * 50)
    recent_errors = filter_by_time(duration="10m", status="ERROR")
    print(f"Found {len(recent_errors)} ERROR spans in the last 10 minutes:")
    for span in recent_errors:
        print(f"  - {span.name}: {span.status_description}")
    print()


def main():
    """Main entry point for the example script."""
    parser = argparse.ArgumentParser(
        description="Demonstrate trace storage and query functionality"
    )
    parser.add_argument(
        "--create-traces",
        action="store_true",
        help="Create example traces"
    )
    parser.add_argument(
        "--query-traces",
        action="store_true",
        help="Query example traces"
    )
    args = parser.parse_args()

    # Default behavior: run both
    run_create = args.create_traces or not args.query_traces
    run_query = args.query_traces or not args.create_traces

    # Setup tracer
    tracer, processor = setup_tracer()

    traces = []
    if run_create:
        print("Creating example traces...")
        traces = create_example_traces(tracer)
        print(f"Created {len(traces)} example traces:")
        for trace in traces:
            print(f"- {trace['name']}: {trace['trace_id']}")

    if run_query:
        if not traces:
            # If we're only querying, try to find some existing traces
            print("Querying existing traces...")
            query_example_traces([], processor)
        else:
            query_example_traces(traces, processor)

    # Clean up
    processor.shutdown()


if __name__ == "__main__":
    main()