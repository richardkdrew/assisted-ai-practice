"""Tests for observability components."""

import pytest

from models.message import Conversation
from observability.tracer import get_trace_id, get_tracer


def test_get_trace_id_returns_current_trace():
    """Test getting the current trace ID."""
    tracer = get_tracer()

    with tracer.start_as_current_span("test_span"):
        trace_id = get_trace_id()
        assert trace_id != ""
        assert len(trace_id) == 32  # Hex string of 128-bit trace ID


def test_tracer_creates_spans():
    """Test that tracer can create spans."""
    tracer = get_tracer()

    with tracer.start_as_current_span("test_operation") as span:
        span.set_attribute("test_attr", "test_value")
        assert span.is_recording()


def test_nested_spans():
    """Test that nested spans work correctly."""
    tracer = get_tracer()

    with tracer.start_as_current_span("parent_span") as parent:
        parent.set_attribute("level", "parent")
        assert parent.is_recording()

        with tracer.start_as_current_span("child_span") as child:
            child.set_attribute("level", "child")
            assert child.is_recording()


def test_conversation_includes_trace_id():
    """Test that conversations can store trace IDs."""
    conv = Conversation(id="test-123", trace_id="abc123")
    assert conv.trace_id == "abc123"


def test_conversation_default_trace_id():
    """Test that conversations have default empty trace ID."""
    conv = Conversation(id="test-456")
    assert conv.trace_id == ""
