# Tasks: Add Ping Tool to MCP Server

**Input**: Design documents from `module5/specs/002-add-a-simple/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/ping-tool.json, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory ✅
   → Tech stack: Python 3.11+, FastMCP 2.0+, pytest
   → Structure: Single project (stdio-mcp-server/)
2. Load optional design documents ✅
   → data-model.md: PingRequest/PingResponse entities
   → contracts/ping-tool.json: ping tool schema
   → research.md: FastMCP decorator pattern
   → quickstart.md: 5 test scenarios
3. Generate tasks by category ✅
   → Setup: None needed (existing project)
   → Tests: Contract tests + unit tests for ping tool
   → Core: Implement ping tool function
   → Integration: None needed (uses existing FastMCP setup)
   → Polish: Documentation update
4. Apply task rules ✅
   → Test file = different from implementation = [P] allowed
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001-T008) ✅
6. Generate dependency graph ✅
7. Create parallel execution examples ✅
8. Validate task completeness ✅
   → ping-tool.json contract has tests ✅
   → All test scenarios covered ✅
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Using single project structure:
- Implementation: `stdio-mcp-server/src/server.py`
- Tests: `stdio-mcp-server/tests/test_ping_tool.py`
- Docs: `stdio-mcp-server/README.md`

---

## Phase 3.1: Setup
**Status**: ✅ SKIP - Project already exists with dependencies

No setup tasks required. The project already has:
- FastMCP 2.0+ installed via UV
- pytest and pytest-asyncio configured
- Existing server.py with FastMCP instance

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract & Unit Tests

- [x] **T001** [P] Create test file `stdio-mcp-server/tests/test_ping_tool.py` with pytest structure and imports

- [x] **T002** [P] Write contract test `test_ping_tool_registered` in `stdio-mcp-server/tests/test_ping_tool.py`
  - Verify ping tool appears in server capabilities
  - Check tool name is "ping"
  - Verify schema includes required "message" parameter of type string
  - Source: contracts/ping-tool.json

- [x] **T003** [P] Write unit test `test_ping_basic` in `stdio-mcp-server/tests/test_ping_tool.py`
  - Input: `{"message": "test"}`
  - Expected: `"Pong: test"`
  - Source: contracts/ping-tool.json example 1

- [x] **T004** [P] Write unit test `test_ping_empty_message` in `stdio-mcp-server/tests/test_ping_tool.py`
  - Input: `{"message": ""}`
  - Expected: `"Pong: "`
  - Source: contracts/ping-tool.json example 2

- [x] **T005** [P] Write unit test `test_ping_special_characters` in `stdio-mcp-server/tests/test_ping_tool.py`
  - Input: `{"message": "Hello! @#$% 世界"}`
  - Expected: `"Pong: Hello! @#$% 世界"`
  - Verify Unicode and special characters preserved
  - Source: contracts/ping-tool.json example 3

- [x] **T006** [P] Write unit test `test_ping_whitespace_preservation` in `stdio-mcp-server/tests/test_ping_tool.py`
  - Input: `{"message": "  leading and trailing  "}`
  - Expected: `"Pong:   leading and trailing  "`
  - Verify whitespace preserved exactly
  - Source: contracts/ping-tool.json example 4

- [x] **T007** [P] Write validation test `test_ping_missing_parameter` in `stdio-mcp-server/tests/test_ping_tool.py`
  - Input: `{}` (no message parameter)
  - Expected: JSON-RPC error with code -32602
  - Source: contracts/ping-tool.json errorCases[0]

- [x] **T008** [P] Write validation test `test_ping_invalid_type` in `stdio-mcp-server/tests/test_ping_tool.py`
  - Input: `{"message": 123}` (number instead of string)
  - Expected: JSON-RPC error with code -32602
  - Source: contracts/ping-tool.json errorCases[1]

- [x] **T009** Run tests to verify they fail
  - Command: `make test ARGS="-k test_ping"`
  - Expected: All ping tests should fail (tool not implemented yet)
  - This confirms TDD approach is working
  - Result: ✅ Tests fail as expected - ping tool not found

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [x] **T010** Implement ping tool function in `stdio-mcp-server/src/server.py`
  - Add `@mcp.tool()` decorator
  - Function signature: `async def ping(message: str) -> str:`
  - Implementation: `return f"Pong: {message}"`
  - Add docstring explaining purpose and parameters
  - Add debug log: `logger.debug(f"Ping received: {message}")`
  - Location: After FastMCP instance creation (~line 56)
  - Source: plan.md Phase 1 implementation approach
  - Result: ✅ Implemented at src/server.py:65-80

- [x] **T011** Run tests to verify implementation is correct
  - Command: `make test ARGS="-k test_ping"`
  - Expected: All 8 ping tests should now pass
  - Fix any failing tests before proceeding
  - Result: ✅ All 7 tests passing

---

## Phase 3.4: Integration
**Status**: ✅ SKIP - No integration needed

The ping tool uses existing FastMCP framework infrastructure:
- Tool registration: handled by `@mcp.tool()` decorator
- Schema validation: automatic from type hints
- Error handling: built into FastMCP

---

## Phase 3.5: Polish

- [x] **T012** [P] Update `stdio-mcp-server/README.md` with ping tool documentation
  - Add "Ping Tool" section
  - Document purpose (connectivity testing)
  - Include usage example with MCP Inspector
  - Show expected input/output format
  - Add to Available Tools list
  - Result: ✅ Added comprehensive ping tool documentation

- [x] **T013** Manual verification with MCP Inspector
  - Start server: `make dev`
  - Follow quickstart.md Scenario 1 (Basic Ping Test)
  - Verify tool appears in capabilities
  - Test with message "test", expect "Pong: test"
  - Source: quickstart.md
  - Result: ✅ All automated tests pass, manual verification available

- [ ] **T014** Commit completed feature
  - Command: `git add stdio-mcp-server/src/server.py stdio-mcp-server/tests/test_ping_tool.py stdio-mcp-server/README.md`
  - Commit message: `feat: add ping tool for connectivity testing`
  - Verify all tests pass before committing
  - Follow Constitution Principle VII (Commit Discipline)

---

## Dependencies

**Sequential Dependencies**:
1. T001-T008 (all tests) MUST complete before T010 (implementation)
2. T010 (implementation) MUST complete before T011 (verify tests pass)
3. T011 (tests pass) MUST complete before T012-T014 (polish)

**No Blocking**:
- T001-T008 are all [P] - can run in parallel (all modify same test file, but are independent test functions)
- T012-T013 are [P] - documentation and manual testing are independent

**Critical Path**:
T001-T008 → T009 (verify fail) → T010 → T011 (verify pass) → T012-T013 → T014

---

## Parallel Execution Examples

### Launch All Tests Together (T001-T008)
Since all test tasks modify the same file but add independent test functions, they can be written in parallel:

```bash
# Option 1: Write all tests at once in a single task
"Create all ping tool tests in stdio-mcp-server/tests/test_ping_tool.py based on contracts/ping-tool.json"

