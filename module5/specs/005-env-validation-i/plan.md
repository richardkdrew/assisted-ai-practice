# Implementation Plan: Environment Validation Layer for MCP Server

**Branch**: `005-env-validation-i` | **Date**: 2025-10-05 | **Status**: ✅ IMPLEMENTED (commit a4e3a6f) | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/Users/richarddrew/working/assitant-to-agentic/practice-files/assisted-ai-practice/specs/005-env-validation-i/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
     Spec loaded successfully
2. Fill Technical Context
     Project Type: single (MCP STDIO server)
     Structure Decision: Extend existing stdio-mcp-server with validation layer
3. Fill Constitution Check section
     Based on Constitution v1.2.0
4. Evaluate Constitution Check section
     No violations - follows all constitutional principles
     Progress Tracking: Initial Constitution Check PASS
5. Execute Phase 0 � research.md
   = Complete
6. Execute Phase 1 � contracts, data-model.md, quickstart.md
   � Complete
7. Re-evaluate Constitution Check section
   � Complete
   � Progress Tracking: Post-Design Constitution Check PASS
8. Plan Phase 2 � Describe task generation approach
   � Complete
9. STOP - Ready for /tasks command
```

## Summary
Add a centralized validation layer for environment name parameters in the MCP server. The validation layer will validate environment names (dev, staging, uat, prod) before CLI execution, providing immediate feedback without subprocess overhead. This implements a defense-in-depth security pattern while improving user experience through faster error responses (<10ms vs ~30s CLI timeout). The validation will be hardcoded for security, use MCP error responses for failures, and automatically trim whitespace while supporting None as "all environments".

## Technical Context
**Language/Version**: Python 3.11+
**Primary Dependencies**: fastmcp>=2.0.0 (existing)
**Storage**: N/A (stateless validation)
**Testing**: pytest, pytest-asyncio (existing)
**Target Platform**: Linux/macOS server (STDIO transport)
**Project Type**: single (MCP server extension)
**Performance Goals**: <10ms validation latency, <1ms overhead for valid inputs
**Constraints**:
- STDIO protocol compliance (stdout reserved for MCP, stderr for logs)
- Hardcoded validation rules (no external configuration)
- MCP error response format (not Python exceptions)
- Must align with CLI validation rules
**Scale/Scope**: 1 validation module, centralized constant, ~150 LOC, integration across 3 existing tools

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Simplicity First 
- Minimal addition: Single validation function with hardcoded constant
- Reuses existing tool structure (no new frameworks)
- No new dependencies required
- Simple set membership check with string normalization
- Rationale: Per NF-005, hardcoded rules prevent tampering and keep implementation minimal

### Principle II: Explicit Over Implicit 
- Explicit error handling for all validation failures (FR-011, FR-014, FR-015)
- Clear validation of all inputs before subprocess (FR-001, FR-006)
- No silent failures - all errors logged and returned as MCP error responses
- Explicit None handling (treat as "all environments" per clarification)
- Rationale: Per FR-012, validation failures must explicitly prevent CLI execution

### Principle III: Type Safety & Documentation 
- Type hints required for validation functions (NF-010)
- Structured logging to stderr for validation failures (FR-014, NF-006)
- Follows existing logging patterns from current tools
- Rationale: Per clarifications, validation must be testable in isolation with clear types

### Principle IV: Human-in-the-Loop Development 
- Implementation planned incrementally (research � design � implementation)
- Test-driven approach (validation tests before implementation)
- Clear checkpoints for review after each phase
- Rationale: Validation layer affects all existing tools - careful incremental approach required

### Principle V: Standard Libraries & Stable Dependencies 
- No new external dependencies
- Uses Python standard library (set, str.lower(), str.strip())
- Reuses existing fastmcp framework for error responses
- Rationale: Per NF-003, validation must be low overhead (no regex compilation)

### Principle VI: MCP Protocol Compliance 
- STDIO transport maintained
- No stdout pollution (logs to stderr only per FR-014)
- MCP error response objects for validation failures (per clarification #3)
- Rationale: Per FR-015, consistent MCP error response formatting required

### Principle VII: Commit Discipline 
- Will commit after validation module implementation
- Will commit after tool integration
- Conventional commit format
- Each commit represents working state
- Rationale: Defense-in-depth pattern requires careful rollout

### Principle VIII: Automation via Make 
- Uses existing `make test` for pytest (validation unit tests)
- Uses existing `make dev` for FastMCP inspector (manual validation)
- No direct command execution
- Rationale: Per constitution, all tasks via make commands

**Initial Gate Status**:  PASS

## Project Structure

### Documentation (this feature)
```
specs/005-env-validation-i/
   spec.md              # Feature specification (complete, clarified)
   plan.md              # This file (/plan command output)
   research.md          # Phase 0 output (/plan command)
   data-model.md        # Phase 1 output (/plan command)
   contracts/           # Phase 1 output (/plan command)
      validation.schema.json  # Validation function contract
   quickstart.md        # Phase 1 output (/plan command)
   tasks.md             # Phase 2 output (/tasks command)
```

### Implementation (single project - extending existing MCP server)
```
module5/stdio-mcp-server/
   src/
      server.py                    # Main server (will import validation)
      validation.py                # NEW: Validation layer module
   tests/
      test_validation.py           # NEW: Validation layer tests
      test_get_deployment_status.py  # UPDATED: Use validation layer
      test_check_health.py         # UPDATED: Use validation layer
