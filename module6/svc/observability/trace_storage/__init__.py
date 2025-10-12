"""
File-based trace storage module for OpenTelemetry.

This module provides functionality for storing OpenTelemetry spans to a file
and maintaining an in-memory index for efficient querying.
"""

from .file_span_processor import FileBasedSpanProcessor

__all__ = ["FileBasedSpanProcessor"]