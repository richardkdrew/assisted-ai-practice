# Detective Agent Implementation Plan (Python)

## Overview
Python implementation of the Detective Agent. See [DESIGN.md](DESIGN.md) for more about **what** the agent does and **why** design decisions were made.

This document covers **how** to build the agent in Python - specific packages, project structure, testing approach, and implementation details.  

## Implementation Goals
- Clear, readable Python code that shows exactly what's happening
- Multi-provider support (Anthropic, OpenRouter, Ollama, etc)
- OpenTelemetry observability
- Context window management
- Retry mechanism with exponential backoff
- Tool calling foundation
- Interaction persistence
- Basic reasoning and evaluations

## Implementation Constitution
- Clear, readable Python code that shows exactly what's happening
- For interfaces, use Protocol, and DO NOT use an ABC
- Place unit tests in the folder as the code under test
- Unit tests have a `_test.py` suffix and DO NOT have a `test_` prefix
- The `/tests` folder should only contain integration tests and common test assets
- When you're running tests and Python scripts, remember that the `python` binary is in the virtual environment
- Use `uv venv` to create the venv and `uv add` when adding dependencies
- Never use `pip` or `uv pip` and never create `requirements.txt`

## Implementation Steps
The recommended order of implementation is defined in [STEPS.md](STEPS.md). The phases of implementation defined later in this document align with these progression of steps.

## Technology Stack
- **Python 3.13.7** with async/await
- **uv** for dependency and venv management
- **httpx** for HTTP client (async, HTTP/2 support)
- **OpenTelemetry SDK** for traces and metrics
- **pydantic** for configuration and validation
- **pytest** + **pytest-asyncio** for testing
- **respx** for mocking httpx in tests

## Project Structure

```
module7/
├── docs/                           # Design and planning documents
│   ├── DESIGN.md                  # Architecture and design decisions
│   ├── STEPS.md                   # Step-by-step implementation guide
│   └── PLAN.md                    # This file - implementation plan
├── src/
│   └── detective_agent/           # Main package
│       ├── __init__.py
│       ├── models/                # Data models
│       │   ├── __init__.py
│       │   ├── message.py         # Message, Conversation models
│       │   ├── tool.py            # Tool definition, call, result models
│       │   └── config.py          # Configuration models
│       ├── providers/             # LLM provider implementations
│       │   ├── __init__.py
│       │   ├── base.py            # Provider protocol/interface
│       │   ├── anthropic.py       # Claude provider
│       │   └── anthropic_test.py  # Claude provider tests
│       ├── tools/                 # Tool implementations
│       │   ├── __init__.py
│       │   ├── registry.py        # Tool registry and execution
│       │   ├── registry_test.py   # Tool registry tests
│       │   ├── release_tools.py   # Release summary and risk report tools
│       │   └── release_tools_test.py
│       ├── context/               # Context window management
│       │   ├── __init__.py
│       │   ├── manager.py         # Context window manager
│       │   └── manager_test.py    # Context manager tests
│       ├── retry/                 # Retry mechanism
│       │   ├── __init__.py
│       │   ├── strategy.py        # Retry logic and backoff
│       │   └── strategy_test.py   # Retry tests
│       ├── observability/         # OpenTelemetry instrumentation
│       │   ├── __init__.py
│       │   ├── tracer.py          # Trace setup and utilities
│       │   └── exporter.py        # File-based trace export
│       ├── persistence/           # Conversation and trace storage
│       │   ├── __init__.py
│       │   ├── store.py           # Filesystem persistence
│       │   └── store_test.py      # Persistence tests
│       ├── evaluation/            # Evaluation framework
│       │   ├── __init__.py
│       │   ├── evaluator.py       # Eval runner and scoring
│       │   ├── evaluator_test.py  # Eval framework tests
│       │   ├── scenarios.py       # Test case definitions
│       │   └── reporters.py       # Report generation
│       ├── agent.py               # Main Agent class
│       ├── agent_test.py          # Agent tests
│       └── cli.py                 # Command-line interface
├── tests/                         # Integration tests
│   ├── __init__.py
│   ├── integration_test.py        # End-to-end tests
│   └── fixtures/                  # Test data
│       ├── release_summaries.json
│       └── eval_scenarios.json
├── data/                          # Runtime data (created automatically)
│   ├── conversations/             # Saved conversations
│   └── traces/                    # OpenTelemetry traces
├── pyproject.toml                 # Project config and dependencies
├── uv.lock                        # Locked dependencies
└── README.md                      # Project documentation
```

