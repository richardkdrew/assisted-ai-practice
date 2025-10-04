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
