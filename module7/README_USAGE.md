# Detective Agent - Usage Guide

A simple, foundational AI agent with conversation capabilities built using Anthropic's Claude.

## Quick Start

### 1. Set up your API key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 2. Run the agent

Start a new conversation:
```bash
uv run python cli.py
```

List all conversations:
```bash
uv run python cli.py list
```

Continue an existing conversation:
```bash
uv run python cli.py continue <conversation-id>
```

## Configuration

Configure via environment variables:

- `ANTHROPIC_API_KEY` (required): Your Anthropic API key
- `ANTHROPIC_MODEL` (optional): Model to use (default: `claude-3-5-sonnet-20241022`)
- `MAX_TOKENS` (optional): Max tokens per response (default: `4096`)
- `CONVERSATIONS_DIR` (optional): Where to store conversations (default: `./conversations`)

## Running Tests

Run all tests:
```bash
uv run pytest
```

Run with coverage:
```bash
uv run pytest -v
```

## Project Structure

```
├── agent.py                 # Core agent logic
├── cli.py                   # Command-line interface
├── models/
│   ├── config.py           # Configuration management
│   └── message.py          # Message and conversation models
├── providers/
│   ├── base.py            # Provider abstraction
│   └── anthropic.py       # Anthropic implementation
├── persistence/
│   └── store.py           # Filesystem storage
└── tests/                  # Comprehensive test suite
```

## Phase 1 Complete ✅

**Implemented Features:**
- Basic conversation with Claude
- Filesystem persistence
- Load and continue conversations
- Simple CLI interface
- 100% test coverage on core components
- 23 passing tests including integration tests

**Next Phase:** Observability with OpenTelemetry