## Phase 0: Project Setup

### Tasks
1. **Initialize Python project structure**
   - Create directory structure as outlined above
   - Initialize git repository (if not already initialized)

2. **Setup uv and virtual environment**
   ```bash
   # Create virtual environment
   uv venv

   # Activate (instructions will be shown)
   source .venv/bin/activate  # On macOS/Linux
   ```

3. **Create pyproject.toml**
   - Define project metadata
   - Setup package configuration
   - Configure pytest

4. **Install core dependencies**
   ```bash
   uv add httpx pydantic opentelemetry-api opentelemetry-sdk pytest pytest-asyncio respx
   ```

### Deliverables
- [ ] Project structure created
- [ ] Virtual environment setup with uv
- [ ] pyproject.toml configured
- [ ] Dependencies installed
- [ ] Can run `pytest` (even with no tests yet)

## Phase 1: Basic Conversation (Step 1)

**Goal:** Build a minimal agent that can converse with Claude

### Configuration System

**File:** `src/detective_agent/models/config.py`

**Implementation:**
- `ProviderConfig` - API key, base URL, model name
- `AnthropicConfig` - Claude-specific settings (model: "claude-3-5-sonnet-20241022", max_tokens: 4096)
- `AgentConfig` - System prompt, temperature, provider config
- Use Pydantic for validation
- Load from environment variables (ANTHROPIC_API_KEY)

**Tests:** Validate config loading and defaults

### Data Models

**File:** `src/detective_agent/models/message.py`

**Implementation:**
- `Message` class with Pydantic
  - `role`: Literal["user", "assistant", "system"]
  - `content`: str
  - `timestamp`: datetime (default to now)
  - `metadata`: dict[str, Any] (default empty)

- `Conversation` class
  - `id`: str (UUID)
  - `system_prompt`: str
  - `messages`: list[Message]
  - `created_at`: datetime
  - `metadata`: dict[str, Any]
  - Methods: `add_message()`, `get_messages()`, `to_dict()`, `from_dict()`

**Tests:** Message creation, conversation operations, serialization

### Provider Abstraction

**File:** `src/detective_agent/providers/base.py`

**Implementation:**
- Define `Provider` Protocol (not ABC)
- Methods:
  - `async def complete(messages: list[Message], **kwargs) -> Message`
  - `def estimate_tokens(messages: list[Message]) -> int`
  - `def get_model_info() -> dict[str, Any]`

**File:** `src/detective_agent/providers/anthropic.py`

**Implementation:**
- `AnthropicProvider` class implementing Provider protocol
- Use httpx.AsyncClient for API calls
- Endpoint: https://api.anthropic.com/v1/messages
- Headers: anthropic-version, x-api-key, content-type
- Convert Message list to Anthropic format
- Parse response and create assistant Message
- Handle errors: auth (401), rate limit (429), validation (400)
- Token estimation: rough approximation (chars / 4) for now
- Model info: return model name, max tokens, context window

**User Preference Applied:**
- Default model: `claude-3-5-sonnet-20241022`
- Max tokens: 4096

**Tests:** Mock httpx calls, test message conversion, error handling

### Conversation Persistence

**File:** `src/detective_agent/persistence/store.py`

**Implementation:**
- `ConversationStore` class
- Save conversation to `data/conversations/{conversation_id}.json`
- Load conversation from file
- List all conversations
- Use Conversation.to_dict() / from_dict()
- Handle file I/O errors gracefully

**Tests:** Save, load, list operations

### Agent Core (Basic)

**File:** `src/detective_agent/agent.py`

**Implementation:**
- `Agent` class
- `__init__(config: AgentConfig, provider: Provider, store: ConversationStore)`
- Current conversation state in memory
- `async def send_message(content: str) -> str`
  1. Create user Message
  2. Add to conversation
  3. Call provider.complete()
  4. Add assistant response to conversation
  5. Save conversation to store
  6. Return assistant content
