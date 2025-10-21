"""Evaluator for assessing Investigator Agent performance on feature readiness scenarios.

Adapted from Module 7's evaluator for Module 8's feature investigation use case.
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from investigator_agent.agent import Agent
from investigator_agent.evaluations.scenarios import EvaluationScenario
from investigator_agent.models import Conversation


@dataclass
class EvaluationResult:
    """Result of evaluating agent performance on a single scenario."""

    scenario_id: str
    passed: bool
    scores: dict[str, float]  # feature_id, tool_usage, decision_quality, context_mgmt, overall
    details: dict[str, Any]
    duration: float
    error: str | None = None


@dataclass
class SuiteResults:
    """Results from running a full evaluation suite."""

    total_scenarios: int
    passed: int
    pass_rate: float
    avg_scores: dict[str, float]
    scenario_results: list[EvaluationResult]
    duration: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Comparison:
    """Comparison between current results and a baseline."""

    pass_rate_delta: float
    score_deltas: dict[str, float]
    regressions: list[str]
    improvements: list[str]
    summary: str


class InvestigatorEvaluator:
    """Evaluates Investigator Agent performance on feature readiness scenarios."""

    def __init__(self, pass_threshold: float = 0.7):
        """Initialize evaluator.

        Args:
            pass_threshold: Minimum overall score to consider a scenario passed (0-1)
        """
        self.pass_threshold = pass_threshold

    async def run_scenario(
        self, agent: Agent, scenario: EvaluationScenario
    ) -> EvaluationResult:
        """Run a single evaluation scenario.

        Args:
            agent: The agent to evaluate
            scenario: The test scenario

        Returns:
            EvaluationResult with scores and details
        """
        start_time = time.time()

        try:
            # Create new conversation for this scenario
            conversation = agent.new_conversation()

            # Run agent with scenario query
            response = await agent.send_message(conversation, scenario.user_query)

            # Evaluate performance across dimensions
            feature_id_score = self._eval_feature_identification(
                conversation, response, scenario
            )
            tool_usage_score = self._eval_tool_usage(conversation, scenario)
            decision_quality_score = self._eval_decision_quality(response, scenario)
            context_mgmt_score = self._eval_context_management(conversation, scenario)

            # Calculate overall score (weighted average)
            overall_score = (
                feature_id_score * 0.2
                + tool_usage_score * 0.3
                + decision_quality_score * 0.4
                + context_mgmt_score * 0.1
            )

            # Determine pass/fail
            passed = overall_score >= self.pass_threshold

            scores = {
                "feature_identification": feature_id_score,
                "tool_usage": tool_usage_score,
                "decision_quality": decision_quality_score,
                "context_management": context_mgmt_score,
                "overall": overall_score,
            }

            details = {
                "response": response[:500],  # Truncate for storage
                "tool_calls": self._extract_tool_calls(conversation),
                "decision_found": self._extract_decision(response),
                "expected_decision": scenario.expected_decision,
                "sub_conversations_count": len(conversation.sub_conversations),
                "expected_sub_conversations": scenario.expected_sub_conversations,
            }

            duration = time.time() - start_time

            return EvaluationResult(
                scenario_id=scenario.id,
                passed=passed,
                scores=scores,
                details=details,
                duration=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            return EvaluationResult(
                scenario_id=scenario.id,
                passed=False,
                scores={
                    "feature_identification": 0.0,
                    "tool_usage": 0.0,
                    "decision_quality": 0.0,
                    "context_management": 0.0,
                    "overall": 0.0,
                },
                details={"error": str(e)},
                duration=duration,
                error=str(e),
            )

    def _eval_feature_identification(
        self, conversation: Conversation, response: str, scenario: EvaluationScenario
    ) -> float:
        """Evaluate if agent correctly identified the feature.

        Args:
            conversation: The conversation
            response: Agent's response
            scenario: The test scenario

        Returns:
            Score from 0.0 to 1.0
        """
        # Check if feature_id appears in response or conversation
        feature_id = scenario.feature_id
        response_lower = response.lower()
        feature_id_lower = feature_id.lower()

        # Check response mentions feature
        if feature_id_lower in response_lower:
            return 1.0

        # Check if JIRA was called (necessary for identification)
        tool_calls = self._extract_tool_calls(conversation)
        if "get_jira_data" in tool_calls:
            return 0.8  # Called right tool, may have identified feature

        return 0.0

    def _eval_tool_usage(
        self, conversation: Conversation, scenario: EvaluationScenario
    ) -> float:
        """Evaluate if correct tools were called.

        Args:
            conversation: The conversation with tool calls
            scenario: Expected scenario behavior

        Returns:
            Score from 0.0 to 1.0
        """
        tool_calls = self._extract_tool_calls(conversation)
        expected_tools = set(scenario.expected_tools)

        if not expected_tools:
            return 1.0 if not tool_calls else 0.5

        if not tool_calls:
            return 0.0

        called_tools = set(tool_calls)

        # Calculate recall (how many expected tools were called)
        correct_calls = len(called_tools & expected_tools)
        recall = correct_calls / len(expected_tools)

        # Calculate precision (how many called tools were expected)
        precision = correct_calls / len(called_tools) if called_tools else 0.0

        # F1 score
        if recall + precision == 0:
            return 0.0

        f1_score = 2 * (precision * recall) / (precision + recall)
        return f1_score

    def _eval_decision_quality(
        self, response: str, scenario: EvaluationScenario
    ) -> float:
        """Evaluate quality of the readiness decision.

        Args:
            response: Agent's final response
            scenario: The test scenario

        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0
        response_lower = response.lower()

        # Check decision (most important - 60%)
        decision_found = self._extract_decision(response)
        if decision_found == scenario.expected_decision:
            score += 0.6
        elif self._is_adjacent_decision(decision_found, scenario.expected_decision):
            score += 0.3  # Partial credit for being close

        # Check for expected justification points (40%)
        keywords_found = sum(
            1
            for kw in scenario.expected_justification_includes
            if kw.lower() in response_lower
        )
        total_keywords = len(scenario.expected_justification_includes)

        if total_keywords > 0:
            keyword_score = keywords_found / total_keywords
            score += 0.4 * keyword_score

        return min(1.0, score)

    def _eval_context_management(
        self, conversation: Conversation, scenario: EvaluationScenario
    ) -> float:
        """Evaluate context management (sub-conversations usage).

        Args:
            conversation: The conversation
            scenario: The test scenario

        Returns:
            Score from 0.0 to 1.0
        """
        has_sub_convs = len(conversation.sub_conversations) > 0
        expected_sub_convs = scenario.expected_sub_conversations

        # Correct usage
        if has_sub_convs == expected_sub_convs:
            return 1.0

        # Incorrect usage (didn't use when should, or used when shouldn't)
        return 0.5

    def _extract_tool_calls(self, conversation: Conversation) -> list[str]:
        """Extract tool names from conversation."""
        tool_names = []
        for message in conversation.messages:
            if message.role == "assistant" and isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_names.append(block["name"])
        return tool_names

    def _extract_decision(self, response: str) -> str | None:
        """Extract readiness decision from response text."""
        response_lower = response.lower()

        # Look for explicit decision statements
        if "ready for production" in response_lower or "production ready" in response_lower:
            return "ready"
        if "not ready" in response_lower or "not production-ready" in response_lower:
            return "not_ready"
        if "borderline" in response_lower or "mixed signals" in response_lower:
            return "borderline"

        # Look for decision keywords
        import re

        if re.search(r'\bready\b', response_lower):
            return "ready"
        if re.search(r'\bnot\b.*\bready\b', response_lower):
            return "not_ready"

        return None

    def _is_adjacent_decision(self, found: str | None, expected: str) -> bool:
        """Check if found decision is adjacent to expected."""
        if found is None:
            return False

        # Borderline is adjacent to both ready and not_ready
        if expected == "borderline":
            return found in ["ready", "not_ready"]
        if found == "borderline":
            return expected in ["ready", "not_ready"]

        return False

    async def run_suite(
        self, agent: Agent, scenarios: list[EvaluationScenario]
    ) -> SuiteResults:
        """Run evaluation on multiple scenarios.

        Args:
            agent: The agent to evaluate
            scenarios: List of test scenarios

        Returns:
            SuiteResults with aggregated metrics
        """
        start_time = time.time()

        results = []
        for scenario in scenarios:
            result = await self.run_scenario(agent, scenario)
            results.append(result)

        # Calculate aggregates
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        pass_rate = passed / total if total > 0 else 0.0

        # Average scores
        avg_scores = {}
        if results:
            score_keys = results[0].scores.keys()
            for key in score_keys:
                scores = [r.scores[key] for r in results if key in r.scores]
                avg_scores[key] = sum(scores) / len(scores) if scores else 0.0

        duration = time.time() - start_time

        return SuiteResults(
            total_scenarios=total,
            passed=passed,
            pass_rate=pass_rate,
            avg_scores=avg_scores,
            scenario_results=results,
            duration=duration,
        )

    def save_baseline(self, results: SuiteResults, version: str) -> None:
        """Save results as baseline for future comparisons.

        Args:
            results: Suite results to save
            version: Version identifier for the baseline
        """
        baseline_dir = Path("data/baselines")
        baseline_dir.mkdir(parents=True, exist_ok=True)

        baseline_file = baseline_dir / f"{version}.json"

        data = {
            "version": version,
            "total_scenarios": results.total_scenarios,
            "passed": results.passed,
            "pass_rate": results.pass_rate,
            "avg_scores": results.avg_scores,
            "duration": results.duration,
            "metadata": results.metadata,
        }

        with open(baseline_file, "w") as f:
            json.dump(data, f, indent=2)

    def load_baseline(self, version: str) -> dict[str, Any] | None:
        """Load baseline results.

        Args:
            version: Version identifier

        Returns:
            Baseline data or None if not found
        """
        baseline_file = Path("data/baselines") / f"{version}.json"

        if not baseline_file.exists():
            return None

        with open(baseline_file) as f:
            return json.load(f)

    def compare_to_baseline(
        self, current: SuiteResults, baseline_data: dict[str, Any]
    ) -> Comparison:
        """Compare current results to baseline.

        Args:
            current: Current suite results
            baseline_data: Baseline data loaded from file

        Returns:
            Comparison object with deltas and analysis
        """
        # Calculate pass rate delta
        baseline_pass_rate = baseline_data["pass_rate"]
        pass_rate_delta = current.pass_rate - baseline_pass_rate

        # Calculate score deltas
        baseline_scores = baseline_data["avg_scores"]
        score_deltas = {}
        for key in current.avg_scores:
            if key in baseline_scores:
                score_deltas[key] = current.avg_scores[key] - baseline_scores[key]

        # Identify regressions (>5% drop)
        regressions = []
        if pass_rate_delta < -0.05:
            regressions.append(f"Pass rate dropped by {abs(pass_rate_delta):.1%}")
        for key, delta in score_deltas.items():
            if delta < -0.05:
                regressions.append(f"{key} score dropped by {abs(delta):.1%}")

        # Identify improvements (>5% gain)
        improvements = []
        if pass_rate_delta > 0.05:
            improvements.append(f"Pass rate improved by {pass_rate_delta:.1%}")
        for key, delta in score_deltas.items():
            if delta > 0.05:
                improvements.append(f"{key} score improved by {delta:.1%}")

        # Generate summary
        if regressions:
            summary = f"⚠️  {len(regressions)} regression(s) detected"
        elif improvements:
            summary = f"✅ {len(improvements)} improvement(s) found"
        else:
            summary = "No significant changes"

        return Comparison(
            pass_rate_delta=pass_rate_delta,
            score_deltas=score_deltas,
            regressions=regressions,
            improvements=improvements,
            summary=summary,
        )
