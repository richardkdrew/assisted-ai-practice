"""
Unit tests for the FileBasedSpanProcessor.

This module tests the FileBasedSpanProcessor class, which implements the
OpenTelemetry SpanProcessor interface to store spans in a file.
"""

import json
import os
import tempfile
import time
from unittest.mock import MagicMock, patch

import pytest
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter
from opentelemetry.trace import SpanContext, SpanKind, TraceFlags

from observability.trace_storage.file_span_processor import FileBasedSpanProcessor
from observability.trace_storage.models import StoredSpan


class TestFileBasedSpanProcessor:
    """Tests for the FileBasedSpanProcessor class."""

    def setup_method(self):
        """Set up the test environment with a temporary directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, "test_trace_storage.jsonl")

    def teardown_method(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def create_mock_span(
        self,
        trace_id="01234567890123456789012345678901",
        span_id="0123456789012345",
        parent_span_id="abcdef0123456789",
        name="test_span",
        start_time=None,
        end_time=None,
        status_code="OK",
        status_description=None,
        attributes=None,
        events=None,
        links=None,
        resource_attributes=None,
        service_name="test_service",
    ):
        """Create a mock ReadableSpan for testing."""
        if start_time is None:
            start_time = int(time.time() * 1e9)
        if end_time is None:
            end_time = start_time + 100000000  # 100 ms
        if attributes is None:
            attributes = {}
        if events is None:
            events = []
        if links is None:
            links = []
        if resource_attributes is None:
            resource_attributes = {"service.name": service_name}

        span_context = SpanContext(
            trace_id=int(trace_id, 16),
            span_id=int(span_id, 16),
            is_remote=False,
            trace_flags=TraceFlags(1),
        )

        mock_span = MagicMock(spec=ReadableSpan)
        mock_span.name = name
        mock_span.context = span_context
        mock_span.parent = (
            SpanContext(
                trace_id=int(trace_id, 16),
                span_id=int(parent_span_id, 16),
                is_remote=False,
                trace_flags=TraceFlags(1),
            )
            if parent_span_id
            else None
        )
        mock_span.start_time = start_time
        mock_span.end_time = end_time
        mock_span.status.status_code = status_code
        mock_span.status.description = status_description
        mock_span.attributes = attributes
        mock_span.events = events
        mock_span.links = links
        mock_span.resource.attributes = resource_attributes
        mock_span.kind = SpanKind.INTERNAL

        return mock_span

    def test_init(self):
        """Test initialization of the processor."""
        processor = FileBasedSpanProcessor(self.file_path)
        assert os.path.exists(self.file_path)

        # Verify default max_spans
        assert processor._max_spans == 1000

        # Verify custom max_spans
        processor = FileBasedSpanProcessor(self.file_path, max_spans=500)
        assert processor._max_spans == 500

    def test_init_with_invalid_max_spans(self):
        """Test initialization with invalid max_spans."""
        with pytest.raises(ValueError):
            FileBasedSpanProcessor(self.file_path, max_spans=0)

    def test_on_start(self):
        """Test on_start method (no-op for this processor)."""
        processor = FileBasedSpanProcessor(self.file_path)
        mock_span = MagicMock()
        parent_context = MagicMock()

        # Should not raise any exceptions
        processor.on_start(mock_span, parent_context)

    def test_on_end(self):
        """Test on_end method processes completed spans."""
        processor = FileBasedSpanProcessor(self.file_path)
        mock_span = self.create_mock_span()

        # Process a span
        processor.on_end(mock_span)

        # Verify the span was written to the file
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1

            # Parse the stored span
            stored_span_dict = json.loads(lines[0])
            stored_span = StoredSpan.from_dict(stored_span_dict)

            # Verify conversion
            assert stored_span.trace_id == "01234567890123456789012345678901"
            assert stored_span.span_id == "0123456789012345"
            assert stored_span.parent_span_id == "abcdef0123456789"
            assert stored_span.name == "test_span"
            assert stored_span.start_time == mock_span.start_time
            assert stored_span.end_time == mock_span.end_time
            assert stored_span.status == "OK"
            assert stored_span.service_name == "test_service"

    def test_process_multiple_spans(self):
        """Test processing multiple spans."""
        processor = FileBasedSpanProcessor(self.file_path)

        # Create and process multiple spans
        spans = [
            self.create_mock_span(
                trace_id="01234567890123456789012345678901",
                span_id=f"{i:016x}",
                name=f"test_span_{i}",
                status_code="OK" if i % 2 == 0 else "ERROR",
                attributes={"key": f"value_{i}"},
            )
            for i in range(5)
        ]

        for span in spans:
            processor.on_end(span)

        # Verify all spans were written
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 5

        # Verify spans can be retrieved by trace ID
        stored_spans = processor.get_trace("01234567890123456789012345678901")
        assert len(stored_spans) == 5

        # Verify order is by start time
        for i in range(len(stored_spans) - 1):
            assert stored_spans[i].start_time <= stored_spans[i + 1].start_time

    def test_shutdown(self):
        """Test shutdown method flushes spans."""
        processor = FileBasedSpanProcessor(self.file_path)

        # Add a span to the processor
        mock_span = self.create_mock_span()
        processor.on_end(mock_span)

        # Call shutdown
        processor.shutdown()

        # Verify the span was written
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1

    def test_force_flush(self):
        """Test force_flush method."""
        processor = FileBasedSpanProcessor(self.file_path)

        # Add a span to the processor
        mock_span = self.create_mock_span()
        processor.on_end(mock_span)

        # Force flush
        result = processor.force_flush()
        assert result is True

        # Verify the span was written
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1

    def test_span_limit(self):
        """Test span count limit is enforced."""
        max_spans = 3
        processor = FileBasedSpanProcessor(self.file_path, max_spans=max_spans)

        # Create and process more spans than the limit
        spans = [
            self.create_mock_span(
                trace_id="01234567890123456789012345678901",
                span_id=f"{i:016x}",
                name=f"test_span_{i}",
            )
            for i in range(5)
        ]

        for span in spans:
            processor.on_end(span)

        # Verify only max_spans are stored in-memory
        assert processor._store.get_span_count() == max_spans

        # Verify file contains all spans
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 5

    def test_convert_otel_span(self):
        """Test conversion from OpenTelemetry span to StoredSpan."""
        processor = FileBasedSpanProcessor(self.file_path)

        # Create a mock span with various attributes
        attrs = {
            "http.method": "GET",
            "http.url": "http://example.com",
            "http.status_code": 200,
            "boolean_attr": True,
            "number_attr": 42,
            "none_attr": None,
        }
        events = [
            MagicMock(
                name="event1",
                timestamp=1000000050,
                attributes={"event.key": "event.value"},
            ),
            MagicMock(
                name="event2",
                timestamp=1000000070,
                attributes={"event.key2": "event.value2"},
            ),
        ]
        links = [
            MagicMock(
                context=SpanContext(
                    trace_id=int("fedcba9876543210fedcba9876543210", 16),
                    span_id=int("fedcba9876543210", 16),
                    is_remote=False,
                    trace_flags=TraceFlags(1),
                ),
                attributes={"link.key": "link.value"},
            )
        ]
        resource_attrs = {
            "service.name": "test_service",
            "service.version": "1.0",
            "deployment.environment": "test",
        }

        mock_span = self.create_mock_span(
            name="complex_span",
            status_code="ERROR",
            status_description="Something went wrong",
            attributes=attrs,
            events=events,
            links=links,
            resource_attributes=resource_attrs,
        )

        # Convert the span
        stored_span = processor._convert_otel_span(mock_span)

        # Verify conversion
        assert stored_span.name == "complex_span"
        assert stored_span.status == "ERROR"
        assert stored_span.status_description == "Something went wrong"

        # Verify attributes
        assert stored_span.attributes["http.method"] == "GET"
        assert stored_span.attributes["http.url"] == "http://example.com"
        assert stored_span.attributes["http.status_code"] == 200
        assert stored_span.attributes["boolean_attr"] is True
        assert stored_span.attributes["number_attr"] == 42
        assert "none_attr" not in stored_span.attributes  # None attributes are filtered

        # Verify events
        assert len(stored_span.events) == 2
        assert stored_span.events[0]["name"] == "event1"
        assert stored_span.events[0]["attributes"]["event.key"] == "event.value"
        assert stored_span.events[1]["name"] == "event2"
        assert stored_span.events[1]["attributes"]["event.key2"] == "event.value2"

        # Verify links
        assert len(stored_span.links) == 1
        assert stored_span.links[0]["trace_id"] == "fedcba9876543210fedcba9876543210"
        assert stored_span.links[0]["span_id"] == "fedcba9876543210"
        assert stored_span.links[0]["attributes"]["link.key"] == "link.value"

        # Verify resource attributes
        assert stored_span.resource_attributes["service.name"] == "test_service"
        assert stored_span.resource_attributes["service.version"] == "1.0"
        assert stored_span.resource_attributes["deployment.environment"] == "test"

        # Verify service name
        assert stored_span.service_name == "test_service"

    def test_invalid_file_path(self):
        """Test initialization with an invalid file path."""
        with pytest.raises(IOError):
            FileBasedSpanProcessor("/invalid/path/that/doesnt/exist/file.jsonl")

    def test_error_status_handling(self):
        """Test handling of error statuses."""
        processor = FileBasedSpanProcessor(self.file_path)

        # Create a span with error status
        error_span = self.create_mock_span(
            status_code="ERROR",
            status_description="Test error",
            attributes={"error.type": "TestError", "error.message": "Test error message"}
        )

        # Process the span
        processor.on_end(error_span)

        # Retrieve all spans
        with open(self.file_path, "r") as f:
            stored_span_dict = json.loads(f.readline())
            stored_span = StoredSpan.from_dict(stored_span_dict)

        # Verify error status
        assert stored_span.status == "ERROR"
        assert stored_span.status_description == "Test error"
        assert stored_span.attributes["error.type"] == "TestError"
        assert stored_span.attributes["error.message"] == "Test error message"