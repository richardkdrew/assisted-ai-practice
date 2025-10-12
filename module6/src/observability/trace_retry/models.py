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
    """
    return {
        "decision": decision,
        "reason": reason,
        "wait_seconds": wait_seconds,
        "trace_id": trace_id,
        "span_id": span_id
    }