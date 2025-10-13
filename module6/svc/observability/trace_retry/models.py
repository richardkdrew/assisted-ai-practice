"""
Models for the trace_retry package.

This module defines the data structures used for retry decisions.
"""

from typing import Dict, Any, Literal


RetryDecisionType = Literal["RETRY", "ABORT", "WAIT"]


def create_retry_decision(
    decision: RetryDecisionType,
    reason: str,
    trace_id: str,
    span_id: str,
    wait_seconds: int = 0
) -> Dict[str, Any]:
    """
    Create a RetryDecision dictionary with the specified values.

    Args:
        decision: One of "RETRY", "ABORT", or "WAIT"
        reason: Human-readable explanation of the decision
        trace_id: The trace ID that was analyzed
        span_id: The span ID that triggered the decision
        wait_seconds: Number of seconds to wait before retry (defaults to 0)

    Returns:
        Dictionary with decision information

    Raises:
        ValueError: If decision is not a valid RetryDecisionType
        ValueError: If required fields are empty
    """
    # Validate decision type
    if decision not in ("RETRY", "ABORT", "WAIT"):
        raise ValueError(f"Invalid decision type: {decision}")

    # Validate required fields
    if not reason:
        raise ValueError("Reason cannot be empty")
    if not trace_id or len(trace_id) != 32:
        raise ValueError(f"Invalid trace_id: {trace_id}. Must be 32-character hex string.")
    if not span_id or len(span_id) != 16:
        raise ValueError(f"Invalid span_id: {span_id}. Must be 16-character hex string.")

    # Validate wait_seconds
    if wait_seconds < 0:
        raise ValueError(f"wait_seconds must be non-negative, got {wait_seconds}")

    return {
        "decision": decision,
        "reason": reason,
        "wait_seconds": wait_seconds,
        "trace_id": trace_id,
        "span_id": span_id
    }