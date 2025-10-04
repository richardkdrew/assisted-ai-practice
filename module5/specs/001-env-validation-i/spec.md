# Feature Specification: Environment Validation Layer for MCP Server

**Feature Branch**: `001-env-validation-i`
**Created**: 2025-10-05
**Status**: ✅ IMPLEMENTED - Feature complete, all tests passing (commit a4e3a6f)
**Input**: User description: "I want to add some input validation to my MCP server for better user experience and defense-in-depth security. Let's focus on environment name validation as a key pattern: 1. Validate environment names against known environments (dev, staging, prod, etc.) before calling the CLI 2. Provide immediate feedback without subprocess overhead 3. Show how MCP validation differs from CLI validation. This demonstrates validation at the MCP layer while the CLI handles comprehensive business logic validation."

## Clarifications

### Session 2025-10-05
- Q: What is the definitive list of valid environment names for validation? → A: Use existing list: dev, staging, uat, prod (4 environments)
- Q: Should validation rules be hardcoded constants or configurable? → A: Hardcoded constants in code (simple, secure, no configuration files)
- Q: When validation fails, how should errors be returned? → A: Return MCP error response objects (structured protocol responses)
- Q: Should validation handle whitespace in environment names? → A: Trim whitespace automatically (e.g., " prod " becomes "prod") then validate
- Q: How should None/null environment parameters be handled? → A: Treat None as "all environments" (check health for all, same as current behavior)

## Execution Flow (main)
```
1. Parse user description from Input
   � Feature requests input validation layer for MCP server
2. Extract key concepts from description
   � Actors: MCP server, CLI tools, API consumers
   � Actions: validate inputs, provide feedback, prevent invalid calls
   � Data: environment names, validation rules
   � Constraints: defense-in-depth, immediate feedback, no subprocess overhead
3. Identify clarification needs:
   � Valid environment list (centralized source of truth?)
   � Validation configuration approach (hardcoded vs. configurable)
   � Error handling strategy (exceptions vs. error responses)
   � Scope of validation (env only or broader pattern?)
   � Extensibility requirements (future validators?)
4. Fill User Scenarios & Testing section
   � User provides valid env � passes validation, calls CLI
   � User provides invalid env � immediate error, no CLI call
   � User provides case-variant env � normalized and validated
5. Generate Functional Requirements
   � Each requirement testable against validation behavior
6. Identify Key Entities
   � Validator (validation logic)
   � ValidationRule (environment constraints)
   � ValidationError (structured error information)
7. Run Review Checklist
   � Critical ambiguities marked for clarification
8. Return: PENDING CLARIFICATION (5 questions outstanding)
```

---

## � Quick Guidelines
-  Focus on WHAT users need and WHY
- L Avoid HOW to implement (no tech stack, APIs, code structure)
- =e Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As an MCP API consumer, I need immediate validation feedback on input parameters (especially environment names), so that I can correct errors quickly without incurring subprocess overhead or waiting for CLI execution to fail.

### Acceptance Scenarios

#### Environment Validation - Valid Inputs
1. **Given** I call a tool with env="prod", **When** the MCP server validates the input, **Then** validation passes and the CLI is invoked with the environment parameter
2. **Given** I call a tool with env="staging", **When** the MCP server validates the input, **Then** validation passes and the CLI is invoked
3. **Given** I call a tool with env="PROD" (uppercase), **When** the MCP server validates the input, **Then** validation normalizes to lowercase, passes, and the CLI is invoked with "prod"
4. **Given** I call a tool with env="Dev" (mixed case), **When** the MCP server validates the input, **Then** validation normalizes to lowercase, passes, and the CLI is invoked with "dev"

#### Environment Validation - Invalid Inputs
1. **Given** I call a tool with env="production", **When** the MCP server validates the input, **Then** validation fails immediately with a clear error message listing valid environments (no CLI call made)
2. **Given** I call a tool with env="test", **When** the MCP server validates the input, **Then** validation fails immediately with error message (no CLI call made)
3. **Given** I call a tool with env="", **When** the MCP server validates the input, **Then** validation fails with error indicating environment cannot be empty (no CLI call made)
4. **Given** I call a tool with env containing special characters (e.g., "prod; rm -rf"), **When** the MCP server validates the input, **Then** validation fails immediately preventing potential injection (no CLI call made)

#### Performance & User Experience
1. **Given** I provide an invalid environment name, **When** validation executes, **Then** I receive an error response in <10ms without subprocess overhead
2. **Given** I provide a valid environment name, **When** validation executes, **Then** validation adds negligible overhead (<1ms) before CLI invocation
3. **Given** validation fails, **When** I receive the error response, **Then** the error message clearly indicates: (a) which parameter failed, (b) the invalid value provided, (c) the list of valid options

