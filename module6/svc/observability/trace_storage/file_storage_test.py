"""
Unit tests for file storage operations.

This module tests the file I/O operations defined in trace_storage.file_storage,
including file creation, span appending, and reading.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from observability.trace_storage.file_storage import FileStorage
from observability.trace_storage.models import StoredSpan


class TestFileStorage:
    """Tests for the FileStorage class."""

    def setup_method(self):
        """Set up the test environment with a temporary directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, "test_trace_storage.jsonl")

    def teardown_method(self):
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_init_creates_file(self):
        """Test that initializing FileStorage creates the file and directories."""
        nested_path = os.path.join(self.temp_dir.name, "subdir", "nested", "trace_file.jsonl")
        storage = FileStorage(nested_path)
        assert os.path.exists(nested_path)
        assert os.path.isfile(nested_path)

    def test_init_with_empty_path(self):
        """Test that initializing with an empty path raises ValueError."""
        with pytest.raises(ValueError):
            FileStorage("")

    def test_append_span(self):
        """Test appending a single span."""
        storage = FileStorage(self.file_path)
        span = StoredSpan(
            trace_id="01234567890123456789012345678901",
            span_id="0123456789012345",
            name="test_span",
            status="OK",
            start_time=1000000000,
            end_time=1000000100,
        )

        # Append the span
        storage.append_span(span)

        # Verify the file contains one line
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1

            # Verify the content
            span_dict = json.loads(lines[0])
            assert span_dict["trace_id"] == span.trace_id
            assert span_dict["span_id"] == span.span_id
            assert span_dict["name"] == span.name

    def test_append_span_as_dict(self):
        """Test appending a span as a dictionary."""
        storage = FileStorage(self.file_path)
        span_dict = {
            "trace_id": "01234567890123456789012345678901",
            "span_id": "0123456789012345",
            "name": "test_span",
            "status": "OK",
            "start_time": 1000000000,
            "end_time": 1000000100,
        }

        # Append the span
        storage.append_span(span_dict)

        # Verify the file contains one line
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1

            # Verify the content
            stored_dict = json.loads(lines[0])
            assert stored_dict["trace_id"] == span_dict["trace_id"]
            assert stored_dict["span_id"] == span_dict["span_id"]
            assert stored_dict["name"] == span_dict["name"]

    def test_append_invalid_span(self):
        """Test that appending an invalid span raises ValueError."""
        storage = FileStorage(self.file_path)
        invalid_span = {"trace_id": "invalid", "span_id": "invalid"}

        with pytest.raises(ValueError):
            storage.append_span(invalid_span)

    def test_append_spans(self):
        """Test appending multiple spans."""
        storage = FileStorage(self.file_path)
        spans = [
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id="0123456789012345",
                name=f"test_span_{i}",
                status="OK",
                start_time=1000000000 + i * 1000,
                end_time=1000000100 + i * 1000,
            )
            for i in range(5)
        ]

        # Append the spans
        storage.append_spans(spans)

        # Verify the file contains five lines
        with open(self.file_path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 5

            # Verify each line
            for i, line in enumerate(lines):
                span_dict = json.loads(line)
                assert span_dict["trace_id"] == spans[i].trace_id
                assert span_dict["span_id"] == spans[i].span_id
                assert span_dict["name"] == spans[i].name

    def test_append_empty_spans_list(self):
        """Test appending an empty list of spans."""
        storage = FileStorage(self.file_path)
        storage.append_spans([])
        assert os.path.getsize(self.file_path) == 0

    def test_read_spans(self):
        """Test reading spans from the file."""
        storage = FileStorage(self.file_path)
        spans = [
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id=f"01234567890{i}2345",
                name=f"test_span_{i}",
                status="OK",
                start_time=1000000000 + i * 1000,
                end_time=1000000100 + i * 1000,
            )
            for i in range(5)
        ]

        # Append the spans
        storage.append_spans(spans)

        # Read the spans
        read_spans = storage.read_spans()
        assert len(read_spans) == 5

        # Verify the spans
        for i, span in enumerate(read_spans):
            assert span.trace_id == spans[i].trace_id
            assert span.span_id == spans[i].span_id
            assert span.name == spans[i].name
            assert span.status == spans[i].status
            assert span.start_time == spans[i].start_time
            assert span.end_time == spans[i].end_time

    def test_read_spans_with_limit(self):
        """Test reading a limited number of spans."""
        storage = FileStorage(self.file_path)
        spans = [
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id=f"01234567890{i}2345",
                name=f"test_span_{i}",
                status="OK",
                start_time=1000000000 + i * 1000,
                end_time=1000000100 + i * 1000,
            )
            for i in range(10)
        ]

        # Append the spans
        storage.append_spans(spans)

        # Read a limited number of spans
        read_spans = storage.read_spans(max_spans=3)
        assert len(read_spans) == 3

        # Verify the spans (should be the first 3)
        for i, span in enumerate(read_spans):
            assert span.trace_id == spans[i].trace_id
            assert span.span_id == spans[i].span_id
            assert span.name == spans[i].name

    def test_read_empty_file(self):
        """Test reading from an empty file."""
        storage = FileStorage(self.file_path)
        spans = storage.read_spans()
        assert len(spans) == 0

    def test_read_malformed_json(self):
        """Test reading malformed JSON."""
        storage = FileStorage(self.file_path)

        # Write valid and invalid JSON
        with open(self.file_path, "w") as f:
            f.write('{"trace_id": "01234567890123456789012345678901", "span_id": "0123456789012345"}\n')
            f.write("this is not json\n")
            f.write('{"trace_id": "12345678901234567890123456789012", "span_id": "5432109876543210"}\n')

        # Reading should raise an error
        with pytest.raises(ValueError):
            storage.read_spans()

    def test_get_file_size(self):
        """Test getting the file size."""
        storage = FileStorage(self.file_path)
        assert storage.get_file_size() == 0

        # Write some data
        storage.append_span(
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id="0123456789012345",
                name="test_span",
                status="OK",
                start_time=1000000000,
                end_time=1000000100,
            )
        )

        # Verify file size is non-zero
        assert storage.get_file_size() > 0

    def test_get_span_count(self):
        """Test getting the span count."""
        storage = FileStorage(self.file_path)
        assert storage.get_span_count() == 0

        # Write some spans
        spans = [
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id=f"01234567890{i}2345",
                name=f"test_span_{i}",
                status="OK",
                start_time=1000000000 + i * 1000,
                end_time=1000000100 + i * 1000,
            )
            for i in range(5)
        ]
        storage.append_spans(spans)

        # Verify span count
        assert storage.get_span_count() == 5

    def test_clear(self):
        """Test clearing the file."""
        storage = FileStorage(self.file_path)

        # Write some spans
        spans = [
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id=f"01234567890{i}2345",
                name=f"test_span_{i}",
                status="OK",
                start_time=1000000000 + i * 1000,
                end_time=1000000100 + i * 1000,
            )
            for i in range(5)
        ]
        storage.append_spans(spans)
        assert storage.get_span_count() == 5

        # Clear the file
        storage.clear()
        assert storage.get_span_count() == 0
        assert os.path.exists(self.file_path)
        assert os.path.getsize(self.file_path) == 0

    def test_truncate_to_last_n_spans(self):
        """Test truncating to last N spans."""
        storage = FileStorage(self.file_path)

        # Write some spans
        spans = [
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id=f"01234567890{i}2345",
                name=f"test_span_{i}",
                status="OK",
                start_time=1000000000 + i * 1000,
                end_time=1000000100 + i * 1000,
            )
            for i in range(10)
        ]
        storage.append_spans(spans)
        assert storage.get_span_count() == 10

        # Truncate to last 3 spans
        storage.truncate_to_last_n_spans(3)
        read_spans = storage.read_spans()
        assert len(read_spans) == 3

        # Verify the spans are the last 3
        for i, span in enumerate(read_spans):
            original_index = i + 7  # 7, 8, 9
            assert span.trace_id == spans[original_index].trace_id
            assert span.span_id == spans[original_index].span_id
            assert span.name == spans[original_index].name

    def test_truncate_with_invalid_n(self):
        """Test truncating with an invalid N."""
        storage = FileStorage(self.file_path)
        with pytest.raises(ValueError):
            storage.truncate_to_last_n_spans(0)

    def test_truncate_with_fewer_spans(self):
        """Test truncating when there are fewer spans than N."""
        storage = FileStorage(self.file_path)

        # Write some spans
        spans = [
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id=f"01234567890{i}2345",
                name=f"test_span_{i}",
                status="OK",
                start_time=1000000000 + i * 1000,
                end_time=1000000100 + i * 1000,
            )
            for i in range(5)
        ]
        storage.append_spans(spans)
        assert storage.get_span_count() == 5

        # Truncate to last 10 spans (more than available)
        storage.truncate_to_last_n_spans(10)
        read_spans = storage.read_spans()
        assert len(read_spans) == 5  # All spans should remain