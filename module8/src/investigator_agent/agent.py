"""Core agent logic for managing conversations."""

from opentelemetry.trace import Link, SpanContext, TraceFlags

from investigator_agent.config import Config
from investigator_agent.context.manager import ContextManager
from investigator_agent.context.subconversation import SubConversationManager
from investigator_agent.context.tokens import count_tokens, should_create_subconversation
from investigator_agent.models import Conversation
from investigator_agent.observability.tracer import get_tracer, get_trace_id
from investigator_agent.persistence.store import ConversationStore
from investigator_agent.providers.base import BaseProvider
from investigator_agent.tools.registry import ToolRegistry


class Agent:
    """AI agent that manages conversations with an AI provider."""

    def __init__(
        self,
        provider: BaseProvider,
        store: ConversationStore,
        config: Config,
        tool_registry: ToolRegistry | None = None,
    ):
        """Initialize the agent with a provider, store, and config."""
        self.provider = provider
        self.store = store
        self.config = config
        self.tool_registry = tool_registry
        self.tracer = get_tracer()
        self.context_manager = ContextManager(max_messages=config.max_messages)
        self.subconversation_manager = SubConversationManager(provider=provider)

    async def send_message(self, conversation: Conversation, user_message: str) -> str:
        """
        Send a user message and get an assistant response.

        Args:
            conversation: The conversation to add messages to
            user_message: The user's message

        Returns:
            The assistant's response
        """
        # Create span links to previous traces in this session
        links = []
        if conversation.trace_ids:
            # Link to the most recent previous trace
            for trace_id_hex in conversation.trace_ids[-3:]:  # Link to last 3 traces
                try:
                    trace_id_int = int(trace_id_hex, 16)
                    span_context = SpanContext(
                        trace_id=trace_id_int,
                        span_id=1,  # Link to root span
                        is_remote=True,
                        trace_flags=TraceFlags(0x01),
                    )
                    links.append(Link(span_context))
                except ValueError:
                    pass  # Skip invalid trace IDs

        with self.tracer.start_as_current_span("send_message", links=links) as span:
            span.set_attribute("session.id", conversation.id)
            span.set_attribute("message_length", len(user_message))
            span.set_attribute("message_count", len(conversation.messages))

            conversation.add_message("user", user_message)

            # Store trace ID in conversation if not already set
            current_trace_id = get_trace_id()
            if not hasattr(conversation, "trace_id") or not conversation.trace_id:
                conversation.trace_id = current_trace_id

            # Track all trace IDs for this session
            if current_trace_id and current_trace_id not in conversation.trace_ids:
                conversation.trace_ids.append(current_trace_id)

            # Prepare tools if registry is available
            tools = None
            if self.tool_registry:
                tools = self.tool_registry.get_tool_definitions()
                span.set_attribute("tools.available", len(tools))

            # Tool execution loop
            max_iterations = 10
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                span.set_attribute("tool_loop.iteration", iteration)

                # Apply context window management
                truncated_messages, was_truncated = self.context_manager.truncate_messages(
                    conversation.messages
                )

                # Track context information in span
                context_info = self.context_manager.get_context_info(conversation.messages)
                span.set_attribute("context.total_messages", context_info["total_messages"])
                span.set_attribute("context.was_truncated", was_truncated)
                if was_truncated:
                    span.set_attribute(
                        "context.messages_dropped", context_info["messages_to_drop"]
                    )

                # Convert truncated messages to API format
                messages = [msg.to_dict() for msg in truncated_messages]
                response = await self.provider.send_message(
                    messages, self.config.max_tokens, system=self.config.system_prompt, tools=tools
                )

                # Extract tool calls from response
                tool_calls = self.provider.extract_tool_calls(response)
                span.set_attribute(f"tool_loop.iteration_{iteration}.tool_calls", len(tool_calls))

                # If no tool calls, we're done - extract text and add to conversation
                if not tool_calls:
                    response_text = self.provider.get_text_content(response)
                    conversation.add_message("assistant", response_text)

                    span.set_attribute("response_length", len(response_text))
                    span.set_attribute("total_messages", len(conversation.messages))
                    span.set_attribute("tool_loop.total_iterations", iteration)

                    self.store.save(conversation)
                    return response_text

                # We have tool calls - add assistant message with tool_use blocks
                # Convert content blocks to dictionaries for serialization
                content_blocks = []
                for block in response.content:
                    if hasattr(block, 'type'):
                        if block.type == "text":
                            content_blocks.append({"type": "text", "text": block.text})
                        elif block.type == "tool_use":
                            content_blocks.append({
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input,
                            })

                conversation.add_message("assistant", content_blocks)

                # Execute each tool call and collect results
                tool_results = []
                with self.tracer.start_as_current_span("execute_tools") as tool_span:
                    tool_span.set_attribute("tool_count", len(tool_calls))

                    for tool_call in tool_calls:
                        tool_span.set_attribute(f"tool.{tool_call.name}.called", True)

                        # Execute the tool
                        tool_result = await self.tool_registry.execute(tool_call)

                        # Check if result is large enough to warrant sub-conversation
                        result_tokens = count_tokens(tool_result.content)
                        tool_span.set_attribute(f"tool.{tool_call.name}.result_tokens", result_tokens)

                        if should_create_subconversation(result_tokens):
                            # Large result - analyze in sub-conversation
                            tool_span.set_attribute(f"tool.{tool_call.name}.uses_subconversation", True)

                            # Create purpose for sub-conversation
                            purpose = f"Analyze {tool_call.name} output for feature assessment"

                            # Build analysis prompt
                            analysis_prompt = (
                                f"Please analyze the following {tool_call.name} output "
                                f"and extract the key information relevant to assessing feature readiness. "
                                f"Focus on identifying any risks, concerns, or positive indicators."
                            )

                            # Execute in sub-conversation
                            sub_conv = await self.subconversation_manager.analyze_in_subconversation(
                                parent_conversation_id=conversation.id,
                                content=tool_result.content,
                                purpose=purpose,
                                analysis_prompt=analysis_prompt,
                            )

                            # Add sub-conversation to conversation
                            conversation.sub_conversations.append(sub_conv)

                            # Replace tool result content with summary
                            tool_result.content = (
                                f"[Analyzed in sub-conversation {sub_conv.id}]\n\n"
                                f"Summary:\n{sub_conv.summary}"
                            )
                            tool_result.metadata["subconversation_id"] = sub_conv.id
                            tool_result.metadata["original_tokens"] = result_tokens
                            tool_result.metadata["summary_tokens"] = count_tokens(sub_conv.summary)

                        tool_results.append(tool_result)

                        tool_span.set_attribute(
                            f"tool.{tool_call.name}.success", tool_result.success
                        )

                    # Add all tool results as a single message
                    conversation.add_tool_result_message(tool_results)

                # Continue loop to get next response from model with tool results

            # If we hit max iterations, return what we have
            span.set_attribute("tool_loop.max_iterations_reached", True)
            raise RuntimeError(
                f"Tool execution loop exceeded maximum iterations ({max_iterations})"
            )

    def new_conversation(self) -> Conversation:
        """Create and save a new conversation."""
        with self.tracer.start_as_current_span("new_conversation") as span:
            conversation = self.store.create_conversation()
            conversation.trace_id = get_trace_id()
            span.set_attribute("session.id", conversation.id)
            self.store.save(conversation)
            return conversation

    def load_conversation(self, conversation_id: str) -> Conversation:
        """Load an existing conversation."""
        return self.store.load(conversation_id)

    def list_conversations(self) -> list[tuple[str, str]]:
        """List all conversations with formatted timestamps."""
        conversations = self.store.list_conversations()
        return [(id, dt.strftime("%Y-%m-%d %H:%M:%S")) for id, dt in conversations]
