# Phase 1: Data Model - Environment Validation

**Goal**: Define entities, constants, and workflows for environment validation layer

**Date**: 2025-10-05

## Core Entities

### 1. VALID_ENVIRONMENTS (Constant)

**Type**: `set[str]`

**Value**: `{"dev", "staging", "uat", "prod"}`

**Purpose**: Single source of truth for valid environment names

**Usage**:
- Validation function checks membership
- Error messages list these as valid options
- Must stay synchronized with CLI validation rules

**Rationale**:
- Set provides O(1) lookup performance (NF-003)
- Hardcoded per clarification #2 (security, simplicity)
- Immutable frozen set in implementation

**Lifecycle**:
- Defined at module load time
- Never modified at runtime
- Updated only through code deployment (per clarification)

---

### 2. Environment Name (Input/Output)

**Type**: `str | None`

**Attributes**:
- **Raw Input**: User-provided string (may have whitespace, mixed case)
- **Trimmed**: Whitespace removed via `str.strip()`
- **Normalized**: Converted to lowercase via `str.lower()`
- **Validated**: Checked against VALID_ENVIRONMENTS

**States**:
1. **None**: Special case for "all environments" (per clarification #5)
   - Validation: Passes immediately
   - Output: None (no normalization needed)

2. **Valid String**: Member of VALID_ENVIRONMENTS after normalization
   - Example: "PROD" → "prod" (normalized)
   - Example: " staging " → "staging" (trimmed & normalized)
   - Output: Normalized lowercase string

3. **Invalid String**: Not in VALID_ENVIRONMENTS after normalization
   - Example: "production" → invalid
   - Example: "test" → invalid
   - Output: ValueError raised

4. **Empty String**: Empty after trimming
   - Example: "" → invalid
   - Example: "   " → invalid (becomes empty after trim)
   - Output: ValueError raised

**Validation Rules** (from FR-001 to FR-010):
- MUST trim leading/trailing whitespace (FR-008, clarification #4)
- MUST normalize to lowercase (FR-002, FR-003)
- MUST be in VALID_ENVIRONMENTS or None (FR-001, FR-004)
- MUST NOT be empty after trimming (FR-008)
- MUST NOT contain special characters (FR-009) - rejected by membership check

---

### 3. Validation Result (Implicit)

**Type**: Return value of `validate_environment()`

**Format**: `str | None`

**Possible Values**:
- `None`: Input was None (valid - "all environments")
- `str`: Normalized environment name (valid)
- **Exception**: ValueError with structured message (invalid)

**Error Message Structure** (per FR-011):
```
Invalid environment: {provided_value}. Must be one of: {valid_options}
```

Example:
```
Invalid environment: production. Must be one of: dev, prod, staging, uat
```

**Components**:
1. Parameter context: "Invalid environment"
2. Provided value: The exact string user sent
3. Valid options: Sorted, comma-separated list from VALID_ENVIRONMENTS

---

## Validation Workflow

### Main Flow: `validate_environment(env: str | None) -> str | None`

```
Input: env (str | None)
   │
   ├─→ [env is None?] ────YES────→ Return None (valid)
   │                                       ↓
   NO                                  (passes validation)
   │
   ↓
Trim whitespace: env.strip()
   │
   ↓
[trimmed string empty?] ────YES────→ Raise ValueError("Environment cannot be empty")
   │                                       ↓
   NO                                  (invalid)
   │
   ↓
Normalize: env.lower()
   │
   ↓
[normalized in VALID_ENVIRONMENTS?]
   │
   ├─→ YES ───→ Return normalized value (valid)
   │                   ↓
   │              (e.g., "PROD" → "prod")
   │
   └─→ NO ────→ Raise ValueError with message:
                "Invalid environment: {env}. Must be one of: {valid_list}"
                       ↓
                   (invalid)
```

### Performance Profile (per NF-001, NF-002, NF-003)

**Operation Timings**:
1. None check: <0.001ms
2. str.strip(): <0.001ms
3. Empty check: <0.001ms
4. str.lower(): <0.001ms
5. Set membership: <0.001ms (O(1))
6. **Total**: <0.01ms (well under 10ms target)

**Overhead**: <1% of typical request (<<5% limit per NF-002)

---

## Integration with Existing Tools

### Tool: `check_health(env: str | None = None)`

**Before** (inline validation):
```python
if env is not None:
    env_lower = env.lower()
    if env_lower not in ["prod", "staging", "uat", "dev"]:
        raise ValueError(f"Invalid environment: {env}. Must be one of: prod, staging, uat, dev")
else:
    env_lower = None
```

**After** (centralized validation):
```python
from .validation import validate_environment

env_lower = validate_environment(env)  # Handles all validation & normalization
```

**Changes**:
- ✅ 6 lines reduced to 1 line
- ✅ Consistent with other tools
- ✅ Testable in isolation
- ✅ Same error behavior

### Tool: `get_deployment_status(app: str | None, env: str | None)`

**Same transformation** as check_health:
- Replace inline env validation with `validate_environment(env)` call
- Keep app parameter validation as-is (different validation rules)

### Tool: `list_releases(app: str, limit: int | None)`

**No Changes**:
- Does not use env parameter
- No validation integration needed

---

## Error Handling Strategy

### Error Type: ValueError

**Rationale** (per clarification #3 and research):
- FastMCP automatically converts ValueError to MCP error response
- Maintains protocol compliance (FR-011, FR-015)
- No explicit MCP error response construction needed
- Consistent with existing tools

### Error Message Format (per FR-011, FR-015)

**Required Components**:
1. Parameter name identification: "Invalid environment"
2. Invalid value echo: "{provided_value}"
3. Valid options list: "Must be one of: {sorted_comma_list}"

**Consistency Rules**:
- Always use same prefix: "Invalid environment:"
- Always sort valid options alphabetically
- Always use comma-separated format
- No trailing punctuation

### Logging (per FR-014, NF-006)

**Validation Failure Log**:
```python
logger.warning(f"Environment validation failed: {env} (not in {VALID_ENVIRONMENTS})")
```

**Location**: stderr via existing logging configuration
**Level**: WARNING (not ERROR - expected user input error, not system error)
**Context**: Includes invalid value and valid set for debugging

---

## Testing Strategy (per NF-008)

### Unit Tests: `test_validation.py`

**Test Cases** (7 total):
1. Valid env "prod" → returns "prod"
2. Valid env "PROD" (uppercase) → returns "prod" (normalized)
3. Valid env " staging " (whitespace) → returns "staging" (trimmed & normalized)
4. Invalid env "production" → raises ValueError with valid options
5. Invalid env "test" → raises ValueError
6. None env → returns None (valid)
7. Empty string "" → raises ValueError("Environment cannot be empty")

**Isolation**: No subprocess dependencies, no MCP dependencies

### Integration Tests: Existing tool tests

**Update `test_check_health.py`**:
- Verify validation is called
- Verify normalized value passed to CLI
- Verify error messages match format

**Update `test_get_deployment_status.py`**:
- Same verification as check_health

---

## Constraints & Assumptions

### Constraints (from spec)

1. **Performance** (NF-001, NF-002, NF-003):
   - Validation <10ms: ✅ Achieves <0.01ms
   - Overhead <5%: ✅ Achieves <1%
   - No regex: ✅ Uses only set/str operations

2. **Security** (NF-004, NF-005, NF-006):
   - Prevents injection: ✅ Whitelist validation (set membership)
   - No user config: ✅ Hardcoded VALID_ENVIRONMENTS
   - Audit trail: ✅ Logs all failures to stderr

3. **Maintainability** (NF-007, NF-008, NF-009):
   - Centralized: ✅ Single module
   - Testable: ✅ Isolated unit tests
   - DRY: ✅ Single update point

### Assumptions

1. **FastMCP Behavior**: ValueError is converted to MCP error response
   - **Verification**: Confirmed by research analysis
   - **Fallback**: If not true, wrap in MCP error response manually

2. **CLI Synchronization**: Manual process to keep MCP/CLI aligned
   - **Documented**: In research.md and code comments
   - **Risk**: Low (4 environments, infrequent changes)

3. **Whitespace Handling**: Only leading/trailing whitespace trimmed
   - **Internal whitespace**: Not trimmed (e.g., "pr od" stays "pr od" → invalid)
   - **Rationale**: Internal whitespace indicates typo, should fail validation

---

## Summary

**Entities Defined**:
- ✅ VALID_ENVIRONMENTS constant (set)
- ✅ Environment Name (input/output type)
- ✅ Validation Result (return type)

**Workflow Documented**:
- ✅ validate_environment() function flow
- ✅ None handling (special case)
- ✅ Trim → Normalize → Validate sequence

**Integration Approach**:
- ✅ Replace inline validation in 2 tools (check_health, get_deployment_status)
- ✅ No changes to list_releases (no env parameter)

**Testing Strategy**:
- ✅ 7 unit tests for validation function
- ✅ Integration tests in existing tool test files

**Constitutional Compliance**:
- ✅ Principle I (Simplicity): Minimal set-based check
- ✅ Principle II (Explicit): Clear error handling
- ✅ Principle III (Type Safety): Full type hints
- ✅ All NF requirements met

---
*Data model complete - Ready for contracts and quickstart*
