# Tasks: Environment Validation Layer for MCP Server

**Status**: ✅ COMPLETE - All 14 tasks executed successfully (commit a4e3a6f)
**Input**: Design documents from `/Users/richarddrew/working/assitant-to-agentic/practice-files/assisted-ai-practice/specs/005-env-validation-i/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   ✅ Tech stack: Python 3.11+, fastmcp>=2.0.0, pytest
   ✅ Structure: Single project (extend stdio-mcp-server)
2. Load design documents:
   ✅ data-model.md: VALID_ENVIRONMENTS constant, validate_environment() function
   ✅ contracts/: validation.schema.json (7 test cases)
   ✅ research.md: Centralized module approach, ValueError→MCP error response
   ✅ quickstart.md: 6 integration scenarios
3. Generate tasks by category:
   ✅ Setup: Create validation.py module (T001)
   ✅ Tests: 7 unit tests for validation function (T002-T008)
   ✅ Core: Implement validate_environment() (T009)
   ✅ Integration: Update 2 tools to use validation (T010-T011)
   ✅ Polish: Run tests, update docs, commit (T012-T014)
4. Apply task rules:
   ✅ Test files = [P] (parallel)
   ✅ server.py = sequential (same file, T010 → T011)
   ✅ TDD: Tests before implementation (T002-T008 → T009)
5. Number tasks sequentially (T001-T014)
6. Dependencies: Tests → Implementation → Integration → Validation
7. Parallel execution: T002-T008 (can run tests in parallel)
8. Validation:
   ✅ All contracts have tests (validation.schema.json → T002-T008)
   ✅ All scenarios have tests (quickstart.md → T002-T008)
   ✅ TDD approach enforced
```

---

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
Single project structure (extending existing MCP server):
- Implementation: `module5/stdio-mcp-server/src/`
- Tests: `module5/stdio-mcp-server/tests/`

## Phase 1: Setup
**Status**: ⏳ Ready to execute

- [x] **T001** Create validation module with VALID_ENVIRONMENTS constant in `module5/stdio-mcp-server/src/validation.py`
  - **Action**: Create new file `validation.py` in src/ directory
  - **Contents**:
    - Module docstring explaining validation layer purpose
    - VALID_ENVIRONMENTS constant: `{"dev", "staging", "uat", "prod"}` (frozen set)
    - Import statements: `from typing import Optional` (for type hints)
    - Placeholder for validate_environment() function (to be implemented in T009)
  - **Success Criteria**: File exists, constant defined, imports correct
  - **Dependencies**: None (first task)

## Phase 2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE PHASE 3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] **T002** [P] Write test: Valid environment (lowercase) in `module5/stdio-mcp-server/tests/test_validation.py`
  - Test: `validate_environment("prod")` → returns "prod"
  - **Contract**: validation.schema.json test case 1
  - **Pattern**: pytest with type checking
  - **Expected**: Test FAILS (function not implemented yet)

- [x] **T003** [P] Write test: Valid environment (uppercase, case-insensitive) in `module5/stdio-mcp-server/tests/test_validation.py`
  - Test: `validate_environment("PROD")` → returns "prod" (normalized to lowercase)
  - **Contract**: validation.schema.json test case 2
  - **Validates**: FR-002 (case-insensitive matching), FR-003 (normalize to lowercase)
  - **Expected**: Test FAILS (function not implemented yet)

- [x] **T004** [P] Write test: Valid environment with whitespace in `module5/stdio-mcp-server/tests/test_validation.py`
  - Test: `validate_environment(" staging ")` → returns "staging" (trimmed & normalized)
  - **Contract**: validation.schema.json test case 3
  - **Validates**: FR-008 (trim whitespace), clarification #4
  - **Expected**: Test FAILS (function not implemented yet)

- [x] **T005** [P] Write test: Invalid environment name in `module5/stdio-mcp-server/tests/test_validation.py`
  - Test: `validate_environment("production")` → raises ValueError with message "Invalid environment: production. Must be one of: dev, prod, staging, uat"
  - **Contract**: validation.schema.json test case 4
  - **Validates**: FR-004 (reject invalid), FR-005 (list valid options), FR-011 (structured error message)
  - **Expected**: Test FAILS (function not implemented yet)

- [x] **T006** [P] Write test: Invalid environment "test" in `module5/stdio-mcp-server/tests/test_validation.py`
  - Test: `validate_environment("test")` → raises ValueError
  - **Contract**: validation.schema.json test case 5
  - **Validates**: FR-004 (reject invalid)
  - **Expected**: Test FAILS (function not implemented yet)