#### Defense-in-Depth Pattern
1. **Given** the MCP validation layer passes an environment, **When** the CLI tool also validates the same parameter, **Then** both validations should agree on valid values (no inconsistency)
2. **Given** the CLI validation rules change, **When** I update the system, **Then** the MCP validation rules should be easily synchronized to match
3. **Given** an attacker attempts shell injection via env parameter, **When** MCP validation runs, **Then** the malicious input is rejected before reaching subprocess execution

### Edge Cases
- What happens when env parameter is None/null? → None is treated as "all environments" (passes validation, CLI receives no env parameter)
- What happens when validation rules are out of sync with CLI? → Manual code review required; both layers must be updated together
- What happens during concurrent validation requests? → Validation should be stateless; no shared mutable state
- What happens when a new environment is added to the infrastructure? → Hardcoded constant must be updated in code (requires deployment)
- What happens with whitespace in env values (e.g., " prod ")? → Whitespace is automatically trimmed before validation

## Requirements *(mandatory)*

### Functional Requirements

#### Input Validation (FR-001 to FR-010)
**FR-001**: The system MUST validate environment names against a predefined list of valid environments before invoking CLI tools
**FR-002**: The system MUST perform case-insensitive matching for environment names (e.g., "PROD", "prod", "Prod" all match "prod")
**FR-003**: The system MUST normalize validated environment names to lowercase before passing to CLI tools
**FR-004**: The system MUST reject environment names not in the valid list with a clear error message
**FR-005**: The system MUST include the list of valid environment options in validation error messages
**FR-006**: The system MUST prevent subprocess execution when validation fails (fail-fast behavior)
**FR-007**: The system MUST validate inputs synchronously without subprocess overhead (<10ms target)
**FR-008**: The system MUST trim leading/trailing whitespace from environment values before validation; empty string after trimming is treated as validation failure
**FR-009**: The system MUST reject environment names containing shell metacharacters or special characters for security
**FR-010**: The system MUST validate environment parameters consistently across all MCP tools (get_deployment_status, check_health, etc.)

#### Error Handling (FR-011 to FR-015)
**FR-011**: When validation fails, the system MUST return an MCP error response object identifying: (a) the parameter name, (b) the invalid value, (c) valid options
**FR-012**: When validation fails, the system MUST NOT execute the subprocess/CLI command
**FR-013**: When validation passes but CLI execution fails, the system MUST distinguish between validation errors and CLI execution errors in responses
**FR-014**: The system MUST log validation failures to stderr with sufficient context for debugging
**FR-015**: The system MUST use consistent MCP error response formatting across all validation failures

#### Defense-in-Depth (FR-016 to FR-020)
**FR-016**: The MCP validation layer MUST validate inputs before CLI validation (defense-in-depth)
**FR-017**: The MCP validation rules MUST align with CLI validation rules to prevent inconsistencies
**FR-018**: When both MCP and CLI validation reject the same input, error messages SHOULD indicate the failure occurred at the MCP layer (faster feedback)
**FR-019**: The validation layer MUST be independent of CLI tool availability (validate even if CLI is not installed)
**FR-020**: The system MUST document the relationship between MCP validation and CLI validation for maintainability

### Non-Functional Requirements

**Performance (NF-001 to NF-003)**
**NF-001**: Input validation MUST complete in <10ms for typical cases (single environment name)
**NF-002**: Validation overhead MUST NOT exceed 5% of total request latency for successful validations
**NF-003**: Validation logic MUST be optimized for low CPU and memory overhead (no regex compilation per request)

**Security (NF-004 to NF-006)**
**NF-004**: Validation MUST prevent shell injection attacks through input sanitization
**NF-005**: Validation rules MUST be defined in code (not user-configurable) to prevent tampering
**NF-006**: The system MUST log all validation failures for security auditing purposes

**Maintainability (NF-007 to NF-010)**
**NF-007**: Validation rules MUST be centralized in a single location to prevent duplication and drift
**NF-008**: The validation layer MUST be easily testable in isolation (unit tests without subprocess dependencies)
**NF-009**: Adding new validation rules MUST require changes in only one place (DRY principle)
**NF-010**: Validation code MUST follow existing constitutional principles (simplicity, explicit error handling, type safety)

## Key Entities *(mandatory)*

### 1. Environment Name
**Description**: A string identifier representing a deployment environment (e.g., "prod", "staging", "uat", "dev")

