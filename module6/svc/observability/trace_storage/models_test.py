"""
Unit tests for span storage data models.

This module tests the data models defined in trace_storage.models,
including validation, serialization, and filtering.
"""

import json
import pytest
from typing import Dict, Any

from observability.trace_storage.models import StoredSpan, AttributeFilter, SpanQuery


class TestStoredSpan:
    """Tests for the StoredSpan class."""

    def test_valid_span(self):
        """Test that a valid span can be created."""
        span = StoredSpan(
            trace_id="01234567890123456789012345678901",
            span_id="0123456789012345",
            name="test_span",
            status="OK",
            start_time=1000000000,
            end_time=1000000100,
        )
        assert span.trace_id == "01234567890123456789012345678901"
        assert span.span_id == "0123456789012345"
        assert span.name == "test_span"
        assert span.status == "OK"
        assert span.start_time == 1000000000
        assert span.end_time == 1000000100
        assert span.duration_ns == 100  # Calculated from start and end time

    def test_invalid_trace_id(self):
        """Test that an invalid trace_id raises ValueError."""
        with pytest.raises(ValueError):
            StoredSpan(
                trace_id="invalid",
                span_id="0123456789012345",
            )

    def test_invalid_span_id(self):
        """Test that an invalid span_id raises ValueError."""
        with pytest.raises(ValueError):
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id="invalid",
            )

    def test_invalid_parent_span_id(self):
        """Test that an invalid parent_span_id raises ValueError."""
        with pytest.raises(ValueError):
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id="0123456789012345",
                parent_span_id="invalid",
            )

    def test_invalid_status(self):
        """Test that an invalid status raises ValueError."""
        with pytest.raises(ValueError):
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id="0123456789012345",
                status="INVALID",
            )

    def test_invalid_timestamps(self):
        """Test that end_time before start_time raises ValueError."""
        with pytest.raises(ValueError):
            StoredSpan(
                trace_id="01234567890123456789012345678901",
                span_id="0123456789012345",
                start_time=1000000100,
                end_time=1000000000,
            )

    def test_serialization(self):
        """Test that a span can be serialized to a dictionary and back."""
        original_span = StoredSpan(
            trace_id="01234567890123456789012345678901",
            span_id="0123456789012345",
            parent_span_id="0123456789abcdef",
            name="test_span",
            status="ERROR",
            status_description="Test error",
            start_time=1000000000,
            end_time=1000000100,
            attributes={"key1": "value1", "key2": 2},
            events=[{"time": 1000000050, "name": "event1"}],
            links=[{"trace_id": "fedcba9876543210fedcba9876543210", "span_id": "fedcba9876543210"}],
            service_name="test_service",
            resource_attributes={"service.version": "1.0"},
        )

        # Convert to dictionary
        span_dict = original_span.to_dict()

        # Verify all fields are included
        assert span_dict["trace_id"] == original_span.trace_id
        assert span_dict["span_id"] == original_span.span_id
        assert span_dict["parent_span_id"] == original_span.parent_span_id
        assert span_dict["name"] == original_span.name
        assert span_dict["status"] == original_span.status
        assert span_dict["status_description"] == original_span.status_description
        assert span_dict["start_time"] == original_span.start_time
        assert span_dict["end_time"] == original_span.end_time
        assert span_dict["duration_ns"] == original_span.duration_ns
        assert span_dict["attributes"] == original_span.attributes
        assert span_dict["events"] == original_span.events
        assert span_dict["links"] == original_span.links
        assert span_dict["service_name"] == original_span.service_name
        assert span_dict["resource_attributes"] == original_span.resource_attributes

        # Convert back to span
        reconstructed_span = StoredSpan.from_dict(span_dict)

        # Verify reconstructed span matches original
        assert reconstructed_span.trace_id == original_span.trace_id
        assert reconstructed_span.span_id == original_span.span_id
        assert reconstructed_span.parent_span_id == original_span.parent_span_id
        assert reconstructed_span.name == original_span.name
        assert reconstructed_span.status == original_span.status
        assert reconstructed_span.status_description == original_span.status_description
        assert reconstructed_span.start_time == original_span.start_time
        assert reconstructed_span.end_time == original_span.end_time
        assert reconstructed_span.duration_ns == original_span.duration_ns
        assert reconstructed_span.attributes == original_span.attributes
        assert reconstructed_span.events == original_span.events
        assert reconstructed_span.links == original_span.links
        assert reconstructed_span.service_name == original_span.service_name
        assert reconstructed_span.resource_attributes == original_span.resource_attributes

    def test_json_serialization(self):
        """Test that a span can be serialized to JSON and back."""
        original_span = StoredSpan(
            trace_id="01234567890123456789012345678901",
            span_id="0123456789012345",
            name="test_span",
            status="OK",
            start_time=1000000000,
            end_time=1000000100,
            attributes={"key1": "value1", "key2": 2},
        )

        # Convert to JSON
        json_str = json.dumps(original_span.to_dict())

        # Convert back from JSON
        span_dict = json.loads(json_str)
        reconstructed_span = StoredSpan.from_dict(span_dict)

        # Verify reconstructed span matches original
        assert reconstructed_span.trace_id == original_span.trace_id
        assert reconstructed_span.span_id == original_span.span_id
        assert reconstructed_span.name == original_span.name
        assert reconstructed_span.status == original_span.status
        assert reconstructed_span.start_time == original_span.start_time
        assert reconstructed_span.end_time == original_span.end_time
        assert reconstructed_span.duration_ns == original_span.duration_ns
        assert reconstructed_span.attributes == original_span.attributes