- `def new_conversation(system_prompt: str = None) -> None`
- `def load_conversation(conversation_id: str) -> None`
- `def get_history() -> list[Message]`

**Tests:** Conversation flow, persistence integration

### CLI Interface

**File:** `src/detective_agent/cli.py`

**Implementation:**
- Simple REPL using `input()`
- Commands:
  - Regular input: send as message
  - `/new` - start new conversation
  - `/history` - show conversation history
  - `/load <id>` - load saved conversation
  - `/list` - list saved conversations
  - `/exit` or `/quit` - exit CLI
- Show conversation ID on start
- Format responses nicely
- Handle errors gracefully

### Deliverables
- [ ] Agent can have basic conversation with Claude
- [ ] Conversations persist to filesystem
- [ ] Can load and continue conversations
- [ ] CLI provides good user experience
- [ ] All components have unit tests (minimum 3 tests per file)
- [ ] Integration test covering end-to-end flow

## Phase 2: Observability (Step 2)

**Goal:** Add OpenTelemetry tracing for complete visibility

### OpenTelemetry Setup

**File:** `src/detective_agent/observability/tracer.py`

**Implementation:**
- Initialize TracerProvider
- Configure file-based span exporter
- Utility functions:
  - `get_tracer() -> Tracer`
  - `start_conversation_trace() -> str` (returns trace_id)
  - `create_span(name: str, attributes: dict) -> Span`
- Span attributes helper functions

**File:** `src/detective_agent/observability/exporter.py`

**Implementation:**
- Custom SpanExporter that writes to files
- Export spans to `data/traces/{trace_id}.json`
- Format: JSON array of spans
- Each span includes:
  - name, span_id, trace_id, parent_span_id
  - start_time, end_time, duration
  - attributes (custom key-value pairs)
  - status (ok, error)

### Instrumentation

**Update:** `src/detective_agent/agent.py`
- Create conversation trace on new conversation
- Add trace_id to conversation metadata
- Span for `send_message` operation
  - Attributes: message length, message count
- Span for provider calls
  - Attributes: model, input_tokens, output_tokens, duration

**Update:** `src/detective_agent/providers/anthropic.py`
- Add span for API calls
- Capture request/response timing
- Include token counts from API response

**Update:** `src/detective_agent/persistence/store.py`
- Export trace when conversation is saved
- Ensure all spans in trace are written to file

### Deliverables
- [ ] Every conversation generates a trace file
- [ ] Spans capture timing and metadata
- [ ] Trace files are human-readable JSON
- [ ] Conversation JSON includes trace_id
- [ ] Can correlate conversation with its trace
- [ ] Tests verify trace generation

## Phase 3: Context Window Management (Step 3)

**Goal:** Handle conversations exceeding token limits

### Context Manager

**File:** `src/detective_agent/context/manager.py`

**Implementation:**
- `ContextManager` class
- `truncate_messages(messages: list[Message], max_tokens: int, system_prompt_tokens: int, reserved_response_tokens: int) -> list[Message]`
  - Calculate token budget: max_tokens - system_prompt_tokens - reserved_response_tokens - buffer (10%)
  - Keep only messages that fit in budget
  - **Truncation Strategy (User Preference):**
    - Keep last 6 messages (3 user + 3 assistant pairs)
    - If 6 messages exceed budget, keep as many as fit
    - Always preserve most recent messages
  - Preserve message order
  - Return truncated list

**User Preference Applied:**
- Strategy: Simple truncation
- Keep: Last 6 messages (3 exchanges)

**Configuration:**
- Add to `AgentConfig`:
  - `context_strategy`: "truncation"
  - `max_messages`: 6
  - `context_window_tokens`: 200000 (Claude 3.5 Sonnet context)
  - `reserved_response_tokens`: 4096
  - `buffer_percentage`: 0.10

### Integration

**Update:** `src/detective_agent/agent.py`
- Add ContextManager to Agent
- Before each provider.complete() call:
  1. Estimate tokens for all messages
  2. If approaching limit, truncate messages
  3. Log truncation event
  4. Add truncation info to trace span
- Track context window utilization in traces

