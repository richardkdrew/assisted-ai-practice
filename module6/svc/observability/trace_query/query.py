"""
Query functions for retrieving and filtering stored spans.

This module provides functions to query spans stored by the FileBasedSpanProcessor,
including filtering by trace ID, time range, status, and attributes.

Key Features:
- Retrieve complete traces by trace ID
- Filter traces by time range with flexible time formats
- Find recent failures within a specified window
- Filter by error type or specific attributes
- Support for advanced queries with multiple criteria
- Flexible time specification (ISO format, relative time, etc.)

Usage Examples:
    ```python
    from observability.trace_query import get_trace, recent_failures, filter_by_time

    # Get all spans for a specific trace
    spans = get_trace("01234567890123456789012345678901")

    # Find recent error spans
    failures = recent_failures(hours=1)

    # Filter by time range and status
    spans = filter_by_time(
        start_time="2023-06-01T12:00:00",
        end_time="2023-06-01T13:00:00",
        status="ERROR"
    )

    # Use relative time formats
    spans = filter_by_time(duration="30m")  # Last 30 minutes

    # Filter by specific attributes
    spans = filter_by_attribute("http.status_code", 500)
    ```

CLI Access:
    This functionality can also be accessed via the command-line using the
    trace-query script in the bin directory:

    ```bash
    # Get a trace by ID
    bin/trace-query trace 01234567890123456789012345678901

    # Show recent failures
    bin/trace-query failures --hours 2

    # Filter by status
    bin/trace-query status ERROR --duration 1h
    ```
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from observability.trace_storage.models import AttributeFilter, SpanQuery, StoredSpan
from observability.trace_storage.file_span_processor import get_span_store

# Constants for time conversion
NANOSECONDS_PER_SECOND = 1_000_000_000
NANOSECONDS_PER_MINUTE = 60 * NANOSECONDS_PER_SECOND
NANOSECONDS_PER_HOUR = 60 * NANOSECONDS_PER_MINUTE
NANOSECONDS_PER_DAY = 24 * NANOSECONDS_PER_HOUR


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
    if not trace_id or len(trace_id) != 32:
        raise ValueError(f"Invalid trace_id: {trace_id}. Must be 32-character hex string.")

    store = get_span_store()
    if store is None:
        return []

    return store.get_trace(trace_id)


def time_to_nanoseconds(time_value: Union[int, float, datetime, str]) -> int:
    """
    Convert various time formats to nanoseconds since epoch.

    Args:
        time_value: Time in one of several formats:
            - int/float: Assumed to be seconds since epoch
            - datetime: Python datetime object
            - str: ISO format datetime string or relative time (e.g., "1h", "30m", "2d")

    Returns:
        Time in nanoseconds since epoch

    Raises:
        ValueError: If time_value is in an invalid format
    """
    if isinstance(time_value, (int, float)):
        # Assume seconds if value is small (< year 2100 in seconds)
        if time_value < 4102444800:  # 2100-01-01 in seconds
            return int(time_value * NANOSECONDS_PER_SECOND)
        # Assume milliseconds if value looks like milliseconds
        elif time_value < 4102444800000:  # 2100-01-01 in milliseconds
            return int(time_value * NANOSECONDS_PER_SECOND / 1000)
        # Assume microseconds if value looks like microseconds
        elif time_value < 4102444800000000:  # 2100-01-01 in microseconds
            return int(time_value * NANOSECONDS_PER_SECOND / 1000000)
        # Otherwise assume nanoseconds
        else:
            return int(time_value)

    elif isinstance(time_value, datetime):
        return int(time_value.timestamp() * NANOSECONDS_PER_SECOND)

    elif isinstance(time_value, str):
        # Try parsing as ISO format
        try:
            dt = datetime.fromisoformat(time_value)
            return int(dt.timestamp() * NANOSECONDS_PER_SECOND)
        except ValueError:
            # Check for relative time format
            if time_value.endswith("s"):
                try:
                    seconds = float(time_value[:-1])
                    return int(seconds * NANOSECONDS_PER_SECOND)
                except ValueError:
                    pass
            elif time_value.endswith("m"):
                try:
                    minutes = float(time_value[:-1])
                    return int(minutes * NANOSECONDS_PER_MINUTE)
                except ValueError:
                    pass
            elif time_value.endswith("h"):
                try:
                    hours = float(time_value[:-1])
                    return int(hours * NANOSECONDS_PER_HOUR)
                except ValueError:
                    pass
            elif time_value.endswith("d"):
                try:
                    days = float(time_value[:-1])
                    return int(days * NANOSECONDS_PER_DAY)
                except ValueError:
                    pass

            raise ValueError(f"Invalid time format: {time_value}")
    else:
        raise ValueError(f"Unsupported time type: {type(time_value)}")

def get_time_range(time_spec: Union[str, float, int, datetime] = None,
                   duration: Union[str, float, int] = None) -> Tuple[int, int]:
    """
    Calculate a time range based on a reference time and duration.

    Args:
        time_spec: Reference time (default: now). Can be:
            - None: Current time
            - "now": Current time
            - datetime: Specific time
            - int/float: Seconds since epoch
            - str: ISO format time or relative time (e.g., "1h ago")
        duration: Duration of the time range. Can be:
            - int/float: Hours (for backward compatibility)
            - str: Relative time (e.g., "1h", "30m", "2d")

    Returns:
        Tuple of (start_time_ns, end_time_ns)

    Raises:
        ValueError: If time_spec or duration is invalid
    """
    # Get current time in nanoseconds
    current_time_ns = int(time.time() * NANOSECONDS_PER_SECOND)

    # Parse reference time
    end_time_ns = current_time_ns
    if time_spec is not None:
        if time_spec == "now":
            end_time_ns = current_time_ns
        elif isinstance(time_spec, str) and time_spec.endswith("ago"):
            # Handle relative time in the past
            rel_time = time_spec.rstrip(" ago")
            offset_ns = time_to_nanoseconds(rel_time)
            end_time_ns = current_time_ns - offset_ns
        else:
            # Handle absolute time
            end_time_ns = time_to_nanoseconds(time_spec)

    # Parse duration
    if duration is None:
        # Default to 1 hour for backward compatibility
        start_time_ns = end_time_ns - NANOSECONDS_PER_HOUR
    elif isinstance(duration, (int, float)):
        # For backward compatibility, treat as hours
        start_time_ns = end_time_ns - int(duration * NANOSECONDS_PER_HOUR)
    elif isinstance(duration, str):
        duration_ns = time_to_nanoseconds(duration)
        start_time_ns = end_time_ns - duration_ns
    else:
        raise ValueError(f"Invalid duration format: {duration}")

    return (start_time_ns, end_time_ns)

def filter_by_time(
    start_time: Union[int, float, datetime, str] = None,
    end_time: Union[int, float, datetime, str] = None,
    duration: Union[str, float, int] = None,
    status: str = None,
    max_results: int = 100,
    order_by: str = "end_time",
    order_direction: str = "DESC"
) -> List[StoredSpan]:
    """
    Filter spans by time range.

    Args:
        start_time: Start time (inclusive)
        end_time: End time (inclusive)
        duration: Alternative to explicit start/end times:
            - If end_time is specified: Duration before end_time
            - If end_time is not specified: Duration before now
        status: Optional status filter ("OK" or "ERROR")
        max_results: Maximum number of results to return
        order_by: Field to sort by (start_time, end_time, duration_ns)
        order_direction: Sort direction (ASC or DESC)

    Returns:
        List of StoredSpan objects within the time range

    Raises:
        ValueError: If time parameters are invalid
    """
    # Get the span store
    store = get_span_store()
    if store is None:
        return []

    # Calculate the time range
    start_time_ns = None
    end_time_ns = None

    if start_time is not None:
        start_time_ns = time_to_nanoseconds(start_time)

    if end_time is not None:
        end_time_ns = time_to_nanoseconds(end_time)

        # If duration is specified and start_time is not, calculate start_time from end_time and duration
        if start_time_ns is None and duration is not None:
            if isinstance(duration, (int, float)):
                # For backward compatibility, treat as hours
                start_time_ns = end_time_ns - int(duration * NANOSECONDS_PER_HOUR)
            elif isinstance(duration, str):
                duration_ns = time_to_nanoseconds(duration)
                start_time_ns = end_time_ns - duration_ns
    else:
        # If neither start_time nor end_time is specified, use current time as end_time
        if start_time_ns is None:
            start_time_ns, end_time_ns = get_time_range(duration=duration)
        else:
            end_time_ns = int(time.time() * NANOSECONDS_PER_SECOND)

    # Create query
    query = SpanQuery(
        start_time_min=start_time_ns,
        start_time_max=end_time_ns,
        status=status,
        max_spans=max_results,
        order_by=order_by,
        order_direction=order_direction,
    )

    return store.get_spans(query)

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
    if hours <= 0:
        raise ValueError(f"Invalid hours: {hours}. Must be positive.")

    # Use the filter_by_time function with ERROR status
    return filter_by_time(
        duration=f"{hours}h",
        status="ERROR",
        max_results=max_results,
        order_by="end_time",
        order_direction="DESC",
    )


def filter_by_status(
    status: str,
    time_range: Union[str, Tuple[Union[int, float, datetime, str], Union[int, float, datetime, str]]] = None,
    max_results: int = 100
) -> List[StoredSpan]:
    """
    Find spans with a specific status.

    Args:
        status: The status to filter by ("OK" or "ERROR")
        time_range: Optional time range to filter within. Can be:
            - None: All time
            - str: Relative time (e.g., "1h") - from now to that duration in the past
            - Tuple: (start_time, end_time) in any format supported by time_to_nanoseconds
        max_results: Maximum number of results to return

    Returns:
        List of StoredSpan objects with the specified status,
        ordered by end time (most recent first)

    Raises:
        ValueError: If status is not "OK" or "ERROR"
    """
    if status not in ["OK", "ERROR"]:
        raise ValueError(f"Invalid status: {status}. Must be 'OK' or 'ERROR'.")

    # Calculate time range if provided
    start_time_ns = None
    end_time_ns = None

    if time_range is not None:
        if isinstance(time_range, str):
            # Relative time from now
            start_time_ns, end_time_ns = get_time_range(duration=time_range)
        elif isinstance(time_range, tuple) and len(time_range) == 2:
            # Explicit start and end times
            start_time, end_time = time_range
            start_time_ns = time_to_nanoseconds(start_time)
            end_time_ns = time_to_nanoseconds(end_time)
        else:
            raise ValueError(f"Invalid time_range: {time_range}")

    # Create query
    query = SpanQuery(
        status=status,
        start_time_min=start_time_ns,
        start_time_max=end_time_ns,
        max_spans=max_results,
        order_by="end_time",
        order_direction="DESC",
    )

    store = get_span_store()
    if store is None:
        return []

    return store.get_spans(query)

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
    if not error_type:
        raise ValueError("error_type cannot be empty")

    # Create a query with an attribute filter for error.type
    query = SpanQuery(
        status="ERROR",
        attribute_filters=[
            AttributeFilter(key="error.type", value=error_type)
        ],
        max_spans=max_results,
        order_by="end_time",
        order_direction="DESC",
    )

    store = get_span_store()
    if store is None:
        return []

    return store.get_spans(query)


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
    if not key:
        raise ValueError("key cannot be empty")

    # Create a query with an attribute filter
    query = SpanQuery(
        attribute_filters=[
            AttributeFilter(key=key, value=value)
        ],
        max_spans=max_results,
        order_by="end_time",
        order_direction="DESC",
    )

    store = get_span_store()
    if store is None:
        return []

    return store.get_spans(query)


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
    store = get_span_store()
    if store is None:
        return []

    return store.get_spans(query)