- [x] **T007** [P] Write test: None environment (all environments) in `module5/stdio-mcp-server/tests/test_validation.py`
  - Test: `validate_environment(None)` → returns None (valid, represents "all environments")
  - **Contract**: validation.schema.json test case 6
  - **Validates**: Clarification #5 (None = all environments)
  - **Expected**: Test FAILS (function not implemented yet)

- [x] **T008** [P] Write test: Empty string after trimming in `module5/stdio-mcp-server/tests/test_validation.py`
  - Test: `validate_environment("")` → raises ValueError("Environment cannot be empty")
  - Test: `validate_environment("   ")` → raises ValueError("Environment cannot be empty") (whitespace-only)
  - **Contract**: validation.schema.json test case 7
  - **Validates**: FR-008 (reject empty after trim)
  - **Expected**: Test FAILS (function not implemented yet)

**Verification Checkpoint**: Run `cd module5/stdio-mcp-server && uv run pytest tests/test_validation.py` → All 7 tests should FAIL

## Phase 3: Core Implementation (ONLY after T002-T008 tests are failing)

- [x] **T009** Implement validate_environment() function in `module5/stdio-mcp-server/src/validation.py`
  - **Location**: Add function after VALID_ENVIRONMENTS constant
  - **Signature**: `def validate_environment(env: str | None) -> str | None:`
  - **Implementation**:
    ```python
    def validate_environment(env: str | None) -> str | None:
        """Validate and normalize environment name.

        Args:
            env: Environment name (case-insensitive) or None for "all environments"

        Returns:
            Normalized environment name (lowercase) or None if input was None

        Raises:
            ValueError: If env is invalid (not in VALID_ENVIRONMENTS after normalization)
        """
        # Handle None (special case - "all environments")
        if env is None:
            return None

        # Trim whitespace (per clarification #4)
        env_trimmed = env.strip()

        # Check empty after trimming
        if not env_trimmed:
            raise ValueError("Environment cannot be empty")

        # Normalize to lowercase
        env_lower = env_trimmed.lower()

        # Validate against allowed set
        if env_lower not in VALID_ENVIRONMENTS:
            valid_options = ", ".join(sorted(VALID_ENVIRONMENTS))
            raise ValueError(
                f"Invalid environment: {env}. Must be one of: {valid_options}"
            )

        return env_lower
    ```
  - **Type Hints**: Complete type annotations on function signature
  - **Docstring**: Include Args, Returns, Raises sections
  - **Logging**: Add `logger.warning()` for validation failures (logs to stderr)
  - **Expected**: Makes T002-T008 tests PASS
  - **Dependencies**: T002-T008 must be failing first (TDD principle)

**Verification Checkpoint**: Run `cd module5/stdio-mcp-server && uv run pytest tests/test_validation.py` → All 7 tests should PASS

## Phase 4: Integration into Existing Tools

- [x] **T010** Integrate validation into check_health tool in `module5/stdio-mcp-server/src/server.py`
  - **Location**: check_health function (around line 439)
  - **Changes**:
    1. Add import: `from .validation import validate_environment` (top of file)
    2. Replace inline validation (lines 440-447) with: `env_lower = validate_environment(env)`
    3. Remove old validation code (if env is not None block)
  - **Before** (6 lines):
    ```python
    if env is not None:
        env_lower = env.lower()
        if env_lower not in ["prod", "staging", "uat", "dev"]:
            raise ValueError(f"Invalid environment: {env}. Must be one of: prod, staging, uat, dev")
    else:
        env_lower = None
    ```
  - **After** (1 line):
    ```python
    env_lower = validate_environment(env)
    ```
  - **Testing**: Existing `test_check_health.py` tests should still pass
  - **Dependencies**: T009 must be complete (validation function must exist)

- [x] **T011** Integrate validation into get_deployment_status tool in `module5/stdio-mcp-server/src/server.py`
  - **Location**: get_deployment_status function (around line 280)
  - **Changes**: Same transformation as T010
    1. Import already added in T010
    2. Replace inline env validation with: `env_lower = validate_environment(env)`
    3. Keep app parameter validation as-is (different validation rules)
  - **Testing**: Existing `test_devops_tools.py` tests should still pass (env validation)
  - **Dependencies**: T010 must be complete (sequential edits to same file)

**Note**: list_releases tool does NOT need integration (no env parameter)

## Phase 5: Polish & Validation

- [x] **T012** [P] Run full test suite via `cd module5/stdio-mcp-server && uv run pytest tests/`
  - All tests in `tests/` must pass
  - Includes: test_validation.py (7 new), test_check_health.py, test_devops_tools.py (updated)
  - Existing tests (test_initialize.py, test_error_handling.py, test_ping_tool.py) still pass
  - **Success Criteria**: 100% pass rate, 0 failures
  - **Expected**: ~65 tests passing (58 existing + 7 new validation tests)

