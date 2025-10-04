# Implementation Plan: Add Ping Tool to MCP Server

**Branch**: `002-add-a-simple` | **Date**: 2025-10-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `module5/specs/002-add-a-simple/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path ✅
   → Found at module5/specs/002-add-a-simple/spec.md
2. Fill Technical Context ✅
   → No NEEDS CLARIFICATION markers in spec
   → Project Type: Single (MCP server application)
3. Fill Constitution Check section ✅
   → Based on constitution.md v1.2.0
4. Evaluate Constitution Check section ✅
   → All gates PASS
   → No violations, no complexity justification needed
5. Execute Phase 0 → research.md ✅
   → Completed: FastMCP patterns, validation, testing strategy
6. Execute Phase 1 → contracts, data-model.md, quickstart.md ✅
   → Completed: All Phase 1 artifacts generated
7. Re-evaluate Constitution Check section ✅
   → Still PASS, no new violations
8. Plan Phase 2 → Describe task generation approach ✅
   → See Phase 2 section below
9. STOP - Ready for /tasks command ✅
```

## Summary

Add a simple "ping" tool to the MCP server for connectivity testing. The tool accepts a string message parameter and returns "Pong: {message}" to verify the server is responsive and handling messages correctly. Implementation uses FastMCP's decorator-based tool registration with automatic schema validation.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: fastmcp>=2.0.0
**Storage**: N/A (stateless operation)
**Testing**: pytest with pytest-asyncio
**Target Platform**: Linux/macOS server (STDIO transport)
**Project Type**: Single (MCP server)
**Performance Goals**: <10ms response time (simple string operation)
**Constraints**: Must follow MCP protocol, maintain STDIO separation
**Scale/Scope**: 1 new tool, ~10 lines of code, 5 test cases

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I - Simplicity First**: ✅ PASS
- Minimal implementation: Single function with decorator
- No unnecessary features
- Clear, straightforward logic

**Principle II - Explicit Over Implicit**: ✅ PASS
- Type hints make parameter types explicit
- FastMCP provides explicit error responses
- No silent failures

**Principle III - Type Safety & Documentation**: ✅ PASS
- Type hint on function signature: `async def ping(message: str) -> str`
- Docstring explains purpose and parameters
- Logging already configured in server

**Principle IV - Human-in-the-Loop**: ✅ PASS
- Plan created for human review before implementation
- Incremental implementation (research → design → tasks → code)
- Small, testable unit

**Principle V - Standard Libraries & Stable Dependencies**: ✅ PASS
- Uses existing fastmcp>=2.0.0 dependency
- No new dependencies required
- Python string formatting (standard library)

**Principle VI - MCP Protocol Compliance**: ✅ PASS
- Tool registered via MCP protocol
- No stdout pollution (tool returns string value)
- Follows FastMCP patterns

**Principle VII - Commit Discipline**: ✅ PASS
- Will commit after feature complete
- Commit message: "feat: add ping tool for connectivity testing"
- Working state (tests pass before commit)

**Principle VIII - Automation via Make**: ✅ PASS
- Uses existing make commands (make test, make dev)
- No new make targets required

**Overall**: ✅ ALL GATES PASS - Proceed to implementation

## Project Structure

### Documentation (this feature)
```
module5/specs/002-add-a-simple/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Research findings
├── data-model.md        # Data model (PingRequest/PingResponse)
├── quickstart.md        # Test scenarios
├── contracts/           # Tool contracts
│   └── ping-tool.json   # Ping tool schema and examples
└── tasks.md             # Task list (created by /tasks command)
```

### Source Code (repository root: module5/)
```
stdio-mcp-server/
├── src/
│   ├── __init__.py
│   └── server.py        # Add ping tool here
├── tests/
│   ├── test_initialize.py
│   ├── test_error_handling.py
│   ├── test_shutdown.py
│   └── test_ping_tool.py    # NEW: Ping tool tests
├── pyproject.toml
└── README.md            # Update with ping tool documentation
```

**Structure Decision**: Single project structure (Option 1). This is a single MCP server application with tools, no separate frontend/backend or mobile components.

## Phase 0: Outline & Research

**Status**: ✅ COMPLETE

See [research.md](./research.md) for full details.

**Key Decisions**:
1. **Tool Registration**: Use `@mcp.tool()` decorator (FastMCP pattern)
2. **Validation**: Type hints only (FastMCP auto-validation)
3. **Testing**: Contract tests + unit tests
4. **Error Handling**: FastMCP built-in (no custom code needed)

**Unknowns Resolved**:
- ✅ How to register tools with FastMCP: decorator-based
- ✅ How to validate parameters: type hints + FastMCP
- ✅ Error handling approach: automatic JSON-RPC errors
- ✅ Testing strategy: pytest with contract and unit tests

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE

### Generated Artifacts:

1. **[data-model.md](./data-model.md)**:
   - PingRequest entity (single string parameter)
   - PingResponse format specification
   - Validation rules documented

2. **[contracts/ping-tool.json](./contracts/ping-tool.json)**:
   - Tool schema definition
   - 4 success examples
   - 2 error case examples
   - JSON-RPC error codes

3. **[quickstart.md](./quickstart.md)**:
   - 5 test scenarios (4 success, 2 error)
   - Manual testing steps with MCP Inspector
   - Automated test commands
   - Verification checklist

### Implementation Approach:

**File**: `stdio-mcp-server/src/server.py`

**Code to Add** (~10 lines):
```python
@mcp.tool()
async def ping(message: str) -> str:
    """
    Test connectivity by echoing back a message.

    Args:
        message: The message to echo back

    Returns:
        A pong response with the echoed message
    """
    logger.debug(f"Ping received: {message}")
    return f"Pong: {message}"
```

**Location**: Add after line ~56 (after FastMCP instance creation, before `if __name__ == "__main__"`)

### Test File to Create:

**File**: `stdio-mcp-server/tests/test_ping_tool.py`

**Test Cases**:
1. `test_ping_basic` - Verify "test" → "Pong: test"
2. `test_ping_empty` - Verify "" → "Pong: "
3. `test_ping_special_chars` - Verify Unicode preservation
4. `test_ping_whitespace` - Verify whitespace preservation
5. `test_ping_tool_discovery` - Verify tool appears in capabilities

## Phase 2: Task Planning Approach

**Task Generation Strategy**:
1. Load `.specify/templates/tasks-template.md` as base
2. Generate tasks from Phase 1 artifacts:
   - Contract test tasks from contracts/ping-tool.json
   - Implementation task from data-model.md
   - Integration test tasks from quickstart.md
3. Follow TDD order: tests first, then implementation

**Ordering Strategy**:
- Create test file with failing tests
- Implement ping tool to make tests pass
- Update documentation
- Manual verification with MCP Inspector

**Estimated Tasks**: ~8-10 tasks

| Task | Type | Parallelizable | Estimated Time |
|------|------|----------------|----------------|
| Create test file structure | Setup | No | 2 min |
| Write contract tests | Test | [P] | 5 min |
| Write unit tests | Test | [P] | 5 min |
| Implement ping tool | Code | No | 3 min |
| Run tests (verify pass) | Validation | No | 1 min |
| Update README | Docs | [P] | 3 min |
| Manual test with Inspector | Validation | No | 5 min |
| Commit changes | VCS | No | 1 min |

**Total Estimated Time**: 25 minutes

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md)

## Complexity Tracking

*No violations - this section is empty*

The implementation requires no complexity justifications. It follows all constitutional principles without deviation.

## Progress Tracking

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none required)

---
*Based on Constitution v1.2.0 - See `.specify/memory/constitution.md`*
