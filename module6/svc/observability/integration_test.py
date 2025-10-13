"""
Integration tests for the trace storage and query system.

This module tests the end-to-end functionality of the trace storage and
query system, from span creation to storage to querying.
"""

import os
import json
import tempfile
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import SpanKind, Status, StatusCode

from observability.trace_storage.file_span_processor import FileBasedSpanProcessor
from observability.trace_storage.models import AttributeFilter, SpanQuery, StoredSpan
from observability.trace_query import (
    get_trace,
    recent_failures,
    filter_by_error_type,
    filter_by_attribute,
    filter_by_status,
    filter_by_time,
    query_spans,
)


class TestIntegration:
    """Integration tests for the trace storage and query system."""

    def setup_method(self):
        """Set up the test environment with a temporary directory and tracer."""
        # Create a temporary directory for the trace file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, "test_trace_storage.jsonl")

        # Set up the tracer with our file-based span processor
        provider = TracerProvider()
        self.span_processor = FileBasedSpanProcessor(self.file_path)
        provider.add_span_processor(self.span_processor)
        trace.set_tracer_provider(provider)

        # Get a tracer for creating spans
        self.tracer = trace.get_tracer("integration_test")

    def teardown_method(self):
        """Clean up the test environment."""
        # Ensure the span processor is shut down
        self.span_processor.shutdown()

        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def create_test_spans(self):
        """Create a set of test spans for various scenarios."""
        # Create spans for the first trace (successful flow)
        with self.tracer.start_as_current_span(
            name="root_operation",
            kind=SpanKind.SERVER,
            attributes={"http.method": "GET", "http.url": "/api/users"}
        ) as root_span:
            # Add events
            root_span.add_event("request_received", {"client_ip": "127.0.0.1"})

            # First child span (database query)
            with self.tracer.start_as_current_span(
                name="database_query",
                kind=SpanKind.CLIENT,
                attributes={"db.system": "postgresql", "db.statement": "SELECT * FROM users"}
            ) as db_span:
                # Simulate work
                time.sleep(0.01)
                db_span.add_event("query_executed", {"rows": 10})

            # Second child span (user processing)
            with self.tracer.start_as_current_span(
                name="process_users",
                kind=SpanKind.INTERNAL,
                attributes={"users.count": 10}
            ) as process_span:
                # Simulate work
                time.sleep(0.01)

            # Add final event
            root_span.add_event("request_completed", {"status_code": 200})

        # Create spans for the second trace (with an error)
        with self.tracer.start_as_current_span(
            name="payment_process",
            kind=SpanKind.SERVER,
            attributes={"http.method": "POST", "http.url": "/api/payments"}
        ) as root_span:
            # Add events
            root_span.add_event("payment_requested", {"amount": 100.00})

            # First child span (validate payment - OK)
            with self.tracer.start_as_current_span(
                name="validate_payment",
                kind=SpanKind.INTERNAL,
                attributes={"payment.amount": 100.00, "payment.currency": "USD"}
            ) as validate_span:
                # Simulate work
                time.sleep(0.01)

            # Second child span (process payment - ERROR)
            with self.tracer.start_as_current_span(
                name="process_payment",
                kind=SpanKind.CLIENT,
                attributes={"payment.provider": "stripe", "payment.method": "credit_card"}
            ) as process_span:
                # Simulate work
                time.sleep(0.01)
                # Set error status
                process_span.set_status(StatusCode.ERROR, "Payment authorization failed")
                # Add error attributes
                process_span.set_attributes({
                    "error.type": "PaymentError",
                    "error.message": "Card declined",
                    "error.code": "card_declined"
                })

            # Set error status on the root span
            root_span.set_status(StatusCode.ERROR, "Payment processing failed")
            root_span.set_attributes({
                "error.type": "TransactionError",
                "error.message": "Failed to complete payment transaction"
            })
            root_span.add_event("request_completed", {"status_code": 400})

        # Ensure all spans are processed
        time.sleep(0.1)

    def test_end_to_end_trace_retrieval(self):
        """Test creating spans and retrieving them by trace ID."""
        # Create the test spans
        self.create_test_spans()

        # Get the first trace (needs to be extracted from the created spans)
        # Since we don't know the actual trace ID, we'll read the file directly
        with open(self.file_path, "r") as f:
            spans_data = [json.loads(line) for line in f.readlines()]

        # Find the root span of the first trace
        root_span1 = next(
            span for span in spans_data
            if span["name"] == "root_operation"
        )
        trace_id1 = root_span1["trace_id"]

        # Query the trace
        spans = get_trace(trace_id1)

        # Verify the results
        assert len(spans) == 3  # Root + 2 children
        assert spans[0].name == "root_operation"
        assert spans[0].trace_id == trace_id1
        assert spans[0].status == "OK"

        # Find the child spans
        db_span = next((span for span in spans if span.name == "database_query"), None)
        process_span = next((span for span in spans if span.name == "process_users"), None)

        # Verify the child spans
        assert db_span is not None
        assert process_span is not None
        assert db_span.attributes["db.system"] == "postgresql"
        assert process_span.attributes["users.count"] == 10

    def test_error_filtering(self):
        """Test filtering spans by error status and error type."""
        # Create the test spans
        self.create_test_spans()

        # Filter by ERROR status
        error_spans = filter_by_status("ERROR")

        # Verify the results
        assert len(error_spans) > 0
        assert all(span.status == "ERROR" for span in error_spans)

        # Find spans with payment errors
        payment_errors = filter_by_error_type("PaymentError")

        # Verify the results
        assert len(payment_errors) > 0
        assert all(span.attributes["error.type"] == "PaymentError" for span in payment_errors)

        # There should also be a TransactionError
        transaction_errors = filter_by_error_type("TransactionError")
        assert len(transaction_errors) > 0

    def test_attribute_filtering(self):
        """Test filtering spans by various attributes."""
        # Create the test spans
        self.create_test_spans()

        # Filter by HTTP method
        get_requests = filter_by_attribute("http.method", "GET")
        post_requests = filter_by_attribute("http.method", "POST")

        # Verify the results
        assert len(get_requests) > 0
        assert all(span.attributes["http.method"] == "GET" for span in get_requests)

        assert len(post_requests) > 0
        assert all(span.attributes["http.method"] == "POST" for span in post_requests)

        # Filter by payment provider
        stripe_spans = filter_by_attribute("payment.provider", "stripe")

        # Verify the results
        assert len(stripe_spans) > 0
        assert all(span.attributes["payment.provider"] == "stripe" for span in stripe_spans)

    def test_time_filtering(self):
        """Test filtering spans by time range."""
        # Create the test spans
        self.create_test_spans()

        # Get current time
        now = datetime.now()

        # Filter spans from the last minute
        recent_spans = filter_by_time(
            start_time=now - timedelta(minutes=1),
            end_time=now
        )

        # All our test spans should be in this range
        assert len(recent_spans) > 0

        # Filter with relative time
        relative_spans = filter_by_time(duration="1m")
        assert len(relative_spans) > 0

        # Filter by time and status
        error_spans = filter_by_time(
            duration="1m",
            status="ERROR"
        )
        assert len(error_spans) > 0
        assert all(span.status == "ERROR" for span in error_spans)

    def test_combined_filtering(self):
        """Test combining multiple filter criteria."""
        # Create the test spans
        self.create_test_spans()

        # Create a complex query
        query = SpanQuery(
            status="ERROR",
            start_time_min=int((datetime.now() - timedelta(minutes=1)).timestamp() * 1e9),
            attribute_filters=[
                AttributeFilter(key="payment.provider", value="stripe")
            ],
            max_spans=10,
            order_by="end_time",
            order_direction="DESC",
        )

        # Execute the query
        results = query_spans(query)

        # Verify the results
        assert len(results) > 0
        assert all(span.status == "ERROR" for span in results)
        assert all(span.attributes.get("payment.provider") == "stripe" for span in results)

    def test_recent_failures(self):
        """Test the recent_failures function."""
        # Create the test spans
        self.create_test_spans()

        # Get recent failures
        failures = recent_failures(hours=1)

        # Verify the results
        assert len(failures) > 0
        assert all(span.status == "ERROR" for span in failures)

        # Failures should be ordered by end_time (most recent first)
        for i in range(len(failures) - 1):
            assert failures[i].end_time >= failures[i + 1].end_time

    def test_performance(self):
        """Test query performance with a larger number of spans."""
        # Create many spans (simulate a high volume of traces)
        for i in range(50):  # Create 50 traces with 2 spans each
            with self.tracer.start_as_current_span(
                name=f"operation_{i}",
                kind=SpanKind.SERVER,
                attributes={"iteration": i}
            ):
                with self.tracer.start_as_current_span(
                    name=f"sub_operation_{i}",
                    kind=SpanKind.INTERNAL
                ):
                    # Minimal sleep to ensure spans are created
                    time.sleep(0.001)

        # Ensure all spans are processed
        time.sleep(0.2)

        # Measure time to perform a query
        start_time = time.time()
        spans = filter_by_time(duration="1m", max_results=100)
        end_time = time.time()

        # Verify results
        assert len(spans) > 0

        # Query should complete quickly (under 100ms is good for tests)
        query_time_ms = (end_time - start_time) * 1000
        assert query_time_ms < 100, f"Query took {query_time_ms}ms, expected <100ms"