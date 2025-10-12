# Trace Query API Contract

This document defines the interfaces for querying traces stored by the File-Based Span Processor.

## Core Query Functions

### Get Trace By ID

```python
def get_trace(trace_id: str) -> List[StoredSpan]:
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
```

### Recent Failures

```python
def recent_failures(
    hours: float = 1,
    max_results: int = 100
) -> List[StoredSpan]:
    """
    Retrieve recent spans with ERROR status within a time window.

    Args:
        hours: Number of hours to look back from now
        max_results: Maximum number of results to return

    Returns:
        List of StoredSpan objects with ERROR status within the time window,
        ordered by end time (most recent first)

    Raises:
        ValueError: If hours is not positive
    """
```

### Filter By Error Type

```python
def filter_by_error_type(
    error_type: str,
    max_results: int = 100
) -> List[StoredSpan]:
    """
    Find spans with a specific error.type attribute value.

    Args:
        error_type: The error type to search for
        max_results: Maximum number of results to return

    Returns:
        List of StoredSpan objects with matching error.type attribute,
        ordered by end time (most recent first)

    Raises:
        ValueError: If error_type is empty
    """
```

### Filter By Attribute

```python
def filter_by_attribute(
    key: str,
    value: Any,
    max_results: int = 100
) -> List[StoredSpan]:
    """
    Find spans with a specific attribute key-value pair.

    Args:
        key: The attribute key to filter on
        value: The attribute value to match
        max_results: Maximum number of results to return

    Returns:
        List of StoredSpan objects with matching attribute,
        ordered by end time (most recent first)

    Raises:
        ValueError: If key is empty
    """
```

## Advanced Query API

### General Query Function

```python
def query_spans(query: SpanQuery) -> List[StoredSpan]:
    """
    Query spans using multiple filters and criteria.

    Args:
        query: SpanQuery object with filter criteria

    Returns:
        List of StoredSpan objects matching all criteria

    Raises:
        ValueError: If query contains invalid parameters
    """
```

## Data Models

### StoredSpan

```python
@dataclass
class StoredSpan:
    """Represents a stored OpenTelemetry span."""

    trace_id: str                  # Trace identifier (32-character hex string)
    span_id: str                   # Span identifier (16-character hex string)
    parent_span_id: Optional[str]  # Parent span ID (or None for root spans)
    name: str                      # Operation name
    status: str                    # "OK" or "ERROR"
    status_description: Optional[str]  # Status description (for errors)
    start_time: int                # Start time (nanoseconds since epoch)
    end_time: int                  # End time (nanoseconds since epoch)
    duration_ns: int               # Duration in nanoseconds
    attributes: Dict[str, Any]     # Span attributes
    events: List[Dict]             # Time-stamped events
    links: List[Dict]              # Links to other spans
    service_name: str              # Service that created the span
    resource_attributes: Dict[str, Any]  # Resource attributes
```

### SpanQuery

```python
@dataclass
class SpanQuery:
    """Query parameters for span filtering."""

    trace_id: Optional[str] = None             # Filter by trace ID
    span_ids: Optional[List[str]] = None       # Filter by span IDs
    status: Optional[str] = None               # Filter by status ("OK" or "ERROR")
    service_name: Optional[str] = None         # Filter by service name
    operation_name: Optional[str] = None       # Filter by operation name
    start_time_min: Optional[int] = None       # Min start time (nanoseconds)
    start_time_max: Optional[int] = None       # Max start time (nanoseconds)
    attribute_filters: Optional[List[AttributeFilter]] = None  # Attribute filters
    max_spans: int = 100                       # Max results to return
    order_by: str = "start_time"               # Field to sort by
    order_direction: str = "DESC"              # Sort direction
```

### AttributeFilter

```python
@dataclass
class AttributeFilter:
    """Filter for span attributes."""

    key: str                       # Attribute key
    value: Any                     # Value to match
    operator: str = "EQUALS"       # Comparison operator
```

## Span Processor API

### FileBasedSpanProcessor

```python
class FileBasedSpanProcessor(SpanProcessor):
    """
    OpenTelemetry SpanProcessor that stores spans to a file and provides querying.

    Args:
        file_path: Path to the trace storage file
        max_spans: Maximum number of spans to retain (default: 1000)

    Raises:
        ValueError: If max_spans <= 0
        IOError: If file cannot be accessed
    """

    def __init__(self, file_path: str, max_spans: int = 1000):
        pass

    def on_start(self, span: Span, parent_context: Optional[SpanContext] = None) -> None:
        """Called when a span starts (no-op for this processor)."""
        pass

    def on_end(self, span: ReadableSpan) -> None:
        """
        Called when a span ends.

        Processes the completed span:
        1. Converts it to StoredSpan format
        2. Writes it to the trace file
        3. Adds it to the in-memory indices
        4. Evicts oldest spans if max_spans is reached
        """
        pass

    def shutdown(self) -> None:
        """
        Shuts down the processor.

        Flushes any pending writes to disk and closes the file.
        """
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """
        Forces flush of any pending spans to disk.

        Args:
            timeout_millis: The maximum time to wait for flush to complete

        Returns:
            True if flush succeeded, False otherwise
        """
        pass
```