"""Tests for evaluation framework."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from investigator_agent.agent import Agent
from investigator_agent.config import Config
from evals.evaluator import Evaluator
from evals.scenarios import HIGH_RISK_SCENARIO, LOW_RISK_SCENARIO
from investigator_agent.persistence.store import ConversationStore
from investigator_agent.providers.anthropic import AnthropicProvider
from investigator_agent.tools.registry import ToolRegistry
from investigator_agent.tools.release_tools import (
    FILE_RISK_REPORT_SCHEMA,
    GET_RELEASE_SUMMARY_SCHEMA,
    file_risk_report,
    get_release_summary,
)


@pytest.fixture
def evaluator():
    """Create an evaluator for testing."""
    return Evaluator(pass_threshold=0.7)


@pytest.fixture
def mock_agent_with_tools(tmp_path):
    """Create a mock agent with tools for testing."""
    # Setup tool registry
    registry = ToolRegistry()
    registry.register(
        name="get_release_summary",
        description="Get release info",
        input_schema=GET_RELEASE_SUMMARY_SCHEMA,
        handler=get_release_summary,
    )
    registry.register(
        name="file_risk_report",
        description="File risk report",
        input_schema=FILE_RISK_REPORT_SCHEMA,
        handler=file_risk_report,
    )

    # Create mock provider
    mock_provider = Mock()
    mock_provider.get_text_content = Mock(
        return_value="I assessed release rel-003 and determined it has HIGH severity risk."
    )
    mock_provider.extract_tool_calls = Mock(return_value=[])
    mock_provider.send_message = AsyncMock()

    # Setup config and store
    config = Config(api_key="test-key", max_tokens=4096)
    config.conversations_dir = tmp_path
    store = ConversationStore(config.conversations_dir)

    # Create agent
    agent = Agent(mock_provider, store, config, tool_registry=registry)

    return agent, mock_provider


def test_extract_severity_explicit(evaluator):
    """Test extracting explicit severity from response."""
    assert evaluator._extract_severity("HIGH severity risk") == "high"
    assert evaluator._extract_severity("This is MEDIUM severity") == "medium"
    assert evaluator._extract_severity("Severity: low for this release") == "low"


def test_extract_severity_implicit(evaluator):
    """Test extracting implicit severity."""
    assert evaluator._extract_severity("The risk is high") == "high"
    assert evaluator._extract_severity("medium risk detected") == "medium"
    assert evaluator._extract_severity("Looks low risk") == "low"


def test_extract_severity_not_found(evaluator):
    """Test when severity is not found."""
    assert evaluator._extract_severity("No severity mentioned") is None
    assert evaluator._extract_severity("Everything looks good") is None


def test_is_adjacent_severity(evaluator):
    """Test checking adjacent severity levels."""
    assert evaluator._is_adjacent_severity("medium", "high") is True
    assert evaluator._is_adjacent_severity("low", "medium") is True
    assert evaluator._is_adjacent_severity("high", "low") is False
    assert evaluator._is_adjacent_severity(None, "high") is False


def test_eval_tool_usage_all_correct(evaluator, mock_agent_with_tools):
    """Test tool usage evaluation when all expected tools are called."""
    agent, _ = mock_agent_with_tools
    conv = agent.new_conversation()

    # Simulate tool calls in conversation
    conv.add_message(
        "assistant",
        [
            {"type": "text", "text": "Let me check"},
            {"type": "tool_use", "id": "1", "name": "get_release_summary", "input": {}},
        ],
    )
    conv.add_message(
        "assistant",
        [
            {"type": "text", "text": "Filing report"},
            {"type": "tool_use", "id": "2", "name": "file_risk_report", "input": {}},
        ],
    )

    score = evaluator._eval_tool_usage(
        conv, ["get_release_summary", "file_risk_report"]
    )
    assert score == 1.0


def test_eval_tool_usage_missing_tools(evaluator, mock_agent_with_tools):
    """Test tool usage evaluation when tools are missing."""
    agent, _ = mock_agent_with_tools
    conv = agent.new_conversation()

    # Only one tool called
    conv.add_message(
        "assistant",
        [
            {"type": "text", "text": "Checking"},
            {"type": "tool_use", "id": "1", "name": "get_release_summary", "input": {}},
        ],
    )

    score = evaluator._eval_tool_usage(
        conv, ["get_release_summary", "file_risk_report"]
    )
    assert score == 0.5  # Called 1 of 2 expected


def test_eval_tool_usage_no_tools_called(evaluator, mock_agent_with_tools):
    """Test tool usage evaluation when no tools called."""
    agent, _ = mock_agent_with_tools
    conv = agent.new_conversation()

    conv.add_message("assistant", "Just text, no tools")

    score = evaluator._eval_tool_usage(
        conv, ["get_release_summary", "file_risk_report"]
    )
    assert score == 0.0


def test_eval_decision_quality_perfect_match(evaluator, mock_agent_with_tools):
    """Test decision quality when everything matches."""
    agent, _ = mock_agent_with_tools
    conv = agent.new_conversation()

    response = "I found HIGH severity risk due to test failures and error rate concerns"
    scenario = HIGH_RISK_SCENARIO

    score = evaluator._eval_decision_quality(conv, response, scenario)
    # Should get 0.6 for correct severity + some for keywords
    assert score >= 0.6


def test_eval_decision_quality_wrong_severity(evaluator, mock_agent_with_tools):
    """Test decision quality with wrong severity."""
    agent, _ = mock_agent_with_tools
    conv = agent.new_conversation()

    response = "This looks like LOW severity"
    scenario = HIGH_RISK_SCENARIO

    score = evaluator._eval_decision_quality(conv, response, scenario)
    # Should get 0 for severity, maybe some for keywords
    assert score < 0.6


def test_eval_decision_quality_adjacent_severity(evaluator, mock_agent_with_tools):
    """Test decision quality with adjacent severity (partial credit)."""
    agent, _ = mock_agent_with_tools
    conv = agent.new_conversation()

    response = "MEDIUM severity due to some issues"
    scenario = HIGH_RISK_SCENARIO  # Expects high

    score = evaluator._eval_decision_quality(conv, response, scenario)
    # Should get 0.3 for adjacent severity
    assert 0.3 <= score < 0.6


@pytest.mark.asyncio
@patch("investigator_agent.providers.anthropic.AsyncAnthropic")
async def test_run_scenario_success(mock_anthropic, tmp_path, evaluator):
    """Test running a successful scenario evaluation."""
    # Setup
    registry = ToolRegistry()
    registry.register(
        name="get_release_summary",
        description="Get release info",
        input_schema=GET_RELEASE_SUMMARY_SCHEMA,
        handler=get_release_summary,
    )
    registry.register(
        name="file_risk_report",
        description="File risk report",
        input_schema=FILE_RISK_REPORT_SCHEMA,
        handler=file_risk_report,
    )

    config = Config(api_key="test-key", max_tokens=4096)
    config.conversations_dir = tmp_path
    store = ConversationStore(config.conversations_dir)

    # Mock Anthropic responses
    mock_client = Mock()

    # Response 1: Get release info
    text_block_1 = Mock()
    text_block_1.type = "text"
    text_block_1.text = "Checking release"

    tool_block_1 = Mock()
    tool_block_1.type = "tool_use"
    tool_block_1.id = "tool_1"
    tool_block_1.name = "get_release_summary"
    tool_block_1.input = {"release_id": "rel-003"}

    response_1 = Mock()
    response_1.content = [text_block_1, tool_block_1]
    response_1.stop_reason = "tool_use"

    # Response 2: File report
    text_block_2 = Mock()
    text_block_2.type = "text"
    text_block_2.text = "Filing report"

    tool_block_2 = Mock()
    tool_block_2.type = "tool_use"
    tool_block_2.id = "tool_2"
    tool_block_2.name = "file_risk_report"
    tool_block_2.input = {
        "release_id": "rel-003",
        "severity": "high",
        "findings": ["test failures", "error rate"],
    }

    response_2 = Mock()
    response_2.content = [text_block_2, tool_block_2]
    response_2.stop_reason = "tool_use"

    # Response 3: Final
    text_block_3 = Mock()
    text_block_3.type = "text"
    text_block_3.text = "HIGH severity risk detected due to test failures and error rate"

    response_3 = Mock()
    response_3.content = [text_block_3]
    response_3.stop_reason = "end_turn"

    mock_client.messages.create = AsyncMock(
        side_effect=[response_1, response_2, response_3]
    )
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider(config.api_key, config.model)
    agent = Agent(provider, store, config, tool_registry=registry)

    # Run evaluation
    result = await evaluator.run_scenario(agent, HIGH_RISK_SCENARIO)

    # Verify result
    assert result.scenario_id == HIGH_RISK_SCENARIO.id
    assert result.error is None
    assert "tool_usage" in result.scores
    assert "decision_quality" in result.scores
    assert "overall" in result.scores


@pytest.mark.asyncio
async def test_run_suite(evaluator, mock_agent_with_tools):
    """Test running a suite of scenarios."""
    agent, mock_provider = mock_agent_with_tools

    # Configure mock responses for multiple scenarios
    # Simulate successful high risk assessment
    mock_provider.send_message.return_value = Mock(
        content=[
            Mock(
                type="text",
                text="HIGH severity risk due to test failures",
            )
        ]
    )

    scenarios = [HIGH_RISK_SCENARIO, LOW_RISK_SCENARIO]
    results = await evaluator.run_suite(agent, scenarios)

    assert results.total_scenarios == 2
    assert results.pass_rate >= 0.0
    assert results.pass_rate <= 1.0
    assert len(results.scenario_results) == 2
    assert "tool_usage" in results.avg_scores
    assert "decision_quality" in results.avg_scores
    assert "overall" in results.avg_scores


def test_save_and_load_baseline(evaluator, tmp_path, monkeypatch):
    """Test saving and loading baseline results."""
    # Change to temp directory for testing
    monkeypatch.chdir(tmp_path)

    from evals.evaluator import EvaluationResult, SuiteResults

    # Create mock results
    results = SuiteResults(
        total_scenarios=3,
        passed=2,
        pass_rate=0.67,
        avg_scores={"tool_usage": 0.8, "decision_quality": 0.75, "overall": 0.775},
        scenario_results=[],
        duration=10.5,
    )

    # Save baseline
    evaluator.save_baseline(results, "v1.0")

    # Load baseline
    loaded = evaluator.load_baseline("v1.0")

    assert loaded is not None
    assert loaded["pass_rate"] == 0.67
    assert loaded["total_scenarios"] == 3
    assert loaded["avg_scores"]["tool_usage"] == 0.8


def test_compare_to_baseline_regression(evaluator):
    """Test comparison detecting regressions."""
    from evals.evaluator import SuiteResults

    baseline = {
        "pass_rate": 0.8,
        "avg_scores": {"tool_usage": 0.85, "decision_quality": 0.80},
    }

    current = SuiteResults(
        total_scenarios=5,
        passed=3,
        pass_rate=0.6,  # Dropped from 0.8
        avg_scores={"tool_usage": 0.75, "decision_quality": 0.70},  # Both dropped
        scenario_results=[],
        duration=5.0,
    )

    comparison = evaluator.compare_to_baseline(current, baseline)

    assert comparison.pass_rate_delta < 0
    assert len(comparison.regressions) > 0
    assert "regression" in comparison.summary.lower()


def test_compare_to_baseline_improvement(evaluator):
    """Test comparison detecting improvements."""
    from evals.evaluator import SuiteResults

    baseline = {
        "pass_rate": 0.6,
        "avg_scores": {"tool_usage": 0.70, "decision_quality": 0.65},
    }

    current = SuiteResults(
        total_scenarios=5,
        passed=5,
        pass_rate=1.0,  # Improved from 0.6
        avg_scores={"tool_usage": 0.90, "decision_quality": 0.85},  # Both improved
        scenario_results=[],
        duration=5.0,
    )

    comparison = evaluator.compare_to_baseline(current, baseline)

    assert comparison.pass_rate_delta > 0
    assert len(comparison.improvements) > 0
    assert "improvement" in comparison.summary.lower()
