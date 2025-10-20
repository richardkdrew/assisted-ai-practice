"""Tool registry for managing and executing agent tools."""

import json
from typing import Any, Callable

from detective_agent.models import ToolCall, ToolDefinition, ToolResult
from detective_agent.observability.tracer import get_tracer


class ToolRegistry:
    """Registry for managing agent tools."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: dict[str, ToolDefinition] = {}
        self.tracer = get_tracer()

    def register(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable,
    ) -> None:
        """
        Register a tool with the registry.

        Args:
            name: Unique name for the tool
            description: Human-readable description
            input_schema: JSON Schema for tool input validation
            handler: Async function to execute the tool
        """
        tool_def = ToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
        )
        self._tools[name] = tool_def

    async def execute(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a tool call.

        Args:
            tool_call: The tool call to execute

        Returns:
            ToolResult with execution outcome
        """
        with self.tracer.start_as_current_span(f"tool.{tool_call.name}") as span:
            span.set_attribute("tool.name", tool_call.name)
            span.set_attribute("tool.call_id", tool_call.id)
            span.set_attribute("tool.input", json.dumps(tool_call.input))

            # Check if tool exists
            if tool_call.name not in self._tools:
                error_msg = f"Tool '{tool_call.name}' not found in registry"
                span.set_attribute("tool.error", error_msg)
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=error_msg,
                    success=False,
                    metadata={"error_type": "tool_not_found"},
                )

            tool_def = self._tools[tool_call.name]

            # TODO: Add input validation against schema here
            # For now, we trust the inputs

            try:
                # Execute the tool handler
                result = await tool_def.handler(**tool_call.input)

                # Convert result to string if needed
                if isinstance(result, dict):
                    content = json.dumps(result, indent=2)
                else:
                    content = str(result)

                span.set_attribute("tool.success", True)
                span.set_attribute("tool.result_length", len(content))

                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=content,
                    success=True,
                    metadata={"result_type": type(result).__name__},
                )

            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                span.set_attribute("tool.error", error_msg)
                span.set_attribute("tool.success", False)

                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=error_msg,
                    success=False,
                    metadata={"error_type": type(e).__name__, "error": str(e)},
                )

    def get_definitions(self) -> list[ToolDefinition]:
        """Get all registered tool definitions."""
        return list(self._tools.values())

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """
        Get tool definitions formatted for API use.

        Returns:
            List of tool definitions in API format
        """
        return self.format_for_anthropic()

    def format_for_anthropic(self) -> list[dict[str, Any]]:
        """
        Format tools for Anthropic API.

        Returns:
            List of tool definitions in Anthropic format
        """
        return [tool.to_anthropic_format() for tool in self._tools.values()]

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def get_tool_names(self) -> list[str]:
        """Get list of registered tool names."""
        return list(self._tools.keys())
