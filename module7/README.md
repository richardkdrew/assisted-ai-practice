# Detective Agent

A production-ready agentic AI system built from first principles for software release risk assessment. Features tool calling, observability, context management, and automated evaluation.

## Overview

The Detective Agent is an AI-powered system that analyzes software releases to identify potential risks. It uses Claude (Anthropic) to assess release information, call tools to gather data, and generate risk reports with severity levels.

**Key Capabilities:**
- 🤖 Agentic tool execution with multi-turn loops
- 📊 Comprehensive observability with OpenTelemetry
- 🔄 Automatic retry with exponential backoff
- 💾 Persistent conversation history
- 📏 Context window management
- ✅ Automated evaluation framework

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Anthropic API key

### Installation

```bash
# Clone the repository
cd module7

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
uv sync
```

### Configuration

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Basic Usage

```python
import asyncio
from detective_agent import Agent, Config
from detective_agent.providers.anthropic import AnthropicProvider
from detective_agent.persistence.store import ConversationStore
from detective_agent.tools.registry import ToolRegistry
from detective_agent.tools.release_tools import (
    get_release_summary,
    file_risk_report,
    GET_RELEASE_SUMMARY_SCHEMA,
    FILE_RISK_REPORT_SCHEMA,
)

async def main():
    # Setup
    config = Config.from_env()
    provider = AnthropicProvider(config.api_key, config.model)
    store = ConversationStore(config.conversations_dir)

    # Register tools
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

    # Create agent with tools
    agent = Agent(provider, store, config, tool_registry=registry)

    # Have a conversation
    conversation = agent.new_conversation()
    response = await agent.send_message(
        conversation,
        "Assess the risk of deploying release rel-003"
    )

    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

### 🤖 Agentic Tool Execution

The agent can autonomously call tools to gather information and complete tasks:

```python
# Agent automatically:
# 1. Calls get_release_summary to gather data
# 2. Analyzes the results
# 3. Calls file_risk_report with severity and findings
# 4. Returns a comprehensive assessment
```

Tools are executed in a loop (max 10 iterations) until the agent has all the information it needs.

### 📊 OpenTelemetry Observability

Every conversation generates detailed traces:

```python
# Traces include:
# - API call timing and token counts
# - Tool execution spans
# - Context window management
# - Retry attempts
```

Traces are saved to `data/traces/{trace_id}.json` for debugging and analysis.

### 🔄 Automatic Retry

Transient failures are automatically retried with exponential backoff:

```python
config = Config(
    api_key="...",
    retry_config=RetryConfig(
        max_attempts=3,
        initial_delay=1.0,
        max_delay=60.0,
        backoff_factor=2.0,
        jitter=True,
    )
)
```

### 💾 Conversation Persistence

Conversations are automatically saved and can be continued:

```python
# Start a new conversation
conversation = agent.new_conversation()

# Continue existing conversation
conversation = agent.load_conversation(conversation_id)
```

### 📏 Context Window Management

Long conversations are automatically truncated to fit within token limits:

```python
# Keeps last 6 messages by default
# Configurable via MAX_MESSAGES environment variable
config = Config(max_messages=10)
```

### ✅ Evaluation Framework

Validate agent behavior with automated evaluations:

```python
from evals import ALL_SCENARIOS
from evals.evaluator import Evaluator

evaluator = Evaluator(pass_threshold=0.7)
results = await evaluator.run_suite(agent, ALL_SCENARIOS)

