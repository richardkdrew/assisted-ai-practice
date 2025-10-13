"""
Trace query module for OpenTelemetry.

This module provides functionality for querying traces stored
by the file-based span processor, including filtering by trace ID,
time range, status, and attributes.
"""

from .query import (
    get_trace,
    recent_failures,
    filter_by_error_type,
    filter_by_attribute,
    filter_by_status,
    filter_by_time,
    time_to_nanoseconds,
    get_time_range,
    query_spans,
)

# Import cli module explicitly
from . import cli

__all__ = [
    "get_trace",
    "recent_failures",
    "filter_by_error_type",
    "filter_by_attribute",
    "filter_by_status",
    "filter_by_time",
    "time_to_nanoseconds",
    "get_time_range",
    "query_spans",
    "cli",
]