class TestAttributeFilter:
    """Tests for the AttributeFilter class."""

    def test_valid_filter(self):
        """Test that a valid filter can be created."""
        filter = AttributeFilter(key="key1", value="value1")
        assert filter.key == "key1"
        assert filter.value == "value1"
        assert filter.operator == "EQUALS"  # Default operator

    def test_empty_key(self):
        """Test that an empty key raises ValueError."""
        with pytest.raises(ValueError):
            AttributeFilter(key="", value="value1")

    def test_invalid_operator(self):
        """Test that an invalid operator raises ValueError."""
        with pytest.raises(ValueError):
            AttributeFilter(key="key1", value="value1", operator="INVALID")

    def create_test_span(self) -> StoredSpan:
        """Create a test span with various attributes."""
        return StoredSpan(
            trace_id="01234567890123456789012345678901",
            span_id="0123456789012345",
            attributes={
                "string_attr": "test_value",
                "int_attr": 42,
                "float_attr": 3.14,
                "bool_attr": True,
                "list_attr": ["a", "b", "c"],
                "dict_attr": {"a": 1, "b": 2},
                "null_attr": None,
            },
        )

    def test_equals_operator(self):
        """Test the EQUALS operator."""
        span = self.create_test_span()

        # String equality
        filter = AttributeFilter(key="string_attr", value="test_value")
        assert filter.matches(span) is True

        # Different value
        filter = AttributeFilter(key="string_attr", value="different")
        assert filter.matches(span) is False

        # Int equality
        filter = AttributeFilter(key="int_attr", value=42)
        assert filter.matches(span) is True

        # Float equality
        filter = AttributeFilter(key="float_attr", value=3.14)
        assert filter.matches(span) is True

        # Boolean equality
        filter = AttributeFilter(key="bool_attr", value=True)
        assert filter.matches(span) is True

        # None equality
        filter = AttributeFilter(key="null_attr", value=None)
        assert filter.matches(span) is True

        # Missing key
        filter = AttributeFilter(key="missing_attr", value="value")
        assert filter.matches(span) is False

    def test_not_equals_operator(self):
        """Test the NOT_EQUALS operator."""
        span = self.create_test_span()

        # String inequality
        filter = AttributeFilter(key="string_attr", value="different", operator="NOT_EQUALS")
        assert filter.matches(span) is True

        # Same value
        filter = AttributeFilter(key="string_attr", value="test_value", operator="NOT_EQUALS")
        assert filter.matches(span) is False

        # Int inequality
        filter = AttributeFilter(key="int_attr", value=43, operator="NOT_EQUALS")
        assert filter.matches(span) is True

        # Missing key
        filter = AttributeFilter(key="missing_attr", value="value", operator="NOT_EQUALS")
        assert filter.matches(span) is False

    def test_contains_operator(self):
        """Test the CONTAINS operator."""
        span = self.create_test_span()

        # String contains
        filter = AttributeFilter(key="string_attr", value="test", operator="CONTAINS")
        assert filter.matches(span) is True

        # String doesn't contain
        filter = AttributeFilter(key="string_attr", value="missing", operator="CONTAINS")
        assert filter.matches(span) is False

        # List contains
        filter = AttributeFilter(key="list_attr", value="b", operator="CONTAINS")
        assert filter.matches(span) is True

        # List doesn't contain
        filter = AttributeFilter(key="list_attr", value="z", operator="CONTAINS")
        assert filter.matches(span) is False

        # Dict contains key
        filter = AttributeFilter(key="dict_attr", value="a", operator="CONTAINS")
        assert filter.matches(span) is True

        # Dict doesn't contain key
        filter = AttributeFilter(key="dict_attr", value="z", operator="CONTAINS")
        assert filter.matches(span) is False

        # Incompatible types
        filter = AttributeFilter(key="int_attr", value="4", operator="CONTAINS")
        assert filter.matches(span) is False

    def test_greater_than_operator(self):
        """Test the GREATER_THAN operator."""
        span = self.create_test_span()

        # Int greater than
        filter = AttributeFilter(key="int_attr", value=41, operator="GREATER_THAN")
        assert filter.matches(span) is True

        # Int not greater than
        filter = AttributeFilter(key="int_attr", value=42, operator="GREATER_THAN")
        assert filter.matches(span) is False

        # Float greater than
        filter = AttributeFilter(key="float_attr", value=3.13, operator="GREATER_THAN")
        assert filter.matches(span) is True

        # String comparison (lexicographic)
        filter = AttributeFilter(key="string_attr", value="aaa", operator="GREATER_THAN")
        assert filter.matches(span) is True

        # Incompatible types
        filter = AttributeFilter(key="string_attr", value=42, operator="GREATER_THAN")
        assert filter.matches(span) is False

    def test_less_than_operator(self):
        """Test the LESS_THAN operator."""
        span = self.create_test_span()

        # Int less than
        filter = AttributeFilter(key="int_attr", value=43, operator="LESS_THAN")
        assert filter.matches(span) is True

        # Int not less than
        filter = AttributeFilter(key="int_attr", value=42, operator="LESS_THAN")
        assert filter.matches(span) is False

        # Float less than
        filter = AttributeFilter(key="float_attr", value=3.15, operator="LESS_THAN")
        assert filter.matches(span) is True

        # String comparison (lexicographic)
        filter = AttributeFilter(key="string_attr", value="zzz", operator="LESS_THAN")
        assert filter.matches(span) is True

        # Incompatible types
        filter = AttributeFilter(key="int_attr", value="42", operator="LESS_THAN")
        assert filter.matches(span) is False


