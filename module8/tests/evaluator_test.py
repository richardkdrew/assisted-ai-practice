"""Tests for InvestigatorEvaluator."""
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from investigator_agent.evaluations.evaluator import (
    InvestigatorEvaluator,
    EvaluationResult,
    SuiteResults,
    Comparison,
)
from investigator_agent.evaluations.scenarios import (
    EvaluationScenario,
    SCENARIO_READY_FOR_PRODUCTION,
)
from investigator_agent.models import Conversation, Message


class TestInvestigatorEvaluator:
    """Test evaluation system."""

    def test_init_default_threshold(self):
        """Test evaluator initializes with default threshold."""
        evaluator = InvestigatorEvaluator()
        assert evaluator.pass_threshold == 0.7

    def test_init_custom_threshold(self):
        """Test evaluator initializes with custom threshold."""
        evaluator = InvestigatorEvaluator(pass_threshold=0.8)
        assert evaluator.pass_threshold == 0.8

    def test_extract_tool_calls_empty_conversation(self):
        """Test extracting tools from empty conversation."""
        evaluator = InvestigatorEvaluator()
        conversation = Conversation(
            id="conv_1",
            messages=[],
            created_at=datetime.now()
        )

        tools = evaluator._extract_tool_calls(conversation)
        assert tools == []

    def test_extract_tool_calls_with_tools(self):
        """Test extracting tools from conversation with tool_use blocks."""
        evaluator = InvestigatorEvaluator()

        messages = [
            Message(role="user", content="test"),
            Message(role="assistant", content=[
                {"type": "tool_use", "name": "get_jira_data", "id": "1"},
                {"type": "text", "text": "checking"}
            ]),
            Message(role="user", content="result"),
            Message(role="assistant", content=[
                {"type": "tool_use", "name": "get_analysis", "id": "2"}
            ]),
        ]

        conversation = Conversation(
            id="conv_1",
            messages=messages,
            created_at=datetime.now()
        )

        tools = evaluator._extract_tool_calls(conversation)
        assert tools == ["get_jira_data", "get_analysis"]

    def test_extract_decision_ready(self):
        """Test extracting 'ready' decision from response."""
        evaluator = InvestigatorEvaluator()

        response = "The feature is ready for production deployment."
        assert evaluator._extract_decision(response) == "ready"

        response = "This is production ready and meets all criteria."
        assert evaluator._extract_decision(response) == "ready"

    def test_extract_decision_not_ready(self):
        """Test extracting 'not_ready' decision from response."""
        evaluator = InvestigatorEvaluator()

        response = "The feature is not ready for production."
        assert evaluator._extract_decision(response) == "not_ready"

        response = "Not production-ready due to test failures."
        assert evaluator._extract_decision(response) == "not_ready"

    def test_extract_decision_borderline(self):
        """Test extracting 'borderline' decision from response."""
        evaluator = InvestigatorEvaluator()

        response = "This is a borderline case with mixed signals."
        assert evaluator._extract_decision(response) == "borderline"

        response = "The feature has mixed signals from UAT."
        assert evaluator._extract_decision(response) == "borderline"

    def test_extract_decision_no_clear_decision(self):
        """Test extracting decision when none is clear."""
        evaluator = InvestigatorEvaluator()

        response = "The feature has some issues to address."
        # Should return None or default
        decision = evaluator._extract_decision(response)
        assert decision is None or decision in ["ready", "not_ready", "borderline"]

    def test_is_adjacent_decision_borderline_to_ready(self):
        """Test borderline is adjacent to ready."""
        evaluator = InvestigatorEvaluator()
        assert evaluator._is_adjacent_decision("borderline", "ready") is True

    def test_is_adjacent_decision_borderline_to_not_ready(self):
        """Test borderline is adjacent to not_ready."""
        evaluator = InvestigatorEvaluator()
        assert evaluator._is_adjacent_decision("borderline", "not_ready") is True

    def test_is_adjacent_decision_ready_to_borderline(self):
        """Test ready is adjacent to borderline."""
        evaluator = InvestigatorEvaluator()
        assert evaluator._is_adjacent_decision("ready", "borderline") is True

    def test_is_adjacent_decision_not_adjacent(self):
        """Test non-adjacent decisions."""
        evaluator = InvestigatorEvaluator()
        assert evaluator._is_adjacent_decision("ready", "not_ready") is False
        assert evaluator._is_adjacent_decision("not_ready", "ready") is False

    def test_is_adjacent_decision_none(self):
        """Test with None decision."""
        evaluator = InvestigatorEvaluator()
        assert evaluator._is_adjacent_decision(None, "ready") is False

    def test_eval_feature_identification_exact_match(self):
        """Test feature identification with exact match in response."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[],
            created_at=datetime.now()
        )

        response = "Feature FEAT-MS-001 is production ready."

        score = evaluator._eval_feature_identification(conversation, response, scenario)
        assert score == 1.0

    def test_eval_feature_identification_case_insensitive(self):
        """Test feature identification is case-insensitive."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[],
            created_at=datetime.now()
        )

        response = "Feature feat-ms-001 looks good."

        score = evaluator._eval_feature_identification(conversation, response, scenario)
        assert score == 1.0

    def test_eval_feature_identification_jira_called(self):
        """Test partial credit when JIRA tool called but feature not in response."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[
                Message(role="user", content="test"),
                Message(role="assistant", content=[
                    {"type": "tool_use", "name": "get_jira_data", "id": "1"}
                ])
            ],
            created_at=datetime.now()
        )

        response = "The feature is ready."

        score = evaluator._eval_feature_identification(conversation, response, scenario)
        assert score == 0.8  # Partial credit

    def test_eval_feature_identification_no_match(self):
        """Test zero score when feature not identified."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[],
            created_at=datetime.now()
        )

        response = "Some generic response."

        score = evaluator._eval_feature_identification(conversation, response, scenario)
        assert score == 0.0

    def test_eval_tool_usage_perfect_match(self):
        """Test tool usage F1 score with perfect match."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=["get_jira_data", "get_analysis", "read_doc"],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[
                Message(role="assistant", content=[
                    {"type": "tool_use", "name": "get_jira_data", "id": "1"},
                    {"type": "tool_use", "name": "get_analysis", "id": "2"},
                    {"type": "tool_use", "name": "read_doc", "id": "3"}
                ])
            ],
            created_at=datetime.now()
        )

        score = evaluator._eval_tool_usage(conversation, scenario)
        # Precision = 3/3 = 1.0, Recall = 3/3 = 1.0, F1 = 1.0
        assert score == 1.0

    def test_eval_tool_usage_missing_tool(self):
        """Test tool usage F1 score with missing expected tool."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=["get_jira_data", "get_analysis"],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[
                Message(role="assistant", content=[
                    {"type": "tool_use", "name": "get_jira_data", "id": "1"}
                ])
            ],
            created_at=datetime.now()
        )

        score = evaluator._eval_tool_usage(conversation, scenario)
        # Precision = 1/1 = 1.0, Recall = 1/2 = 0.5, F1 = 2*1*0.5/(1+0.5) = 0.67
        assert 0.66 < score < 0.68

    def test_eval_tool_usage_extra_tool(self):
        """Test tool usage F1 score with unexpected tool."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=["get_jira_data"],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[
                Message(role="assistant", content=[
                    {"type": "tool_use", "name": "get_jira_data", "id": "1"},
                    {"type": "tool_use", "name": "list_docs", "id": "2"}
                ])
            ],
            created_at=datetime.now()
        )

        score = evaluator._eval_tool_usage(conversation, scenario)
        # Precision = 1/2 = 0.5, Recall = 1/1 = 1.0, F1 = 2*0.5*1/(0.5+1) = 0.67
        assert 0.66 < score < 0.68

    def test_eval_tool_usage_no_tools_expected_or_called(self):
        """Test tool usage when no tools expected or called."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[],
            created_at=datetime.now()
        )

        score = evaluator._eval_tool_usage(conversation, scenario)
        assert score == 1.0  # Perfect match when both empty

    def test_eval_tool_usage_no_tools_called_when_expected(self):
        """Test zero score when expected tools not called."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=["get_jira_data"],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[],
            created_at=datetime.now()
        )

        score = evaluator._eval_tool_usage(conversation, scenario)
        assert score == 0.0

    def test_eval_decision_quality_exact_match_with_keywords(self):
        """Test decision quality with exact match and all keywords."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=["tests", "passing", "approved"],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        response = "The feature is ready for production. All tests are passing and stakeholders have approved it."

        score = evaluator._eval_decision_quality(response, scenario)
        # Exact match (0.6) + 3/3 keywords (0.4) = 1.0
        assert score == 1.0

    def test_eval_decision_quality_exact_match_partial_keywords(self):
        """Test decision quality with exact match and some keywords."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=["tests", "security", "approved"],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        response = "The feature is ready for production. Tests are passing."

        score = evaluator._eval_decision_quality(response, scenario)
        # Exact match (0.6) + 1/3 keywords (0.4 * 0.33) = 0.73
        assert 0.72 < score < 0.74

    def test_eval_decision_quality_partial_credit_adjacent(self):
        """Test decision quality with adjacent decision (partial credit)."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        response = "This is a borderline case with some concerns."

        score = evaluator._eval_decision_quality(response, scenario)
        # Adjacent decision gets 0.3 partial credit, no keywords
        assert score == 0.3

    def test_eval_decision_quality_wrong_decision(self):
        """Test decision quality with completely wrong decision."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=[],
            expected_sub_conversations=False,
            expected_memory_retrieval=False,
            description="test"
        )

        response = "The feature is not ready for production."

        score = evaluator._eval_decision_quality(response, scenario)
        # Wrong decision (not adjacent), no keywords
        assert score == 0.0

    def test_eval_context_management_correct_usage(self):
        """Test context management when used correctly."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=[],
            expected_sub_conversations=True,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[],
            created_at=datetime.now()
        )
        conversation.sub_conversations = [MagicMock()]  # Has sub-conversation

        score = evaluator._eval_context_management(conversation, scenario)
        assert score == 1.0

    def test_eval_context_management_incorrect_usage(self):
        """Test context management when used incorrectly."""
        evaluator = InvestigatorEvaluator()

        scenario = EvaluationScenario(
            id="test",
            feature_id="FEAT-MS-001",
            user_query="test",
            expected_decision="ready",
            expected_tools=[],
            expected_justification_includes=[],
            expected_sub_conversations=True,
            expected_memory_retrieval=False,
            description="test"
        )

        conversation = Conversation(
            id="conv_1",
            messages=[],
            created_at=datetime.now()
        )
        # No sub-conversations when expected

        score = evaluator._eval_context_management(conversation, scenario)
        assert score == 0.5  # Penalty for incorrect usage

    @pytest.mark.asyncio
    async def test_run_scenario_success(self):
        """Test running a scenario successfully."""
        evaluator = InvestigatorEvaluator(pass_threshold=0.7)

        # Mock agent
        mock_agent = MagicMock()
        mock_agent.new_conversation = MagicMock(return_value=Conversation(
            id="conv_1",
            messages=[
                Message(role="assistant", content=[
                    {"type": "tool_use", "name": "get_jira_data", "id": "1"}
                ])
            ],
            created_at=datetime.now()
        ))
        mock_agent.send_message = AsyncMock(
            return_value="Feature FEAT-MS-001 is ready for production. Tests are passing."
        )

        result = await evaluator.run_scenario(mock_agent, SCENARIO_READY_FOR_PRODUCTION)

        assert result.scenario_id == "ready_for_production"
        assert isinstance(result.passed, bool)
        assert "feature_identification" in result.scores
        assert "tool_usage" in result.scores
        assert "decision_quality" in result.scores
        assert "context_management" in result.scores
        assert "overall" in result.scores
        assert result.duration > 0
        assert result.error is None

    @pytest.mark.asyncio
    async def test_run_scenario_error_handling(self):
        """Test scenario handles errors gracefully."""
        evaluator = InvestigatorEvaluator()

        # Mock agent that raises error
        mock_agent = MagicMock()
        mock_agent.new_conversation = MagicMock(side_effect=Exception("Test error"))

        result = await evaluator.run_scenario(mock_agent, SCENARIO_READY_FOR_PRODUCTION)

        assert result.scenario_id == "ready_for_production"
        assert result.passed is False
        assert result.scores["overall"] == 0.0
        assert result.error == "Test error"

    @pytest.mark.asyncio
    async def test_run_suite_multiple_scenarios(self):
        """Test running suite with multiple scenarios."""
        evaluator = InvestigatorEvaluator()

        # Mock agent
        mock_agent = MagicMock()
        mock_agent.new_conversation = MagicMock(return_value=Conversation(
            id="conv_1",
            messages=[],
            created_at=datetime.now()
        ))
        mock_agent.send_message = AsyncMock(return_value="Feature is ready")

        scenarios = [
            SCENARIO_READY_FOR_PRODUCTION,
            SCENARIO_READY_FOR_PRODUCTION,  # Use same scenario twice for simplicity
        ]

        results = await evaluator.run_suite(mock_agent, scenarios)

        assert results.total_scenarios == 2
        assert isinstance(results.passed, int)
        assert 0.0 <= results.pass_rate <= 1.0
        assert len(results.avg_scores) > 0
        assert len(results.scenario_results) == 2
        assert results.duration > 0

    def test_save_and_load_baseline(self, tmp_path):
        """Test saving and loading baseline."""
        evaluator = InvestigatorEvaluator()

        # Create results
        results = SuiteResults(
            total_scenarios=8,
            passed=6,
            pass_rate=0.75,
            avg_scores={
                "feature_identification": 0.85,
                "tool_usage": 0.72,
                "decision_quality": 0.68,
                "context_management": 0.90,
                "overall": 0.74
            },
            scenario_results=[],
            duration=25.5,
            metadata={"version": "1.0"}
        )

        # Save baseline
        baseline_path = tmp_path / "baselines"
        baseline_path.mkdir()

        with patch('investigator_agent.evaluations.evaluator.Path', return_value=baseline_path):
            evaluator.save_baseline(results, "v1")

        # Load baseline
        baseline_file = baseline_path / "v1.json"
        assert baseline_file.exists()

        with open(baseline_file) as f:
            loaded = json.load(f)

        assert loaded["version"] == "v1"
        assert loaded["total_scenarios"] == 8
        assert loaded["passed"] == 6
        assert loaded["pass_rate"] == 0.75
        assert loaded["avg_scores"]["overall"] == 0.74

    def test_load_baseline_not_found(self):
        """Test loading non-existent baseline returns None."""
        evaluator = InvestigatorEvaluator()
        loaded = evaluator.load_baseline("nonexistent_version")
        assert loaded is None

    def test_compare_to_baseline_no_regression(self):
        """Test comparison when no regression detected."""
        evaluator = InvestigatorEvaluator()

        current = SuiteResults(
            total_scenarios=8,
            passed=7,
            pass_rate=0.875,
            avg_scores={"overall": 0.75, "feature_identification": 0.85},
            scenario_results=[],
            duration=20.0
        )

        baseline_data = {
            "pass_rate": 0.80,
            "avg_scores": {"overall": 0.73, "feature_identification": 0.83}
        }

        comparison = evaluator.compare_to_baseline(current, baseline_data)

        assert comparison.pass_rate_delta > 0
        assert comparison.score_deltas["overall"] > 0
        assert len(comparison.regressions) == 0
        assert "improvement" in comparison.summary.lower() or "no significant" in comparison.summary.lower()

    def test_compare_to_baseline_regression_detected(self):
        """Test comparison when regression detected (>5% drop)."""
        evaluator = InvestigatorEvaluator()

        current = SuiteResults(
            total_scenarios=8,
            passed=4,
            pass_rate=0.50,
            avg_scores={"overall": 0.60},
            scenario_results=[],
            duration=20.0
        )

        baseline_data = {
            "pass_rate": 0.80,
            "avg_scores": {"overall": 0.75}
        }

        comparison = evaluator.compare_to_baseline(current, baseline_data)

        assert comparison.pass_rate_delta < -0.05
        assert comparison.score_deltas["overall"] < -0.05
        assert len(comparison.regressions) > 0
        assert "regression" in comparison.summary.lower()

    def test_compare_to_baseline_improvement_detected(self):
        """Test comparison when improvement detected (>5% gain)."""
        evaluator = InvestigatorEvaluator()

        current = SuiteResults(
            total_scenarios=8,
            passed=8,
            pass_rate=1.0,
            avg_scores={"overall": 0.90},
            scenario_results=[],
            duration=20.0
        )

        baseline_data = {
            "pass_rate": 0.75,
            "avg_scores": {"overall": 0.70}
        }

        comparison = evaluator.compare_to_baseline(current, baseline_data)

        assert comparison.pass_rate_delta > 0.05
        assert comparison.score_deltas["overall"] > 0.05
        assert len(comparison.improvements) > 0
        assert "improvement" in comparison.summary.lower()
