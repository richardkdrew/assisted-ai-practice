# Tasks: File-Based Trace Storage and Query

**Input**: Design documents from `/specs/002-find-analyse-traces/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/query_api.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure setup

- [x] T001 Create `trace_storage` directory in `module6/svc/observability/`
- [x] T002 [P] Create `trace_query` directory in `module6/svc/observability/`
- [x] T003 [P] Create `__init__.py` files in both new directories
- [x] T004 [P] Create test directories for the new modules

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core components required by all user stories

- [ ] T005 [P] Create data models for spans in `module6/svc/observability/trace_storage/models.py`
  - StoredSpan model with all fields and validation
  - SpanQuery model for filtering spans
  - AttributeFilter model for attribute filtering

- [ ] T006 [P] Implement base file I/O operations in `module6/svc/observability/trace_storage/file_storage.py`
  - File path validation and creation
  - Append operations for writing spans
  - Basic reading operations for loading spans
  - Error handling for file operations

- [ ] T007 Implement thread safety utilities in `module6/svc/observability/trace_storage/span_store.py`
  - Thread-safe storage container class
  - Read-write lock implementation
  - Copy-on-read functionality

- [ ] T008 [P] Create unit tests for foundational components
  - Test data models and validation
  - Test file I/O operations
  - Test thread safety

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Store and Retrieve Complete Traces (Priority: P1) 🎯 MVP

**Goal**: Implement a custom OpenTelemetry SpanProcessor that stores spans to a file and provides the ability to retrieve all spans for a given trace ID.

**Independent Test**: Can be tested by generating traces, storing them via the processor, then retrieving by trace ID and verifying all spans are returned correctly.

### Tests for User Story 1

- [ ] T009 [P] [US1] Create test for FileBasedSpanProcessor in `module6/svc/tests/observability/test_file_span_processor.py`
  - Test span processing and storage
  - Test file persistence works correctly
  - Test processor lifecycle (init, shutdown, flush)

- [ ] T010 [P] [US1] Create test for trace retrieval in `module6/svc/tests/observability/test_span_store.py`
  - Test retrieving traces by trace ID
  - Test span relationships are preserved
  - Test data integrity

### Implementation for User Story 1

- [ ] T011 [US1] Implement SpanStore class in `module6/svc/observability/trace_storage/span_store.py`
  - In-memory storage with indices
  - Thread-safe operations
  - Basic trace_id indexing and retrieval
  - FIFO eviction when limit reached

- [ ] T012 [US1] Implement FileBasedSpanProcessor in `module6/svc/observability/trace_storage/file_span_processor.py`
  - Implement SpanProcessor interface
  - on_end method to process completed spans
  - Convert OTel spans to StoredSpan format
  - Store spans in file and in-memory

- [ ] T013 [US1] Implement span serialization/deserialization in `module6/svc/observability/trace_storage/file_span_processor.py`
  - Convert between OTel spans and JSON
  - Handle all span attributes and data
  - Maintain parent-child relationships

- [ ] T014 [US1] Implement get_trace query in `module6/svc/observability/trace_query/query.py`
  - Function to retrieve all spans for a trace ID
  - Order spans by start time
  - Include parameter validation
  - Handle empty results case

- [ ] T015 [US1] Update `module6/svc/observability.py` to register and configure the span processor
  - Add configuration options for file path and max spans
  - Register processor with tracer provider
  - Add setup documentation

**Checkpoint**: At this point, User Story 1 should be fully functional - spans can be stored and retrieved by trace ID

---

## Phase 4: User Story 2 - Filter Traces by Time and Error Status (Priority: P2)

**Goal**: Implement functionality to filter traces by time range and error status, including a specific function for recent failures.

**Independent Test**: Can be tested by generating spans with various timestamps and statuses, then querying with time and status filters to verify the correct spans are returned.

### Tests for User Story 2

- [ ] T016 [P] [US2] Create test for time-based filtering in `module6/svc/tests/observability/test_queries.py`
  - Test recent_failures function
  - Test time range filtering
  - Test combined time and status filtering

### Implementation for User Story 2

- [ ] T017 [P] [US2] Enhance SpanStore in `module6/svc/observability/trace_storage/span_store.py`
  - Add time-based indexing
  - Add status-based indexing
  - Optimize for time range queries

- [ ] T018 [US2] Implement time filter functionality in `module6/svc/observability/trace_query/query.py`
  - Filter by start time ranges
  - Handle relative time (hours ago)
  - Convert between datetime and nanoseconds

- [ ] T019 [US2] Implement status filter in `module6/svc/observability/trace_query/query.py`
  - Filter by ERROR/OK status
  - Combine with time filters
  - Add parameter validation

- [ ] T020 [US2] Implement recent_failures function in `module6/svc/observability/trace_query/query.py`
  - Calculate time window
  - Retrieve ERROR spans in window
  - Sort by most recent first

**Checkpoint**: At this point, User Stories 1 & 2 should be functional - spans can be stored, retrieved by ID, and filtered by time and status

---

## Phase 5: User Story 3 - Filter Traces by Attributes (Priority: P3)

**Goal**: Implement functionality to filter traces by specific attributes, including a specialized filter for error types and a generic attribute filter.

**Independent Test**: Can be tested by generating spans with various attributes, then querying with attribute filters to verify the correct spans are returned.

### Tests for User Story 3

- [ ] T021 [P] [US3] Create test for attribute filtering in `module6/svc/tests/observability/test_queries.py`
  - Test error_type filtering
  - Test generic attribute filtering
  - Test complex query combinations

### Implementation for User Story 3

- [ ] T022 [P] [US3] Enhance SpanStore in `module6/svc/observability/trace_storage/span_store.py`
  - Add attribute-based indexing
  - Optimize for attribute queries
  - Handle different attribute value types

- [ ] T023 [US3] Implement filter_by_error_type in `module6/svc/observability/trace_query/query.py`
  - Filter by error.type attribute
  - Sort results by recency
  - Parameter validation

- [ ] T024 [US3] Implement filter_by_attribute in `module6/svc/observability/trace_query/query.py`
  - Generic attribute filtering
  - Handle different value types
  - Parameter validation

- [ ] T025 [US3] Implement general query_spans function in `module6/svc/observability/trace_query/query.py`
  - Support multiple filter criteria
  - Implement SpanQuery processing
  - Result sorting and limiting
  - Combine all filter types

- [ ] T026 [P] [US3] Create CLI interface in `module6/svc/observability/trace_query/cli.py`
  - Command-line query tools
  - Support all query types
  - Format output for console

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Integration

**Purpose**: Cross-cutting concerns, optimization, and final integration

- [ ] T027 [P] Create integration tests in `module6/svc/tests/observability/test_integration.py`
  - Test end-to-end trace storage and query
  - Test with real OpenTelemetry spans
  - Test performance with many spans

- [ ] T028 Optimize memory usage and performance
  - Profile and optimize memory usage
  - Ensure stays under 256MB limit
  - Optimize query performance

- [ ] T029 [P] Add detailed docstrings and comments
  - Document classes and functions
  - Include examples
  - Update module documentation

- [ ] T030 [P] Create example usage code for the README
  - Example of setting up the processor
  - Example queries for each user story
  - Example error scenarios and handling

- [ ] T031 Update quickstart.md with actual implementation details
  - Update API examples if changed
  - Add any new functionality
  - Update usage instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion
- **User Story 3 (Phase 5)**: Depends on Foundational phase completion
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of User Story 1
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of User Stories 1 and 2

### Within Each User Story

- Tests should be written before implementation
- Models before services
- Core functionality before integration
- Story complete before moving to next priority

### Parallel Opportunities

- Setup tasks can run in parallel
- Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Tests for each user story can be developed in parallel with implementation
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch tests and implementation in parallel:
Task: "Create test for FileBasedSpanProcessor in module6/svc/tests/observability/test_file_span_processor.py"
Task: "Create test for trace retrieval in module6/svc/tests/observability/test_span_store.py"

# After foundational components are complete:
Task: "Implement SpanStore class in module6/svc/observability/trace_storage/span_store.py"
Task: "Implement FileBasedSpanProcessor in module6/svc/observability/trace_storage/file_span_processor.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Store and Retrieve Traces)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Demo the ability to store traces and query by trace ID

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Demo (MVP!)
3. Add User Story 2 → Test independently → Demo
4. Add User Story 3 → Test independently → Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Store and Retrieve)
   - Developer B: User Story 2 (Time and Status Filtering)
   - Developer C: User Story 3 (Attribute Filtering)
3. Stories complete and integrate independently

---

## Notes

- The feature focuses on adding trace storage and query capabilities to the existing OpenTelemetry setup
- Memory usage must remain under 256MB with maximum spans
- Query performance should be under 100ms for 95% of queries
- This implementation enables developers to analyze traces for debugging without external tools
- Each user story provides distinct value that can be delivered independently