class TestSpanQuery:
    """Tests for the SpanQuery class."""

    def test_default_values(self):
        """Test that a query with default values can be created."""
        query = SpanQuery()
        assert query.trace_id is None
        assert query.span_ids is None
        assert query.status is None
        assert query.service_name is None
        assert query.operation_name is None
        assert query.start_time_min is None
        assert query.start_time_max is None
        assert query.attribute_filters is None
        assert query.max_spans == 100
        assert query.order_by == "start_time"
        assert query.order_direction == "DESC"

    def test_custom_values(self):
        """Test that a query with custom values can be created."""
        query = SpanQuery(
            trace_id="01234567890123456789012345678901",
            span_ids=["0123456789012345", "fedcba9876543210"],
            status="ERROR",
            service_name="test_service",
            operation_name="test_operation",
            start_time_min=1000000000,
            start_time_max=2000000000,
            attribute_filters=[AttributeFilter(key="key1", value="value1")],
            max_spans=10,
            order_by="duration_ns",
            order_direction="ASC",
        )
        assert query.trace_id == "01234567890123456789012345678901"
        assert query.span_ids == ["0123456789012345", "fedcba9876543210"]
        assert query.status == "ERROR"
        assert query.service_name == "test_service"
        assert query.operation_name == "test_operation"
        assert query.start_time_min == 1000000000
        assert query.start_time_max == 2000000000
        assert len(query.attribute_filters) == 1
        assert query.attribute_filters[0].key == "key1"
        assert query.attribute_filters[0].value == "value1"
        assert query.max_spans == 10
        assert query.order_by == "duration_ns"
        assert query.order_direction == "ASC"

    def test_invalid_trace_id(self):
        """Test that an invalid trace_id raises ValueError."""
        with pytest.raises(ValueError):
            SpanQuery(trace_id="invalid")

    def test_invalid_span_ids(self):
        """Test that invalid span_ids raise ValueError."""
        with pytest.raises(ValueError):
            SpanQuery(span_ids=["invalid"])

    def test_invalid_status(self):
        """Test that an invalid status raises ValueError."""
        with pytest.raises(ValueError):
            SpanQuery(status="INVALID")

    def test_invalid_max_spans(self):
        """Test that an invalid max_spans raises ValueError."""
        with pytest.raises(ValueError):
            SpanQuery(max_spans=0)

    def test_invalid_order_by(self):
        """Test that an invalid order_by raises ValueError."""
        with pytest.raises(ValueError):
            SpanQuery(order_by="invalid")

    def test_invalid_order_direction(self):
        """Test that an invalid order_direction raises ValueError."""
        with pytest.raises(ValueError):
            SpanQuery(order_direction="INVALID")

    def test_invalid_time_range(self):
        """Test that an invalid time range raises ValueError."""
        with pytest.raises(ValueError):
            SpanQuery(start_time_min=2000000000, start_time_max=1000000000)

    def test_empty_lists(self):
        """Test handling of empty lists."""
        query = SpanQuery(span_ids=[], attribute_filters=[])
        assert query.span_ids is None
        assert query.attribute_filters is None