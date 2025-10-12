# Example prompt for retry logic implementation

Using my OpenTelemetry trace querying functions, help me implement should_retry(trace_id):

1. Query the trace to get all spans
2. Find the span(s) with status=ERROR
3. Extract the error.type attribute from the span
4. Return a decision object:
   {
     "decision": "RETRY|ABORT|WAIT",
     "reason": "explanation",
     "wait_seconds": 5,  // if RETRY
     "trace_id": "...",
     "span_id": "..."
   }

## Decision rules

- ABORT for: ValidationError, AuthenticationError, NotFoundError, AuthorizationError
- RETRY for: ConnectionError, TimeoutError, ServiceUnavailableError, RateLimitError
- WAIT for: Unknown error types

For transient errors, include a wait_seconds field (start with 5 seconds).

If I added a custom 'error.retriable' attribute to spans in Step 1, use that
to make the decision simpler.

## Testing the Logic

Create test cases:

- Test with validation error → should return ABORT
- Test with connection error → should return RETRY
- Test with unknown error → should return WAIT

## Success Criteria

[ ] Function queries OpenTelemetry traces correctly
[ ] Correctly identifies permanent vs transient errors from span attributes
[ ] Returns structured decision with reasoning
[ ] (Bonus) Implements backoff and circuit breaker logic