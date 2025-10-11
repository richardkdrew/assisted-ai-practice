# Tasks: Structured Error Tracing

**Input**: Design documents from `/specs/001-structured-error-tracing/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tasks include tests based on the explicit testing requirements in the specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare environment for structured error tracing implementation

- [x] T001 [P] Install OpenTelemetry packages in Python environment: `uv pip install -e ".[observability]"`
- [x] T002 [P] Verify package installation with a test import script
- [x] T003 Review existing observability.py file to understand current implementation

**Checkpoint**: Environment ready - core implementation can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that must be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Update Docker Compose with Jaeger container in `module6/svc/docker-compose.yml`
- [ ] T005 [P] Update OTEL collector configuration in `module6/svc/observability/otel-collector.yml`
- [ ] T006 [P] Create Jaeger configuration directory in `module6/svc/observability/jaeger/`
- [ ] T007 Add OTEL environment variables to Python service in `module6/svc/docker-compose.yml`
- [ ] T008 Configure trace context propagation in `module6/svc/observability.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Capture Errors with Context (Priority: P1) 🎯 MVP

**Goal**: Capture structured error information including request ID, timestamp, error type, and context data

**Independent Test**: Trigger an error condition (e.g., create application with invalid data) and verify error log contains structured fields

### Tests for User Story 1

- [ ] T009 [P] [US1] Create error trigger test in `module6/tests/test_error_tracing.py` to validate error context capture
- [ ] T010 [P] [US1] Create middleware test in `module6/tests/test_error_tracing.py` for error capture

### Implementation for User Story 1

- [ ] T011 [US1] Implement error tracking middleware in `module6/svc/observability.py`
- [ ] T012 [US1] Configure standard error attributes based on OpenTelemetry best practices in `module6/svc/observability.py`
- [ ] T013 [P] [US1] Add helper function to truncate error payloads to 10KB in `module6/svc/observability.py`
- [ ] T014 [US1] Add error-specific middleware registration in `module6/svc/main.py`
- [ ] T015 [US1] Create custom exception handlers in `module6/svc/main.py`
- [ ] T016 [US1] Implement structured error response format in exception handlers in `module6/svc/main.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Trace Errors Across Operations (Priority: P2)

**Goal**: Enable tracing of a request through multiple service operations by propagating a unique request identifier

**Independent Test**: Make a request that triggers multiple operations and verify all log entries share the same request ID

### Tests for User Story 2

- [ ] T017 [P] [US2] Create multi-step operation test in `module6/tests/test_error_tracing.py` to verify request ID propagation
- [ ] T018 [P] [US2] Create test for trace context propagation through async operations in `module6/tests/test_error_tracing.py`

### Implementation for User Story 2

- [ ] T019 [US2] Configure W3C TraceContext and Baggage propagators in `module6/svc/observability.py`
- [ ] T020 [US2] Add request ID extraction from trace context in `module6/svc/observability.py`
- [ ] T021 [US2] Implement span context propagation through database operations in `module6/svc/observability.py`
- [ ] T022 [US2] Add trace-specific attributes to spans for operation steps in `module6/svc/observability.py`
- [ ] T023 [US2] Enhance error middleware to capture operation step information in `module6/svc/observability.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Query and Filter Error Logs (Priority: P3)

**Goal**: Enable querying error logs by various criteria for efficient debugging and incident response

**Independent Test**: Generate various error types and verify they can be queried by different filters (error type, time range, application ID)

### Tests for User Story 3

- [ ] T024 [P] [US3] Create test for error filtering by type in `module6/tests/test_error_tracing.py`
- [ ] T025 [P] [US3] Create test for error filtering by time range in `module6/tests/test_error_tracing.py`
- [ ] T026 [P] [US3] Create test for error filtering by application ID in `module6/tests/test_error_tracing.py`
- [ ] T027 [P] [US3] Create test for error query by request ID in `module6/tests/test_error_tracing.py`

### Implementation for User Story 3

- [ ] T028 [US3] Define Jaeger tag keys for filtering in `module6/svc/observability.py`
- [ ] T029 [US3] Add timestamp attribute formatting for time range queries in `module6/svc/observability.py`
- [ ] T030 [US3] Add application ID attribute to error spans in `module6/svc/observability.py`
- [ ] T031 [US3] Configure proper sampling strategy for errors vs regular traces in `module6/svc/observability.py`
- [ ] T032 [US3] Update Jaeger UI configuration for optimized error queries in `module6/svc/observability/jaeger/ui-config.json`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T033 [P] Create helper utility for manual error span creation in `module6/svc/observability.py`
- [ ] T034 Load testing for error tracing performance impact using `module6/svc/load_testing.py`
- [ ] T035 Update documentation with error tracing usage examples in README.md
- [ ] T036 [P] Add sample error queries in `module6/svc/observability/jaeger/example-queries.md`
- [ ] T037 Add error sampling configuration in `module6/svc/observability.py`
- [ ] T038 Optimize trace payload sizes and buffering in `module6/svc/observability.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Builds on US1 but focuses on tracing across operations
- **User Story 3 (P3)**: Builds on US1 and US2 but focuses on querying capabilities

### Within Each User Story

- Tests should be written before implementation
- Core middleware functionality before custom exception handlers
- Base implementation before extensions/refinements
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create error trigger test in module6/tests/test_error_tracing.py"
Task: "Create middleware test in module6/tests/test_error_tracing.py"

# Launch independent implementations together:
Task: "Add helper function to truncate error payloads to 10KB in module6/svc/observability.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Capture Errors with Context) → Deploy/Demo (MVP!)
3. Add User Story 2 (Trace Errors Across Operations) → Deploy/Demo
4. Add User Story 3 (Query and Filter Error Logs) → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- All implementation should maintain the 10KB payload size limit
- Ensure error tracing doesn't impact performance by more than 5ms average
- Each user story should be independently testable
- Commit after each task or logical group