- [x] **T013** [P] Update CLAUDE.md to document Feature 001 in `module5/CLAUDE.md`
  - **Location**: "Recent Changes" section (top of file, before Feature 004)
  - **Add Entry**:
    ```markdown
    1. **Feature 005-env-validation-i implemented** (2025-10-05): Environment validation layer - centralized validation for environment names (dev, staging, uat, prod) with defense-in-depth security, <10ms validation overhead, 7 unit tests added
    ```
  - **Pattern**: Follow existing feature entries format
  - **Result**: CLAUDE.md updated with Feature 001

- [x] **T014** Commit implementation with conventional commit message
  - **Command**:
    ```bash
    cd module5 && git add stdio-mcp-server/src/validation.py stdio-mcp-server/tests/test_validation.py stdio-mcp-server/src/server.py CLAUDE.md
    ```
  - **Message** (use heredoc for formatting):
    ```bash
    git commit -m "$(cat <<'EOF'
    feat: add environment validation layer for defense-in-depth security

    Add centralized validation module for environment name validation across
    all MCP tools. Validates against hardcoded set (dev, staging, uat, prod)
    with automatic whitespace trimming and case-insensitive matching.

    Implementation:
    - validation.py: VALID_ENVIRONMENTS constant + validate_environment() function
    - Integrated into check_health and get_deployment_status tools
    - Replaces inline validation (6 lines → 1 line per tool)

    Benefits:
    - Defense-in-depth: Validation before CLI execution
    - Performance: <0.01ms overhead (vs ~30s CLI timeout for invalid inputs)
    - Maintainability: Single source of truth (DRY principle)
    - Security: Hardcoded whitelist prevents injection attacks

    Tests:
    - 7 unit tests covering all scenarios (valid, invalid, None, empty, whitespace)
    - All existing tool tests pass (check_health, get_deployment_status)
    - Total: ~65 tests passing

    🤖 Generated with [Claude Code](https://claude.com/claude-code)

    Co-Authored-By: Claude <noreply@anthropic.com>
    EOF
    )"
    ```
  - **Validation**: Commit represents working, tested state
  - **Dependencies**: T012 must pass (all tests passing before commit)

## Parallel Execution Examples

### Tests (Can Run in Parallel)
```bash
# T002-T008: All validation tests can be written concurrently
# Each test is independent, tests different scenarios
```

These tasks are marked [P] and can run in parallel:
- T002, T003, T004, T005, T006, T007, T008 (validation tests)
- T012, T013 (polish tasks - different files)

### Sequential Tasks (MUST Run in Order)
```bash
# T001 → T002-T008 → T009 → T010 → T011 → T012-T014
```

**Critical Dependencies**:
- T001 must complete before T002-T008 (need validation.py file to exist)
- T002-T008 must ALL FAIL before T009 (TDD principle)
- T009 must complete before T010 (need working validate_environment())
- T010 must complete before T011 (same file, sequential edits)
- T012 must pass before T014 (commit only working code)

## Task Summary

**Total Tasks**: 14
- Setup: 1 (T001)
- Tests (TDD): 7 (T002-T008) [P]
- Implementation: 1 (T009)
- Integration: 2 (T010-T011)
- Polish: 3 (T012-T014)

**Parallelizable**: 9 tasks marked [P]
**Sequential**: 5 tasks (T001, T009, T010, T011, T014)

**Test Coverage**:
- Unit tests: 7 (validation function)
- Integration tests: Existing tool tests verify integration
- Total new tests: 7

**Files Modified**:
- Created: `src/validation.py`, `tests/test_validation.py`
- Modified: `src/server.py` (2 tools), `CLAUDE.md`

---

## Execution Checklist

Before starting implementation:
- [x] Design documents reviewed (plan.md, data-model.md, contracts/, quickstart.md)
- [x] Constitution compliance verified (all 8 principles)
- [x] TDD approach understood (tests fail → implement → tests pass)
- [x] Task dependencies clear (T001 → T002-T008 → T009 → T010 → T011 → T012-T014)

During implementation:
- [ ] T001: validation.py created with VALID_ENVIRONMENTS
- [ ] T002-T008: All 7 tests written and FAILING
- [ ] T009: validate_environment() implemented, tests PASSING
- [ ] T010-T011: Integration complete, existing tests passing
- [ ] T012: Full test suite passing (~65 tests)
- [ ] T013: CLAUDE.md updated
- [ ] T014: Conventional commit created

**Success Signal**: All 14 tasks complete, 100% test pass rate, working commit created

---
*Tasks ready for execution - Follow TDD: Write failing tests (T002-T008) → Implement (T009) → Integrate (T010-T011) → Validate (T012-T014)*