```

**Decision Rationale**:
- Centralized validation module allows DRY principle (NF-007, NF-009)
- Separate file for testability in isolation (NF-008)
- Integration via imports maintains simplicity
- Existing tests updated to verify validation integration

## Phase 0: Research

**Goal**: Analyze existing validation patterns and determine integration approach

**Deliverable**: `research.md` containing:
1. Current validation implementation analysis (get_deployment_status, check_health)
2. Validation placement decision (inline vs. centralized module)
3. Error handling pattern analysis (current: ValueError, target: MCP error responses)
4. Performance baseline (current inline validation timing)
5. Integration approach recommendation

**Key Questions**:
- Where is env validation currently implemented? (Expected: inline in each tool)
- How do current tools handle validation errors? (Expected: raise ValueError)
- How can we convert ValueError to MCP error responses? (Research FastMCP error handling)
- What's the performance of current inline validation? (Benchmark to ensure <1ms addition)

**Output Location**: `/Users/richarddrew/working/assitant-to-agentic/practice-files/assisted-ai-practice/specs/005-env-validation-i/research.md`

**Success Criteria**:
- [x] Documented current validation locations
- [x] Documented current error handling patterns
- [x] Recommended integration approach (centralized module)
- [x] Performance baseline established

## Phase 1: Design

**Goal**: Design validation layer architecture, data model, and contracts

### Artifact 1: Data Model (`data-model.md`)
Defines:
- ValidationResult entity (success/failure with details)
- VALID_ENVIRONMENTS constant (["dev", "staging", "uat", "prod"])
- Validation workflow (input � trim � lowercase � check � return)
- Error structure (parameter name, invalid value, valid options)

### Artifact 2: Contracts (`contracts/validation.schema.json`)
Defines validation function contract:
```json
{
  "function": "validate_environment",
  "input": {
    "env": "string | None"
  },
  "output": {
    "valid": "boolean",
    "normalized_value": "string | None",
    "error": "MCPErrorResponse | None"
  }
}
```

### Artifact 3: Integration Scenarios (`quickstart.md`)
6 test scenarios:
1. Valid env "prod" � normalized to "prod", passes
2. Valid env "PROD" � normalized to "prod", passes
3. Valid env " prod " � trimmed & normalized, passes
4. Invalid env "production" � MCP error response, no CLI call
5. None env � passes (treated as "all environments")
6. Empty string "" � MCP error response after trimming

**Output Locations**:
- `/Users/richarddrew/working/assitant-to-agentic/practice-files/assisted-ai-practice/specs/005-env-validation-i/data-model.md`
- `/Users/richarddrew/working/assitant-to-agentic/practice-files/assisted-ai-practice/specs/005-env-validation-i/contracts/validation.schema.json`
- `/Users/richarddrew/working/assitant-to-agentic/practice-files/assisted-ai-practice/specs/005-env-validation-i/quickstart.md`

**Success Criteria**:
- [ ] VALID_ENVIRONMENTS constant defined
- [ ] Validation workflow documented
- [ ] Function contract specified
- [ ] 6 integration scenarios defined
- [ ] All scenarios map to functional requirements

## Phase 2: Task Planning

**Goal**: Generate dependency-ordered implementation tasks following TDD

**Approach**:
1. Setup tasks: Create validation.py module structure
2. Test tasks (TDD): Write failing tests for validation function
3. Implementation tasks: Implement validation to make tests pass
4. Integration tasks: Update existing tools to use validation layer
5. Validation tasks: Run full test suite, update documentation

**Expected Task Categories**:
- T001: Create validation.py with VALID_ENVIRONMENTS constant
- T002-T008: Write validation tests (7 tests for 6 scenarios + edge cases)
- T009: Implement validate_environment function
- T010-T012: Integrate validation into get_deployment_status, check_health, list_releases
- T013: Run full test suite
- T014: Update CLAUDE.md
- T015: Commit with conventional format

**Output Location**: `/Users/richarddrew/working/assitant-to-agentic/practice-files/assisted-ai-practice/specs/005-env-validation-i/tasks.md`

**Success Criteria**:
- [ ] Tasks follow TDD approach (tests before implementation)
- [ ] Clear dependencies identified (T002-T008 must fail before T009)
- [ ] Integration tasks ordered properly (T009 complete before T010-T012)
- [ ] All tasks mapped to functional requirements
- [ ] Commit discipline maintained (T015 after completion)

## Progress Tracking

### Phase 0: Research 
- [x] Initial Constitution Check: PASS
- [x] Feature specification loaded and analyzed
- [x] Clarifications validated (5 questions resolved)
- [x] Ready to execute research phase

### Phase 1: Design ✅
- [x] Post-Design Constitution Check: PASS (no violations introduced)
- [x] Data model defined: data-model.md created
- [x] Contracts defined: contracts/validation.schema.json created
- [x] Integration scenarios defined: quickstart.md with 6 scenarios

### Phase 2: Task Planning ✅
- [x] Task approach documented in plan.md
- [x] Expected task categories outlined (T001-T015)
- [x] Dependencies identified (TDD: tests before implementation)

### Completion ✅
- [x] All Phase 0 and Phase 1 artifacts generated
- [x] No ERROR states in execution
- [x] Ready for /tasks command

## Next Steps

1. **Execute Phase 0**: Generate research.md
2. **Execute Phase 1**: Generate data-model.md, contracts/, quickstart.md
3. **Re-evaluate Constitution**: Verify design maintains compliance
4. **Execute Phase 2**: Describe task generation approach in tasks.md
5. **Stop**: Ready for /tasks command to generate implementation tasks

---
*Based on Constitution v1.2.0 - See `module5/.specify/memory/constitution.md`*
*Clarifications completed: 2025-10-05 (5 questions resolved)*
