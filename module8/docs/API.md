# API Reference

## Core Classes

### Agent

The main agent class that orchestrates conversations and tool execution.

```python
from investigator_agent import Agent

agent = Agent(
    provider: BaseProvider,
    store: ConversationStore,
    config: Config,
    tool_registry: ToolRegistry | None = None
)
```

**Methods:**

- `new_conversation() -> Conversation`
  - Creates a new conversation with a unique ID
  - Returns: Conversation object

- `async send_message(conversation: Conversation, user_message: str) -> str`
  - Sends a message and gets agent response
  - Handles tool loop automatically
  - Args:
    - `conversation`: Conversation object
    - `user_message`: User's message text
  - Returns: Agent's final response text

- `load_conversation(conversation_id: str) -> Conversation`
  - Loads a saved conversation
  - Args:
    - `conversation_id`: UUID of the conversation
  - Returns: Conversation object
  - Raises: `FileNotFoundError` if conversation doesn't exist

- `list_conversations() -> list[tuple[str, str]]`
  - Lists all saved conversations
  - Returns: List of (conversation_id, timestamp) tuples

### Config

Configuration management for the agent.

```python
from investigator_agent import Config

config = Config(
    api_key: str,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 4096,
    max_messages: int = 6,
    conversations_dir: Path = Path("./conversations"),
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
)
```

**Class Methods:**

- `Config.from_env() -> Config`
  - Creates config from environment variables
  - Environment variables:
    - `ANTHROPIC_API_KEY` (required)
    - `ANTHROPIC_MODEL`
    - `MAX_TOKENS`
    - `MAX_MESSAGES`
    - `CONVERSATIONS_DIR`
    - `SYSTEM_PROMPT`
  - Returns: Config object

### Conversation

Represents a conversation with message history.

```python
@dataclass
class Conversation:
    id: str
    messages: list[Message]
    created_at: datetime
    updated_at: datetime
    trace_id: str | None = None
```

**Methods:**

- `add_message(role: Literal["user", "assistant"], content: str | list[dict]) -> None`
  - Adds a message to the conversation
  - Args:
    - `role`: Either "user" or "assistant"
    - `content`: Text string or list of content blocks

- `add_tool_result_message(tool_results: list[ToolResult]) -> None`
  - Adds tool results as a user message
  - Args:
    - `tool_results`: List of ToolResult objects

## Tool System

### ToolRegistry

Manages tool registration and execution.

```python
from investigator_agent.tools.registry import ToolRegistry

registry = ToolRegistry()
```

**Methods:**

- `register(name: str, description: str, input_schema: dict, handler: Callable) -> None`
  - Registers a new tool
  - Args:
    - `name`: Unique tool name
    - `description`: What the tool does
    - `input_schema`: JSON Schema for input validation
    - `handler`: Async function to execute

- `async execute(tool_call: ToolCall) -> ToolResult`
  - Executes a tool call
  - Args:
    - `tool_call`: ToolCall object with name and input
  - Returns: ToolResult with output or error

- `get_tool_definitions() -> list[dict]`
  - Gets tool definitions in API format
  - Returns: List of tool definition dicts

### ToolCall

Represents a request to call a tool.

```python
@dataclass
class ToolCall:
    id: str
    name: str
    input: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
```

### ToolResult

Represents the result of a tool execution.

```python
@dataclass
class ToolResult:
    tool_call_id: str
    content: str
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
```

## Providers

### BaseProvider

Abstract interface for LLM providers.

```python
from investigator_agent.providers.base import BaseProvider

class BaseProvider(ABC):
    @abstractmethod
    async def send_message(
        self,
        messages: list[dict],
        max_tokens: int,
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        pass

    @abstractmethod
    def extract_tool_calls(self, response: Any) -> list[ToolCall]:
        pass

    @abstractmethod
    def get_text_content(self, response: Any) -> str:
        pass
```

### AnthropicProvider

Claude implementation of the provider interface.

```python
from investigator_agent.providers.anthropic import AnthropicProvider

provider = AnthropicProvider(
    api_key: str,
    model: str = "claude-3-5-sonnet-20241022"
)
```

