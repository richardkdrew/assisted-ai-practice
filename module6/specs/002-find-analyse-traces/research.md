# Research: File-Based Trace Storage and Query

## 1. OpenTelemetry SpanProcessor Implementation

### Decision: Custom SpanProcessor with Hybrid Storage Model

We will implement a custom `FileBasedSpanProcessor` class that extends OpenTelemetry's `SpanProcessor` interface. This processor will:
1. Store span data in JSON format in a file (for persistence)
2. Maintain an in-memory index for efficient querying
3. Implement thread-safe operations for concurrent processing and querying

### Rationale:
- OpenTelemetry's modular design specifically allows for custom span processors
- JSON format provides human-readable storage that can be inspected directly if needed
- Dual storage approach (file + in-memory) balances persistence with query performance
- Existing code already uses OpenTelemetry, making integration seamless

### Alternatives Considered:
1. **Database Storage (SQLite/PostgreSQL)**:
   - Pro: Better query capabilities
   - Con: Additional dependency and complexity
   - Rejected due to unnecessary complexity and overhead for the scale required

2. **Memory-Only Storage**:
   - Pro: Fastest performance
   - Con: No persistence across restarts
   - Rejected due to lack of persistence for historical analysis

3. **Existing Exporters**:
   - Pro: Reuse of existing code
   - Con: No query capabilities within the application
   - Rejected as they don't provide the query functionality we need

## 2. Storage Format and Indexing

### Decision: Append-Only File with In-Memory Index

We will implement:
1. An append-only JSON file (one span per line for easy parsing)
2. An in-memory index using Python dictionaries and lists:
   - Primary index by trace_id (dict)
   - Secondary indices for status (error vs success) and timestamp
   - Attribute lookup index for common attributes like error.type

### Rationale:
- Append-only writes are thread-safe and efficient
- JSON-per-line format makes partial reads possible without parsing the entire file
- In-memory indices provide fast lookups for the query patterns specified
- This approach stays within memory constraints while providing query performance

### Alternatives Considered:
1. **Single JSON Document**:
   - Pro: Simpler file format
   - Con: Entire file needs to be parsed/written
   - Rejected due to performance issues with large trace volumes

2. **Binary Format**:
   - Pro: More compact storage
   - Con: Not human-readable
   - Rejected as human-readability is important for debugging

3. **External Search Engine**:
   - Pro: Better search capabilities
   - Con: Significant additional complexity
   - Rejected as overkill for the scale required

## 3. Query Interface Design

### Decision: Function-Based Query API with Filter Objects

We will implement:
1. A `Query` class to define filter parameters (trace_id, time range, attributes)
2. Core query functions following the prompt:
   - `get_trace(trace_id)`
   - `recent_failures(hours=1)`
   - `filter_by_error_type(error_type)`
   - `filter_by_attribute(key, value)`
3. A generic `query_spans(filters)` method for combined filters

### Rationale:
- Direct mapping to the requirements in the prompt
- Simple function-based API is easy to use
- Filter objects allow for future extensibility
- Consistent return format makes results predictable

### Alternatives Considered:
1. **SQL-like Query Language**:
   - Pro: More expressive queries
   - Con: More complex to implement and use
   - Rejected as too complex for current needs

2. **ORM-style API**:
   - Pro: More familiar to developers used to ORMs
   - Con: Requires more boilerplate
   - Rejected as unnecessarily complex

## 4. Span Data Serialization

### Decision: Custom Serialization with Span-Specific Logic

We will implement:
1. Custom serialization for OpenTelemetry Span objects to capture all needed information
2. Store a simplified representation with all essential fields:
   - trace_id, span_id, parent_span_id, name, status
   - start_time, end_time, duration
   - attributes (dict)
   - events
3. Deserialize back into a span-like object with all query-relevant fields

### Rationale:
- OpenTelemetry Span objects aren't directly serializable
- Custom approach ensures we capture exactly what we need
- Maintaining span relationships allows for reconstructing trace hierarchy

### Alternatives Considered:
1. **Store Raw OpenTelemetry Protocol**:
   - Pro: Official format
   - Con: More complex, harder to query directly
   - Rejected due to complexity and query performance concerns

2. **Store Only Minimal Fields**:
   - Pro: More space-efficient
   - Con: Loses valuable debugging context
   - Rejected as the value is in having complete span information

## 5. Performance and Constraints Management

### Decision: Configurable Limits with FIFO Eviction

We will implement:
1. Configurable maximum span count (default: 1000)
2. FIFO (First-In-First-Out) eviction policy when limit is reached
3. Periodic file pruning to match in-memory state
4. Memory usage monitoring to stay under 256MB limit

### Rationale:
- FIFO policy keeps the most recent spans which are typically most valuable for debugging
- Configurable limits allow adjustment based on available resources
- Regular pruning maintains alignment between file and memory
- Memory monitoring prevents resource exhaustion

### Alternatives Considered:
1. **LRU (Least Recently Used) Eviction**:
   - Pro: Keeps frequently accessed spans
   - Con: More complex to implement
   - Rejected as recent spans are more valuable than frequently accessed ones for debugging

2. **Time-Based Expiration**:
   - Pro: More intuitive time window
   - Con: Could lead to unpredictable storage usage
   - Rejected in favor of the simpler count-based approach

## 6. Thread Safety Implementation

### Decision: Lock-Based Concurrency with Read-Write Separation

We will implement:
1. Python's `threading.RLock` for write operations
2. Reader-writer pattern for query operations
3. Copy-on-read for query results to prevent mutation during iteration

### Rationale:
- RLock allows reentrant locking for write operations
- Reader-writer pattern optimizes for the common case of many reads and few writes
- Copy-on-read prevents mutation of returned data

### Alternatives Considered:
1. **Global Lock**:
   - Pro: Simpler implementation
   - Con: Reduced concurrency
   - Rejected due to performance concerns

2. **Lock-Free Data Structures**:
   - Pro: Better concurrency
   - Con: Much more complex to implement correctly
   - Rejected as unnecessary given the scale and Python's GIL