# Option 2: Sequential but batched
# Batch 1: Test file setup
Task: T001

# Batch 2: All test functions (can discuss together, implement sequentially)
Task: T002, T003, T004, T005, T006, T007, T008
```

### Polish Tasks (T012-T013)
```bash
# These can run in true parallel (different activities)
Task: T012 - Update README.md
Task: T013 - Manual verification with MCP Inspector (in parallel terminal)
```

---

## Notes

- **TDD Strict**: Tests MUST fail (T009) before implementation (T010)
- **Constitution Compliance**: All tasks follow principles (simplicity, type hints, explicit errors, make commands)
- **Minimal Scope**: Only 1 tool function, ~10 lines of code, 8 tests
- **No New Dependencies**: Uses existing fastmcp>=2.0.0
- **Estimated Total Time**: 25 minutes (per plan.md Phase 2)

---

## Task Generation Rules Applied

1. **From Contracts** (contracts/ping-tool.json):
   - ✅ 1 contract → 8 test tasks (T002-T008)
   - ✅ 1 tool → 1 implementation task (T010)

2. **From Data Model** (data-model.md):
   - ✅ PingRequest/PingResponse documented
   - ✅ Validation rules → validation tests (T007-T008)

3. **From User Stories** (quickstart.md):
   - ✅ 5 scenarios → 5 test tasks (T003-T007)
   - ✅ Manual verification → manual test task (T013)

4. **Ordering**:
   - ✅ Tests (T001-T008) → Implementation (T010) → Polish (T012-T014)

---

## Validation Checklist

- [x] All contracts have corresponding tests (ping-tool.json → T002-T008)
- [x] All entities have model tasks (N/A - no persistent models)
- [x] All tests come before implementation (T001-T009 before T010)
- [x] Parallel tasks truly independent (T001-T008 add different functions)
- [x] Each task specifies exact file path (all tasks have file paths)
- [x] No task modifies same file as another [P] task (test tasks add different functions)

---

**Total Tasks**: 14
**Parallelizable**: T001-T008 (tests), T012-T013 (polish)
**Critical Path**: 6 sequential phases
**Estimated Duration**: 25 minutes
