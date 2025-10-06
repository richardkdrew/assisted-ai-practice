# Tasks: Additional DevOps CLI Tools (list-releases & check-health)

**Input**: Design documents from `module5/specs/004-now-that-i/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   ✅ Tech stack: Python 3.11+, fastmcp>=2.0.0, pytest
   ✅ Structure: Single project (extend stdio-mcp-server)
2. Load design documents:
   ✅ data-model.md: 2 tools (list_releases, check_health)
   ✅ contracts/: 2 contract schemas
   ✅ research.md: Follow get_deployment_status pattern
   ✅ quickstart.md: 6 test scenarios
3. Generate tasks by category:
   ✅ Setup: No new dependencies needed
   ✅ Tests: 2 contract test files + 6 integration scenarios
   ✅ Core: 2 tool implementations in server.py
   ✅ Integration: Use existing execute_cli_command wrapper
   ✅ Polish: Manual testing via FastMCP inspector
4. Apply task rules:
   ✅ Test files = [P] (parallel)
   ✅ server.py = sequential (same file)
   ✅ TDD: Tests before implementation
5. Number tasks sequentially (T001-T013)
6. Dependencies: Tests → Implementation → Validation
7. Parallel execution: T001-T002 (test files)
8. Validation:
   ✅ All contracts have tests
   ✅ All tools have implementations
   ✅ All quickstart scenarios covered
9. SUCCESS - Ready for execution
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Single project structure (extending existing MCP server):
- Implementation: `stdio-mcp-server/src/server.py`
- Tests: `stdio-mcp-server/tests/test_*.py`

## Phase 3.1: Setup
**Status**: ✅ No setup needed - using existing infrastructure

All dependencies already installed:
- fastmcp>=2.0.0 (installed)
- pytest, pytest-asyncio (installed)
- execute_cli_command wrapper (exists in server.py)

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] **T001** [P] Write contract tests for list-releases tool in `stdio-mcp-server/tests/test_list_releases.py`
  - Test: Valid app parameter → returns releases
  - Test: Valid app + limit → returns limited releases
  - Test: Missing app parameter → raises ValueError("app parameter is required")
  - Test: limit=0 → raises ValueError("limit must be a positive integer")
  - Test: limit=-1 → raises ValueError("limit must be a positive integer")
  - Test: CLI timeout → raises appropriate error
  - Test: Malformed JSON from CLI → raises ValueError
  - **Contract**: [contracts/list-releases.schema.json](contracts/list-releases.schema.json)
  - **Pattern**: Follow existing `test_ping.py` structure with pytest-asyncio
  - **Result**: ✅ All 7 tests FAIL as expected (tool not implemented yet)

- [x] **T002** [P] Write contract tests for check-health tool in `stdio-mcp-server/tests/test_check_health.py`
  - Test: Valid env parameter → returns health for that environment
  - Test: Uppercase env ("PROD") → case-insensitive match works
  - Test: Invalid env → raises ValueError with valid options
  - Test: No env parameter → returns health for ALL environments
  - Test: CLI timeout → raises appropriate error
  - Test: Malformed JSON from CLI → raises ValueError
  - **Contract**: [contracts/check-health.schema.json](contracts/check-health.schema.json)
  - **Pattern**: Follow existing `test_ping.py` structure with pytest-asyncio
  - **Result**: ✅ All 6 tests FAIL as expected (tool not implemented yet)

## Phase 3.3: Core Implementation (ONLY after T001-T002 tests are failing)

- [x] **T003** Implement list_releases tool in `stdio-mcp-server/src/server.py`
  - **Location**: Add after `get_deployment_status` function (around line 300)
  - **Signature**: `@mcp.tool() async def list_releases(app: str, limit: int | None = None) -> dict[str, Any]:`
  - **Validation**:
    ```python
    if not app:
        raise ValueError("app parameter is required")
    if limit is not None and limit < 1:
        raise ValueError("limit must be a positive integer")
    ```
  - **CLI Args**: `["releases", "--app", app, "--format", "json"]` + optional `["--limit", str(limit)]`
  - **Pattern**: Copy `get_deployment_status` structure exactly:
    - Build args list
    - Call `await execute_cli_command(args, timeout=30.0)`
    - Check returncode
    - Parse JSON with try/except
    - Log errors to stderr
  - **Expected**: Makes T001 tests PASS
  - **Dependencies**: T001 must be failing first

- [x] **T004** Implement check_health tool in `stdio-mcp-server/src/server.py`
  - **Location**: Add after `list_releases` function
  - **Signature**: `@mcp.tool() async def check_health(env: str | None = None) -> dict[str, Any]:`
  - **Validation**:
    ```python
    if env is not None:
        env_lower = env.lower()
        if env_lower not in ["prod", "staging", "uat", "dev"]:
            raise ValueError(f"Invalid environment: {env}. Must be one of: prod, staging, uat, dev")
    ```
  - **CLI Args**: `["health", "--format", "json"]` + optional `["--env", env_lower]`
  - **Pattern**: Same as `get_deployment_status`:
    - Build args list
    - Call `await execute_cli_command(args, timeout=30.0)`
    - Check returncode
    - Parse JSON with try/except
    - Log errors to stderr
  - **Expected**: Makes T002 tests PASS
  - **Dependencies**: T002 must be failing first, T003 must be complete (sequential edits to same file)

## Phase 3.4: Integration
**Status**: ✅ No integration tasks needed

- Existing `execute_cli_command` wrapper handles all subprocess interaction
- Existing error handling patterns apply
- Existing logging configuration (stderr only) applies
- No new middleware or DB connections needed

## Phase 3.5: Polish & Validation

- [x] **T005** [P] Run full test suite via `make test`
  - All tests in `stdio-mcp-server/tests/` must pass
  - Includes: test_ping.py, test_list_releases.py, test_check_health.py
  - Existing tests (test_initialize.py, test_error_handling.py) still pass
  - **Result**: ✅ 45 passed, 1 skipped - 100% pass rate

- [ ] **T006** [P] Manual test Scenario 1 via FastMCP Inspector (Query Release History)
  - Start inspector: `make dev`
  - Call `list-releases` with `app="web-app"`, `limit=5`
  - **Validation**: Returns max 5 releases, status="success"
  - **Reference**: [quickstart.md](quickstart.md) Scenario 1

- [ ] **T007** [P] Manual test Scenario 2 via FastMCP Inspector (Check Production Health)
  - Call `check-health` with `env="prod"`
  - **Validation**: Returns production health only
  - **Reference**: [quickstart.md](quickstart.md) Scenario 2

- [ ] **T008** [P] Manual test Scenario 3 via FastMCP Inspector (Check All Environments)
  - Call `check-health` with no env parameter
  - **Validation**: Returns health for all 4 environments
  - **Reference**: [quickstart.md](quickstart.md) Scenario 3

- [ ] **T009** [P] Manual test Scenario 4 (Error: Missing Required Parameter)
  - Call `list-releases` with no app parameter
  - **Validation**: Returns clear error message
  - **Reference**: [quickstart.md](quickstart.md) Scenario 4

- [ ] **T010** [P] Manual test Scenario 5 (Error: Invalid Environment)
  - Call `check-health` with `env="invalid-env"`
  - **Validation**: Returns error listing valid options
  - **Reference**: [quickstart.md](quickstart.md) Scenario 5

- [ ] **T011** [P] Manual test Scenario 6 (Case-Insensitive Environment)
  - Call `check-health` with `env="PROD"` (uppercase)
  - **Validation**: Same result as Scenario 2
  - **Reference**: [quickstart.md](quickstart.md) Scenario 6

- [x] **T012** Update CLAUDE.md to mark Feature 004 as implemented
  - Change "Feature 004-now-that-i **planned**" → "Feature 004-now-that-i **implemented**"
  - **File**: `CLAUDE.md` line 254
  - **Pattern**: Same as Features 002 and 003 entries
  - **Result**: ✅ CLAUDE.md updated

- [x] **T014** [P] Write integration tests using FastMCP Client in-memory transport
  - **File**: `stdio-mcp-server/tests/test_integration_devops_tools.py`
  - **Pattern**: `async with Client(mcp) as client:`
  - **Tests**: 12 integration tests covering:
    - list_releases: success, with limit, missing app, invalid limit, CLI failure
    - check_health: single env, case-insensitive, all envs, invalid env, CLI timeout
    - Tool discovery validation
    - Concurrent tool execution
  - **Result**: ✅ All 12 integration tests passing (57 total project tests, 1 skipped)

- [x] **T013** Commit implementation with conventional commit message
  - **Command**: `git add stdio-mcp-server/src/server.py stdio-mcp-server/tests/test_*.py CLAUDE.md`
  - **Message**:
    ```
    feat: add list-releases and check-health MCP tools

    - list_releases: query release history with app filtering and limit
    - check_health: check environment health (single or all environments)
    - Both tools follow get_deployment_status pattern
    - Input validation prevents injection and provides clear errors
    - Case-insensitive environment matching
    - Comprehensive test coverage (13 tests total)

    🤖 Generated with [Claude Code](https://claude.com/claude-code)

    Co-Authored-By: Claude <noreply@anthropic.com>
    ```

## Dependencies

**Sequential Dependencies**:
- T001, T002 (tests) → T003, T004 (implementation)
- T003 → T004 (same file, sequential edits)
- T003, T004 → T005-T013 (validation after implementation)

**Parallel Groups**:
- Group 1: T001, T002 (different test files)
- Group 2: T005-T011 (independent validation tasks)
- T012, T013 sequential (documentation then commit)

## Parallel Execution Example

**Phase 3.2 - Write Tests** (run in parallel):
```bash
# Launch T001 and T002 together:
Task: "Write contract tests for list-releases in stdio-mcp-server/tests/test_list_releases.py"
Task: "Write contract tests for check-health in stdio-mcp-server/tests/test_check_health.py"
```

**Phase 3.5 - Manual Testing** (run in parallel):
```bash
# Launch T006-T011 together (all use FastMCP inspector):
Task: "Manual test Scenario 1 - Query Release History"
Task: "Manual test Scenario 2 - Check Production Health"
Task: "Manual test Scenario 3 - Check All Environments"
Task: "Manual test Scenario 4 - Missing Required Parameter"
Task: "Manual test Scenario 5 - Invalid Environment"
Task: "Manual test Scenario 6 - Case-Insensitive Environment"
```

## Notes

- **[P] tasks**: Different files or independent operations
- **TDD Critical**: T001-T002 must FAIL before T003-T004
- **Same File**: T003 and T004 edit same file (server.py) - MUST be sequential
- **Constitution**: All tasks follow Constitutional principles (simplicity, explicit errors, type hints, stderr logging)
- **Pattern Consistency**: Both tools follow `get_deployment_status` pattern exactly
- **Validation**: 6 quickstart scenarios provide comprehensive coverage

## Task Generation Rules Applied

1. **From Contracts** ✅:
   - list-releases.schema.json → T001 (contract test)
   - check-health.schema.json → T002 (contract test)
   - Both contracts → T003, T004 (implementations)

2. **From Data Model** ✅:
   - list_releases tool → T003 (implementation with validation)
   - check_health tool → T004 (implementation with validation)

3. **From User Stories** ✅:
   - 6 quickstart scenarios → T006-T011 (manual validation)

4. **Ordering** ✅:
   - Setup (none needed) → Tests (T001-T002) → Implementation (T003-T004) → Polish (T005-T013)

## Validation Checklist

- [x] All contracts have corresponding tests (T001, T002)
- [x] All tools have implementation tasks (T003, T004)
- [x] All tests come before implementation (T001-T002 before T003-T004)
- [x] Parallel tasks truly independent (different files or read-only operations)
- [x] Each task specifies exact file path
- [x] No [P] task modifies same file as another [P] task

---

**Total Tasks**: 13
**Estimated Time**: 2-3 hours (tests: 1h, implementation: 30min, validation: 1h)
**Ready for Execution**: ✅
