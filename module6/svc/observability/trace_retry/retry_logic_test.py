"""
Tests for the trace retry logic.
"""

import unittest
from unittest.mock import patch, MagicMock
import pytest

from ..trace_storage.models import StoredSpan
from .models import RetryDecisionType
from .retry_logic import (
    find_error_spans,
    get_retry_decision_from_span,
    analyze_multiple_errors,
    should_retry,
    PERMANENT_ERROR_TYPES,
    TRANSIENT_ERROR_TYPES
)


class RetryLogicTests(unittest.TestCase):
    """Tests for the retry logic functions."""

    def test_find_error_spans(self):
        """Test that error spans are correctly identified."""
        # Create test spans
        spans = [
            StoredSpan(trace_id="a" * 32, span_id="1" * 16, status="OK"),
            StoredSpan(trace_id="a" * 32, span_id="2" * 16, status="ERROR"),
            StoredSpan(trace_id="a" * 32, span_id="3" * 16, status="OK"),
            StoredSpan(trace_id="a" * 32, span_id="4" * 16, status="ERROR"),
        ]

        # Find error spans
        error_spans = find_error_spans(spans)

        # Verify results
        self.assertEqual(len(error_spans), 2)
        self.assertEqual(error_spans[0].span_id, "2" * 16)
        self.assertEqual(error_spans[1].span_id, "4" * 16)

    def test_get_retry_decision_from_span_with_retriable_true(self):
        """Test retry decision with error.retriable=true attribute."""
        # Create a span with error.retriable=true
        span = StoredSpan(
            trace_id="a" * 32,
            span_id="1" * 16,
            status="ERROR",
            attributes={"error.retriable": True}
        )

        # Get retry decision
        decision, reason, wait_seconds = get_retry_decision_from_span(span)

        # Verify results
        self.assertEqual(decision, "RETRY")
        self.assertEqual(wait_seconds, 5)

    def test_get_retry_decision_from_span_with_retriable_false(self):
        """Test retry decision with error.retriable=false attribute."""
        # Create a span with error.retriable=false
        span = StoredSpan(
            trace_id="a" * 32,
            span_id="1" * 16,
            status="ERROR",
            attributes={"error.retriable": False}
        )

        # Get retry decision
        decision, reason, wait_seconds = get_retry_decision_from_span(span)

        # Verify results
        self.assertEqual(decision, "ABORT")
        self.assertEqual(wait_seconds, 0)

    def test_get_retry_decision_from_span_with_permanent_error(self):
        """Test retry decision with permanent error type."""
        # Try each permanent error type
        for error_type in PERMANENT_ERROR_TYPES:
            # Create a span with permanent error type
            span = StoredSpan(
                trace_id="a" * 32,
                span_id="1" * 16,
                status="ERROR",
                attributes={"error.type": error_type}
            )

            # Get retry decision
            decision, reason, wait_seconds = get_retry_decision_from_span(span)

            # Verify results
            self.assertEqual(decision, "ABORT", f"Expected ABORT for {error_type}")
            self.assertEqual(wait_seconds, 0, f"Expected wait_seconds=0 for {error_type}")

    def test_get_retry_decision_from_span_with_transient_error(self):
        """Test retry decision with transient error type."""
        # Try each transient error type
        for error_type in TRANSIENT_ERROR_TYPES:
            # Create a span with transient error type
            span = StoredSpan(
                trace_id="a" * 32,
                span_id="1" * 16,
                status="ERROR",
                attributes={"error.type": error_type}
            )

            # Get retry decision
            decision, reason, wait_seconds = get_retry_decision_from_span(span)

            # Verify results
            self.assertEqual(decision, "RETRY", f"Expected RETRY for {error_type}")
            self.assertEqual(wait_seconds, 5, f"Expected wait_seconds=5 for {error_type}")

    def test_get_retry_decision_from_span_with_unknown_error(self):
        """Test retry decision with unknown error type."""
        # Create a span with unknown error type
        span = StoredSpan(
            trace_id="a" * 32,
            span_id="1" * 16,
            status="ERROR",
            attributes={"error.type": "UnknownError"}
        )

        # Get retry decision
        decision, reason, wait_seconds = get_retry_decision_from_span(span)

        # Verify results
        self.assertEqual(decision, "WAIT")
        self.assertEqual(wait_seconds, 5)

    def test_get_retry_decision_from_span_without_error_type(self):
        """Test retry decision without error.type attribute."""
        # Create a span without error.type
        span = StoredSpan(
            trace_id="a" * 32,
            span_id="1" * 16,
            status="ERROR",
            attributes={}
        )

        # Get retry decision
        decision, reason, wait_seconds = get_retry_decision_from_span(span)

        # Verify results
        self.assertEqual(decision, "WAIT")
        self.assertEqual(wait_seconds, 5)

    def test_analyze_multiple_errors_permanent_takes_precedence(self):
        """Test that permanent errors take precedence over transient errors."""
        # Create test spans with mixed error types
        spans = [
            StoredSpan(
                trace_id="a" * 32,
                span_id="1" * 16,
                status="ERROR",
                attributes={"error.type": "ConnectionError"}
            ),
            StoredSpan(
                trace_id="a" * 32,
                span_id="2" * 16,
                status="ERROR",
                attributes={"error.type": "ValidationError"}
            ),
            StoredSpan(
                trace_id="a" * 32,
                span_id="3" * 16,
                status="ERROR",
                attributes={"error.type": "UnknownError"}
            )
        ]

        # Analyze multiple errors
        decision, reason, wait_seconds, span_id = analyze_multiple_errors(spans)

        # Verify results (ValidationError should take precedence)
        self.assertEqual(decision, "ABORT")
        self.assertEqual(wait_seconds, 0)
        self.assertEqual(span_id, "2" * 16)

    def test_analyze_multiple_errors_transient_takes_precedence_over_unknown(self):
        """Test that transient errors take precedence over unknown errors."""
        # Create test spans with mixed error types
        spans = [
            StoredSpan(
                trace_id="a" * 32,
                span_id="1" * 16,
                status="ERROR",
                attributes={"error.type": "UnknownError"}
            ),
            StoredSpan(
                trace_id="a" * 32,
                span_id="2" * 16,
                status="ERROR",
                attributes={"error.type": "TimeoutError"}
            )
        ]

        # Analyze multiple errors
        decision, reason, wait_seconds, span_id = analyze_multiple_errors(spans)

        # Verify results (TimeoutError should take precedence)
        self.assertEqual(decision, "RETRY")
        self.assertEqual(wait_seconds, 5)
        self.assertEqual(span_id, "2" * 16)

    def test_analyze_multiple_errors_all_unknown(self):
        """Test analyzing multiple unknown error types."""
        # Create test spans with all unknown error types
        spans = [
            StoredSpan(
                trace_id="a" * 32,
                span_id="1" * 16,
                status="ERROR",
                attributes={"error.type": "UnknownError1"}
            ),
            StoredSpan(
                trace_id="a" * 32,
                span_id="2" * 16,
                status="ERROR",
                attributes={"error.type": "UnknownError2"}
            )
        ]

        # Analyze multiple errors
        decision, reason, wait_seconds, span_id = analyze_multiple_errors(spans)

        # Verify results (first unknown error is used)
        self.assertEqual(decision, "WAIT")
        self.assertEqual(wait_seconds, 5)
        self.assertEqual(span_id, "1" * 16)

    @patch("observability.trace_retry.retry_logic.get_span_store")
    def test_should_retry_with_permanent_error(self, mock_get_span_store):
        """Test should_retry with a permanent error."""
        # Create mock span store and spans
        mock_store = MagicMock()
        mock_spans = [
            StoredSpan(
                trace_id="a" * 32,
                span_id="1" * 16,
                status="OK"
            ),
            StoredSpan(
                trace_id="a" * 32,
                span_id="2" * 16,
                status="ERROR",
                attributes={"error.type": "ValidationError"}
            )
        ]
        mock_store.get_trace.return_value = mock_spans
        mock_get_span_store.return_value = mock_store

        # Call should_retry
        result = should_retry("a" * 32)

        # Verify results
        self.assertEqual(result["decision"], "ABORT")
        self.assertEqual(result["wait_seconds"], 0)
        self.assertEqual(result["trace_id"], "a" * 32)
        self.assertEqual(result["span_id"], "2" * 16)

    @patch("observability.trace_retry.retry_logic.get_span_store")
    def test_should_retry_with_transient_error(self, mock_get_span_store):
        """Test should_retry with a transient error."""
        # Create mock span store and spans
        mock_store = MagicMock()
        mock_spans = [
            StoredSpan(
                trace_id="a" * 32,
                span_id="1" * 16,
                status="OK"
            ),
            StoredSpan(
                trace_id="a" * 32,
                span_id="2" * 16,
                status="ERROR",
                attributes={"error.type": "ConnectionError"}
            )
        ]
        mock_store.get_trace.return_value = mock_spans
        mock_get_span_store.return_value = mock_store

        # Call should_retry
        result = should_retry("a" * 32)

        # Verify results
        self.assertEqual(result["decision"], "RETRY")
        self.assertEqual(result["wait_seconds"], 5)
        self.assertEqual(result["trace_id"], "a" * 32)
        self.assertEqual(result["span_id"], "2" * 16)

    @patch("observability.trace_retry.retry_logic.get_span_store")
    def test_should_retry_with_unknown_error(self, mock_get_span_store):
        """Test should_retry with an unknown error."""
        # Create mock span store and spans
        mock_store = MagicMock()
        mock_spans = [
            StoredSpan(
                trace_id="a" * 32,
                span_id="1" * 16,
                status="OK"
            ),
            StoredSpan(
                trace_id="a" * 32,
                span_id="2" * 16,
                status="ERROR",
                attributes={"error.type": "UnknownError"}
            )
        ]
        mock_store.get_trace.return_value = mock_spans
        mock_get_span_store.return_value = mock_store

        # Call should_retry
        result = should_retry("a" * 32)

        # Verify results
        self.assertEqual(result["decision"], "WAIT")
        self.assertEqual(result["wait_seconds"], 5)
        self.assertEqual(result["trace_id"], "a" * 32)
        self.assertEqual(result["span_id"], "2" * 16)

    @patch("observability.trace_retry.retry_logic.get_span_store")
    def test_should_retry_with_retriable_attribute(self, mock_get_span_store):
        """Test should_retry with error.retriable attribute."""
        # Create mock span store and spans
        mock_store = MagicMock()
        mock_spans = [
            StoredSpan(
                trace_id="a" * 32,
                span_id="1" * 16,
                status="OK"
            ),
            StoredSpan(
                trace_id="a" * 32,
                span_id="2" * 16,
                status="ERROR",
                attributes={
                    "error.type": "ValidationError",  # Normally permanent
                    "error.retriable": True  # But explicitly marked as retriable
                }
            )
        ]
        mock_store.get_trace.return_value = mock_spans
        mock_get_span_store.return_value = mock_store

        # Call should_retry
        result = should_retry("a" * 32)

        # Verify results
        self.assertEqual(result["decision"], "RETRY")
        self.assertEqual(result["wait_seconds"], 5)
        self.assertEqual(result["trace_id"], "a" * 32)
        self.assertEqual(result["span_id"], "2" * 16)

    @patch("observability.trace_retry.retry_logic.get_span_store")
    def test_should_retry_with_no_errors(self, mock_get_span_store):
        """Test should_retry with no error spans."""
        # Create mock span store and spans
        mock_store = MagicMock()
        mock_spans = [
            StoredSpan(
                trace_id="a" * 32,
                span_id="1" * 16,
                status="OK"
            ),
            StoredSpan(
                trace_id="a" * 32,
                span_id="2" * 16,
                status="OK"
            )
        ]
        mock_store.get_trace.return_value = mock_spans
        mock_get_span_store.return_value = mock_store

        # Call should_retry
        result = should_retry("a" * 32)

        # Verify results
        self.assertEqual(result["decision"], "ABORT")
        self.assertTrue("No errors found" in result["reason"])
        self.assertEqual(result["trace_id"], "a" * 32)
        self.assertEqual(result["span_id"], "1" * 16)

    @patch("observability.trace_retry.retry_logic.get_span_store")
    def test_should_retry_with_invalid_trace_id(self, mock_get_span_store):
        """Test should_retry with an invalid trace ID."""
        # Setup mock
        mock_get_span_store.return_value = MagicMock()

        # Call should_retry with invalid trace ID
        with pytest.raises(ValueError, match="Invalid trace_id"):
            should_retry("invalid")

    @patch("observability.trace_retry.retry_logic.get_span_store")
    def test_should_retry_with_no_trace(self, mock_get_span_store):
        """Test should_retry with a non-existent trace."""
        # Create mock span store that returns empty list
        mock_store = MagicMock()
        mock_store.get_trace.return_value = []
        mock_get_span_store.return_value = mock_store

        # Call should_retry
        with pytest.raises(ValueError, match="No trace found"):
            should_retry("a" * 32)

    @patch("observability.trace_retry.retry_logic.get_span_store")
    def test_should_retry_with_span_store_error(self, mock_get_span_store):
        """Test should_retry when span store raises an exception."""
        # Create mock span store that raises exception
        mock_store = MagicMock()
        mock_store.get_trace.side_effect = Exception("Test exception")
        mock_get_span_store.return_value = mock_store

        # Call should_retry
        with pytest.raises(ValueError, match="Error retrieving trace data"):
            should_retry("a" * 32)


if __name__ == "__main__":
    unittest.main()