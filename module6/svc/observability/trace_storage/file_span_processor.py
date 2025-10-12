"""
File-based OpenTelemetry span processor.

This module provides a custom OpenTelemetry SpanProcessor implementation
that stores spans to a file and provides querying functionality.

Key Features:
- Persists spans to a JSON Lines file for durability
- Maintains an in-memory index for efficient querying
- Thread-safe operations for concurrent processing
- Memory usage monitoring and adaptive capacity
- Implements the OpenTelemetry SpanProcessor interface

Environment Variables:
- TRACE_STORAGE_PATH: Path to store trace data (default: data/traces/trace_storage.jsonl)
- TRACE_MAX_SPANS: Maximum spans to keep in memory (default: 1000)
- TRACE_MEMORY_CHECK_INTERVAL: How often to check memory usage (default: every 100 spans)
- TRACE_MAX_MEMORY_MB: Maximum memory usage in MB (default: 256)

Usage Example:
    ```python
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from observability.trace_storage.file_span_processor import FileBasedSpanProcessor

    # Set up the tracer with file-based processor
    provider = TracerProvider()
    processor = FileBasedSpanProcessor("traces/app_traces.jsonl")
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Now spans will be automatically stored to the file
    ```
"""

import gc
import logging
import os
import sys
import threading
import time
from typing import Dict, List, Optional, Set, Tuple

from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor
from opentelemetry.trace import SpanContext, Status, StatusCode

from .file_storage import FileStorage
from .models import StoredSpan
from .span_store import SpanStore

# Global span store instance
_GLOBAL_SPAN_STORE = None
_GLOBAL_SPAN_STORE_LOCK = threading.Lock()

# Setup module logger
logger = logging.getLogger(__name__)


def get_span_store() -> SpanStore:
    """
    Get the global span store instance.

    Returns:
        The global SpanStore instance
    """
    global _GLOBAL_SPAN_STORE
    return _GLOBAL_SPAN_STORE


