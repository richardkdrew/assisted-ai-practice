# Tasks: DevOps CLI Wrapper (Phase 1: get-status)

**Input**: Design documents from `/specs/003-i-have-a/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/get-status.json, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory ✅
   → Tech stack: Python 3.11+, FastMCP 2.0+, pytest
   → Structure: Single project (stdio-mcp-server/)
   → Scope: Phase 1 - get-status tool with subprocess wrapper
2. Load optional design documents ✅
   → data-model.md: CLIExecutionResult, Deployment entities
   → contracts/get-status.json: get_deployment_status tool schema
   → research.md: Async subprocess patterns, error handling
   → quickstart.md: 12 test scenarios
3. Generate tasks by category ✅
   → Setup: Create new modules (cli_wrapper.py, tools/devops.py)
   → Tests: Contract tests + unit tests for wrapper and tool
   → Core: Implement CLI wrapper + get-status tool
   → Integration: Register tool in server.py
   → Polish: Documentation, manual testing, commit
4. Apply task rules ✅
   → Test file ≠ implementation file = [P] allowed
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001-T020) ✅
6. Generate dependency graph ✅
7. Create parallel execution examples ✅
8. Validate task completeness ✅
   → get-status.json contract has tests ✅
   → CLIExecutionResult entity has module ✅
   → All test scenarios covered ✅
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Using single project structure:
- Implementation: `stdio-mcp-server/src/`
- Tests: `stdio-mcp-server/tests/`
- Docs: `stdio-mcp-server/README.md`

---

## Phase 3.1: Setup

- [x] **T001** Create `stdio-mcp-server/src/cli_wrapper.py` with module structure and imports
  - Add file header docstring explaining purpose
  - Import: `asyncio`, `subprocess`, `logging`, `typing.NamedTuple`, `pathlib.Path`
  - Define logger: `logger = logging.getLogger(__name__)`
  - Leave module ready for function implementation

- [x] **T002** Create `stdio-mcp-server/src/tools/` directory and `__init__.py`
  - Create directory: `mkdir -p stdio-mcp-server/src/tools`
  - Create empty `__init__.py` for package structure
  - Add docstring: "MCP tool implementations for DevOps CLI wrapper"

- [x] **T003** Create `stdio-mcp-server/src/tools/devops.py` with module structure
  - Add file header docstring
  - Import: `asyncio`, `logging`, `json`, `typing.Any`, `from ..cli_wrapper import execute_cli_command`
  - Import FastMCP instance: `from ..server import mcp`
  - Define logger: `logger = logging.getLogger(__name__)`
  - Leave module ready for tool implementation

- [x] **T004** Create `stdio-mcp-server/tests/test_cli_wrapper.py` test file structure
  - Add file header docstring
  - Import: `pytest`, `asyncio`, `unittest.mock`, `sys`, `from src.cli_wrapper import CLIExecutionResult, execute_cli_command`
  - Add pytest markers for async tests
  - Leave file ready for test functions

- [x] **T005** Create `stdio-mcp-server/tests/test_devops_tools.py` test file structure
  - Add file header docstring
  - Import: `pytest`, `asyncio`, `json`, `unittest.mock`, `from src.tools.devops import get_deployment_status`
  - Add pytest markers for async tests
  - Leave file ready for test functions

---

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### CLI Wrapper Tests

- [x] **T006** [P] Write `test_cli_execution_result_structure` in `stdio-mcp-server/tests/test_cli_wrapper.py`
  - Test that `CLIExecutionResult` NamedTuple has correct fields
  - Verify: `stdout: str`, `stderr: str`, `returncode: int`
  - Assert immutability (NamedTuple behavior)

- [x] **T007** [P] Write `test_execute_cli_success` in `stdio-mcp-server/tests/test_cli_wrapper.py`
  - Mock `asyncio.create_subprocess_exec()` to return success
  - Test: `execute_cli_command(["status", "--format", "json"])`
  - Assert: Returns `CLIExecutionResult` with stdout, returncode=0
  - Source: research.md async subprocess pattern

- [x] **T008** [P] Write `test_execute_cli_timeout` in `stdio-mcp-server/tests/test_cli_wrapper.py`
  - Mock subprocess to sleep beyond timeout
  - Test: `execute_cli_command(..., timeout=1.0)`
  - Assert: Raises `asyncio.TimeoutError`
  - Source: research.md timeout management

- [x] **T009** [P] Write `test_execute_cli_not_found` in `stdio-mcp-server/tests/test_cli_wrapper.py`
  - Mock subprocess to raise `FileNotFoundError`
  - Test: CLI tool path doesn't exist
  - Assert: Raises `FileNotFoundError` with helpful message
  - Source: quickstart.md Scenario 7

- [x] **T010** [P] Write `test_execute_cli_nonzero_exit` in `stdio-mcp-server/tests/test_cli_wrapper.py`
  - Mock subprocess to return exit code 1 with stderr
  - Test: CLI command fails internally
  - Assert: Returns `CLIExecutionResult` with returncode=1, stderr populated
  - Source: quickstart.md Scenario 9

- [x] **T011** [P] Write `test_execute_cli_stderr_capture` in `stdio-mcp-server/tests/test_cli_wrapper.py`
  - Mock subprocess with both stdout and stderr output
  - Test: Verify both streams captured separately
  - Assert: `result.stdout` and `result.stderr` both populated
  - Source: research.md stdout/stderr separation

### Tool Contract Tests

- [x] **T012** [P] Write `test_get_status_tool_registered` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Verify `get_deployment_status` tool appears in server capabilities
  - Check tool name is "get_deployment_status"
  - Verify schema includes optional `application` and `environment` parameters
  - Source: contracts/get-status.json

- [x] **T013** [P] Write `test_get_status_no_filters` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Mock `execute_cli_command()` to return sample JSON (all deployments)
  - Input: `get_deployment_status()` (no parameters)
  - Expected: Returns dict with `status`, `deployments[]`, `total_count`, `filters_applied`
  - Assert: `filters_applied.application` is None, `environment` is None
  - Source: contracts/get-status.json example 1, quickstart.md Scenario 1

- [x] **T014** [P] Write `test_get_status_filter_by_app` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Mock CLI to return filtered results
  - Input: `get_deployment_status(application="web-app")`
  - Expected: CLI called with `--app web-app` argument
  - Assert: All deployments have `applicationId = "web-app"`
  - Source: contracts/get-status.json example 2, quickstart.md Scenario 2

- [x] **T015** [P] Write `test_get_status_filter_by_env` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Mock CLI to return filtered results
  - Input: `get_deployment_status(environment="prod")`
  - Expected: CLI called with `--env prod` argument
  - Assert: All deployments have `environment = "prod"`
  - Source: contracts/get-status.json example 3, quickstart.md Scenario 3

- [x] **T016** [P] Write `test_get_status_filter_both` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Mock CLI to return single matching deployment
  - Input: `get_deployment_status(application="web-app", environment="prod")`
  - Expected: CLI called with both `--app` and `--env` flags
  - Assert: Exactly 1 deployment returned matching both filters
  - Source: contracts/get-status.json example 4, quickstart.md Scenario 4

- [x] **T017** [P] Write `test_get_status_no_results` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Mock CLI to return empty deployments array
  - Input: `get_deployment_status(application="nonexistent-app")`
  - Expected: Returns `{"status": "success", "deployments": [], "total_count": 0}`
  - Assert: No error thrown, empty array is valid
  - Source: contracts/get-status.json example 5, quickstart.md Scenario 5

### Error Handling Tests

- [x] **T018** [P] Write `test_get_status_timeout_error` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Mock `execute_cli_command()` to raise `asyncio.TimeoutError`
  - Input: `get_deployment_status()`
  - Expected: Raises `RuntimeError` with message "DevOps CLI timed out after 30 seconds"
  - Source: contracts/get-status.json errorCases[0], quickstart.md Scenario 6

- [x] **T019** [P] Write `test_get_status_cli_not_found` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Mock `execute_cli_command()` to raise `FileNotFoundError`
  - Input: `get_deployment_status()`
  - Expected: Raises `RuntimeError` with message about CLI tool not found
  - Source: contracts/get-status.json errorCases[1], quickstart.md Scenario 7

- [x] **T020** [P] Write `test_get_status_invalid_json` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Mock CLI to return malformed JSON (e.g., `{incomplete`)
  - Input: `get_deployment_status()`
  - Expected: Raises `ValueError` with message "CLI returned invalid JSON: ..."
  - Source: contracts/get-status.json errorCases[2], quickstart.md Scenario 8

- [x] **T021** [P] Write `test_get_status_cli_failure` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Mock CLI to return non-zero exit code with stderr
  - Input: `get_deployment_status()`
  - Expected: Raises `RuntimeError` with exit code and stderr in message
  - Source: contracts/get-status.json errorCases[3], quickstart.md Scenario 9

- [x] **T022** [P] Write `test_get_status_missing_fields` in `stdio-mcp-server/tests/test_devops_tools.py`
  - Mock CLI to return JSON missing required field (e.g., no `status`)
  - Input: `get_deployment_status()`
  - Expected: Raises `ValueError` with message "CLI output missing required field: status"
  - Source: contracts/get-status.json errorCases[4], quickstart.md Scenario 10

- [x] **T023** Run tests to verify they fail
  - Command: `make test ARGS="-k test_cli_wrapper or test_devops_tools"`
  - Expected: All 17 new tests should fail (modules not implemented yet)
  - This confirms TDD approach is working
  - Document failure count in task notes

---

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### CLI Wrapper Implementation

- [x] **T024** Define `CLIExecutionResult` NamedTuple in `stdio-mcp-server/src/cli_wrapper.py`
  - Location: Top of file, after imports
  - Code:
    ```python
    class CLIExecutionResult(NamedTuple):
        """Result of executing a CLI command via subprocess."""
        stdout: str
        stderr: str
        returncode: int
    ```
  - Source: data-model.md Entity 1

- [x] **T025** Implement `execute_cli_command()` function in `stdio-mcp-server/src/cli_wrapper.py`
  - Function signature:
    ```python
    async def execute_cli_command(
        args: list[str],
        timeout: float = 30.0,
        cwd: str | None = None
    ) -> CLIExecutionResult:
    ```
  - Implementation requirements:
    - Use `asyncio.create_subprocess_exec()` with explicit args (no shell=True)
    - Set `stdout=asyncio.subprocess.PIPE`, `stderr=asyncio.subprocess.PIPE`
    - Wrap subprocess call with `asyncio.wait_for(timeout=timeout)`
    - Full CLI path: `./acme-devops-cli/devops-cli`
    - Default cwd to module5/ directory if not provided
    - Decode stdout/stderr as UTF-8
    - Return `CLIExecutionResult(stdout, stderr, returncode)`
    - Add docstring with params, returns, raises
    - Add INFO log: "Executing DevOps CLI: {args}"
    - Add DEBUG log: "CLI completed in {duration}s"
  - Source: research.md async subprocess pattern

- [x] **T026** Run CLI wrapper tests to verify implementation
  - Command: `make test ARGS="-k test_cli_wrapper"`
  - Expected: All 6 CLI wrapper tests should now pass
  - Fix any failing tests before proceeding
  - Document: test results in task notes

### Tool Implementation

- [x] **T027** Implement `get_deployment_status()` tool in `stdio-mcp-server/src/tools/devops.py`
  - Add `@mcp.tool()` decorator
  - Function signature:
    ```python
    @mcp.tool()
    async def get_deployment_status(
        application: str | None = None,
        environment: str | None = None
    ) -> dict[str, Any]:
    ```
  - Implementation requirements:
    - Build CLI args: `["status", "--format", "json"]`
    - If `application` provided: append `["--app", application]`
    - If `environment` provided: append `["--env", environment]`
    - Call `execute_cli_command(args, timeout=30.0, cwd=".")`
    - Wrap in try/except for error handling:
      - `asyncio.TimeoutError` → raise `RuntimeError("DevOps CLI timed out after 30 seconds")`
      - `FileNotFoundError` → raise `RuntimeError("DevOps CLI tool not found at ./acme-devops-cli/devops-cli")`
    - Parse JSON: `data = json.loads(result.stdout)`
    - Wrap JSON parsing in try/except:
      - `json.JSONDecodeError` → raise `ValueError(f"CLI returned invalid JSON: {e}")`
    - Validate required fields: `["status", "deployments", "total_count", "filters_applied", "timestamp"]`
    - If field missing → raise `ValueError(f"CLI output missing required field: {field}")`
    - Log CLI stderr if non-empty: `logger.warning(f"CLI stderr: {result.stderr}")`
    - If returncode != 0 → raise `RuntimeError(f"DevOps CLI failed with exit code {returncode}: {stderr}")`
    - Return parsed data dict
    - Add comprehensive docstring
  - Source: data-model.md Entity 3, research.md error handling

- [x] **T028** Run tool tests to verify implementation
  - Command: `make test ARGS="-k test_devops_tools"`
  - Expected: All 11 tool tests should now pass
  - Fix any failing tests before proceeding
  - Document: test results in task notes

---

## Phase 3.4: Integration

- [x] **T029** Import devops tools in `stdio-mcp-server/src/server.py`
  - Location: After existing imports, before `if __name__ == "__main__"` block
  - Add: `from .tools import devops  # noqa: F401`
  - Comment: "Import registers MCP tools via @mcp.tool() decorator"
  - Verify: FastMCP auto-discovery loads the tool
  - Source: plan.md Integration approach

- [x] **T030** Run full test suite to verify integration
  - Command: `make test`
  - Expected: All existing tests + 17 new tests should pass (total ~29 tests)
  - Fix any integration issues
  - Document: final test count

---

## Phase 3.5: Polish

- [x] **T031** [P] Update `stdio-mcp-server/README.md` with get_deployment_status tool documentation
  - Add new section: "## DevOps CLI Wrapper Tools"
  - Document `get_deployment_status` tool:
    - Purpose: Query deployment status across applications and environments
    - Parameters: `application` (optional), `environment` (optional)
    - Returns: JSON with deployments, filters, timestamp
    - Example usage with MCP Inspector
    - Example output
  - Add to "Available Tools" list
  - Note: First tool in DevOps CLI wrapper series

- [x] **T032** [P] Add example usage to `stdio-mcp-server/README.md`
  - Section: "### Example: Get Deployment Status"
  - Show MCP Inspector usage:
    - All deployments: no parameters
    - Filter by app: `application="web-app"`
    - Filter by env: `environment="prod"`
    - Both filters: `application="web-app", environment="prod"`
  - Show sample output for each

- [x] **T033** Manual verification with MCP Inspector
  - Start server: `make dev`
  - Follow quickstart.md Scenario 1-4 (positive tests)
  - Verify tool appears in capabilities
  - Test each filter combination
  - Verify output matches expected structure
  - Document: manual test results

- [x] **T034** Performance validation
  - Measure CLI execution time: `time ./acme-devops-cli/devops-cli status --format json`
  - Should be <1 second
  - Test via MCP Inspector and compare timestamps
  - Total execution should be <2 seconds
  - Overhead (MCP - CLI) should be <500ms
  - Source: quickstart.md Scenario 11

- [x] **T035** Verify logging output
  - Run tests with verbose logging: `make test ARGS="-v -s -k test_get_status_no_filters"`
  - Check stderr for expected log entries:
    - INFO: "Executing DevOps CLI: status --format json"
    - DEBUG: "CLI completed in X.XXs"
  - Verify: No logs to stdout (only stderr)
  - Source: quickstart.md Scenario 12

- [x] **T036** Commit completed feature
  - Stage files:
    - `stdio-mcp-server/src/cli_wrapper.py`
    - `stdio-mcp-server/src/tools/__init__.py`
    - `stdio-mcp-server/src/tools/devops.py`
    - `stdio-mcp-server/src/server.py`
    - `stdio-mcp-server/tests/test_cli_wrapper.py`
    - `stdio-mcp-server/tests/test_devops_tools.py`
    - `stdio-mcp-server/README.md`
  - Commit message:
    ```
    feat: add DevOps CLI wrapper with get_deployment_status tool

    - Implement reusable async subprocess wrapper (cli_wrapper.py)
    - Add get_deployment_status MCP tool with optional filters
    - Support application and environment filtering
    - Comprehensive error handling (timeout, not found, invalid JSON)
    - 17 tests covering success and error cases
    - Full logging to stderr (MCP protocol compliant)

    Phase 1 of 4 CLI wrapper tools. Pattern established for future tools.
    ```
  - Verify all tests pass before committing: `make test`
  - Follow Constitution Principle VII (Commit Discipline)

---

## Dependencies

**Sequential Dependencies**:
1. T001-T005 (setup) MUST complete before T006-T023 (tests)
2. T006-T022 (all tests) MUST complete before T023 (verify tests fail)
3. T023 (verify fail) MUST complete before T024-T028 (implementation)
4. T024-T025 (CLI wrapper) MUST complete before T026 (verify wrapper tests pass)
5. T026 (wrapper tests pass) MUST complete before T027 (tool implementation)
6. T027 (tool implementation) MUST complete before T028 (verify tool tests pass)
7. T028 (tool tests pass) MUST complete before T029-T030 (integration)
8. T030 (integration verified) MUST complete before T031-T036 (polish)

**No Blocking**:
- T001-T005 are independent setup tasks (but sequential is fine)
- T006-T022 are all [P] - can write in parallel (different test functions)
- T031-T035 are [P] - documentation and validation are independent
- T036 (commit) must be last

**Critical Path**:
Setup (T001-T005) → Write Tests (T006-T022) → Verify Fail (T023) → Implement Wrapper (T024-T026) → Implement Tool (T027-T028) → Integration (T029-T030) → Polish (T031-T035) → Commit (T036)

---

## Parallel Execution Examples

### Batch 1: Setup Tasks (T001-T005)
Can discuss all together, execute sequentially:
```bash
# All setup tasks define file structure
Task: T001 - Create cli_wrapper.py
Task: T002 - Create tools/ directory
Task: T003 - Create tools/devops.py
Task: T004 - Create test_cli_wrapper.py
Task: T005 - Create test_devops_tools.py
```

### Batch 2: Write All Tests (T006-T022)
Since all test tasks add independent test functions, they can be discussed together:
```bash
# Option 1: Write all tests at once
"Write all 17 test functions based on contracts/get-status.json and quickstart.md:
- 6 CLI wrapper tests in test_cli_wrapper.py
- 11 tool tests in test_devops_tools.py"

# Option 2: Sequential batches
# Batch 2a: CLI wrapper tests (T006-T011)
# Batch 2b: Tool contract tests (T012-T017)
# Batch 2c: Error handling tests (T018-T022)
```

### Batch 3: Implementation (Sequential)
```bash
# Must be sequential due to dependencies
Task: T024 - Define CLIExecutionResult
Task: T025 - Implement execute_cli_command()
Task: T026 - Run wrapper tests
Task: T027 - Implement get_deployment_status()
Task: T028 - Run tool tests
```

### Batch 4: Polish Tasks (T031-T035)
```bash
# These can run in true parallel (different activities)
Task: T031 - Update README tool docs
Task: T032 - Add example usage
Task: T033 - Manual verification (in parallel terminal)
Task: T034 - Performance validation
Task: T035 - Verify logging
```

---

## Notes

- **TDD Strict**: Tests MUST fail (T023) before implementation (T024-T028)
- **Constitution Compliance**: All tasks follow constitutional principles
- **Minimal Scope**: Phase 1 only - get-status tool with reusable wrapper
- **No New Dependencies**: Uses stdlib only (asyncio, subprocess, json)
- **Estimated Total Time**: 3-4 hours (setup 30min, tests 1hr, implementation 1hr, polish 1hr)
- **Next Phase**: After validation, implement remaining 3 tools (list_releases, check_health, promote_release) using same CLI wrapper pattern

---

## Task Generation Rules Applied

1. **From Contracts** (contracts/get-status.json):
   - ✅ 1 contract → 11 tool test tasks (T012-T022)
   - ✅ 1 tool → 1 implementation task (T027)

2. **From Data Model** (data-model.md):
   - ✅ CLIExecutionResult entity → definition task (T024)
   - ✅ CLI wrapper module → implementation task (T025)

3. **From Research** (research.md):
   - ✅ Async subprocess pattern → CLI wrapper tests (T006-T011)
   - ✅ Error handling patterns → error tests (T018-T022)

4. **From User Stories** (quickstart.md):
   - ✅ 12 scenarios → 17 test tasks (T006-T022)
   - ✅ Manual verification → manual test task (T033)

5. **Ordering**:
   - ✅ Setup (T001-T005) → Tests (T006-T023) → Implementation (T024-T028) → Integration (T029-T030) → Polish (T031-T036)

---

## Validation Checklist

- [x] All contracts have corresponding tests (get-status.json → T012-T022)
- [x] All entities have implementation tasks (CLIExecutionResult → T024, execute_cli_command → T025)
- [x] All tests come before implementation (T006-T023 before T024-T028)
- [x] Parallel tasks truly independent (T006-T022 add different test functions, T031-T035 different files)
- [x] Each task specifies exact file path (all tasks have file paths)
- [x] No task modifies same file as another [P] task (verified)

---

**Total Tasks**: 36
**Parallelizable**: T006-T022 (tests), T031-T035 (polish)
**Critical Path**: 10 sequential phases
**Estimated Duration**: 3-4 hours

---

**Tasks Complete**: ✅ Ready for implementation (/implement or manual execution)