### Deliverables
- [ ] Truncation works correctly
- [ ] Keeps last 6 messages as specified
- [ ] System prompt always preserved
- [ ] Context state visible in traces
- [ ] Long conversations don't cause errors
- [ ] Tests verify truncation logic with various scenarios

## Phase 4: Retry Mechanism (Step 4)

**Goal:** Handle transient failures with exponential backoff

### Retry Strategy

**File:** `src/detective_agent/retry/strategy.py`

**Implementation:**
- `RetryConfig` dataclass
  - `max_attempts`: int = 3
  - `initial_delay`: float = 1.0 (seconds)
  - `max_delay`: float = 60.0
  - `backoff_factor`: float = 2.0
  - `jitter`: bool = True

- `async def with_retry(operation: Callable, config: RetryConfig, is_retryable: Callable[[Exception], bool]) -> T`
  - Try operation
  - On exception:
    - Check if retryable (429, 500, 502, 503, network errors)
    - If not retryable, raise immediately
    - Calculate backoff: min(initial_delay * (backoff_factor ** attempt), max_delay)
    - Add jitter: backoff * (0.5 + random.random() * 0.5)
    - Sleep for backoff duration
    - Create retry span with attempt number and delay
    - Retry operation
  - Max attempts reached: raise last exception

- `is_retryable_error(exc: Exception) -> bool`
  - Check httpx status codes: 429, 500, 502, 503
  - Check httpx timeout/network errors
  - Return False for 401, 403, 400, 404

### Integration

**Update:** `src/detective_agent/providers/anthropic.py`
- Wrap API calls with `with_retry`
- Create retry span for each attempt
- Include attempt number and backoff time in span

**Update:** `src/detective_agent/agent.py`
- Pass retry config to provider
- Track retry metrics in traces

### Deliverables
- [ ] Rate limits trigger retries
- [ ] Exponential backoff implemented
- [ ] Jitter prevents thundering herd
- [ ] Auth/validation errors fail fast
- [ ] Retry attempts visible in traces
- [ ] Tests mock failures and verify retry behavior
- [ ] Manual test with rate limit simulation

## Phase 5: System Prompt Engineering (Step 5)

**Goal:** Give agent clear purpose and instructions

### System Prompt

**File:** `src/detective_agent/models/config.py`

**Add default system prompt:**
```python
DEFAULT_SYSTEM_PROMPT = """You are a Detective Agent, part of a Release Confidence System.

Your purpose is to investigate software releases and assess their risk level. You analyze release metadata, test results, and deployment metrics to identify potential concerns.

You have access to tools that allow you to:
1. Retrieve release summary information
2. File risk reports with severity assessments

When analyzing a release:
- Look for test failures, especially in critical areas
- Assess error rates and performance metrics
- Evaluate the impact of code changes
- Consider the overall risk profile

Severity guidelines:
- HIGH: Critical test failures, elevated error rates (>5%), risky changes to core systems
- MEDIUM: Minor test failures, slight metric degradation (2-5%), moderate-impact changes
- LOW: All tests passing, healthy metrics (<2% error rate), low-impact changes

Always explain your reasoning clearly and base your assessment on the data provided.
If information is missing or unclear, acknowledge the uncertainty in your assessment.

You are concise but thorough. You focus on actionable insights."""
```

### Configuration Updates

**Update:** `src/detective_agent/models/config.py`
- Make system_prompt configurable in AgentConfig
- Default to DEFAULT_SYSTEM_PROMPT
- Allow override for different use cases

**Update:** `src/detective_agent/agent.py`
- Use configured system prompt for all conversations
- Include system prompt in context calculations

### Deliverables
- [ ] Default system prompt defines agent purpose
- [ ] System prompt includes tool usage guidance
- [ ] System prompt is easily configurable
- [ ] Agent behavior reflects instructions
- [ ] Tested with different prompts

## Phase 6: Tool Abstraction (Step 6)

**Goal:** Enable agent to use tools for release risk assessment

### Tool Models

**File:** `src/detective_agent/models/tool.py`

**Implementation:**
- `ToolDefinition` class
  - `name`: str
  - `description`: str
  - `input_schema`: dict (JSON Schema)

- `ToolCall` class
  - `id`: str
  - `name`: str
  - `input`: dict
  - `timestamp`: datetime

