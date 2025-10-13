# Function Contract: should_retry

## Purpose

The `should_retry` function analyzes an OpenTelemetry trace to determine whether a failed operation should be retried based on the error types contained in the trace spans.

## Function Signature

```python
def should_retry(trace_id: str) -> Dict[str, Any]:
    """
    Analyze a trace to determine whether the operation should be retried.

    Args:
        trace_id: The trace ID to analyze (32-character hex string)

    Returns:
        Dictionary with decision information:
        {
            "decision": "RETRY"|"ABORT"|"WAIT",
            "reason": "explanation",
            "wait_seconds": 5,  # if RETRY or WAIT
            "trace_id": "...",
            "span_id": "..."
        }

    Raises:
        ValueError: If trace_id is invalid or no trace found
    """
```

## Parameters

| Parameter | Type | Description | Required | Validation |
|-----------|------|-------------|----------|------------|
| trace_id | String | 32-character hex string identifying the trace | Yes | Must be 32-character hex string |

## Return Value

A dictionary with the following structure:

| Field | Type | Description | Always Present |
|-------|------|-------------|----------------|
| decision | String | One of: "RETRY", "ABORT", or "WAIT" | Yes |
| reason | String | Human-readable explanation of the decision | Yes |
| wait_seconds | Integer | Number of seconds to wait before retry (for RETRY/WAIT decisions) | Yes |
| trace_id | String | The trace ID passed to the function | Yes |
| span_id | String | The span ID that triggered the decision | Yes |

## Exceptions

| Exception | Condition |
|-----------|-----------|
| ValueError | If trace_id is not a valid 32-character hex string |
| ValueError | If no trace with the given ID is found |

## Usage Examples

### Example 1: Permanent Error (ABORT decision)

```python
result = should_retry("abcdef1234567890abcdef1234567890")
# Result:
# {
#     "decision": "ABORT",
#     "reason": "ValidationError detected which is a permanent error",
#     "wait_seconds": 0,
#     "trace_id": "abcdef1234567890abcdef1234567890",
#     "span_id": "1234567890abcdef"
# }
```

### Example 2: Transient Error (RETRY decision)

```python
result = should_retry("abcdef1234567890abcdef1234567890")
# Result:
# {
#     "decision": "RETRY",
#     "reason": "ConnectionError detected which is a transient error",
#     "wait_seconds": 5,
#     "trace_id": "abcdef1234567890abcdef1234567890",
#     "span_id": "1234567890abcdef"
# }
```

### Example 3: Unknown Error (WAIT decision)

```python
result = should_retry("abcdef1234567890abcdef1234567890")
# Result:
# {
#     "decision": "WAIT",
#     "reason": "Unknown error type detected, using cautious retry approach",
#     "wait_seconds": 5,
#     "trace_id": "abcdef1234567890abcdef1234567890",
#     "span_id": "1234567890abcdef"
# }
```

## Decision Logic

The function makes retry decisions based on the following rules:

1. If any span has `error.retriable=false` attribute, return ABORT
2. If any span has `error.retriable=true` attribute, return RETRY
3. If any span has error type in the permanent errors list, return ABORT
4. If any span has error type in the transient errors list, return RETRY
5. For unknown error types, return WAIT
6. If multiple error spans exist with different classifications, permanent errors take precedence over transient or unknown errors

### Permanent Error Types

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

### Transient Error Types

- ConnectionError
- TimeoutError
- ServiceUnavailableError
- RateLimitError

## Implementation Notes

- The function should use the existing `get_span_store().get_trace(trace_id)` method to retrieve spans.
- The function should prioritize the `error.retriable` attribute when present in spans.
- The function should set `wait_seconds` to 5 by default for transient errors as specified in FR-008.