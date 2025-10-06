# Quickstart: Environment Validation Integration Scenarios

**Goal**: Define 6 integration test scenarios demonstrating environment validation in real tool usage

**Date**: 2025-10-05

## Test Scenarios

### Scenario 1: Valid Environment (Lowercase)

**Description**: User provides valid environment name in lowercase format

**Tool**: `check_health`

**Input**:
```json
{
  "env": "prod"
}
```

**Validation**:
1. `validate_environment("prod")` is called
2. env is not None → proceed
3. Trim whitespace: "prod" → "prod" (no change)
4. Normalize: "prod".lower() → "prod" (no change)
5. Check membership: "prod" in {"dev", "staging", "uat", "prod"} → ✅ True
6. Return: "prod"

**Expected Behavior**:
- ✅ Validation passes
- ✅ Normalized value "prod" passed to CLI
- ✅ CLI called with `--env prod`
- ✅ Returns health check data for production environment

**Acceptance Criteria** (FR-001, FR-003):
- No validation error raised
- CLI execution proceeds
- Response contains production health data

---

### Scenario 2: Valid Environment (Uppercase)

**Description**: User provides valid environment name in uppercase format (case-insensitive match)

**Tool**: `check_health`

**Input**:
```json
{
  "env": "PROD"
}
```

**Validation**:
1. `validate_environment("PROD")` is called
2. env is not None → proceed
3. Trim whitespace: "PROD" → "PROD" (no change)
4. Normalize: "PROD".lower() → "prod" ✅
5. Check membership: "prod" in VALID_ENVIRONMENTS → ✅ True
6. Return: "prod"

**Expected Behavior**:
- ✅ Validation passes (case-insensitive per FR-002)
- ✅ Normalized to lowercase per FR-003
- ✅ CLI called with `--env prod` (not "PROD")
- ✅ Returns health check data for production environment

**Acceptance Criteria** (FR-002, FR-003):
- Case-insensitive matching works
- Environment name normalized to lowercase
- CLI receives lowercase value

---

### Scenario 3: Valid Environment with Whitespace

**Description**: User provides valid environment with leading/trailing whitespace (common typo)

**Tool**: `get_deployment_status`

**Input**:
```json
{
  "app": "web-app",
  "env": " prod "
}
```

**Validation**:
1. `validate_environment(" prod ")` is called
2. env is not None → proceed
3. Trim whitespace: " prod ".strip() → "prod" ✅
4. Normalize: "prod".lower() → "prod"
5. Check membership: "prod" in VALID_ENVIRONMENTS → ✅ True
6. Return: "prod"

