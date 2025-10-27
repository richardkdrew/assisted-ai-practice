"""Evaluator for assessing agent performance on test scenarios."""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from investigator_agent.agent import Agent
from evals.scenarios import Scenario
from investigator_agent.models import Conversation


@dataclass
class EvaluationResult:
    """Result of evaluating agent performance on a single scenario."""

    scenario_id: str
    passed: bool
    scores: dict[str, float]  # tool_usage, decision_quality, overall
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


class Evaluator:
    """Evaluates agent performance on test scenarios."""

    def __init__(self, pass_threshold: float = 0.7):
        """Initialize evaluator.

        Args:
            pass_threshold: Minimum overall score to consider a scenario passed (0-1)
        """
        self.pass_threshold = pass_threshold

    async def run_scenario(self, agent: Agent, scenario: Scenario) -> EvaluationResult:
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

            # Construct evaluation prompt
            prompt = self._build_prompt(scenario)

            # Run agent
            response = await agent.send_message(conversation, prompt)

            # Evaluate performance
            tool_usage_score = self._eval_tool_usage(
                conversation, scenario.expected_tools
            )
            decision_quality_score = self._eval_decision_quality(
                conversation, response, scenario
            )

            # Calculate overall score
            overall_score = (tool_usage_score + decision_quality_score) / 2

            # Determine pass/fail
            passed = overall_score >= self.pass_threshold

            scores = {
                "tool_usage": tool_usage_score,
                "decision_quality": decision_quality_score,
                "overall": overall_score,
            }

            details = {
                "response": response,
                "tool_calls": self._extract_tool_calls(conversation),
                "severity_found": self._extract_severity(response),
                "expected_severity": scenario.expected_severity,
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
                scores={"tool_usage": 0.0, "decision_quality": 0.0, "overall": 0.0},
                details={"error": str(e)},
                duration=duration,
                error=str(e),
            )

    def _build_prompt(self, scenario: Scenario) -> str:
        """Build evaluation prompt from scenario."""
        return f"Assess the risk of deploying release {scenario.release_data.get('release_id', 'unknown')}"

    def _eval_tool_usage(
        self, conversation: Conversation, expected_tools: list[str]
    ) -> float:
        """Evaluate if correct tools were called.

        Args:
            conversation: The conversation with tool calls
            expected_tools: List of expected tool names

        Returns:
            Score from 0.0 to 1.0
        """
        # Extract tool names from conversation
        tool_calls = self._extract_tool_calls(conversation)

        if not expected_tools:
            # If no tools expected, score based on whether tools were called
            return 1.0 if not tool_calls else 0.5

        if not tool_calls:
            # Expected tools but none called
            return 0.0

        # Check how many expected tools were called
        called_tools = set(tool_calls)
        expected_set = set(expected_tools)

        # Calculate overlap
        correct_calls = len(called_tools & expected_set)
        total_expected = len(expected_set)

        # Bonus: penalize if unexpected tools were called
        unexpected_calls = len(called_tools - expected_set)
        penalty = unexpected_calls * 0.1

        score = correct_calls / total_expected - penalty
        return max(0.0, min(1.0, score))

    def _eval_decision_quality(
        self, conversation: Conversation, response: str, scenario: Scenario
    ) -> float:
        """Evaluate quality of the decision.

        Args:
            conversation: The conversation
            response: Agent's final response
            scenario: The test scenario

        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0

        # Check severity assessment (most important)
        severity_found = self._extract_severity(response)
        if severity_found == scenario.expected_severity:
            score += 0.6
        elif self._is_adjacent_severity(severity_found, scenario.expected_severity):
            score += 0.3  # Partial credit for being close

        # Check for expected keywords in findings
        response_lower = response.lower()
        keywords_found = sum(
            1 for kw in scenario.expected_findings_keywords if kw.lower() in response_lower
        )
        total_keywords = len(scenario.expected_findings_keywords)

        if total_keywords > 0:
            keyword_score = keywords_found / total_keywords
            score += 0.4 * keyword_score

        return min(1.0, score)

    def _extract_tool_calls(self, conversation: Conversation) -> list[str]:
        """Extract tool names from conversation."""
        tool_names = []
        for message in conversation.messages:
            if message.role == "assistant" and isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_names.append(block["name"])
        return tool_names

    def _extract_severity(self, response: str) -> str | None:
        """Extract severity level from response text."""
        response_lower = response.lower()

        # Look for explicit severity mentions
        if "high severity" in response_lower or "severity: high" in response_lower:
            return "high"
        if "medium severity" in response_lower or "severity: medium" in response_lower:
            return "medium"
        if "low severity" in response_lower or "severity: low" in response_lower:
            return "low"

        # Look for severity keywords with boundaries
        # Check for "is high", "looks high", "risk is high", etc.
        import re

        # Match high with word boundaries
        if re.search(r'\bhigh\b', response_lower):
            return "high"
        if re.search(r'\bmedium\b', response_lower):
            return "medium"
        if re.search(r'\blow\b', response_lower):
            return "low"

        return None

    def _is_adjacent_severity(self, found: str | None, expected: str) -> bool:
        """Check if found severity is adjacent to expected."""
        if found is None:
            return False

        severity_order = ["low", "medium", "high"]
        try:
            found_idx = severity_order.index(found)
            expected_idx = severity_order.index(expected)
            return abs(found_idx - expected_idx) == 1
        except ValueError:
            return False

    async def run_suite(
        self, agent: Agent, scenarios: list[Scenario]
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