**Attributes**:
- Value: lowercase string from predefined set
- Case-insensitive matching before normalization
- No special characters or whitespace

**Validation Rules**:
- Leading/trailing whitespace is trimmed before validation
- MUST be one of: dev, staging, uat, prod (after trimming)
- MUST match case-insensitively
- MUST be normalized to lowercase
- MUST NOT contain special characters
- MUST NOT be empty after trimming

**Lifecycle**:
- Provided by MCP API consumer (may be None for "all environments")
- Whitespace trimmed if present
- Validated at MCP layer (None passes validation)
- Normalized to lowercase if not None
- Passed to CLI tool if valid (None results in no env parameter to CLI)
- Rejected before CLI invocation if invalid

### 2. Validation Rule
**Description**: A constraint that defines what constitutes a valid environment name

**Attributes**:
- Valid values: hardcoded set of allowed environment names (dev, staging, uat, prod)
- Normalization function: case-insensitive matching
- Error message template: what to show when validation fails

**Behavior**:
- Applied before CLI invocation
- Returns success (normalized value) or failure (error details)
- Stateless operation (no side effects)

### 3. Validation Error
**Description**: Structured information about why validation failed

**Attributes**:
- Parameter name: which input failed (e.g., "env")
- Invalid value: what the user provided
- Valid options: list of acceptable values
- Error message: human-readable explanation

**Usage**:
- Returned to MCP API consumer as MCP error response object
- Logged to stderr for debugging
- Prevents CLI subprocess execution

## Out of Scope *(optional)*

The following are explicitly NOT part of this feature:

1. **Validation of other parameter types** (e.g., app names, limit values) - This feature focuses on environment validation as a pattern demonstration
2. **Dynamic/configurable validation rules** - Rules are hardcoded for simplicity and security
3. **CLI tool validation changes** - This feature only adds MCP-layer validation; CLI validation remains unchanged
4. **Backward compatibility with invalid inputs** - Previously accepted invalid inputs may now be rejected (breaking change acceptable for security)
5. **Validation rule versioning** - No support for multiple validation rule versions
6. **Custom error message localization** - Error messages in English only

## Success Metrics *(optional)*

### User Experience
- **Validation error response time**: <10ms (vs. ~30s CLI timeout for invalid inputs)
- **Error message clarity**: User can identify and correct error without external documentation

### Security
- **Shell injection prevention**: 100% of injection attempts blocked at validation layer
- **Validation failure audit trail**: All failures logged to stderr with timestamp and context

### Maintainability
- **Test coverage**: e95% code coverage for validation logic
- **Validation rule consistency**: Zero discrepancies between MCP and CLI validation for environment names

## Dependencies & Constraints *(optional)*

### Dependencies
- Existing MCP tools: get_deployment_status, check_health (currently have inline validation)
- Python type system: Type hints for validation functions
- Logging infrastructure: stderr logging for validation failures

### Constraints
- **Constitutional Principle I (Simplicity)**: Validation logic must be minimal and clear
- **Constitutional Principle II (Explicit Error Handling)**: All validation failures must have explicit error messages
- **Constitutional Principle III (Type Safety)**: Validation functions must have complete type hints
- **Constitutional Principle VI (MCP Protocol Compliance)**: Validation errors must not corrupt stdout (use stderr)
- **Performance**: Validation must not add significant latency (<10ms target)
- **Security**: Validation must prevent injection attacks (defense-in-depth)

## Review Checklist *(mandatory)*

Self-assessment before marking spec as complete:

- [x] **User story is clear**: Primary user story describes who, what, and why
- [x] **Scenarios are testable**: Each acceptance scenario can be verified with concrete tests
- [x] **Requirements are unambiguous**: All critical requirements clarified (5 questions resolved)
- [x] **Edge cases are considered**: All edge cases clarified (None handling, whitespace, sync)
- [x] **Out of scope is explicit**: Clear boundaries on what this feature does NOT include
- [x] **No implementation details**: Spec focuses on WHAT and WHY, not HOW
- [x] **Key entities are identified**: Environment Name, Validation Rule, Validation Error
- [x] **Dependencies are listed**: No additional dependencies required beyond existing infrastructure
- [x] **Success is measurable**: Clear metrics for UX, security, and maintainability
- [x] **All ambiguities marked**: All critical ambiguities resolved via clarification session

**Status**: ✅ READY - Specification complete, ready for planning phase

---

*This specification follows the constitutional principles defined in `.specify/memory/constitution.md` and focuses on educational value: demonstrating defense-in-depth validation, user experience optimization, and security best practices at the MCP layer.*