print(f"Pass Rate: {results.pass_rate:.1%}")
print(f"Tool Usage Score: {results.avg_scores['tool_usage']:.2f}")
print(f"Decision Quality: {results.avg_scores['decision_quality']:.2f}")
```

## Project Structure

```
module7/
├── src/detective_agent/         # Main package
│   ├── __init__.py
│   ├── agent.py                # Core agent with tool loop
│   ├── config.py               # Configuration management
│   ├── models.py               # Data models
│   ├── system_prompt.py        # Agent instructions
│   ├── providers/              # LLM provider implementations
│   │   ├── base.py            # Provider interface
│   │   └── anthropic.py       # Claude implementation
│   ├── tools/                 # Tool system
│   │   ├── registry.py        # Tool registration and execution
│   │   └── release_tools.py   # Release assessment tools
│   ├── context/               # Context window management
│   │   └── manager.py
│   ├── retry/                 # Retry mechanism
│   │   └── strategy.py
│   ├── observability/         # OpenTelemetry tracing
│   │   ├── tracer.py
│   │   └── exporter.py
│   └── persistence/           # Conversation storage
│       └── store.py
├── evals/                      # Evaluation framework
│   ├── scenarios.py           # Test scenarios
│   ├── evaluator.py           # Scoring engine
│   └── reporters.py           # Report generation
├── tests/                      # 91 comprehensive tests
├── data/                       # Runtime data
│   ├── conversations/         # Saved conversations
│   ├── traces/               # OpenTelemetry traces
│   ├── reports/              # Risk assessment reports
│   └── baselines/            # Evaluation baselines
└── docs/                       # Documentation
    ├── DESIGN.md             # Architecture
    ├── PLAN.md               # Implementation plan
    └── PROGRESS.md           # Progress tracking
```

## Configuration

Configure via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |
| `ANTHROPIC_MODEL` | Claude model to use | `claude-3-5-sonnet-20241022` |
| `MAX_TOKENS` | Max tokens per response | `4096` |
| `MAX_MESSAGES` | Context window size (messages) | `6` |
| `CONVERSATIONS_DIR` | Where to store conversations | `./conversations` |
| `SYSTEM_PROMPT` | Custom system prompt | See `system_prompt.py` |

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=detective_agent --cov-report=html

# Run specific test file
uv run pytest tests/agent_test.py -v
```

**Test Coverage:** 91% (91/91 tests passing)

### Running Evaluations

```bash
# Run evaluation suite
python -c "
import asyncio
from evals import ALL_SCENARIOS
from evals.evaluator import Evaluator
from detective_agent import Agent, Config
# ... setup agent ...
evaluator = Evaluator()
results = asyncio.run(evaluator.run_suite(agent, ALL_SCENARIOS))
print(f'Pass Rate: {results.pass_rate:.1%}')
"
```

### Adding New Tools

```python
from detective_agent.tools.registry import ToolRegistry

# Define tool function
async def my_tool(param: str) -> dict:
    # Tool implementation
    return {"result": "success"}

# Register tool
registry.register(
    name="my_tool",
    description="Does something useful",
    input_schema={
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    },
    handler=my_tool,
)
```

## Use Case: Release Risk Assessment

The Detective Agent assesses software release risk by:

1. **Gathering Data**: Calls `get_release_summary` to retrieve:
   - Version and changes
   - Test results (passed/failed/skipped)
   - Deployment metrics (error rate, response time)

2. **Analyzing Risk**: Evaluates:
   - Test failure rate
   - Error rate thresholds
   - Impact of changes
   - Performance metrics

3. **Filing Reports**: Calls `file_risk_report` with:
   - Severity level (HIGH/MEDIUM/LOW)
   - Specific findings
   - Recommendations

### Severity Guidelines

- **HIGH**: >5% error rate, critical test failures, risky changes
- **MEDIUM**: 2-5% error rate, minor test failures, moderate changes
- **LOW**: <2% error rate, all tests passing, low-impact changes

## Technology Stack

- **Python 3.11+** with async/await
- **httpx** - HTTP client with HTTP/2 support
- **Anthropic SDK** - Claude API client
- **Pydantic** - Configuration validation
- **OpenTelemetry** - Observability and tracing
- **pytest** - Testing framework
- **uv** - Fast Python package manager

## Project Status

✅ **Production Ready** - All 7 core phases complete:

1. ✅ Basic Conversation
2. ✅ Observability
3. ✅ Context Management
4. ✅ Retry Mechanism
5. ✅ System Prompt Engineering
6. ✅ Tool Abstraction
7. ✅ Evaluation System

See [docs/PROGRESS.md](docs/PROGRESS.md) for detailed status.

## Documentation

- [Design Specification](docs/DESIGN.md) - Architecture and design decisions
- [Implementation Plan](docs/PLAN.md) - Detailed implementation plan
- [Progress Tracking](docs/PROGRESS.md) - Current implementation status
- [Implementation Steps](docs/STEPS.md) - Step-by-step guide

## Contributing

Contributions are welcome! Please:

1. Write tests for new features
2. Maintain test coverage >90%
3. Follow existing code style
4. Update documentation

## License

[Add your license here]
