"""End-to-end integration test for tool execution loop with release tools."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from investigator_agent.agent import Agent
from investigator_agent.config import Config
from investigator_agent.models import ToolCall
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
def tool_registry():
    """Create a tool registry with release tools registered."""
    registry = ToolRegistry()

    # Register get_release_summary tool
    registry.register(
        name="get_release_summary",
        description="Retrieve information about a software release",
        input_schema=GET_RELEASE_SUMMARY_SCHEMA,
        handler=get_release_summary,
    )

    # Register file_risk_report tool
    registry.register(
        name="file_risk_report",
        description="File a risk assessment report for a release",
        input_schema=FILE_RISK_REPORT_SCHEMA,
        handler=file_risk_report,
    )

    return registry


@pytest.mark.asyncio
@patch("investigator_agent.providers.anthropic.AsyncAnthropic")
async def test_full_tool_loop_with_release_assessment(
    mock_anthropic, tmp_path, tool_registry
):
    """Test a complete tool loop: check release -> assess risk -> file report."""
    # Setup config and store
    config = Config(api_key="test-key", max_tokens=4096)
    config.conversations_dir = tmp_path
    store = ConversationStore(config.conversations_dir)

    # Create mock client
    mock_client = Mock()

    # Step 1: Initial response with tool call to get_release_summary
    text_block_1 = Mock()
    text_block_1.type = "text"
    text_block_1.text = "Let me check the release information."

    tool_block_1 = Mock()
    tool_block_1.type = "tool_use"
    tool_block_1.id = "tool_001"
    tool_block_1.name = "get_release_summary"
    tool_block_1.input = {"release_id": "rel-003"}

    mock_response_1 = Mock()
    mock_response_1.content = [text_block_1, tool_block_1]
    mock_response_1.usage = Mock(input_tokens=50, output_tokens=30)
    mock_response_1.stop_reason = "tool_use"

    # Step 2: After getting release info, call file_risk_report
    text_block_2 = Mock()
    text_block_2.type = "text"
    text_block_2.text = "I see several concerning issues. Filing a report."

    tool_block_2 = Mock()
    tool_block_2.type = "tool_use"
    tool_block_2.id = "tool_002"
    tool_block_2.name = "file_risk_report"
    tool_block_2.input = {
        "release_id": "rel-003",
        "severity": "high",
        "findings": [
            "12 test failures out of 135 tests",
            "Error rate of 6.5% is significantly elevated",
            "Response time p95 of 890ms exceeds acceptable threshold",
            "Major authentication refactor increases risk",
        ],
    }

    mock_response_2 = Mock()
    mock_response_2.content = [text_block_2, tool_block_2]
    mock_response_2.usage = Mock(input_tokens=200, output_tokens=50)
    mock_response_2.stop_reason = "tool_use"

    # Step 3: Final response after filing report
    text_block_3 = Mock()
    text_block_3.type = "text"
    text_block_3.text = (
        "I've assessed release rel-003 (v2.3.0) and filed a HIGH severity risk report. "
        "Key concerns: 12 test failures, 6.5% error rate, and slow response times. "
        "I recommend addressing these issues before deployment."
    )

    mock_response_3 = Mock()
    mock_response_3.content = [text_block_3]
    mock_response_3.usage = Mock(input_tokens=300, output_tokens=60)
    mock_response_3.stop_reason = "end_turn"

    # Set up mock to return responses in sequence
    mock_client.messages.create = AsyncMock(
        side_effect=[mock_response_1, mock_response_2, mock_response_3]
    )
    mock_anthropic.return_value = mock_client

    # Create agent with tools
    provider = AnthropicProvider(config.api_key, config.model)
    agent = Agent(provider, store, config, tool_registry=tool_registry)

    # Start conversation
    conv = agent.new_conversation()
    response = await agent.send_message(
        conv, "Assess the risk of deploying release rel-003"
    )

    # Verify final response
    assert "HIGH severity" in response or "high severity" in response.lower()
    assert "rel-003" in response

    # Verify conversation history structure
    messages = conv.messages
    # Should have: user message, assistant with tool_use, tool_result,
    # assistant with tool_use, tool_result, final assistant text
    assert len(messages) >= 6

    # Verify first tool call (get_release_summary)
    assert messages[1].role == "assistant"
    assert isinstance(messages[1].content, list)
    tool_use_blocks = [b for b in messages[1].content if b.get("type") == "tool_use"]
    assert len(tool_use_blocks) == 1
    assert tool_use_blocks[0]["name"] == "get_release_summary"

    # Verify tool result message
    assert messages[2].role == "user"
    assert isinstance(messages[2].content, list)
    tool_result_blocks = [b for b in messages[2].content if b.get("type") == "tool_result"]
    assert len(tool_result_blocks) == 1
    assert "v2.3.0" in tool_result_blocks[0]["content"]

    # Verify API was called 3 times (initial + 2 tool loops)
    assert mock_client.messages.create.call_count == 3

    # Verify tools were passed in API calls
    first_call_kwargs = mock_client.messages.create.call_args_list[0][1]
    assert "tools" in first_call_kwargs
    assert len(first_call_kwargs["tools"]) == 2


@pytest.mark.asyncio
@patch("investigator_agent.providers.anthropic.AsyncAnthropic")
async def test_tool_execution_with_single_tool_call(mock_anthropic, tmp_path, tool_registry):
    """Test tool loop with a single tool call."""
    config = Config(api_key="test-key", max_tokens=4096)
    config.conversations_dir = tmp_path
    store = ConversationStore(config.conversations_dir)

    mock_client = Mock()

    # Response with single tool call
    text_block = Mock()
    text_block.type = "text"
    text_block.text = "Getting release information..."

    tool_block = Mock()
    tool_block.type = "tool_use"
    tool_block.id = "tool_123"
    tool_block.name = "get_release_summary"
    tool_block.input = {"release_id": "rel-001"}

    mock_response_1 = Mock()
    mock_response_1.content = [text_block, tool_block]
    mock_response_1.usage = Mock(input_tokens=20, output_tokens=15)
    mock_response_1.stop_reason = "tool_use"

    # Final response
    final_text = Mock()
    final_text.type = "text"
    final_text.text = "Release rel-001 (v2.1.0) looks good with 142 passing tests."

    mock_response_2 = Mock()
    mock_response_2.content = [final_text]
    mock_response_2.usage = Mock(input_tokens=100, output_tokens=20)
    mock_response_2.stop_reason = "end_turn"

    mock_client.messages.create = AsyncMock(side_effect=[mock_response_1, mock_response_2])
    mock_anthropic.return_value = mock_client

    provider = AnthropicProvider(config.api_key, config.model)
    agent = Agent(provider, store, config, tool_registry=tool_registry)

    conv = agent.new_conversation()
    response = await agent.send_message(conv, "Tell me about release rel-001")

    # Verify response
    assert "rel-001" in response or "v2.1.0" in response

    # Verify 2 API calls (1 with tool, 1 final)
    assert mock_client.messages.create.call_count == 2

    # Verify conversation has proper structure
    assert len(conv.messages) == 4  # user, assistant+tool, tool_result, assistant
