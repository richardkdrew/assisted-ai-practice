# Data Model: Retry Logic

## Overview

This document defines the data model for the retry logic functionality. The primary entity is the `RetryDecision` which represents the result of analyzing a trace for retry determination.

## Entities

### RetryDecision

The `RetryDecision` represents the outcome of analyzing a trace to determine whether an operation should be retried. It includes the decision, reason, and related metadata.

#### Attributes

| Attribute | Type | Description | Required |
|-----------|------|-------------|----------|
| decision | String | One of: "RETRY", "ABORT", or "WAIT" | Yes |
| reason | String | Human-readable explanation of the decision | Yes |
| wait_seconds | Integer | Number of seconds to wait before retry (for RETRY/WAIT decisions) | Yes |
| trace_id | String | 32-character hex string identifying the trace | Yes |
| span_id | String | 16-character hex string identifying the span that triggered the decision | Yes |

#### Decision Types

1. **RETRY**: The operation should be retried after the specified wait period
   - Used for transient errors (ConnectionError, TimeoutError, etc.)
   - Indicates the operation may succeed if retried

2. **ABORT**: The operation should not be retried
   - Used for permanent errors (ValidationError, AuthenticationError, etc.)
   - Indicates the operation will never succeed without changes

3. **WAIT**: The operation should be retried with caution
   - Used for unknown error types
   - Indicates uncertainty about whether retry will succeed

#### Example

```json
{
  "decision": "RETRY",
  "reason": "ConnectionError detected which is a retriable error",
  "wait_seconds": 5,
  "trace_id": "abcdef1234567890abcdef1234567890",
  "span_id": "1234567890abcdef"
}
```

## Relationships

The `RetryDecision` is derived from analyzing `StoredSpan` objects from a trace. It does not have persistent relationships with other entities but is generated on-demand based on trace data.

## Validation Rules

1. `decision` must be one of: "RETRY", "ABORT", or "WAIT"
2. `wait_seconds` must be a non-negative integer
3. `trace_id` must be a valid 32-character hex string
4. `span_id` must be a valid 16-character hex string
5. `reason` must not be empty

## State Transitions

The `RetryDecision` is a stateless object that is generated on-demand. It does not undergo state transitions.

## Notes

- The `RetryDecision` is returned as a dictionary rather than a formal class to keep the implementation lightweight.
- The decision relies on error classification logic already implemented in the error tracking middleware.
- Default `wait_seconds` is 5 for transient errors as specified in the requirements.