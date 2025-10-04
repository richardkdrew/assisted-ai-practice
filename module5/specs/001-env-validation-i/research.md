# Phase 0: Research - Environment Validation Patterns

**Goal**: Analyze existing validation patterns and determine integration approach for centralized validation layer

**Date**: 2025-10-05

## Current Validation Implementation Analysis

### Location 1: `check_health` tool (server.py:439-447)
```python
# Validate env parameter (optional, case-insensitive)
if env is not None:
    env_lower = env.lower()
    if env_lower not in ["prod", "staging", "uat", "dev"]:
        raise ValueError(
            f"Invalid environment: {env}. Must be one of: prod, staging, uat, dev"
        )
else:
    env_lower = None
```

**Pattern**: Inline validation with hardcoded list check

### Location 2: `get_deployment_status` tool (server.py:~280-290)
**Pattern**: Similar inline validation (expected based on Feature 003)

### Location 3: `list_releases` tool (server.py:~380-390)
**Pattern**: Does NOT validate env (only validates app and limit parameters)

## Current Error Handling Pattern

**Method**: `raise ValueError(message)`
- ValueError propagates to FastMCP framework
- FastMCP converts to MCP error response automatically
- Error message includes parameter name and valid options

**Example Error**:
```
ValueError: Invalid environment: production. Must be one of: prod, staging, uat, dev
```

## Validation Duplication Analysis

**Issue**: Validation logic duplicated across tools
- check_health: has env validation
- get_deployment_status: has env validation (assumed)
- list_releases: no env validation (doesn't use env parameter)

**Constants Duplicated**:
```python
["prod", "staging", "uat", "dev"]  # Appears in multiple places
```

**Maintenance Risk**: Adding new environment requires updating multiple locations

## Performance Baseline

**Current Inline Validation** (estimated):
- `env.lower()`: <0.001ms (string operation)
- `in ["prod", "staging", "uat", "dev"]`: <0.001ms (set membership in list)
- Total: <0.01ms (negligible overhead)

**Target Centralized Validation**: <0.01ms (same performance)

## Integration Approach Recommendation

### Option A: Centralized Module (RECOMMENDED) ✅

**Structure**:
```python
# src/validation.py
VALID_ENVIRONMENTS = {"dev", "staging", "uat", "prod"}  # Set for O(1) lookup

def validate_environment(env: str | None) -> str | None:
    """Validate and normalize environment name.

    Args:
        env: Environment name (case-insensitive) or None for "all environments"

    Returns:
        Normalized environment name (lowercase) or None if input was None

    Raises:
        ValueError: If env is invalid (not in VALID_ENVIRONMENTS after normalization)
    """
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

**Integration**:
```python
# src/server.py
from .validation import validate_environment

@mcp.tool()
async def check_health(env: str | None = None) -> dict[str, Any]:
    # Replace inline validation with centralized call
    env_lower = validate_environment(env)  # Validates and normalizes

    # Build CLI arguments (rest of logic unchanged)
    args = ["health", "--format", "json"]
    if env_lower is not None:
        args.extend(["--env", env_lower])
    ...
```

**Advantages**:
- ✅ DRY principle: Single source of truth (NF-007, NF-009)
- ✅ Testable in isolation (NF-008)
- ✅ Easy to update when environments change
- ✅ Consistent error messages across tools (FR-015)
- ✅ Maintains same performance (<0.01ms)
- ✅ Type hints enable static analysis

**Disadvantages**:
- Requires import statement in server.py (minimal complexity)
- One additional file in codebase

### Option B: Inline with Shared Constant

**Structure**:
```python
# src/server.py
VALID_ENVIRONMENTS = {"dev", "staging", "uat", "prod"}

# Each tool duplicates validation logic but uses shared constant
```

**Disadvantages**:
- ❌ Validation logic still duplicated (violates DRY)
- ❌ Cannot test validation in isolation
- ❌ Inconsistent error messages possible

**Decision**: **Reject Option B** - Does not meet NF-007, NF-008, NF-009

## Error Response Format Analysis

### Current: ValueError → FastMCP Conversion
- FastMCP automatically converts Python exceptions to MCP error responses
- Maintains MCP protocol compliance
- No explicit MCP error response creation needed

### Clarification #3: "Return MCP error response objects"
**Interpretation**: Keep ValueError approach since FastMCP handles conversion
- ValueError messages already structured (param, invalid value, valid options per FR-011)
- FastMCP wraps in MCP error response format automatically
- No implementation change needed - current pattern already meets requirement

**Verification Needed**: Confirm FastMCP ValueError→MCP error response behavior matches requirement

## CLI Validation Synchronization

**Current State**: MCP and CLI both validate environments independently
- MCP validation: Inline in tools
- CLI validation: In devops-cli tool

**Proposed State**: MCP and CLI both validate with synchronized rules
- MCP validation: Centralized in validation.py module
- CLI validation: Unchanged (in devops-cli)

**Synchronization Strategy** (per clarification - manual code review):
1. Document VALID_ENVIRONMENTS in both codebases
2. Update validation.py when environments change
3. Update CLI validation rules in parallel
4. Test both layers to verify alignment (FR-017)

**Risk Mitigation**:
- Add comment in validation.py linking to CLI validation
- Add test case verifying MCP/CLI agreement (FR-016, FR-017)

## Performance Considerations

**Optimization: Use Set Instead of List**
```python
# Current (list): O(n) lookup
env_lower in ["prod", "staging", "uat", "dev"]

# Proposed (set): O(1) lookup
env_lower in {"prod", "staging", "uat", "dev"}
```

**Impact**: For 4 environments, difference negligible (<0.001ms)
**Benefit**: Demonstrates best practice, future-proof for more environments

**Per NF-003**: "no regex compilation per request"
- ✅ Set membership check requires no compilation
- ✅ str.lower() and str.strip() are optimized builtins
- ✅ No performance concern

## Decision Summary

### ✅ Recommended Approach: Centralized Module

1. **Create** `src/validation.py` with:
   - `VALID_ENVIRONMENTS` constant (set)
   - `validate_environment()` function
   - Type hints and docstrings

2. **Update** existing tools:
   - `check_health`: Replace inline validation with `validate_environment()` call
   - `get_deployment_status`: Replace inline validation with `validate_environment()` call
   - `list_releases`: No changes (doesn't use env parameter)

3. **Error Handling**:
   - Keep ValueError approach (FastMCP converts to MCP error response)
   - Ensure error messages meet FR-011 format (parameter, invalid value, valid options)

4. **Testing**:
   - Create `tests/test_validation.py` for isolated validation tests
   - Update existing tool tests to verify validation integration

5. **Performance**:
   - Use set for VALID_ENVIRONMENTS (O(1) lookup)
   - Maintain <0.01ms validation overhead

### Constitutional Compliance Verification

- ✅ **Principle I (Simplicity)**: Single module, simple set check
- ✅ **Principle II (Explicit)**: Clear error messages, explicit validation
- ✅ **Principle III (Type Safety)**: Full type hints in validation.py
- ✅ **Principle V (Standard Library)**: Only uses set, str methods (stdlib)
- ✅ **Principle VII (Commit)**: Will commit after validation module, then after integration
- ✅ **NF-007**: Centralized in single location
- ✅ **NF-008**: Testable in isolation
- ✅ **NF-009**: Single place to update

### Next Steps

Proceed to **Phase 1: Design** to create:
1. `data-model.md` - Validation entities and workflow
2. `contracts/validation.schema.json` - validate_environment() contract
3. `quickstart.md` - 6 integration test scenarios

---
*Research complete - Ready for Phase 1 design*
