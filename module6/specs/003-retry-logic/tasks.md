# Tasks: Retry Logic

**Input**: Design documents from `/specs/003-retry-logic/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [US1] Create trace_retry package structure in src/observability/trace_retry/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T002 [US1] Create RetryDecision structure in src/observability/trace_retry/models.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Implement Trace-Based Retry Decision Function (Priority: P1) 🎯 MVP

**Goal**: Implement a function that analyzes OpenTelemetry trace data to determine whether a failed operation should be retried.

**Independent Test**: Can be tested by creating traces with different error types and verifying the function returns the expected decision.

### Tests for User Story 1

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T003 [P] [US1] Create test for should_retry with permanent error in tests/unit/observability/trace_retry/test_retry_logic.py
- [ ] T004 [P] [US1] Create test for should_retry with transient error in tests/unit/observability/trace_retry/test_retry_logic.py
- [ ] T005 [P] [US1] Create test for should_retry with unknown error in tests/unit/observability/trace_retry/test_retry_logic.py
- [ ] T006 [P] [US1] Create test for should_retry with error.retriable attribute in tests/unit/observability/trace_retry/test_retry_logic.py
- [ ] T007 [P] [US1] Create test for should_retry with multiple error spans in tests/unit/observability/trace_retry/test_retry_logic.py
- [ ] T008 [P] [US1] Create test for should_retry with no error spans in tests/unit/observability/trace_retry/test_retry_logic.py

### Implementation for User Story 1

- [ ] T009 [US1] Implement helper functions for finding error spans in src/observability/trace_retry/retry_logic.py
- [ ] T010 [US1] Implement helper function for determining retry decision from a span in src/observability/trace_retry/retry_logic.py
- [ ] T011 [US1] Implement should_retry function in src/observability/trace_retry/retry_logic.py
- [ ] T012 [US1] Add validation and error handling for trace_id parameter
- [ ] T013 [US1] Export the should_retry function in src/observability/trace_retry/__init__.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T014 [P] Create comprehensive docstrings and type hints
- [ ] T015 [P] Create quickstart documentation with usage examples
- [ ] T016 Run all tests to verify feature works as expected

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **Polish (Final Phase)**: Depends on User Story 1 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tests should be written and FAIL before implementation
- Helper functions before main functionality
- Core implementation before integration
- Story complete before moving to polish phase

### Parallel Opportunities

- All tests for User Story 1 marked [P] can run in parallel
- Documentation tasks in the Polish phase can run in parallel

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all tests for User Story 1 together:
Task: "Create test for should_retry with permanent error in tests/unit/observability/trace_retry/test_retry_logic.py"
Task: "Create test for should_retry with transient error in tests/unit/observability/trace_retry/test_retry_logic.py"
Task: "Create test for should_retry with unknown error in tests/unit/observability/trace_retry/test_retry_logic.py"
Task: "Create test for should_retry with error.retriable attribute in tests/unit/observability/trace_retry/test_retry_logic.py"
Task: "Create test for should_retry with multiple error spans in tests/unit/observability/trace_retry/test_retry_logic.py"
Task: "Create test for should_retry with no error spans in tests/unit/observability/trace_retry/test_retry_logic.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Complete Polish & Cross-Cutting Concerns

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 Tests → Ensure they fail
3. Implement core functionality → Test independently
4. Polish documentation and examples → Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently