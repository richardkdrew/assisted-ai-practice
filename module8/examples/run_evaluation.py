"""Example of running evaluation suite on the Detective Agent."""

import asyncio

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from investigator_agent import Agent, Config
from investigator_agent.persistence.store import ConversationStore
from investigator_agent.providers.anthropic import AnthropicProvider
from investigator_agent.tools.registry import ToolRegistry
from investigator_agent.tools.release_tools import (
    FILE_RISK_REPORT_SCHEMA,
    GET_RELEASE_SUMMARY_SCHEMA,
    file_risk_report,
    get_release_summary,
)
from evals import ALL_SCENARIOS
from evals.evaluator import Evaluator
from evals.reporters import (
    generate_markdown_report,
    print_summary,
    save_report,
)


async def main():
    """Run evaluation suite and generate reports."""
    # Setup agent with tools
    config = Config.from_env()

    # Initialize observability
    from investigator_agent.observability.tracer import setup_tracer
    setup_tracer(config.traces_dir)

    provider = AnthropicProvider(config.api_key, config.model)
    store = ConversationStore(config.conversations_dir)

    registry = ToolRegistry()
    registry.register(
        name="get_release_summary",
        description="Retrieve release information",
        input_schema=GET_RELEASE_SUMMARY_SCHEMA,
        handler=get_release_summary,
    )
    registry.register(
        name="file_risk_report",
        description="File a risk assessment report",
        input_schema=FILE_RISK_REPORT_SCHEMA,
        handler=file_risk_report,
    )

    agent = Agent(provider, store, config, tool_registry=registry)

    # Create evaluator
    evaluator = Evaluator(pass_threshold=0.7)

    # Run evaluation suite
    print("Running evaluation suite...")
    print(f"Scenarios: {len(ALL_SCENARIOS)}")
    print()

    results = await evaluator.run_suite(agent, ALL_SCENARIOS)

    # Print summary to console
    print_summary(results)

    # Generate and save Markdown report
    markdown = generate_markdown_report(results)
    save_report(markdown, "data/reports/evaluation_results.md")
    print("Markdown report saved to: data/reports/evaluation_results.md")

    # Optionally save baseline (only in interactive mode)
    try:
        save_baseline = input("\nSave as baseline? (y/n): ")
        if save_baseline.lower() == "y":
            version = input("Version name: ")
            evaluator.save_baseline(results, version)
            print(f"Baseline saved as: data/baselines/{version}.json")

        # Optionally compare to baseline
        compare = input("\nCompare to baseline? (y/n): ")
        if compare.lower() == "y":
            version = input("Baseline version: ")
            baseline = evaluator.load_baseline(version)
            if baseline:
                comparison = evaluator.compare_to_baseline(results, baseline)
                print(f"\n{comparison.summary}")
                if comparison.regressions:
                    print("\n⚠️  Regressions:")
                    for reg in comparison.regressions:
                        print(f"  - {reg}")
                if comparison.improvements:
                    print("\n✅ Improvements:")
                    for imp in comparison.improvements:
                        print(f"  - {imp}")
            else:
                print(f"Baseline '{version}' not found")
    except EOFError:
        # Running non-interactively, skip prompts
        print("\nRunning in non-interactive mode - skipping baseline operations")


if __name__ == "__main__":
    asyncio.run(main())
