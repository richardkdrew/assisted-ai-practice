# Trace Retry Module

A module for analyzing OpenTelemetry traces to make intelligent retry decisions based on error types.

## Overview

The `trace_retry` module provides functionality to analyze OpenTelemetry trace data to determine whether a failed operation should be retried based on the error types contained in the trace spans. It examines span attributes like `error.retriable` and `error.type` to classify errors as permanent or transient, and returns a structured decision object.

## Key Features

- Analyze OpenTelemetry traces to determine retry suitability
- Leverage existing error classification from middleware
- Handle both explicitly marked errors (via `error.retriable`) and known error types
- Provide structured decision objects with detailed reasons
- Support graceful degradation with cautious "WAIT" decisions for unknown errors

## Usage

```python
from observability.trace_retry import should_retry
import time

# After an operation fails, analyze the trace
result = should_retry(trace_id)

if result["decision"] == "RETRY":
    # Wait and retry
    time.sleep(result["wait_seconds"])
    # Retry the operation
    retry_operation()
elif result["decision"] == "ABORT":
    # Log permanent failure
    logger.error(f"Operation failed permanently: {result['reason']}")
    # Handle permanent failure (e.g., notify user)
    handle_permanent_failure()
elif result["decision"] == "WAIT":
    # Apply more cautious retry strategy for unknown errors
    time.sleep(result["wait_seconds"])
    # Maybe retry with backoff or limited attempts
    cautious_retry_operation()
```

## Integration with Retry Policies

```python
from observability.trace_retry import should_retry

def retry_with_backoff(operation, max_retries=3, initial_wait=1):
    """Retry an operation with exponential backoff."""
    attempt = 0
    last_trace_id = None

    while attempt <= max_retries:
        try:
            return operation()
        except Exception as e:
            # Get trace ID from the current span
            current_span = trace.get_current_span()
            trace_id = format(current_span.get_span_context().trace_id, "032x")
            last_trace_id = trace_id

            # Analyze trace for retry decision
            if attempt < max_retries:  # Don't check on last attempt
                result = should_retry(trace_id)

                if result["decision"] == "ABORT":
                    # Don't retry permanent errors
                    logger.error(f"Operation failed permanently: {result['reason']}")
                    raise

                # Wait based on decision and attempt number
                wait_time = result["wait_seconds"] * (2 ** attempt)
                time.sleep(wait_time)
                attempt += 1
            else:
                # Max retries exceeded
                raise

    # If we got here, max retries exceeded
    raise Exception(f"Max retries exceeded. Last trace ID: {last_trace_id}")
```

## Decision Logic

The function makes retry decisions based on the following rules:

1. If any span has `error.retriable=false` attribute, return ABORT
2. If any span has `error.retriable=true` attribute, return RETRY
3. If any span has error type in the permanent errors list, return ABORT
4. If any span has error type in the transient errors list, return RETRY
5. For unknown error types, return WAIT
6. If multiple error spans exist with different classifications, permanent errors take precedence over transient or unknown errors

### Error Classifications

#### Permanent Error Types (ABORT)

- ValidationError
- AuthenticationError
- NotFoundError
- AuthorizationError
- ValueError
- TypeError
- KeyError
- AttributeError
- RequestValidationError
- NotAuthenticatedError
- PermissionDeniedError
- ForbiddenError

#### Transient Error Types (RETRY)

- ConnectionError
- TimeoutError
- ServiceUnavailableError
- RateLimitError

## API Reference

### `should_retry(trace_id)`

Analyze a trace to determine whether the operation should be retried.

**Args**:
- `trace_id` (str): The trace ID to analyze (32-character hex string)

**Returns**:
- Dictionary with decision information:
  ```python
  {
      "decision": "RETRY"|"ABORT"|"WAIT",
      "reason": "explanation",
      "wait_seconds": 5,  # if RETRY or WAIT
      "trace_id": "...",
      "span_id": "..."
  }
  ```

**Raises**:
- `ValueError`: If trace_id is invalid or no trace found

## Testing

The module includes comprehensive tests covering all decision paths, including:

- Permanent errors resulting in ABORT decisions
- Transient errors resulting in RETRY decisions
- Unknown errors resulting in WAIT decisions
- Error prioritization with multiple error spans
- Explicit retry decisions using the `error.retriable` attribute
- Edge cases like empty traces and error handling