**Expected Behavior**:
- ✅ Validation passes (whitespace trimmed per clarification #4 and FR-008)
- ✅ CLI called with `--env prod` (trimmed value)
- ✅ Returns deployment status for web-app in production

**Acceptance Criteria** (FR-008, clarification #4):
- Leading/trailing whitespace automatically removed
- Validation succeeds after trimming
- Clean value passed to CLI

---

### Scenario 4: Invalid Environment Name

**Description**: User provides invalid environment name not in allowed list

**Tool**: `check_health`

**Input**:
```json
{
  "env": "production"
}
```

**Validation**:
1. `validate_environment("production")` is called
2. env is not None → proceed
3. Trim whitespace: "production" → "production"
4. Normalize: "production".lower() → "production"
5. Check membership: "production" in VALID_ENVIRONMENTS → ❌ False
6. Raise ValueError: "Invalid environment: production. Must be one of: dev, prod, staging, uat"

**Expected Behavior**:
- ❌ Validation fails (per FR-004)
- ❌ MCP error response returned (per clarification #3, FR-011)
- ❌ CLI NOT executed (per FR-006, FR-012)
- ✅ Error message includes parameter name, invalid value, valid options (per FR-011)

**Acceptance Criteria** (FR-004, FR-006, FR-011, FR-012):
- ValueError raised with structured message
- No subprocess execution
- Error message lists valid environments
- Response time <10ms (no CLI timeout per NF-001)

**Error Response**:
```json
{
  "error": {
    "code": "invalid_parameter",
    "message": "Invalid environment: production. Must be one of: dev, prod, staging, uat"
  }
}
```

---

### Scenario 5: None Environment (All Environments)

**Description**: User provides None/null for environment (check all environments)

**Tool**: `check_health`

**Input**:
```json
{
  "env": null
}
```
Or tool called with no env parameter:
```python
await check_health()  # env defaults to None
```

**Validation**:
1. `validate_environment(None)` is called
2. env is None → ✅ Return None immediately (per clarification #5)

**Expected Behavior**:
- ✅ Validation passes (None is valid per clarification #5)
- ✅ No normalization (None stays None)
- ✅ CLI called WITHOUT `--env` parameter
- ✅ CLI returns health for ALL environments (dev, staging, uat, prod)

**Acceptance Criteria** (clarification #5, FR-010):
- None treated as "all environments" use case
- No validation error
- CLI behavior: check all environments (existing behavior preserved)

**Response Example**:
```json
{
  "status": "success",
  "health_checks": [
    {"environment": "dev", "status": "healthy"},
    {"environment": "staging", "status": "healthy"},
    {"environment": "uat", "status": "degraded"},
    {"environment": "prod", "status": "healthy"}
  ]
}
```

---

### Scenario 6: Empty String After Trimming

**Description**: User provides empty string or whitespace-only string

**Tool**: `check_health`

**Input**:
```json
{
  "env": "   "
}
```
Or:
```json
{
  "env": ""
}
```

**Validation**:
1. `validate_environment("   ")` is called
2. env is not None → proceed
3. Trim whitespace: "   ".strip() → "" ✅
4. Check if empty: "" is falsy → ❌ True
5. Raise ValueError: "Environment cannot be empty"

**Expected Behavior**:
- ❌ Validation fails (empty after trimming per FR-008)
- ❌ MCP error response returned
- ❌ CLI NOT executed
- ✅ Clear error message about empty environment

**Acceptance Criteria** (FR-008):
- Empty string rejected
- Whitespace-only string rejected (becomes empty after trim)
- Specific error message for empty case
- Response time <10ms

**Error Response**:
```json
{
  "error": {
    "code": "invalid_parameter",
    "message": "Environment cannot be empty"
  }
}
```

---

## Integration Test Implementation

### Test File: `test_validation_integration.py`

**Purpose**: End-to-end validation of validation layer integrated with MCP tools

**Test Cases** (maps to scenarios):
```python
@pytest.mark.asyncio
async def test_scenario_1_valid_lowercase():
    """Scenario 1: Valid environment (lowercase)"""
    result = await check_health(env="prod")
    assert result["status"] == "success"
    assert any(h["environment"] == "prod" for h in result["health_checks"])

@pytest.mark.asyncio
async def test_scenario_2_valid_uppercase():
    """Scenario 2: Valid environment (uppercase) - case insensitive"""
    result = await check_health(env="PROD")
    assert result["status"] == "success"
    # Verify CLI received lowercase
    # (check via mock or log inspection)

@pytest.mark.asyncio
async def test_scenario_3_valid_with_whitespace():
    """Scenario 3: Valid environment with whitespace - trimmed"""
    result = await get_deployment_status(app="web-app", env=" prod ")
    assert result["status"] == "success"

@pytest.mark.asyncio
async def test_scenario_4_invalid_environment():
    """Scenario 4: Invalid environment name - error"""
    with pytest.raises(ValueError, match="Invalid environment: production"):
        await check_health(env="production")

@pytest.mark.asyncio
async def test_scenario_5_none_environment():
    """Scenario 5: None environment - all environments"""
    result = await check_health(env=None)
    assert len(result["health_checks"]) == 4  # All environments

@pytest.mark.asyncio
async def test_scenario_6_empty_string():
    """Scenario 6: Empty string - error"""
    with pytest.raises(ValueError, match="Environment cannot be empty"):
        await check_health(env="   ")
```

### Success Criteria

**All 6 scenarios must**:
- ✅ Execute validation function
- ✅ Demonstrate expected behavior (pass or fail)
- ✅ Meet performance targets (<10ms validation)
- ✅ Use consistent error message format
- ✅ Maintain MCP protocol compliance

---

## Manual Testing with FastMCP Inspector

### Command
```bash
make dev  # Starts FastMCP Inspector
```

### Scenario Testing

**Scenario 1** (Valid lowercase):
```bash
# Call: check_health with env="prod"
# Expected: Success, returns prod health data
```

**Scenario 2** (Valid uppercase):
```bash
# Call: check_health with env="PROD"
# Expected: Success, CLI receives "prod" (lowercase)
```

**Scenario 3** (Whitespace):
```bash
# Call: check_health with env=" staging "
# Expected: Success, trimmed to "staging"
```

**Scenario 4** (Invalid):
```bash
# Call: check_health with env="production"
# Expected: Error with valid options listed
```

**Scenario 5** (None):
```bash
# Call: check_health with no env parameter
# Expected: Success, returns all 4 environments
```

**Scenario 6** (Empty):
```bash
# Call: check_health with env=""
# Expected: Error "Environment cannot be empty"
```

---

## Coverage Mapping

| Scenario | Functional Requirements | Clarifications |
|----------|------------------------|----------------|
| 1 | FR-001, FR-003, FR-010 | - |
| 2 | FR-002, FR-003 | - |
| 3 | FR-008 | #4 (trim whitespace) |
| 4 | FR-004, FR-005, FR-006, FR-011, FR-012 | #3 (MCP error response) |
| 5 | FR-010 | #5 (None = all envs) |
| 6 | FR-008 | #4 (trim, then validate) |

**Additional Coverage**:
- Performance: All scenarios verify <10ms (NF-001)
- Security: Scenarios 4, 6 verify rejection (NF-004)
- Consistency: All scenarios use same error format (FR-015)

---

## Next Steps

1. **Implement validation.py** based on data model
2. **Write unit tests** in test_validation.py (7 tests)
3. **Integrate into tools** (check_health, get_deployment_status)
4. **Run integration tests** to verify all 6 scenarios
5. **Manual testing** via FastMCP Inspector for final validation

---
*Quickstart scenarios complete - Ready for task generation*
