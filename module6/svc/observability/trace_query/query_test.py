"""
Unit tests for trace query functions.

This module tests the query functions defined in trace_query.query,
including get_trace, recent_failures, and others.
"""

import json
import os
import tempfile
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from observability.trace_storage.models import AttributeFilter, SpanQuery, StoredSpan
from observability.trace_query.query import (
    get_trace,
    recent_failures,
    filter_by_error_type,
    filter_by_attribute,
    query_spans,
)


class TestTraceQueries:
    """Tests for trace query functions."""

    def setup_method(self):
        """Set up test data with a variety of spans."""
        # Create spans with different trace IDs, statuses, times, and attributes
        self.trace_id_1 = "01234567890123456789012345678901"
        self.trace_id_2 = "abcdef0123456789abcdef0123456789"

        # Calculate timestamps for testing time-based queries
        current_time_ns = int(time.time() * 1e9)
        hour_ago_ns = int((datetime.now() - timedelta(hours=1)).timestamp() * 1e9)
        two_hours_ago_ns = int((datetime.now() - timedelta(hours=2)).timestamp() * 1e9)
        day_ago_ns = int((datetime.now() - timedelta(days=1)).timestamp() * 1e9)

        # Create spans for first trace (mix of OK and ERROR)
        self.spans_trace_1 = [
            StoredSpan(
                trace_id=self.trace_id_1,
                span_id="0000000000000001",
                name="root_span",
                status="OK",
                start_time=current_time_ns - 10000000,
                end_time=current_time_ns,
                attributes={"http.method": "GET", "http.route": "/api/items"},
                service_name="api-service",
            ),
            StoredSpan(
                trace_id=self.trace_id_1,
                span_id="0000000000000002",
                parent_span_id="0000000000000001",
                name="db_query",
                status="OK",
                start_time=current_time_ns - 8000000,
                end_time=current_time_ns - 6000000,
                attributes={"db.system": "postgresql", "db.operation": "SELECT"},
                service_name="db-service",
            ),
            StoredSpan(
                trace_id=self.trace_id_1,
                span_id="0000000000000003",
                parent_span_id="0000000000000001",
                name="external_api_call",
                status="ERROR",
                status_description="Connection timeout",
                start_time=current_time_ns - 5000000,
                end_time=current_time_ns - 2000000,
                attributes={
                    "http.method": "POST",
                    "http.url": "https://api.example.com",
                    "error.type": "ConnectionError",
                    "error.message": "Connection timed out",
                },
                service_name="api-service",
            ),
        ]

        # Create spans for second trace (all ERROR, older)
        self.spans_trace_2 = [
            StoredSpan(
                trace_id=self.trace_id_2,
                span_id="abcdefabcdef0001",
                name="checkout",
                status="ERROR",
                status_description="Payment failed",
                start_time=hour_ago_ns,
                end_time=hour_ago_ns + 5000000,
                attributes={
                    "http.method": "POST",
                    "http.route": "/api/checkout",
                    "error.type": "PaymentError",
                    "error.message": "Payment authorization failed",
                    "user.id": "user-123",
                },
                service_name="payment-service",
            ),
            StoredSpan(
                trace_id=self.trace_id_2,
                span_id="abcdefabcdef0002",
                parent_span_id="abcdefabcdef0001",
                name="process_payment",
                status="ERROR",
                status_description="Invalid card",
                start_time=hour_ago_ns + 1000000,
                end_time=hour_ago_ns + 4000000,
                attributes={
                    "payment.provider": "stripe",
                    "payment.method": "credit_card",
                    "error.type": "PaymentError",
                    "error.message": "Card declined",
                },
                service_name="payment-service",
            ),
        ]

        # Create additional spans with different timestamps for time filtering tests
        self.recent_error_span = StoredSpan(
            trace_id="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            span_id="aaaaaaaaaaaaaaaa",
            name="recent_error",
            status="ERROR",
            start_time=current_time_ns - 100000000,  # Very recent
            end_time=current_time_ns - 90000000,
            attributes={"error.type": "RecentError"},
            service_name="test-service",
        )

        self.old_error_span = StoredSpan(
            trace_id="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            span_id="bbbbbbbbbbbbbbbb",
            name="old_error",
            status="ERROR",
            start_time=day_ago_ns,
            end_time=day_ago_ns + 10000000,
            attributes={"error.type": "OldError"},
            service_name="test-service",
        )

        # Combine all spans for testing
        self.all_spans = self.spans_trace_1 + self.spans_trace_2 + [
            self.recent_error_span,
            self.old_error_span,
        ]

        # Create a mock for the span store with our test data
        self.mock_store_patcher = patch(
            "observability.trace_query.query.get_span_store"
        )
        self.mock_get_store = self.mock_store_patcher.start()
        self.mock_store = MagicMock()
        self.mock_store.get_spans.side_effect = self.mock_get_spans
        self.mock_store.get_trace.side_effect = self.mock_get_trace
        self.mock_get_store.return_value = self.mock_store

    def teardown_method(self):
        """Clean up after tests."""
        self.mock_store_patcher.stop()

    def mock_get_spans(self, query=None):
        """Mock implementation of get_spans for testing."""
        # If no query, return all spans in descending start_time order
        if query is None:
            return sorted(self.all_spans, key=lambda s: s.start_time, reverse=True)

        # Filter by trace ID
        if query.trace_id:
            spans = [s for s in self.all_spans if s.trace_id == query.trace_id]
        else:
            spans = self.all_spans.copy()

        # Filter by span IDs
        if query.span_ids:
            spans = [s for s in spans if s.span_id in query.span_ids]

        # Filter by status
        if query.status:
            spans = [s for s in spans if s.status == query.status]

        # Filter by service name
        if query.service_name:
            spans = [s for s in spans if s.service_name == query.service_name]

        # Filter by operation name
        if query.operation_name:
            spans = [s for s in spans if s.name == query.operation_name]

        # Filter by time range
        if query.start_time_min is not None:
            spans = [s for s in spans if s.start_time >= query.start_time_min]
        if query.start_time_max is not None:
            spans = [s for s in spans if s.start_time <= query.start_time_max]

        # Filter by attributes
        if query.attribute_filters:
            for attr_filter in query.attribute_filters:
                spans = [s for s in spans if attr_filter.matches(s)]

        # Sort by the specified field
        if query.order_by == "start_time":
            key_func = lambda s: s.start_time
        elif query.order_by == "end_time":
            key_func = lambda s: s.end_time
        elif query.order_by == "duration_ns":
            key_func = lambda s: s.duration_ns
        else:
            key_func = lambda s: s.start_time

        reverse = query.order_direction == "DESC"
        spans = sorted(spans, key=key_func, reverse=reverse)

        # Apply limit
        if len(spans) > query.max_spans:
            spans = spans[:query.max_spans]

        return spans

    def mock_get_trace(self, trace_id):
        """Mock implementation of get_trace for testing."""
        spans = [s for s in self.all_spans if s.trace_id == trace_id]
        return sorted(spans, key=lambda s: s.start_time)

    def test_get_trace(self):
        """Test retrieving spans by trace ID."""
        # Test retrieving the first trace
        spans = get_trace(self.trace_id_1)
        assert len(spans) == 3
        assert all(s.trace_id == self.trace_id_1 for s in spans)
        assert spans[0].span_id == "0000000000000001"  # Root span should be first

        # Test retrieving the second trace
        spans = get_trace(self.trace_id_2)
        assert len(spans) == 2
        assert all(s.trace_id == self.trace_id_2 for s in spans)

        # Test retrieving a non-existent trace
        spans = get_trace("nonexistenttraceid12345678901234")
        assert len(spans) == 0

    def test_get_trace_invalid_id(self):
        """Test get_trace with an invalid trace ID."""
        with pytest.raises(ValueError):
            get_trace("invalid-trace-id")

    def test_recent_failures(self):
        """Test retrieving recent spans with ERROR status."""
        # Test with default parameters (1 hour)
        spans = recent_failures()

        # Should include recent errors from the last hour
        assert len(spans) > 0
        assert all(s.status == "ERROR" for s in spans)
        assert any(s.span_id == "0000000000000003" for s in spans)  # Recent error from trace 1
        assert any(s.span_id == "abcdefabcdef0001" for s in spans)  # Error from trace 2
        assert any(s.span_id == "aaaaaaaaaaaaaaaa" for s in spans)  # Very recent error

        # Should not include old errors
        assert not any(s.span_id == "bbbbbbbbbbbbbbbb" for s in spans)  # Old error

        # Test with a shorter time window
        spans = recent_failures(hours=0.01)  # ~36 seconds
        assert len(spans) > 0
        assert all(s.status == "ERROR" for s in spans)
        # Should only include the very recent errors
        assert any(s.span_id == "0000000000000003" for s in spans)  # Recent error from trace 1
        assert any(s.span_id == "aaaaaaaaaaaaaaaa" for s in spans)  # Very recent error

        # Should not include less recent errors
        assert not any(s.span_id == "abcdefabcdef0001" for s in spans)  # Error from trace 2
        assert not any(s.span_id == "bbbbbbbbbbbbbbbb" for s in spans)  # Old error

        # Test with a limit
        spans = recent_failures(max_results=1)
        assert len(spans) == 1
        assert spans[0].status == "ERROR"

    def test_recent_failures_invalid_hours(self):
        """Test recent_failures with an invalid hours parameter."""
        with pytest.raises(ValueError):
            recent_failures(hours=0)

        with pytest.raises(ValueError):
            recent_failures(hours=-1)

    def test_filter_by_error_type(self):
        """Test filtering spans by error type."""
        # Test filtering by ConnectionError
        spans = filter_by_error_type("ConnectionError")
        assert len(spans) == 1
        assert spans[0].span_id == "0000000000000003"
        assert spans[0].attributes["error.type"] == "ConnectionError"

        # Test filtering by PaymentError
        spans = filter_by_error_type("PaymentError")
        assert len(spans) == 2
        assert all(s.attributes["error.type"] == "PaymentError" for s in spans)

        # Test filtering by non-existent error type
        spans = filter_by_error_type("NonExistentError")
        assert len(spans) == 0

        # Test with a limit
        spans = filter_by_error_type("PaymentError", max_results=1)
        assert len(spans) == 1
        assert spans[0].attributes["error.type"] == "PaymentError"

    def test_filter_by_error_type_invalid(self):
        """Test filter_by_error_type with an invalid error_type."""
        with pytest.raises(ValueError):
            filter_by_error_type("")

    def test_filter_by_attribute(self):
        """Test filtering spans by attribute."""
        # Test filtering by http.method = GET
        spans = filter_by_attribute("http.method", "GET")
        assert len(spans) == 1
        assert spans[0].span_id == "0000000000000001"
        assert spans[0].attributes["http.method"] == "GET"

        # Test filtering by http.method = POST
        spans = filter_by_attribute("http.method", "POST")
        assert len(spans) == 2
        assert all(s.attributes["http.method"] == "POST" for s in spans)

        # Test filtering by payment.provider = stripe
        spans = filter_by_attribute("payment.provider", "stripe")
        assert len(spans) == 1
        assert spans[0].span_id == "abcdefabcdef0002"
        assert spans[0].attributes["payment.provider"] == "stripe"

        # Test filtering by non-existent attribute
        spans = filter_by_attribute("non.existent", "value")
        assert len(spans) == 0

        # Test with a limit
        spans = filter_by_attribute("http.method", "POST", max_results=1)
        assert len(spans) == 1
        assert spans[0].attributes["http.method"] == "POST"

    def test_filter_by_attribute_invalid(self):
        """Test filter_by_attribute with an invalid key."""
        with pytest.raises(ValueError):
            filter_by_attribute("", "value")

    def test_query_spans(self):
        """Test the general query_spans function."""
        # Test query with multiple filters
        query = SpanQuery(
            status="ERROR",
            service_name="payment-service",
            attribute_filters=[
                AttributeFilter(key="payment.provider", value="stripe")
            ],
            max_spans=10,
        )
        spans = query_spans(query)
        assert len(spans) == 1
        assert spans[0].status == "ERROR"
        assert spans[0].service_name == "payment-service"
        assert spans[0].attributes["payment.provider"] == "stripe"

        # Test complex query with time range and multiple attributes
        query = SpanQuery(
            status="ERROR",
            start_time_min=int((datetime.now() - timedelta(hours=2)).timestamp() * 1e9),
            start_time_max=int((datetime.now() - timedelta(minutes=30)).timestamp() * 1e9),
            attribute_filters=[
                AttributeFilter(key="error.type", value="PaymentError"),
                AttributeFilter(key="payment.method", value="credit_card"),
            ],
            max_spans=10,
        )
        spans = query_spans(query)
        assert len(spans) > 0
        assert all(s.status == "ERROR" for s in spans)
        assert all(s.attributes["error.type"] == "PaymentError" for s in spans)
        assert all(s.attributes["payment.method"] == "credit_card" for s in spans)

        # Test query with custom ordering
        query = SpanQuery(
            order_by="end_time",
            order_direction="ASC",
            max_spans=3,
        )
        spans = query_spans(query)
        assert len(spans) == 3
        # Verify ordering
        for i in range(len(spans) - 1):
            assert spans[i].end_time <= spans[i + 1].end_time

    def test_query_spans_invalid(self):
        """Test query_spans with an invalid query."""
        # Invalid trace ID
        with pytest.raises(ValueError):
            query_spans(SpanQuery(trace_id="invalid"))

        # Invalid time range
        with pytest.raises(ValueError):
            query_spans(
                SpanQuery(
                    start_time_min=1000000100,
                    start_time_max=1000000000,  # Max before min
                )
            )