class FileBasedSpanProcessor(SpanProcessor):
    """
    OpenTelemetry SpanProcessor that stores spans to a file and provides querying.

    This processor stores completed spans to a file in JSON Lines format
    and maintains an in-memory index for efficient querying.

    Args:
        file_path: Path to the trace storage file
        max_spans: Maximum number of spans to retain in memory (default: 1000)

    Raises:
        ValueError: If max_spans <= 0
        IOError: If file cannot be accessed
    """

    def __init__(self, file_path: str, max_spans: int = 1000):
        """
        Initialize the file-based span processor.

        Args:
            file_path: Path to the trace storage file
            max_spans: Maximum number of spans to retain in memory

        Raises:
            ValueError: If max_spans <= 0
            IOError: If file cannot be created or accessed
        """
        if max_spans <= 0:
            raise ValueError(f"Invalid max_spans: {max_spans}. Must be positive.")

        self._file_path = file_path
        self._max_spans = max_spans
        self._storage = FileStorage(file_path)
        self._store = SpanStore(max_spans)
        self._lock = threading.Lock()
        self.logger = logger  # Use the module-level logger

        # Initialize or re-use global span store
        global _GLOBAL_SPAN_STORE
        with _GLOBAL_SPAN_STORE_LOCK:
            if _GLOBAL_SPAN_STORE is None:
                _GLOBAL_SPAN_STORE = self._store

        # Populate from existing file if it exists and has content
        self._load_existing_spans()

        # Memory management parameters
        self._memory_check_interval = int(os.getenv("TRACE_MEMORY_CHECK_INTERVAL", "100"))
        self._max_memory_mb = int(os.getenv("TRACE_MAX_MEMORY_MB", "256"))
        self._span_count = 0
        self._last_memory_check = 0

    def _load_existing_spans(self):
        """
        Load existing spans from the storage file into memory.

        This is called during initialization to populate the in-memory store
        from previously stored spans.
        """
        try:
            spans = self._storage.read_spans(self._max_spans)
            for span in spans:
                self._store.add_span(span)

            if spans:
                self.logger.info(f"Loaded {len(spans)} spans from {self._file_path}")
        except Exception as e:
            self.logger.error(f"Error loading spans from file: {e}")

    def on_start(self, span: "opentelemetry.trace.Span", parent_context: Optional[SpanContext] = None) -> None:
        """
        Called when a span starts.

        This is a no-op for this processor as we only care about completed spans.

        Args:
            span: The span that started
            parent_context: The parent context, if any
        """
        # No-op: we only process completed spans

    def _check_memory_usage(self) -> bool:
        """
        Check memory usage and potentially reduce the max spans if needed.

        This method periodically checks memory usage and reduces the max_spans
        parameter if memory usage is too high.

        Returns:
            True if memory usage is within limits, False otherwise
        """
        # Only check memory usage periodically
        self._span_count += 1
        if self._span_count - self._last_memory_check < self._memory_check_interval:
            return True

        # Update the last check counter
        self._last_memory_check = self._span_count

        # Ensure garbage collection has run to get accurate memory usage
        gc.collect()

        # Check memory usage
        try:
            # Get current memory usage in MB
            memory_usage_mb = sys.getsizeof(self._store) / (1024 * 1024)

            # If we're using more than 90% of max memory, reduce the max spans
            if memory_usage_mb > 0.9 * self._max_memory_mb:
                # Calculate a new, lower max_spans value (reduce by 20%)
                new_max_spans = int(self._store.max_spans * 0.8)
                if new_max_spans < 100:
                    new_max_spans = 100  # Ensure we don't go too low

                # If the new value is lower than the current, update it
                if new_max_spans < self._store.max_spans:
                    self.logger.warning(
                        f"Memory usage high ({memory_usage_mb:.2f} MB), reducing max spans "
                        f"from {self._store.max_spans} to {new_max_spans}"
                    )
                    self._store.max_spans = new_max_spans

                    # Force eviction of spans
                    self._store._enforce_max_spans()

                    # Run garbage collection again
                    gc.collect()
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking memory usage: {e}")
            return True

    def on_end(self, span: ReadableSpan) -> None:
        """
        Called when a span ends.

        Processes the completed span by converting it to StoredSpan format,
        writing it to the trace file, and adding it to the in-memory indices.

        Args:
            span: The completed span
        """
        try:
            # Convert to StoredSpan format
            stored_span = self._convert_otel_span(span)

            # Write to file
            self._storage.append_span(stored_span)

            # Add to in-memory store
            with self._lock:
                self._store.add_span(stored_span)

                # Check memory usage periodically
                self._check_memory_usage()

        except Exception as e:
            self.logger.error(f"Error processing span: {e}")

    def _convert_otel_span(self, span: ReadableSpan) -> StoredSpan:
        """
        Convert an OpenTelemetry span to StoredSpan format.

        Args:
            span: The OpenTelemetry ReadableSpan to convert

        Returns:
            StoredSpan: The converted span
        """
        # Extract trace and span IDs
        trace_id_hex = format(span.context.trace_id, "032x")
        span_id_hex = format(span.context.span_id, "016x")

        # Extract parent span ID if present
        parent_span_id = None
        if span.parent is not None:
            parent_span_id = format(span.parent.span_id, "016x")

        # Extract status
        status = "OK"
        status_description = None
        if span.status.status_code == StatusCode.ERROR:
            status = "ERROR"
            status_description = span.status.description

        # Extract attributes (filter out None values)
        attributes = {k: v for k, v in span.attributes.items() if v is not None}

        # Extract events
        events = []
        for event in span.events:
            events.append({
                "name": event.name,
                "timestamp": event.timestamp,
                "attributes": {k: v for k, v in event.attributes.items() if v is not None}
            })

        # Extract links
        links = []
        for link in span.links:
            links.append({
                "trace_id": format(link.context.trace_id, "032x"),
                "span_id": format(link.context.span_id, "016x"),
                "attributes": {k: v for k, v in link.attributes.items() if v is not None}
            })

        # Extract resource attributes
        resource_attributes = {k: v for k, v in span.resource.attributes.items() if v is not None}

        # Extract service name
        service_name = resource_attributes.get("service.name", "unknown-service")

        # Create StoredSpan
        return StoredSpan(
            trace_id=trace_id_hex,
            span_id=span_id_hex,
            parent_span_id=parent_span_id,
            name=span.name,
            status=status,
            status_description=status_description,
            start_time=span.start_time,
            end_time=span.end_time,
            duration_ns=(span.end_time - span.start_time),
            attributes=attributes,
            events=events,
            links=links,
            service_name=service_name,
            resource_attributes=resource_attributes,
        )

    def shutdown(self) -> None:
        """
        Shuts down the processor.

        Flushes any pending writes to disk.
        """
        self.force_flush()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """
        Forces flush of any pending spans to disk.

        This method ensures that all spans that have been processed are
        written to disk. Since our implementation writes spans immediately
        in the on_end method, this is primarily a no-op that's included
        for compatibility with the SpanProcessor interface.

        Args:
            timeout_millis: The maximum time to wait for flush to complete.
                            This parameter is required by the interface but
                            not used in this implementation.

        Returns:
            True if flush succeeded, False otherwise
        """
        try:
            # Nothing to do for this implementation as spans are written immediately
            # in the on_end method, but we could add a flush call to the storage if needed
            # self._storage.flush() # Example if we had a flush method
            return True
        except Exception as e:
            self.logger.error(f"Error during force_flush: {e}")
            return False

    def get_trace(self, trace_id: str) -> List[StoredSpan]:
        """
        Retrieve all spans associated with a specific trace ID.

        Args:
            trace_id: The trace ID to retrieve (32-character hex string)

        Returns:
            List of StoredSpan objects that belong to the trace,
            ordered by start time

        Raises:
            ValueError: If trace_id is not a valid format
        """
        if not trace_id or len(trace_id) != 32:
            raise ValueError(f"Invalid trace_id: {trace_id}. Must be 32-character hex string.")

        return self._store.get_trace(trace_id)