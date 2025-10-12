# Implementation Plan: Retry Logic

**Branch**: `003-retry-logic` | **Date**: 2025-10-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-retry-logic/spec.md`

## Summary

Implement a `should_retry(trace_id)` function that analyzes OpenTelemetry trace data to determine whether failed operations should be retried. The function will examine error spans to classify errors as permanent or transient, with a focus on leveraging the existing error.retriable attribute when available.

## Technical Context

**Language/Version**: Python 3.13.5
**Primary Dependencies**: OpenTelemetry SDK
**Storage**: File-based span storage (existing implementation)
**Testing**: pytest
**Target Platform**: Any platform running the Configuration Service
**Project Type**: Single-service backend functionality
**Performance Goals**: Function response time < 50ms for trace analysis
**Constraints**: Must use existing span store and error classification logic
**Scale/Scope**: Small, focused utility function (single file)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Feature Size**: This feature is right-sized, completable in one focused session (2-4 hours)
✅ **Clear Value**: Function provides clear value by enabling intelligent retry decisions based on error types
✅ **Testable Scope**: All requirements are testable with specific error scenarios
✅ **Implementation Time**: Can be completed within a single development session

## Project Structure

### Documentation (this feature)

```
specs/003-retry-logic/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── contracts/           # Phase 1 output (/speckit.plan command)
```

### Source Code (repository root)

```
src/
├── observability/
│   ├── trace_retry/
│   │   ├── __init__.py          # Package definition
│   │   └── retry_logic.py       # Implementation of should_retry function
│   └── trace_storage/
│       ├── file_span_processor.py # Existing span processor
│       ├── models.py             # Existing span models
│       └── span_store.py         # Existing span storage
```

**Structure Decision**: We'll create a new `trace_retry` module under the existing observability package to contain the retry logic. This maintains a clean separation of concerns while leveraging the existing observability components.

## Phase 0: Research

### Required Knowledge

1. **OpenTelemetry Trace Structure**:
   - Need to understand how to query traces using the FileBasedSpanProcessor and SpanStore
   - Need to understand StoredSpan model structure and how to extract error information

2. **Error Classification Logic**:
   - Understand the existing error.retriable attribute implementation
   - Confirm that ValidationError, AuthenticationError, NotFoundError, and AuthorizationError are permanent errors
   - Confirm that ConnectionError, TimeoutError, ServiceUnavailableError, and RateLimitError are transient errors

3. **Decision Return Format**:
   - Define the structure of the decision object with fields for decision, reason, wait_seconds, trace_id, and span_id

### Research Tasks

1. **Examine span storage interface**:
   - Investigate FileBasedSpanProcessor.get_trace() and SpanStore.get_trace() methods
   - Understand how to filter spans with status=ERROR

2. **Review error attribute structure**:
   - Identify how error.type and error.retriable attributes are stored in span attributes
   - Understand the format of these attributes and how to extract them

3. **Verify error classification**:
   - Confirm that the is_retriable_error() function categorizes errors correctly
   - Ensure that our error types match with this classification

### Output

All research findings will be documented in `research.md`, addressing the knowledge requirements and providing clear guidance for implementation.

## Phase 1: Design

### RetryDecision Data Model

The core data model will be the RetryDecision object that contains:
- decision: RETRY, ABORT, or WAIT
- reason: Explanation of the decision
- wait_seconds: Time to wait before retry (for RETRY or WAIT decisions)
- trace_id: The original trace ID
- span_id: The span ID that triggered the decision

### Function Contract

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

### Implementation Strategy

1. Query trace data using FileBasedSpanProcessor.get_trace()
2. Filter spans with status=ERROR
3. For each error span:
   a. Check if error.retriable attribute exists and use it if present
   b. Otherwise, check error.type and classify based on permanent vs transient types
4. If multiple error spans exist, prioritize the most severe error (permanent errors)
5. Return decision object with appropriate values

## Phase 2: Implementation Plan

The implementation will be a single module with the following components:

1. **RetryDecision Class**:
   - Define a dataclass or dictionary structure for the return value
   - Include all required fields (decision, reason, wait_seconds, trace_id, span_id)

2. **should_retry Function**:
   - Implement the main function following the contract
   - Include input validation, error handling, and detailed logging
   - Use existing FileBasedSpanProcessor.get_trace() to retrieve span data

3. **Helper Functions**:
   - find_error_spans: Filter spans with status=ERROR
   - get_retry_decision: Analyze an error span and determine retry decision
   - analyze_multiple_errors: Handle cases with multiple error spans

4. **Tests**:
   - test_should_retry_with_permanent_error: Verify ABORT for permanent errors
   - test_should_retry_with_transient_error: Verify RETRY for transient errors
   - test_should_retry_with_unknown_error: Verify WAIT for unknown error types
   - test_should_retry_with_retriable_attribute: Verify decisions respect error.retriable
   - test_should_retry_with_multiple_errors: Verify prioritization of permanent errors
   - test_should_retry_with_no_errors: Verify handling of traces with no errors

5. **Integration**:
   - Export the function from the observability package
   - Add appropriate documentation and examples

This implementation plan focuses on creating the exact function described in the specification without adding unnecessary complexity. It leverages existing components while maintaining a clean separation of concerns.