# Research: Retry Logic

## Objective

Investigate the technical requirements and components needed to implement a `should_retry(trace_id)` function that analyzes OpenTelemetry trace data to make intelligent retry decisions.

## Findings

### 1. OpenTelemetry Trace Structure

#### How to Query Traces

The existing codebase already has a robust implementation for storing and querying traces:

```python
# From file_span_processor.py
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
```

To get a trace, we can use:

```python
from observability.trace_storage.file_span_processor import get_span_store

# Get the global span store instance
span_store = get_span_store()
if span_store is not None:
    # Get the trace
    spans = span_store.get_trace(trace_id)
```

#### StoredSpan Model Structure

The `StoredSpan` model from `models.py` contains all the information we need:

```python
@dataclass
class StoredSpan:
    trace_id: str  # Trace identifier (32-character hex string)
    span_id: str  # Span identifier (16-character hex string)
    parent_span_id: Optional[str] = None  # Parent span ID (or None for root spans)
    name: str = ""  # Operation name
    status: str = "OK"  # "OK" or "ERROR"
    status_description: Optional[str] = None  # Status description (for errors)
    start_time: int = 0  # Start time (nanoseconds since epoch)
    end_time: int = 0  # End time (nanoseconds since epoch)
    duration_ns: int = 0  # Duration in nanoseconds
    attributes: Dict[str, Any] = field(default_factory=dict)  # Span attributes
    events: List[Dict[str, Any]] = field(default_factory=list)  # Time-stamped events
    links: List[Dict[str, Any]] = field(default_factory=list)  # Links to other spans
    service_name: str = ""  # Service that created the span
    resource_attributes: Dict[str, Any] = field(default_factory=dict)  # Resource attributes
```

Key fields for our function:
- `status`: We need to filter spans with `status="ERROR"`
- `attributes`: Contains `error.type` and `error.retriable` attributes
- `span_id`: Needed for the return value

### 2. Error Classification Logic

The error tracking middleware already implements a comprehensive `is_retriable_error()` function:

```python
def is_retriable_error(exception: Exception) -> bool:
    """Determine if an error is retriable (transient) or permanent."""
    # Common retriable error types (connection, timeout, and similar transient errors)
    retriable_error_types = (
        ConnectionError,
        TimeoutError,
        # Request-related errors
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.RetryError,
        # Database connection issues
        psycopg2.OperationalError,
        # Include any custom service unavailable errors
        # ServiceUnavailableError,
    )

    # Explicitly define permanent (non-retriable) error types for clarity
    permanent_error_types = (
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        # Validation errors
        "ValidationError",  # Check by name since imports might vary
        "RequestValidationError",
        # Authentication errors
        "AuthenticationError",
        "NotAuthenticatedError",
        # Permission errors
        "PermissionDeniedError",
        "ForbiddenError",
    )

    # Check if error type is explicitly listed as permanent
    if exception.__class__.__name__ in permanent_error_types:
        return False

    # For HTTP errors, some status codes indicate retriable errors
    if hasattr(exception, "status_code"):
        retriable_status_codes = {408, 425, 429, 500, 502, 503, 504}
        if exception.status_code in retriable_status_codes:
            return True

        # Non-retriable HTTP status codes
        permanent_status_codes = {400, 401, 403, 404, 405, 422}
        if exception.status_code in permanent_status_codes:
            return False

    # Check if the exception is an instance of any retriable error types
    if isinstance(exception, retriable_error_types):
        return True

    # By default, errors are not retriable
    return False
```

The middleware sets the `error.retriable` attribute in the `record_exception_to_span` function:

```python
def record_exception_to_span(span, exception: Exception, http_context: Optional[Dict[str, Any]] = None) -> None:
    """Record exception details to the current span."""
    # Set span status to ERROR
    span.set_status(Status(StatusCode.ERROR))

    # Basic error attributes
    span.set_attribute("error", True)
    span.set_attribute("error.type", exception.__class__.__name__)
    span.set_attribute("error.message", str(exception))

    # Determine if error is retriable
    is_retriable = is_retriable_error(exception)
    span.set_attribute("error.retriable", is_retriable)

    # Additional error information...
```

This means in the span's attributes we can expect:
- `error.type`: The exception class name
- `error.retriable`: Boolean indicating if the error is retriable

### 3. Decision Return Format

Based on the specification, the return format should be:

```python
{
    "decision": "RETRY"|"ABORT"|"WAIT",
    "reason": "explanation string",
    "wait_seconds": 5,  # for RETRY/WAIT decisions
    "trace_id": "32-character hex string",
    "span_id": "16-character hex string"
}
```

Decision types:
- `RETRY`: For transient errors that should be retried after waiting
- `ABORT`: For permanent errors that will never succeed
- `WAIT`: For unknown error types, use cautious approach

### 4. Handling Multiple Error Spans

When a trace contains multiple error spans, the specification requires that we:
1. Analyze all error spans
2. Prioritize the most severe errors (permanent errors take precedence)

This means if any span has a permanent error, we should return ABORT, even if other spans have transient errors.

## Conclusion

Based on the research, the implementation strategy will be:

1. Use `get_span_store().get_trace(trace_id)` to retrieve all spans for a trace
2. Filter spans with `status="ERROR"`
3. For each error span:
   - Check if `error.retriable` attribute exists and use it if present
   - Otherwise, check `error.type` and match against known error classifications
4. Determine final decision based on error types found:
   - If any permanent errors found, return ABORT
   - If only transient errors found, return RETRY
   - If only unknown errors found, return WAIT
5. Return a properly structured decision object

All necessary components are already available in the codebase; we simply need to integrate them into the new function.