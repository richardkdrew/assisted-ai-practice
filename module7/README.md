# Detective Agent

A foundational LLM agent built from first principles for release risk assessment.

## Overview

The Detective Agent is the first line of defense in a Release Confidence System. It investigates software releases by analyzing changes, test results, and deployment metrics to identify potential risks.

## Features

- **Multi-provider Support**: Works with Claude (Anthropic), OpenRouter, Ollama, and other LLM providers
- **OpenTelemetry Observability**: Complete visibility into agent operations with traces and spans
- **Context Window Management**: Intelligent truncation to handle long conversations
- **Retry Mechanism**: Exponential backoff for handling rate limits and transient failures
- **Tool Calling**: Extensible tool framework for external system integration
- **Evaluation Framework**: Automated validation of agent behavior and regression tracking

## Project Status

🚧 **In Development** - Currently implementing Phase 0: Project Setup

See [docs/PROGRESS.md](docs/PROGRESS.md) for detailed implementation status.

## Quick Start

### Prerequisites

- Python 3.11 or higher
- uv package manager
- API key for your chosen LLM provider (e.g., ANTHROPIC_API_KEY)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd module7

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv sync
```

### Configuration

Set up your environment variables:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Usage

```bash
# Run the CLI
python -m detective_agent.cli

# Or use the installed command (after installation)
detective-agent
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=detective_agent --cov-report=html

# Run specific test file
pytest src/detective_agent/providers/anthropic_test.py
```

### Project Structure

```
module7/
├── src/detective_agent/    # Main package
│   ├── models/            # Data models
│   ├── providers/         # LLM provider implementations
│   ├── tools/             # Tool implementations
│   ├── context/           # Context window management
│   ├── retry/             # Retry mechanism
│   ├── observability/     # OpenTelemetry instrumentation
│   ├── persistence/       # Conversation storage
│   └── evaluation/        # Evaluation framework
├── tests/                 # Integration tests
├── data/                  # Runtime data
│   ├── conversations/     # Saved conversations
│   ├── traces/           # OpenTelemetry traces
│   └── reports/          # Risk assessment reports
└── docs/                  # Documentation
    ├── DESIGN.md         # Architecture and design
    ├── PLAN.md           # Implementation plan
    ├── STEPS.md          # Implementation steps
    └── PROGRESS.md       # Progress tracking
```

## Documentation

- [Design Specification](docs/DESIGN.md) - Architecture and design decisions
- [Implementation Plan](docs/PLAN.md) - Detailed implementation plan
- [Implementation Steps](docs/STEPS.md) - Step-by-step guide
- [Progress Tracking](docs/PROGRESS.md) - Current implementation status

## Use Case: Release Risk Assessment

The Detective Agent analyzes software releases by:

1. Retrieving release summaries (code changes, test results, metrics)
2. Analyzing data to identify potential risks
3. Filing risk reports with severity assessments

**Severity Levels:**
- **HIGH**: Critical test failures, elevated error rates (>5%), risky changes
- **MEDIUM**: Minor test failures, slight metric degradation (2-5%)
- **LOW**: All tests passing, healthy metrics (<2% error rate)

## Technology Stack

- **Python 3.11+** with async/await
- **httpx** for HTTP client (async, HTTP/2 support)
- **Pydantic** for configuration and validation
- **OpenTelemetry** for observability
- **pytest** for testing

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
