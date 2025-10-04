"""Unit tests for environment validation layer.

Tests validate_environment() function against all contract requirements
and integration scenarios. Following TDD approach - these tests are written
before implementation and will initially fail.
"""

import pytest
from src.validation import validate_environment, VALID_ENVIRONMENTS


def test_valid_environments_constant():
    """Verify VALID_ENVIRONMENTS constant is correctly defined."""
    assert VALID_ENVIRONMENTS == frozenset({"dev", "staging", "uat", "prod"})
    assert len(VALID_ENVIRONMENTS) == 4


# T002: Valid environment (lowercase)
def test_validate_environment_lowercase():
    """Test validation with lowercase environment name.

    Contract: validation.schema.json test case 1
    Validates: FR-001 (validate against predefined list)
    """
    result = validate_environment("prod")
    assert result == "prod"


# T003: Valid environment (uppercase, case-insensitive)
def test_validate_environment_uppercase():
    """Test validation with uppercase environment name (case-insensitive).

    Contract: validation.schema.json test case 2
    Validates: FR-002 (case-insensitive matching), FR-003 (normalize to lowercase)
    """
    result = validate_environment("PROD")
    assert result == "prod", "Should normalize uppercase to lowercase"


# T004: Valid environment with whitespace
def test_validate_environment_with_whitespace():
    """Test validation with leading/trailing whitespace.

    Contract: validation.schema.json test case 3
    Validates: FR-008 (trim whitespace), clarification #4
    """
    result = validate_environment(" staging ")
    assert result == "staging", "Should trim whitespace and normalize"


# T005: Invalid environment name
def test_validate_environment_invalid():
    """Test validation with invalid environment name.

    Contract: validation.schema.json test case 4
    Validates: FR-004 (reject invalid), FR-005 (list valid options), FR-011 (structured error message)
    """
    with pytest.raises(ValueError) as exc_info:
        validate_environment("production")

    error_message = str(exc_info.value)
    assert "Invalid environment: production" in error_message
    assert "Must be one of:" in error_message
    # Verify all valid options are listed (order may vary)
    assert "dev" in error_message
    assert "prod" in error_message
    assert "staging" in error_message
    assert "uat" in error_message


# T006: Invalid environment "test"
def test_validate_environment_invalid_test():
    """Test validation with another invalid environment name.

    Contract: validation.schema.json test case 5
    Validates: FR-004 (reject invalid)
    """
    with pytest.raises(ValueError) as exc_info:
        validate_environment("test")

    error_message = str(exc_info.value)
    assert "Invalid environment: test" in error_message


# T007: None environment (all environments)
def test_validate_environment_none():
    """Test validation with None (represents 'all environments').

    Contract: validation.schema.json test case 6
    Validates: Clarification #5 (None = all environments)
    """
    result = validate_environment(None)
    assert result is None, "None should pass validation and return None"


# T008: Empty string after trimming
def test_validate_environment_empty_string():
    """Test validation with empty string and whitespace-only string.

    Contract: validation.schema.json test case 7
    Validates: FR-008 (reject empty after trim)
    """
    # Empty string
    with pytest.raises(ValueError) as exc_info:
        validate_environment("")
    assert "Environment cannot be empty" in str(exc_info.value)

    # Whitespace-only string (becomes empty after trim)
    with pytest.raises(ValueError) as exc_info:
        validate_environment("   ")
    assert "Environment cannot be empty" in str(exc_info.value)


# Additional edge case: Mixed case with whitespace
def test_validate_environment_mixed_case_with_whitespace():
    """Test validation with mixed case and whitespace (combined scenario)."""
    result = validate_environment("  DeV  ")
    assert result == "dev", "Should trim and normalize mixed case to lowercase"
