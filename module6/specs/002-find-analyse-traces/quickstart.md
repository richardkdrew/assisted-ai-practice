# Quickstart Guide: File-Based Trace Storage and Query

This guide provides a quick overview of how to use the File-Based Trace Storage and Query functionality in the Configuration Service.

## Setup

1. **Enable the File-Based Span Processor**

Add the file-based span processor to your OpenTelemetry configuration:

```python
from observability.trace_storage import FileBasedSpanProcessor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

# Create a tracer provider if you don't have one already
provider = TracerProvider()
trace.set_tracer_provider(provider)

# Create the file-based span processor
file_processor = FileBasedSpanProcessor(
    file_path="/path/to/traces.jsonl",
    max_spans=1000  # Optional, defaults to 1000
)

# Add it to your tracer provider
trace.get_tracer_provider().add_span_processor(file_processor)

# The processor will now receive and store all spans
```

2. **Configure the System**

The file-based span processor can be configured using environment variables:

```bash
# In your .env file or environment
TRACE_STORAGE_PATH=data/traces/trace_storage.jsonl
TRACE_MAX_SPANS=1000
TRACE_MEMORY_CHECK_INTERVAL=100
TRACE_MAX_MEMORY_MB=256
```

## Basic Usage

### Query Traces by Trace ID

```python
from observability.trace_query import get_trace

# Query by trace ID (returns all spans in the trace)
trace_spans = get_trace("0af7651916cd43dd8448eb211c80319c")

# Print trace details
print(f"Found {len(trace_spans)} spans in trace")
for span in trace_spans:
    print(f"Span: {span.name}, Status: {span.status}, Duration: {span.duration_ns}ns")
```

### Find Recent Error Traces

```python
from observability.trace_query import recent_failures

# Get error spans from the last hour
error_spans = recent_failures(hours=1)

# Or specify a different time range
error_spans = recent_failures(hours=24)  # Last 24 hours

# Process the results
for span in error_spans:
    print(f"Error in {span.name}: {span.attributes.get('error.message')}")
    print(f"Trace ID: {span.trace_id} (for further investigation)")
```

### Filter by Error Type

```python
from observability.trace_query import filter_by_error_type

# Find all spans with a specific error type
timeout_errors = filter_by_error_type("TimeoutError")

# Get error details
for span in timeout_errors:
    print(f"Timeout in {span.name} at {span.end_time}")
    print(f"Error message: {span.attributes.get('error.message')}")
```

### Filter by Any Attribute

```python
from observability.trace_query import filter_by_attribute

# Find spans with a specific attribute value
http_404_errors = filter_by_attribute("http.status_code", 404)
database_errors = filter_by_attribute("db.error", True)

# Use for any custom attribute you've added to spans
custom_spans = filter_by_attribute("business_transaction_id", "ORDER-123")
```

### Advanced Querying

```python
from observability.trace_query import query_spans
from observability.trace_query.models import SpanQuery, AttributeFilter, ComparisonOperator

# Create a complex query
query = SpanQuery(
    status="ERROR",
    start_time_min=datetime.now() - timedelta(hours=2),  # Last 2 hours
    attribute_filters=[
        AttributeFilter(key="http.method", value="POST", operator=ComparisonOperator.EQUALS),
        AttributeFilter(key="http.status_code", value=500, operator=ComparisonOperator.EQUALS),
    ],
    max_spans=100,
    order_by="start_time",
    order_direction="DESC"  # Most recent first
)

# Execute the query
results = query_spans(query)

# Process results
print(f"Found {len(results)} matching spans")
for span in results:
    print(f"Span: {span.name}, Time: {span.start_time}")
```

## Command Line Interface

For quick checks, you can use the included CLI:

```bash
# Find a trace by ID
bin/trace-query trace 01234567890123456789012345678901

# Show recent failures
bin/trace-query failures --hours 1 --limit 10

# Filter by status (OK or ERROR) with time window
bin/trace-query status ERROR --duration 30m

# Filter by time range
bin/trace-query time --start "2023-06-01T12:00:00" --end "2023-06-01T13:00:00"
bin/trace-query time --duration 15m --status ERROR

# Filter by error type
bin/trace-query error-type ConnectionError

# Filter by attribute
bin/trace-query attribute http.status_code 500
bin/trace-query attribute http.method GET --limit 10

# Advanced query with multiple filters
bin/trace-query query --status ERROR --service auth-service --attr error.type ConnectionError

# Output in JSON format
bin/trace-query failures --json
```

## Example Code

The repository includes a complete example in `svc/examples/trace_query_examples.py` that demonstrates:

1. Setting up a tracer with the FileBasedSpanProcessor
2. Creating traces with different span patterns
3. Simulating various error scenarios
4. Querying traces with different criteria

Run the example with:

```bash
# Create and query example traces
python svc/examples/trace_query_examples.py

# Just create new traces
python svc/examples/trace_query_examples.py --create-traces

# Just query existing traces
python svc/examples/trace_query_examples.py --query-traces
```

## Example Workflow: Debugging an Issue

1. User reports an error with ID 12345
2. Query for related traces:
   ```python
   # Search by order ID in span attributes
   related_traces = filter_by_attribute("order_id", "12345")
   ```
3. If found, examine the trace:
   ```python
   for span in get_trace(related_traces[0].trace_id):
      print(f"{span.name}: {span.status}")
      if span.status == "ERROR":
         print(f"Error details: {span.attributes.get('error.message')}")
   ```
4. Look for patterns in similar errors:
   ```python
   similar_errors = filter_by_error_type(related_traces[0].attributes.get("error.type"))
   ```

## Features and Limitations

### Features

- **Hybrid Storage**: File-based persistence with in-memory indexing
- **Thread Safety**: Concurrent read/write operations with read-write lock pattern
- **Memory Management**: Adaptive max spans based on memory usage
- **Efficient Querying**: Indexed access for trace ID, status, time, and attributes
- **Flexible Time Formats**: Support for absolute and relative time specifications
- **CLI Interface**: Command-line tools for quick debugging and analysis

### Limitations

- Memory usage limited to 256MB by default (configurable)
- Default maximum of 1000 spans in memory (configurable)
- Spans are stored in FIFO order (oldest removed first when limit is reached)
- Queries on non-indexed fields require full scan of spans
- The file is append-only (manual cleanup required for long-term storage)
- Complex attribute filters may impact query performance

## Next Steps

- Explore the [Data Model](./data-model.md) for details on the span format
- Check the [API Contract](./contracts/query_api.md) for function specifications
- View the [Research](./research.md) for implementation decisions
- Run the example code to see the system in action