## Evaluation

### Evaluator

Evaluates agent performance on test scenarios.

```python
from evals.evaluator import Evaluator

evaluator = Evaluator(pass_threshold: float = 0.7)
```

**Methods:**

- `async run_scenario(agent: Agent, scenario: Scenario) -> EvaluationResult`
  - Runs a single evaluation scenario
  - Args:
    - `agent`: Agent to evaluate
    - `scenario`: Test scenario
  - Returns: EvaluationResult with scores

- `async run_suite(agent: Agent, scenarios: list[Scenario]) -> SuiteResults`
  - Runs multiple scenarios
  - Args:
    - `agent`: Agent to evaluate
    - `scenarios`: List of test scenarios
  - Returns: SuiteResults with aggregated metrics

- `save_baseline(results: SuiteResults, version: str) -> None`
  - Saves results as a baseline
  - Args:
    - `results`: Suite results to save
    - `version`: Version identifier

- `load_baseline(version: str) -> dict | None`
  - Loads a saved baseline
  - Args:
    - `version`: Version identifier
  - Returns: Baseline data or None

- `compare_to_baseline(current: SuiteResults, baseline_data: dict) -> Comparison`
  - Compares current results to baseline
  - Args:
    - `current`: Current suite results
    - `baseline_data`: Loaded baseline data
  - Returns: Comparison object with deltas

### Scenario

Defines a test scenario for evaluation.

```python
@dataclass
class Scenario:
    id: str
    description: str
    release_data: dict[str, Any]
    expected_severity: str
    expected_tools: list[str]
    expected_findings_keywords: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
```

### EvaluationResult

Result of evaluating a single scenario.

```python
@dataclass
class EvaluationResult:
    scenario_id: str
    passed: bool
    scores: dict[str, float]  # tool_usage, decision_quality, overall
    details: dict[str, Any]
    duration: float
    error: str | None = None
```

### SuiteResults

Aggregated results from multiple scenarios.

```python
@dataclass
class SuiteResults:
    total_scenarios: int
    passed: int
    pass_rate: float
    avg_scores: dict[str, float]
    scenario_results: list[EvaluationResult]
    duration: float
    metadata: dict[str, Any] = field(default_factory=dict)
```

## Utilities

### ConversationStore

Handles conversation persistence.

```python
from investigator_agent.persistence.store import ConversationStore

store = ConversationStore(directory: Path)
```

**Methods:**

- `save(conversation: Conversation) -> None`
  - Saves conversation to disk
  - Args:
    - `conversation`: Conversation to save

- `load(conversation_id: str) -> Conversation`
  - Loads conversation from disk
  - Args:
    - `conversation_id`: UUID of conversation
  - Returns: Conversation object
  - Raises: `FileNotFoundError` if not found

- `list_all() -> list[tuple[str, str]]`
  - Lists all saved conversations
  - Returns: List of (id, updated_at) tuples

### ContextManager

Manages context window truncation.

```python
from investigator_agent.context.manager import ContextManager

manager = ContextManager(max_messages: int = 6)
```

**Methods:**

- `truncate_messages(messages: list[Message]) -> tuple[list[Message], bool]`
  - Truncates messages to fit in context window
  - Args:
    - `messages`: List of messages
  - Returns: Tuple of (truncated_messages, was_truncated)

- `get_context_info(messages: list[Message]) -> dict`
  - Gets information about context usage
  - Args:
    - `messages`: List of messages
  - Returns: Dict with total_messages, messages_to_keep, messages_to_drop

## Observability

### Tracer Functions

```python
from investigator_agent.observability.tracer import get_tracer, get_trace_id

# Get tracer instance
tracer = get_tracer()

# Get current trace ID
trace_id = get_trace_id()

# Create a span
with tracer.start_as_current_span("operation_name") as span:
    span.set_attribute("key", "value")
    # ... do work ...
```

## Examples

See the [examples/](../examples/) directory for complete usage examples:

- `basic_usage.py` - Basic agent conversation
- `run_evaluation.py` - Running evaluation suite
