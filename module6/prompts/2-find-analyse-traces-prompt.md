# Finad and Analyse Traces

Help me set up a file-based span processor for OpenTelemetry that I can query.

1. Create a custom SpanProcessor that:
   - Reads completed spans from a file log
   - Stores them in a queryable structure (list, database, etc.)
   - Keeps the last N spans (say 1000)

2. Add this processor to my tracer providerœ

3. Create query functions:

   get_trace(trace_id):
     - Find all spans with this trace_id
     - Return span details including attributes

   recent_failures(hours=1):
     - Find spans with status=ERROR
     - Filter by timestamp (last N hours)
     - Return span details

   filter_by_error_type(error_type):
     - Query spans where span.attributes['error.type'] == error_type

   filter_by_attribute(key, value):
     - Generic filter for any span attribute

The OpenTelemetry span object has:

- span.context.trace_id
- span.context.span_id
- span.name
- span.status
- span.attributes (dict)
- span.start_time / span.end_time

Show me how to work with these in Python

## To test the queries, we will

- Generate some test traces with different error types
- Query for a specific trace and verify you get the right spans
- Query for recent failures and verify the time filtering works
- Filter by error.type attribute and verify accuracy

## We will later check off this success criteria

[ ] We can retrieve traces by trace_id
[ ] We can filter traces by time range
[ ] We can query spans by attributes (including error.type)
[ ] Our queries return OpenTelemetry span data in a usable format
