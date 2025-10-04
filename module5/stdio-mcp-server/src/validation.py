"""Environment validation layer for MCP server.

This module provides centralized validation for environment name parameters
across all MCP tools. Validates environment names against a hardcoded whitelist
(dev, staging, uat, prod) with automatic whitespace trimming and case-insensitive
matching.

Defense-in-depth security pattern: Validates inputs at MCP layer before CLI
execution, providing immediate feedback (<10ms) without subprocess overhead.
"""

from typing import Optional
import logging
import sys

# Configure logging to stderr (MCP protocol compliance)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)

# Valid environment names (hardcoded for security - per clarification #2)
# Source of truth for environment validation across all MCP tools
VALID_ENVIRONMENTS = frozenset({"dev", "staging", "uat", "prod"})


def validate_environment(env: str | None) -> str | None:
    """Validate and normalize environment name.

    Args:
        env: Environment name (case-insensitive) or None for "all environments"

    Returns:
        Normalized environment name (lowercase) or None if input was None

    Raises:
        ValueError: If env is invalid (not in VALID_ENVIRONMENTS after normalization)
    """
    # Handle None (special case - "all environments" per clarification #5)
    if env is None:
        return None

    # Trim whitespace (per clarification #4 and FR-008)
    env_trimmed = env.strip()

    # Check empty after trimming (FR-008)
    if not env_trimmed:
        raise ValueError("Environment cannot be empty")

    # Normalize to lowercase (FR-002, FR-003)
    env_lower = env_trimmed.lower()

    # Validate against allowed set (FR-001, FR-004)
    if env_lower not in VALID_ENVIRONMENTS:
        valid_options = ", ".join(sorted(VALID_ENVIRONMENTS))
        logger.warning(f"Environment validation failed: {env} (not in {VALID_ENVIRONMENTS})")
        raise ValueError(
            f"Invalid environment: {env}. Must be one of: {valid_options}"
        )

    return env_lower


def validate_non_empty(param_name: str, value: str) -> str:
    """
    Validate that a parameter is non-empty after trimming whitespace.

    Args:
        param_name: Name of parameter (for error messages)
        value: Value to validate

    Returns:
        Trimmed value if non-empty

    Raises:
        ValueError: If value is empty after trimming
    """
    value_trimmed = value.strip()
    if not value_trimmed:
        logger.warning(f"Validation failed: {param_name} cannot be empty")
        raise ValueError(f"{param_name} cannot be empty")
    return value_trimmed


# Valid promotion paths (strict forward flow only)
VALID_PROMOTION_PATHS = frozenset({
    ("dev", "staging"),
    ("staging", "uat"),
    ("uat", "prod"),
})


def validate_promotion_path(from_env: str, to_env: str) -> None:
    """
    Validate promotion path follows strict forward flow rules.

    Valid paths: dev→staging, staging→uat, uat→prod
    No skipping environments, no backward promotion.

    Args:
        from_env: Source environment (must be normalized lowercase)
        to_env: Target environment (must be normalized lowercase)

    Raises:
        ValueError: If promotion path is invalid
    """
    if from_env == to_env:
        logger.warning(f"Validation failed: cannot promote to same environment ({from_env})")
        raise ValueError("cannot promote to same environment")

    if (from_env, to_env) not in VALID_PROMOTION_PATHS:
        # Check if this is a backward promotion (to_env appears before from_env in the chain)
        # Build reverse mapping to detect backward promotions
        env_order = {"dev": 0, "staging": 1, "uat": 2, "prod": 3}

        if to_env in env_order and from_env in env_order and env_order[to_env] < env_order[from_env]:
            # Backward promotion detected
            logger.warning(
                f"Validation failed: backward or invalid promotion {from_env}→{to_env}"
            )
            raise ValueError(
                f"invalid promotion path: {from_env}→{to_env} "
                f"(backward or invalid promotion not allowed)"
            )

        # Not backward, so it's skipping environments
        valid_next = [to for (frm, to) in VALID_PROMOTION_PATHS if frm == from_env]

        if valid_next:
            logger.warning(
                f"Validation failed: invalid promotion path {from_env}→{to_env}, "
                f"valid next: {valid_next}"
            )
            raise ValueError(
                f"invalid promotion path: {from_env}→{to_env} "
                f"(valid next environment from {from_env}: {', '.join(valid_next)})"
            )
        else:
            # No valid next (e.g., promoting from prod)
            logger.warning(
                f"Validation failed: invalid promotion {from_env}→{to_env}"
            )
            raise ValueError(
                f"invalid promotion path: {from_env}→{to_env} "
                f"(no valid promotion from {from_env})"
            )