- `ToolResult` class
  - `tool_call_id`: str
  - `content`: str
  - `success`: bool
  - `timestamp`: datetime
  - `metadata`: dict

### Tool Registry

**File:** `src/detective_agent/tools/registry.py`

**Implementation:**
- `ToolRegistry` class
- `register(name: str, description: str, schema: dict, handler: Callable) -> None`
- `async def execute(tool_call: ToolCall) -> ToolResult`
  - Validate tool exists
  - Validate input against schema
  - Call handler with input
  - Wrap result in ToolResult
  - Handle errors gracefully
- `get_definitions() -> list[ToolDefinition]`
- `format_for_anthropic() -> list[dict]`
  - Convert to Anthropic tool format

### Release Tools

**File:** `src/detective_agent/tools/release_tools.py`

**Implementation:**

**1. Get Release Summary Tool**
```python
async def get_release_summary(release_id: str) -> dict:
    """Retrieve release information from mock data"""
    # Mock implementation - return test data
    # In real system, would call HTTP endpoint
    return {
        "version": "v2.1.0",
        "changes": ["Added payment processing", "Fixed auth bug"],
        "tests": {"passed": 142, "failed": 2, "skipped": 5},
        "deployment_metrics": {
            "error_rate": 0.02,
            "response_time_p95": 450
        }
    }
```

Schema:
```json
{
  "type": "object",
  "properties": {
    "release_id": {
      "type": "string",
      "description": "Unique identifier for the release"
    }
  },
  "required": ["release_id"]
}
```

**2. File Risk Report Tool**
```python
async def file_risk_report(
    release_id: str,
    severity: str,
    findings: list[str]
) -> dict:
    """File a risk assessment report"""
    # Validate severity
    if severity not in ["high", "medium", "low"]:
        raise ValueError("Severity must be high, medium, or low")

    # Mock implementation - save to file
    report = {
        "report_id": str(uuid.uuid4()),
        "release_id": release_id,
        "severity": severity,
        "findings": findings,
        "timestamp": datetime.now().isoformat()
    }

    # Save to data/reports/{report_id}.json
    save_report(report)

    return {
        "status": "filed",
        "report_id": report["report_id"]
    }
```

Schema:
```json
{
  "type": "object",
  "properties": {
    "release_id": {"type": "string"},
    "severity": {
      "type": "string",
      "enum": ["high", "medium", "low"],
      "description": "Risk severity level"
    },
    "findings": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of identified risks or concerns"
    }
  },
  "required": ["release_id", "severity", "findings"]
}
```

### Provider Tool Support

**Update:** `src/detective_agent/providers/anthropic.py`
- Add tools parameter to complete()
- Format tools in Anthropic format
- Handle tool_use blocks in response
- Parse tool calls from response
- Support tool_result messages

**Update:** `src/detective_agent/models/message.py`
- Add support for tool_use content blocks
- Add support for tool_result content blocks
- Update Message to handle complex content types

### Agent Tool Loop

**Update:** `src/detective_agent/agent.py`
- Add ToolRegistry to Agent
- `register_tool()` method
- Update `send_message()` with tool loop:
  1. Send user message
  2. Call provider with tool definitions
  3. If response contains tool calls:
     a. Execute each tool via registry
     b. Create tool_result messages
     c. Add to conversation
     d. Call provider again (loop to step 3)
  4. If no tool calls:
     a. Return final response
- Add tool spans to traces
- Track tool execution timing

### CLI Enhancement

**Update:** `src/detective_agent/cli.py`
- Add command to trigger release assessment: `/assess <release_id>`
- Show tool calls as they happen
- Display tool results
- Show final assessment

### Deliverables
- [ ] Tool registry and execution framework working
- [ ] get_release_summary tool implemented and tested
- [ ] file_risk_report tool implemented and tested
- [ ] Tool loop works end-to-end
- [ ] Tools formatted correctly for Anthropic API
- [ ] Tool calls and results in conversation history
- [ ] Tool execution captured in traces
- [ ] Error handling for tool failures
- [ ] Unit tests for tool framework
- [ ] Integration test for full release assessment workflow
- [ ] CLI demo works smoothly

## Phase 7: Evaluation System (Step 7)

**Goal:** Automated validation of agent behavior

