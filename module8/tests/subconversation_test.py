"""Tests for SubConversationManager."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from investigator_agent.context.subconversation import SubConversationManager
from investigator_agent.models import SubConversation
from investigator_agent.providers.anthropic import AnthropicProvider


@pytest.fixture
def mock_provider():
    """Create a mock Anthropic provider."""
    with patch("investigator_agent.providers.anthropic.AsyncAnthropic"), patch(
        "investigator_agent.providers.anthropic.get_tracer"
    ) as mock_tracer:
        # Mock the tracer
        mock_tracer.return_value = Mock()

        provider = AnthropicProvider(api_key="test-key", model="claude-3-haiku-20240307")
        # Create a mock response
        mock_response = Mock()
        mock_response.content = "Test analysis response"
        mock_response.usage = Mock(input_tokens=100, output_tokens=50)
        mock_response.stop_reason = "end_turn"

        # Mock the generate method
        provider.generate = AsyncMock(return_value=mock_response)

        yield provider


@pytest.mark.asyncio
async def test_analyze_in_subconversation(mock_provider):
    """Test creating and executing a sub-conversation."""
    manager = SubConversationManager(provider=mock_provider)

    content = "This is a large documentation file with important information."
    purpose = "Analyze architecture documentation"
    analysis_prompt = "What are the key architectural components?"

    sub_conv = await manager.analyze_in_subconversation(
        parent_conversation_id="parent-123",
        content=content,
        purpose=purpose,
        analysis_prompt=analysis_prompt,
    )

    # Verify sub-conversation structure
    assert isinstance(sub_conv, SubConversation)
    assert sub_conv.parent_id == "parent-123"
    assert sub_conv.purpose == purpose
    assert sub_conv.system_prompt != ""

    # Verify messages were added
    assert len(sub_conv.messages) == 2  # User + Assistant (summarization happens separately)
    assert sub_conv.messages[0].role == "user"
    assert sub_conv.messages[1].role == "assistant"

    # Verify completion
    assert sub_conv.completed_at is not None
    assert sub_conv.summary != ""
    assert sub_conv.token_count > 0


@pytest.mark.asyncio
async def test_subconversation_includes_content(mock_provider):
    """Test that sub-conversation includes the document content."""
    manager = SubConversationManager(provider=mock_provider)

    content = "Specific content that should be included"
    sub_conv = await manager.analyze_in_subconversation(
        parent_conversation_id="parent-123",
        content=content,
        purpose="Test",
        analysis_prompt="What does this say?",
    )

    # Check that content was included in the user message
    user_message = sub_conv.messages[0].get_text_content()
    assert "Specific content that should be included" in user_message


@pytest.mark.asyncio
async def test_subconversation_includes_prompt(mock_provider):
    """Test that sub-conversation includes the analysis prompt."""
    manager = SubConversationManager(provider=mock_provider)

    analysis_prompt = "What are the security considerations?"
    sub_conv = await manager.analyze_in_subconversation(
        parent_conversation_id="parent-123",
        content="Some document content",
        purpose="Security review",
        analysis_prompt=analysis_prompt,
    )

    # Check that prompt was included
    user_message = sub_conv.messages[0].get_text_content()
    assert "security considerations" in user_message.lower()


@pytest.mark.asyncio
async def test_subconversation_no_tools(mock_provider):
    """Test that sub-conversations don't use tools."""
    manager = SubConversationManager(provider=mock_provider)

    sub_conv = await manager.analyze_in_subconversation(
        parent_conversation_id="parent-123",
        content="Test content",
        purpose="Test",
        analysis_prompt="Test prompt",
    )

    # Sub-conversation should complete successfully without tool use
    assert sub_conv.completed_at is not None
    # Verify generate was called with empty tools list
    assert mock_provider.generate.called
    for call_args in mock_provider.generate.call_args_list:
        assert call_args[1]["tools"] == []


@pytest.mark.asyncio
async def test_build_analysis_system_prompt(mock_provider):
    """Test the analysis system prompt builder."""
    manager = SubConversationManager(provider=mock_provider)

    system_prompt = manager._build_analysis_system_prompt()

    # Should include key instructions
    assert "analysis" in system_prompt.lower()
    assert "document" in system_prompt.lower()
    assert "concise" in system_prompt.lower()


@pytest.mark.asyncio
async def test_build_summarization_prompt(mock_provider):
    """Test the summarization prompt builder."""
    manager = SubConversationManager(provider=mock_provider)

    # Create a simple sub-conversation
    sub_conv = SubConversation(
        id="sub-123",
        parent_id="parent-123",
        purpose="Test",
        system_prompt="Test prompt",
    )
    sub_conv.add_message("user", "What is the main idea?\n\n<document>Test doc</document>")
    sub_conv.add_message("assistant", "The main idea is testing.")

    prompt = manager._build_summarization_prompt(sub_conv)

    # Should include key elements
    assert "summarize" in prompt.lower()
    assert "10:1" in prompt or "10" in prompt
    assert "main idea" in prompt.lower()
    assert "testing" in prompt.lower()


@pytest.mark.asyncio
async def test_subconversation_token_count(mock_provider):
    """Test that token count is calculated."""
    manager = SubConversationManager(provider=mock_provider)

    sub_conv = await manager.analyze_in_subconversation(
        parent_conversation_id="parent-123",
        content="Test content for token counting",
        purpose="Test",
        analysis_prompt="Analyze this",
    )

    # Token count should be positive
    assert sub_conv.token_count > 0
    # Should be reasonable (at least covers the messages)
    assert sub_conv.token_count > 10


@pytest.mark.asyncio
async def test_subconversation_unique_ids(mock_provider):
    """Test that sub-conversations get unique IDs."""
    manager = SubConversationManager(provider=mock_provider)

    sub_conv1 = await manager.analyze_in_subconversation(
        parent_conversation_id="parent-123",
        content="Content 1",
        purpose="Test 1",
        analysis_prompt="Test",
    )

    sub_conv2 = await manager.analyze_in_subconversation(
        parent_conversation_id="parent-123",
        content="Content 2",
        purpose="Test 2",
        analysis_prompt="Test",
    )

    # IDs should be different
    assert sub_conv1.id != sub_conv2.id
    # Both should have same parent
    assert sub_conv1.parent_id == sub_conv2.parent_id


@pytest.mark.asyncio
async def test_subconversation_preserves_purpose(mock_provider):
    """Test that purpose is preserved in sub-conversation."""
    manager = SubConversationManager(provider=mock_provider)

    purpose = "Detailed architecture analysis for feature FEAT-MS-001"
    sub_conv = await manager.analyze_in_subconversation(
        parent_conversation_id="parent-123",
        content="Architecture doc",
        purpose=purpose,
        analysis_prompt="What are the components?",
    )

    assert sub_conv.purpose == purpose
