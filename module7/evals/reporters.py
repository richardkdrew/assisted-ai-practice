"""Report generation for evaluation results."""

import json
from pathlib import Path
from typing import Any

from evals.evaluator import Comparison, SuiteResults


def generate_json_report(
    results: SuiteResults, comparison: Comparison | None = None
) -> dict[str, Any]:
    """Generate machine-readable JSON report.

    Args:
        results: Suite results to report
        comparison: Optional comparison to baseline

    Returns:
        Dictionary suitable for JSON serialization
    """
    report = {
        "summary": {
            "total_scenarios": results.total_scenarios,
            "passed": results.passed,
            "failed": results.total_scenarios - results.passed,
            "pass_rate": results.pass_rate,
            "duration_seconds": results.duration,
        },
        "scores": results.avg_scores,
        "scenarios": [],
    }

    # Add individual scenario results
    for result in results.scenario_results:
        scenario_data = {
            "id": result.scenario_id,
            "passed": result.passed,
            "scores": result.scores,
            "duration": result.duration,
        }
        if result.error:
            scenario_data["error"] = result.error
        report["scenarios"].append(scenario_data)

    # Add comparison if provided
    if comparison:
        report["comparison"] = {
            "summary": comparison.summary,
            "pass_rate_delta": comparison.pass_rate_delta,
            "score_deltas": comparison.score_deltas,
            "regressions": comparison.regressions,
            "improvements": comparison.improvements,
        }

    return report


def generate_markdown_report(
    results: SuiteResults, comparison: Comparison | None = None
) -> str:
    """Generate human-readable Markdown report.

    Args:
        results: Suite results to report
        comparison: Optional comparison to baseline

    Returns:
        Markdown formatted string
    """
    lines = []

    # Title
    lines.append("# Evaluation Results")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total Scenarios**: {results.total_scenarios}")
    lines.append(f"- **Passed**: {results.passed}")
    lines.append(f"- **Failed**: {results.total_scenarios - results.passed}")
    lines.append(f"- **Pass Rate**: {results.pass_rate:.1%}")
    lines.append(f"- **Duration**: {results.duration:.2f}s")
    lines.append("")

    # Average Scores
    lines.append("## Average Scores")
    lines.append("")
    lines.append("| Metric | Score |")
    lines.append("|--------|-------|")
    for key, value in results.avg_scores.items():
        lines.append(f"| {key.replace('_', ' ').title()} | {value:.2f} |")
    lines.append("")

    # Comparison to baseline
    if comparison:
        lines.append("## Comparison to Baseline")
        lines.append("")
        lines.append(f"**{comparison.summary}**")
        lines.append("")

        if comparison.regressions:
            lines.append("### ⚠️  Regressions")
            lines.append("")
            for regression in comparison.regressions:
                lines.append(f"- {regression}")
            lines.append("")

        if comparison.improvements:
            lines.append("### ✅ Improvements")
            lines.append("")
            for improvement in comparison.improvements:
                lines.append(f"- {improvement}")
            lines.append("")

        lines.append("### Score Deltas")
        lines.append("")
        lines.append("| Metric | Delta |")
        lines.append("|--------|-------|")
        for key, delta in comparison.score_deltas.items():
            emoji = "📈" if delta > 0 else "📉" if delta < 0 else "➡️"
            lines.append(
                f"| {key.replace('_', ' ').title()} | {emoji} {delta:+.2f} |"
            )
        lines.append("")

    # Individual Scenarios
    lines.append("## Scenario Results")
    lines.append("")
    lines.append("| Scenario | Status | Tool Usage | Decision Quality | Overall |")
    lines.append("|----------|--------|------------|------------------|---------|")

    for result in results.scenario_results:
        status = "✅ Pass" if result.passed else "❌ Fail"
        tool_usage = result.scores.get("tool_usage", 0.0)
        decision = result.scores.get("decision_quality", 0.0)
        overall = result.scores.get("overall", 0.0)

        lines.append(
            f"| {result.scenario_id} | {status} | {tool_usage:.2f} | {decision:.2f} | {overall:.2f} |"
        )

    lines.append("")

    # Failed scenarios details
    failed = [r for r in results.scenario_results if not r.passed]
    if failed:
        lines.append("## Failed Scenarios Details")
        lines.append("")
        for result in failed:
            lines.append(f"### {result.scenario_id}")
            lines.append("")
            lines.append(f"- **Overall Score**: {result.scores.get('overall', 0.0):.2f}")
            lines.append(
                f"- **Tool Usage**: {result.scores.get('tool_usage', 0.0):.2f}"
            )
            lines.append(
                f"- **Decision Quality**: {result.scores.get('decision_quality', 0.0):.2f}"
            )
            if result.error:
                lines.append(f"- **Error**: {result.error}")
            if "expected_severity" in result.details:
                lines.append(
                    f"- **Expected Severity**: {result.details['expected_severity']}"
                )
            if "severity_found" in result.details:
                lines.append(f"- **Found Severity**: {result.details['severity_found']}")
            lines.append("")

    return "\n".join(lines)


def save_report(content: str | dict, path: str | Path) -> None:
    """Save report to file.

    Args:
        content: Report content (string for text, dict for JSON)
        path: File path to save to
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(content, dict):
        # Save as JSON
        with open(path, "w") as f:
            json.dump(content, f, indent=2)
    else:
        # Save as text
        with open(path, "w") as f:
            f.write(content)


def print_summary(results: SuiteResults, comparison: Comparison | None = None) -> None:
    """Print a quick summary to console.

    Args:
        results: Suite results
        comparison: Optional comparison to baseline
    """
    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Scenarios: {results.passed}/{results.total_scenarios} passed")
    print(f"Pass Rate: {results.pass_rate:.1%}")
    print(f"Duration: {results.duration:.2f}s")
    print("\nAverage Scores:")
    for key, value in results.avg_scores.items():
        print(f"  {key.replace('_', ' ').title()}: {value:.2f}")

    if comparison:
        print(f"\n{comparison.summary}")
        if comparison.regressions:
            print("\n⚠️  Regressions:")
            for reg in comparison.regressions:
                print(f"  - {reg}")
        if comparison.improvements:
            print("\n✅ Improvements:")
            for imp in comparison.improvements:
                print(f"  - {imp}")

    print("=" * 60 + "\n")
