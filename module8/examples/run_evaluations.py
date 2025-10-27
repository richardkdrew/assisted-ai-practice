"""Run comprehensive evaluations on the Investigator Agent.

This script evaluates the agent across 8 scenarios covering:
- Ready for production
- Not ready (test failures, incomplete)
- Borderline cases
- Large documentation handling
- Feature identification
- Memory retrieval

Usage:
    python examples/run_evaluations.py                 # Run evaluations
    python examples/run_evaluations.py --baseline v1   # Save as baseline
    python examples/run_evaluations.py --compare v1    # Compare to baseline
"""

import argparse
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from investigator_agent import Agent, AnthropicProvider, Config, ConversationStore
from investigator_agent.evaluations import (
    EVALUATION_SCENARIOS,
    InvestigatorEvaluator,
)
from investigator_agent.memory import FileMemoryStore, Memory
from investigator_agent.observability import setup_tracer
from investigator_agent.system_prompt import DEFAULT_SYSTEM_PROMPT
from investigator_agent.tools import get_analysis, get_jira_data, list_docs, read_doc
from investigator_agent.tools.registry import ToolRegistry

# Load environment variables
load_dotenv()


async def setup_agent(with_memory: bool = False) -> Agent:
    """Setup the Investigator Agent for evaluation.

    Args:
        with_memory: Whether to enable memory system

    Returns:
        Configured Agent instance
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment")

    # Initialize components
    provider = AnthropicProvider(api_key=api_key, model="claude-3-5-sonnet-20241022")
    store = ConversationStore(Path("conversations"))
    config = Config(system_prompt=DEFAULT_SYSTEM_PROMPT, max_tokens=4096)

    # Setup memory if requested
    memory_store = None
    if with_memory:
        memory_store = FileMemoryStore(Path("memory_store_eval"))
        # Pre-populate with sample memory for memory test scenario
        sample_memory = Memory(
            id="eval_mem_001",
            feature_id="FEAT-MS-001",
            decision="ready",
            justification="Previous assessment showed all quality gates passed",
            key_findings={"test_coverage": 95, "uat_status": "approved"},
            timestamp=datetime(2025, 10, 15, 10, 30, 0),
            metadata={},
        )
        memory_store.store(sample_memory)

    # Register tools
    tool_registry = ToolRegistry()
    tool_registry.register(
        name="get_jira_data",
        description="Retrieves metadata for all features",
        input_schema={"type": "object", "properties": {}, "required": []},
        handler=get_jira_data,
    )
    tool_registry.register(
        name="get_analysis",
        description="Retrieves analysis data for a feature",
        input_schema={
            "type": "object",
            "properties": {
                "feature_id": {"type": "string"},
                "analysis_type": {"type": "string"},
            },
            "required": ["feature_id", "analysis_type"],
        },
        handler=get_analysis,
    )
    tool_registry.register(
        name="list_docs",
        description="Lists documentation files for a feature",
        input_schema={
            "type": "object",
            "properties": {"feature_id": {"type": "string"}},
            "required": ["feature_id"],
        },
        handler=list_docs,
    )
    tool_registry.register(
        name="read_doc",
        description="Reads a documentation file",
        input_schema={
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
        handler=read_doc,
    )

    return Agent(
        provider=provider,
        store=store,
        config=config,
        tool_registry=tool_registry,
        memory_store=memory_store,
    )


async def main():
    """Run evaluations."""
    parser = argparse.ArgumentParser(description="Run Investigator Agent evaluations")
    parser.add_argument(
        "--baseline", type=str, help="Save results as baseline with this version ID"
    )
    parser.add_argument(
        "--compare", type=str, help="Compare results to baseline version"
    )
    args = parser.parse_args()

    print("=" * 80)
    print("Investigator Agent - Comprehensive Evaluation")
    print("=" * 80)
    print()

    # Setup
    traces_dir = Path("traces")
    traces_dir.mkdir(exist_ok=True)
    setup_tracer(traces_dir)

    # Check for memory scenarios
    has_memory_scenario = any(s.expected_memory_retrieval for s in EVALUATION_SCENARIOS)

    # Create agent
    print(f"Setting up agent (memory: {has_memory_scenario})...")
    agent = await setup_agent(with_memory=has_memory_scenario)

    # Create evaluator
    evaluator = InvestigatorEvaluator(pass_threshold=0.7)

    # Run evaluations
    print(f"Running {len(EVALUATION_SCENARIOS)} evaluation scenarios...")
    print()

    results = await evaluator.run_suite(agent, EVALUATION_SCENARIOS)

    # Display results
    print("=" * 80)
    print("EVALUATION RESULTS")
    print("=" * 80)
    print()
    print(f"Total Scenarios: {results.total_scenarios}")
    print(f"Passed: {results.passed}/{results.total_scenarios}")
    print(f"Pass Rate: {results.pass_rate:.1%}")
    print(f"Duration: {results.duration:.2f}s")
    print()

    print("Average Scores:")
    for metric, score in results.avg_scores.items():
        print(f"  {metric}: {score:.2f}")
    print()

    print("Individual Results:")
    for result in results.scenario_results:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"  [{status}] {result.scenario_id}")
        print(f"       Overall: {result.scores['overall']:.2f}")
        if result.error:
            print(f"       Error: {result.error}")
    print()

    # Save baseline if requested
    if args.baseline:
        evaluator.save_baseline(results, args.baseline)
        print(f"💾 Baseline saved as: {args.baseline}")
        print()

    # Compare to baseline if requested
    if args.compare:
        baseline = evaluator.load_baseline(args.compare)
        if baseline:
            comparison = evaluator.compare_to_baseline(results, baseline)
            print("=" * 80)
            print(f"COMPARISON TO BASELINE: {args.compare}")
            print("=" * 80)
            print()
            print(f"Summary: {comparison.summary}")
            print(f"Pass Rate Delta: {comparison.pass_rate_delta:+.1%}")
            print()

            if comparison.regressions:
                print("⚠️  Regressions:")
                for reg in comparison.regressions:
                    print(f"  - {reg}")
                print()

            if comparison.improvements:
                print("✅ Improvements:")
                for imp in comparison.improvements:
                    print(f"  - {imp}")
                print()
        else:
            print(f"❌ Baseline '{args.compare}' not found")
            print()

    # Final assessment
    print("=" * 80)
    if results.pass_rate >= 0.7:
        print("✅ EVALUATION PASSED - Agent meets quality threshold (>70%)")
    else:
        print("❌ EVALUATION FAILED - Agent below quality threshold (<70%)")
    print("=" * 80)


if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(main())
