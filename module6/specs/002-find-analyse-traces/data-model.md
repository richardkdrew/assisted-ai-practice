# Data Model: File-Based Trace Storage and Query

This document outlines the data model for the File-Based Trace Storage and Query feature, including the key entities, their relationships, and data structures used throughout the system.

## Core Entities

### StoredSpan

The primary entity representing a stored OpenTelemetry span with all necessary information for querying and analysis.

**Fields:**
- `trace_id`: String - The trace identifier (hexadecimal string)
- `span_id`: String - The span identifier (hexadecimal string)
- `parent_span_id`: String - The parent span identifier (or None for root spans)
- `name`: String - The operation name
- `status`: Enum - The span status (OK, ERROR)
- `status_description`: String - Optional description for the status
- `start_time`: DateTime - When the span started (nanosecond precision)
- `end_time`: DateTime - When the span ended (nanosecond precision)
- `duration_ns`: Integer - Duration in nanoseconds
- `attributes`: Dict - Key-value pairs of span attributes
- `events`: List - Time-stamped events that occurred during the span
- `links`: List - Links to other spans (rarely used)
- `service_name`: String - Name of the service that generated the span
- `resource_attributes`: Dict - Resource attributes associated with the span

**Validation Rules:**
- `trace_id` must be a valid 32-character hexadecimal string
- `span_id` must be a valid 16-character hexadecimal string
- `parent_span_id` must be a valid 16-character hexadecimal string or None
- `start_time` must be before `end_time`
- `duration_ns` must be >= 0

### SpanQuery

Entity representing a query for spans with various filter criteria.

**Fields:**
- `trace_id`: String - Filter by trace ID (exact match)
- `span_ids`: List[String] - Filter by span IDs (multiple allowed)
- `status`: Enum - Filter by status (OK, ERROR, or ALL)
- `service_name`: String - Filter by service name
- `operation_name`: String - Filter by operation name
- `start_time_min`: DateTime - Filter spans that started after this time
- `start_time_max`: DateTime - Filter spans that started before this time
- `attribute_filters`: List[AttributeFilter] - Filters for span attributes
- `max_spans`: Integer - Maximum number of spans to return
- `order_by`: String - Field to sort results by
- `order_direction`: String - Sort direction (ASC or DESC)

**Validation Rules:**
- `trace_id` if provided, must be a valid 32-character hexadecimal string
- `span_ids` if provided, must contain valid 16-character hexadecimal strings
- `max_spans` must be > 0
- `start_time_min` must be before `start_time_max` if both provided

### AttributeFilter

Entity representing a filter on a specific span attribute.

**Fields:**
- `key`: String - The attribute key to filter on
- `value`: Any - The value to match
- `operator`: Enum - The comparison operator (EQUALS, CONTAINS, STARTS_WITH, etc.)

**Validation Rules:**
- `key` cannot be empty
- `operator` must be a valid comparison operator

### TraceFile

Entity representing the on-disk storage format for spans.

**Fields:**
- `file_path`: String - Path to the trace storage file
- `max_spans`: Integer - Maximum number of spans to retain
- `format_version`: String - Version of the file format
- `metadata`: Dict - Additional metadata about the trace file

**Validation Rules:**
- `file_path` must be a valid path
- `max_spans` must be > 0

## Relationships

### StoredSpan Relationships

- **Parent-Child**: A span can have one parent span and multiple child spans
  - `parent_span_id` references another span's `span_id`
  - Child spans are identified by querying for spans with `parent_span_id` equal to a specific `span_id`

- **Trace Membership**: Multiple spans belong to a single trace
  - All spans with the same `trace_id` form a complete trace
  - Represents the full request flow through the system

### SpanStore to StoredSpan

- **One-to-Many**: The SpanStore contains multiple StoredSpan objects
  - SpanStore indexes StoredSpan objects by trace_id, status, and other criteria for efficient querying
  - SpanStore is responsible for enforcing the maximum span count

## State Transitions

### Span Lifecycle

1. **Created**: When an OpenTelemetry span is created
2. **In-Progress**: While the span is active with operations being tracked
3. **Ended**: When the span is ended (with end time set)
4. **Processed**: When our SpanProcessor receives the ended span
5. **Stored**: When the span is written to the trace file and indexed in memory
6. **Evicted**: When the span is removed due to exceeding max_spans limit (FIFO policy)

## File Format

The trace file uses a JSON Lines format (one JSON object per line) for efficient appending and partial reading. Each line contains a serialized StoredSpan object with the following structure:

```json
{
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "span_id": "b7ad6b7169203331",
  "parent_span_id": "8448eb211c80319c",
  "name": "GET /api/users",
  "status": "ERROR",
  "status_description": "User not found",
  "start_time": 1601234567000000000,
  "end_time": 1601234567100000000,
  "duration_ns": 100000000,
  "attributes": {
    "http.method": "GET",
    "http.url": "/api/users/123",
    "http.status_code": 404,
    "error.type": "NotFoundError",
    "error.message": "User with ID 123 not found",
    "error.stack": "...",
    "error.retriable": false
  },
  "events": [
    {
      "name": "db.query",
      "timestamp": 1601234567050000000,
      "attributes": {
        "db.statement": "SELECT * FROM users WHERE id = ?",
        "db.params": "123"
      }
    }
  ],
  "service_name": "user-service",
  "resource_attributes": {
    "service.version": "1.0.0",
    "host.name": "web-1"
  }
}
```

## In-Memory Indices

The SpanStore maintains the following in-memory indices for efficient querying:

1. **Trace Index**: Map of trace_id to list of spans within that trace
   ```
   {
     "0af7651916cd43dd8448eb211c80319c": [span1, span2, span3],
     "1bf8762027de54ee9559fc322d91420d": [span4, span5]
   }
   ```

2. **Status Index**: Map of status to list of spans
   ```
   {
     "OK": [span1, span3, span5],
     "ERROR": [span2, span4]
   }
   ```

3. **Time Index**: List of spans sorted by start_time for range queries

4. **Attribute Index**: Map of common attribute keys to maps of values to spans
   ```
   {
     "error.type": {
       "NotFoundError": [span2],
       "TimeoutError": [span4]
     }
   }
   ```

These indices are updated atomically when spans are added or evicted to maintain consistency.