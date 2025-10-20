"""Tests for ToolRegistry."""

import pytest

from detective_agent.models import ToolCall
from detective_agent.tools.registry import ToolRegistry


@pytest.fixture
def registry():
    """Create a tool registry for testing."""
    return ToolRegistry()


@pytest.fixture
def sample_tool():
    """Create a sample tool handler."""

    async def add_numbers(a: int, b: int) -> dict:
        return {"result": a + b}

    return add_numbers


def test_register_tool(registry, sample_tool):
    """Test registering a tool."""
    registry.register(
        name="add",
        description="Add two numbers",
        input_schema={"type": "object", "properties": {"a": {}, "b": {}}},
        handler=sample_tool,
    )

    assert registry.has_tool("add")
    assert len(registry.get_tool_names()) == 1
    assert "add" in registry.get_tool_names()


def test_has_tool(registry, sample_tool):
    """Test checking if tool exists."""
    assert not registry.has_tool("add")

    registry.register(
        name="add",
        description="Add two numbers",
        input_schema={},
        handler=sample_tool,
    )

    assert registry.has_tool("add")
    assert not registry.has_tool("subtract")


def test_get_tool_names(registry, sample_tool):
    """Test getting list of tool names."""

    async def multiply(a: int, b: int) -> int:
        return a * b

    registry.register("add", "Add numbers", {}, sample_tool)
    registry.register("multiply", "Multiply numbers", {}, multiply)

    names = registry.get_tool_names()
    assert len(names) == 2
    assert "add" in names
    assert "multiply" in names


def test_get_definitions(registry, sample_tool):
    """Test getting tool definitions."""
    registry.register(
        name="add",
        description="Add two numbers",
        input_schema={"type": "object"},
        handler=sample_tool,
    )

    definitions = registry.get_definitions()
    assert len(definitions) == 1
    assert definitions[0].name == "add"
    assert definitions[0].description == "Add two numbers"


def test_get_tool_definitions(registry, sample_tool):
    """Test getting tool definitions in API format."""
    registry.register(
        name="add",
        description="Add two numbers",
        input_schema={"type": "object", "properties": {"a": {}, "b": {}}},
        handler=sample_tool,
    )

    api_defs = registry.get_tool_definitions()
    assert len(api_defs) == 1
    assert api_defs[0]["name"] == "add"
    assert api_defs[0]["description"] == "Add two numbers"
    assert "input_schema" in api_defs[0]


def test_format_for_anthropic(registry, sample_tool):
    """Test formatting tools for Anthropic API."""
    registry.register(
        name="add",
        description="Add two numbers",
        input_schema={"type": "object", "properties": {"a": {}, "b": {}}},
        handler=sample_tool,
    )

    formatted = registry.format_for_anthropic()
    assert len(formatted) == 1
    assert formatted[0]["name"] == "add"
    assert "input_schema" in formatted[0]


@pytest.mark.asyncio
async def test_execute_tool_success_dict_result(registry, sample_tool):
    """Test executing a tool that returns a dict."""
    registry.register(
        name="add",
        description="Add two numbers",
        input_schema={},
        handler=sample_tool,
    )

    tool_call = ToolCall(id="call_123", name="add", input={"a": 5, "b": 3})
    result = await registry.execute(tool_call)

    assert result.success is True
    assert result.tool_call_id == "call_123"
    assert '"result": 8' in result.content
    assert result.metadata["result_type"] == "dict"


@pytest.mark.asyncio
async def test_execute_tool_success_non_dict_result(registry):
    """Test executing a tool that returns a non-dict value."""

    async def get_count() -> int:
        return 42

    registry.register(
        name="count",
        description="Get count",
        input_schema={},
        handler=get_count,
    )

    tool_call = ToolCall(id="call_456", name="count", input={})
    result = await registry.execute(tool_call)

    assert result.success is True
    assert result.content == "42"
    assert result.metadata["result_type"] == "int"


@pytest.mark.asyncio
async def test_execute_tool_not_found(registry):
    """Test executing a tool that doesn't exist."""
    tool_call = ToolCall(id="call_789", name="nonexistent", input={})
    result = await registry.execute(tool_call)

    assert result.success is False
    assert result.tool_call_id == "call_789"
    assert "not found" in result.content
    assert result.metadata["error_type"] == "tool_not_found"


@pytest.mark.asyncio
async def test_execute_tool_handler_raises_exception(registry):
    """Test executing a tool where the handler raises an exception."""

    async def failing_tool(value: int) -> int:
        if value < 0:
            raise ValueError("Value must be positive")
        return value * 2

    registry.register(
        name="double",
        description="Double a number",
        input_schema={},
        handler=failing_tool,
    )

    tool_call = ToolCall(id="call_error", name="double", input={"value": -5})
    result = await registry.execute(tool_call)

    assert result.success is False
    assert result.tool_call_id == "call_error"
    assert "Tool execution failed" in result.content
    assert "Value must be positive" in result.content
    assert result.metadata["error_type"] == "ValueError"
    assert "error" in result.metadata


@pytest.mark.asyncio
async def test_execute_tool_with_complex_input(registry):
    """Test executing a tool with complex input parameters."""

    async def process_data(items: list[str], prefix: str) -> dict:
        return {"processed": [f"{prefix}{item}" for item in items]}

    registry.register(
        name="process",
        description="Process items",
        input_schema={},
        handler=process_data,
    )

    tool_call = ToolCall(
        id="call_complex",
        name="process",
        input={"items": ["a", "b", "c"], "prefix": "item_"},
    )
    result = await registry.execute(tool_call)

    assert result.success is True
    assert "item_a" in result.content
    assert "item_b" in result.content
    assert "item_c" in result.content


def test_empty_registry(registry):
    """Test registry with no tools."""
    assert len(registry.get_tool_names()) == 0
    assert len(registry.get_definitions()) == 0
    assert len(registry.get_tool_definitions()) == 0
    assert len(registry.format_for_anthropic()) == 0
    assert not registry.has_tool("anything")