### Test Scenarios

**File:** `src/detective_agent/evaluation/scenarios.py`

**Implementation:**
- `Scenario` dataclass
  - `id`: str
  - `description`: str
  - `release_data`: dict
  - `expected_severity`: str
  - `expected_tools`: list[str]
  - `expected_findings`: list[str] (keywords to check)
  - `metadata`: dict

- Define test scenarios:
  1. **High Risk Release**
     - 5+ test failures
     - Error rate > 5%
     - Critical changes
     - Expected: HIGH severity

  2. **Medium Risk Release**
     - 1-2 test failures
     - Error rate 2-4%
     - Moderate changes
     - Expected: MEDIUM severity

  3. **Low Risk Release**
     - All tests pass
     - Error rate < 2%
     - Minor changes
     - Expected: LOW severity

  4. **Missing Data**
     - Incomplete release data
     - Expected: Graceful handling, acknowledge uncertainty

  5. **Tool Failure**
     - Simulate tool error
     - Expected: Error handling, clear reporting

### Evaluator

**File:** `src/detective_agent/evaluation/evaluator.py`

**Implementation:**

- `EvaluationResult` dataclass
  - `scenario_id`: str
  - `passed`: bool
  - `scores`: dict[str, float]
  - `details`: dict
  - `duration`: float

- `Evaluator` class
  - `async def run_scenario(agent: Agent, scenario: Scenario) -> EvaluationResult`
    - Reset agent conversation
    - Provide scenario to agent
    - Capture tool calls
    - Evaluate tool usage
    - Evaluate decision quality
    - Calculate scores
    - Return result

  - `def eval_tool_usage(tool_calls: list[ToolCall], expected: list[str]) -> float`
    - Check correct tools called
    - Check reasonable order
    - Return score 0.0-1.0

  - `def eval_decision_quality(severity: str, findings: list[str], expected_severity: str, expected_findings: list[str]) -> float`
    - Check severity match
    - Check finding keyword overlap
    - Return score 0.0-1.0

  - `def eval_error_handling(scenario: Scenario, agent_behavior: dict) -> float`
    - Check graceful error handling
    - Check clear error reporting
    - Return score 0.0-1.0

  - `async def run_suite(agent: Agent, scenarios: list[Scenario]) -> SuiteResults`
    - Run all scenarios
    - Collect results
    - Calculate aggregates
    - Return suite results

- `SuiteResults` dataclass
  - `total_scenarios`: int
  - `passed`: int
  - `pass_rate`: float
  - `avg_scores`: dict[str, float]
  - `scenario_results`: list[EvaluationResult]
  - `duration`: float

### Regression Tracking

**File:** `src/detective_agent/evaluation/evaluator.py` (continued)

**Implementation:**
- `save_baseline(results: SuiteResults, version: str) -> None`
  - Save to `data/baselines/{version}.json`

- `load_baseline(version: str) -> SuiteResults`
  - Load from file

- `compare_to_baseline(current: SuiteResults, baseline: SuiteResults) -> Comparison`
  - Calculate delta for pass_rate
  - Calculate delta for each score dimension
  - Identify regressions (>5% drop)
  - Identify improvements (>5% gain)
  - Return comparison report

- `Comparison` dataclass
  - `pass_rate_delta`: float
  - `score_deltas`: dict[str, float]
  - `regressions`: list[str]
  - `improvements`: list[str]
  - `summary`: str

### Report Generation

**File:** `src/detective_agent/evaluation/reporters.py`

**Implementation:**
- `generate_json_report(results: SuiteResults, comparison: Comparison = None) -> dict`
  - Machine-readable format
  - Include all scores and details
  - Include comparison if provided

- `generate_markdown_report(results: SuiteResults, comparison: Comparison = None) -> str`
  - Human-readable format
  - Tables for results
  - Highlights for regressions/improvements

- `save_report(report: dict, path: str) -> None`
  - Save to file

### CLI Commands

**Update:** `src/detective_agent/cli.py`
- `/eval` - Run evaluation suite
- `/eval-baseline <version>` - Save current results as baseline
- `/eval-compare <version>` - Compare to baseline
- `/eval-report` - Generate and display report

### Deliverables
- [ ] Evaluation framework runs scenarios automatically
- [ ] Tool usage evaluated correctly
- [ ] Decision quality measured against expectations
- [ ] Error handling scenarios validate robustness
- [ ] Test suite includes 5+ scenarios
- [ ] Regression tracking compares to baseline
- [ ] JSON and Markdown reports generated
- [ ] CLI supports eval commands
- [ ] Tests verify evaluator itself
- [ ] Documentation for adding new scenarios

## Testing Strategy

### Unit Tests
- Each module has `_test.py` file in same directory
- Test individual functions and classes
- Mock external dependencies (httpx, file I/O)
- Use pytest and pytest-asyncio
- Use respx for mocking HTTP

**Coverage Goals:**
- Models: 100% (they're simple)
- Providers: >80% (focus on error handling)
- Tools: >90% (critical for correctness)
- Agent: >80% (core logic)
- Context Manager: 100% (algorithm correctness)
- Retry: >90% (edge cases)

### Integration Tests
- Located in `tests/` directory
- Test full workflows end-to-end
- Use real provider (with mock server option)
- Verify persistence, tracing, tool execution
- Test error scenarios

### Manual Testing
- CLI interaction testing
- Real API calls to Claude
- Rate limit testing (if possible)
- Long conversation testing

## Development Workflow

### 1. TDD Approach
For each component:
1. Write test first (or at least plan tests)
2. Implement minimal code to pass
3. Refactor as needed
4. Ensure all tests pass before moving on

### 2. Incremental Development
- Complete each phase fully before starting next
- Run all tests after each change
- Keep main branch working at all times
- Commit frequently with clear messages

### 3. Code Quality
- Use type hints everywhere
- Follow PEP 8 style guide
- Use descriptive variable names
- Add docstrings for public APIs
- Keep functions focused and small

### 4. Testing Commands
```bash
# Run all tests
pytest

# Run specific test file
pytest src/detective_agent/providers/anthropic_test.py

# Run with coverage
pytest --cov=src/detective_agent --cov-report=html

# Run integration tests only
pytest tests/

# Run with verbose output
pytest -v
```

## Configuration Management

### Environment Variables
- `ANTHROPIC_API_KEY` - Required for Claude provider
- `AGENT_MODEL` - Override default model
- `AGENT_MAX_TOKENS` - Override max tokens
- `AGENT_DATA_DIR` - Override data directory (default: ./data)

### Config File (Optional Future Enhancement)
- Could support `.detective-agent.yaml` for configuration
- Would override defaults but be overridden by env vars

## Deployment Considerations

### As a Library
```python
from detective_agent import Agent, AnthropicProvider, AgentConfig

config = AgentConfig(
    system_prompt="...",
    provider=AnthropicConfig(api_key="...")
)
provider = AnthropicProvider(config.provider)
agent = Agent(config, provider)

response = await agent.send_message("Assess release v2.1.0")
```

### As a CLI Tool
```bash
# Install
uv pip install detective-agent

# Run
detective-agent

# Or with Python
python -m detective_agent.cli
```

## Success Metrics

### Functional
- [ ] Can converse with Claude reliably
- [ ] Handles context window limits correctly
- [ ] Retries work for transient failures
- [ ] Tools execute successfully
- [ ] Conversations persist across sessions
- [ ] Traces provide complete visibility
- [ ] Evaluations validate behavior

### Quality
- [ ] >80% test coverage
- [ ] All tests pass
- [ ] Type hints on all functions
- [ ] No linting errors
- [ ] Clear documentation

### Performance
- [ ] Response latency <5s (excluding LLM time)
- [ ] Traces add <100ms overhead
- [ ] Context management adds <50ms overhead

## Future Enhancements

### Short Term
- Add more providers (OpenRouter, Ollama)
- Add web search tool
- Improve token estimation (use tiktoken)
- Add streaming responses
- Add conversation export formats

### Medium Term
- Advanced context management (summarization)
- Tool composition
- Multi-agent coordination
- Real-time observability dashboard
- Cost tracking and budgeting

### Long Term
- Self-healing and feedback loops
- Automated prompt optimization
- Tool auto-discovery
- Multi-modal inputs (images, documents)
- Production-ready deployment (Docker, K8s)