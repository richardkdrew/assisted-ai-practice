
# Investigator Agent - Feature Readiness Assessment

An advanced agentic AI system for assessing software feature production readiness. Built with sophisticated context management, memory capabilities, and comprehensive evaluation.

## Overview

The Investigator Agent analyzes feature metadata, test results, and documentation to determine if features are ready for production deployment. It intelligently manages context through sub-conversations, learns from past assessments via memory, and provides evidence-based recommendations.

**Module 8 Capabilities:**
- 🔍 Feature investigation via JIRA, analysis data, and documentation
- 🧠 Sub-conversation context management for large documents
- 💾 File-based memory system for learning from past assessments
- 📊 Comprehensive evaluation framework with 8 test scenarios
- 🤖 Agentic tool execution with multi-turn reasoning
- 📈 Full OpenTelemetry observability
- 🔄 Automatic retry with exponential backoff
- ✅ 160+ tests with 72% coverage

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Anthropic API key

### Installation

```bash
# Navigate to module8
cd module8

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux

# Install dependencies
uv sync
```

### Configuration

Create a `.env` file with your API key:

```bash
ANTHROPIC_API_KEY="your-api-key-here"
```

### Basic Usage

```python
import asyncio
from pathlib import Path
from investigator_agent import Agent, AnthropicProvider, Config, ConversationStore
from investigator_agent.tools import get_jira_data, get_analysis, list_docs, read_doc
from investigator_agent.tools.registry import ToolRegistry

async def main():
    # Setup
    provider = AnthropicProvider(api_key="your-key", model="claude-3-5-sonnet-20241022")
    store = ConversationStore(Path("conversations"))
    config = Config()

    # Register tools
    tool_registry = ToolRegistry()
    tool_registry.register_tool(
        name="get_jira_data",
        description="Retrieves metadata for all features",
        input_schema={"type": "object", "properties": {}, "required": []},
        handler=get_jira_data,
    )
    # ... register other tools ...

    # Create agent
    agent = Agent(provider, store, config, tool_registry=tool_registry)

    # Assess a feature
    conversation = agent.new_conversation()
    response = await agent.send_message(
        conversation,
        "Is the Maintenance Scheduling feature ready for production?"
    )

    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

### 🔍 Feature Investigation Tools

The agent uses three categories of tools:

**1. JIRA Metadata** (`get_jira_data`)
- Returns metadata for all features
- Includes feature_id, status, data_quality
- No parameters - returns complete feature list

**2. Analysis Data** (`get_analysis`)
- Metrics: test_coverage, unit_tests, pipeline_results, performance, security_scans
- Reviews: security reviews, stakeholder approvals, UAT results
- Parameterized by feature_id and analysis_type

**3. Documentation** (`list_docs`, `read_doc`)
- Lists available planning documents
- Reads architecture, design, deployment plans
- Triggers sub-conversations for large documents (>10K tokens)

### 🧠 Sub-Conversation Context Management

Large documents are analyzed in isolated sub-conversations:

```
Main Conversation (Decision Making)
├── Phase 1: Feature Identification → get_jira_data()
├── Phase 2: Analysis Gathering → get_analysis()
├── Phase 3: Documentation Review
│   ├── read_doc("ARCHITECTURE.md") → [15KB, triggers sub-conversation]
│   │   └── Sub-Conversation: Analyze architecture
│   │       ├── Specialized analysis prompt
│   │       ├── LLM-based summarization (10:1 compression)
│   │       └── Returns: Concise summary
│   └── Main receives summary (not full 15KB)
└── Phase 4: Final Assessment → Production readiness decision
```

**Benefits:**
- Main conversation stays under token limits
- Can analyze unlimited documentation
- Preserves critical information via intelligent summarization
- Uses tiktoken for ~90% accurate token counting

### 💾 Memory System

Optional file-based memory for learning from past assessments:

```python
from investigator_agent.memory import FileMemoryStore, Memory

# Initialize memory
memory_store = FileMemoryStore(Path("memory_store"))

# Create agent with memory
agent = Agent(..., memory_store=memory_store)

# Memory automatically retrieved for relevant queries
response = await agent.send_message(conv, "We assessed this feature before...")
```

**Memory Features:**
- JSON file storage in `memory_store/` directory
- Indexed by feature_id and timestamp
- Query by text, feature_id, or decision type
- Graceful degradation (agent works without memory)

### 📊 Evaluation System

Comprehensive evaluation across 8 scenarios:

```bash
# Run evaluations
python examples/run_evaluations.py

# Save as baseline
python examples/run_evaluations.py --baseline v1

# Compare to baseline
python examples/run_evaluations.py --compare v1
```

**Evaluation Dimensions:**
- Feature Identification (20%) - Correct feature from NLP query
- Tool Usage (30%) - Expected tools called (F1 score)
- Decision Quality (40%) - Correct readiness decision + justification
- Context Management (10%) - Proper sub-conversation usage

**Pass Threshold:** 70% overall score

## Project Structure

```
module8/
├── src/investigator_agent/          # Main package
│   ├── agent.py                    # Core agent with sub-conversations
│   ├── config.py                   # Configuration
│   ├── models.py                   # Data models + SubConversation
│   ├── system_prompt.py            # Agent instructions
│   ├── providers/                  # LLM providers
│   │   ├── base.py
│   │   └── anthropic.py
│   ├── tools/                      # Tool system
│   │   ├── registry.py
│   │   ├── jira.py                # JIRA metadata tool
│   │   ├── analysis.py            # Analysis data tool
│   │   └── docs.py                # Documentation tools
│   ├── context/                    # Context management
│   │   ├── manager.py
│   │   ├── tokens.py              # Token counting (tiktoken)
│   │   └── subconversation.py     # Sub-conversation manager
│   ├── memory/                     # Memory system
│   │   ├── protocol.py            # Memory interface
│   │   └── file_store.py          # File-based implementation
│   ├── evaluations/                # Evaluation system
│   │   ├── scenarios.py           # 8 test scenarios
│   │   └── evaluator.py           # Scoring engine
│   ├── observability/              # OpenTelemetry tracing
│   ├── persistence/                # Conversation storage
│   └── retry/                      # Retry mechanism
├── examples/                        # Usage examples
│   ├── feature_investigation_phase*.py
│   └── run_evaluations.py         # Evaluation runner
├── incoming_data/                   # Test data (4 features)
│   ├── feature1/                   # Maintenance Scheduling (ready)
│   ├── feature2/                   # QR Code Check-in (not ready)
│   ├── feature3/                   # Resource Reservation (borderline)
│   └── feature4/                   # Contribution Tracking (incomplete)
├── tests/                           # 160+ tests (72% coverage)
├── data/                            # Runtime data
│   ├── conversations/
│   ├── traces/
│   ├── baselines/                  # Evaluation baselines
│   └── memory_store/               # Memory files
└── docs/                            # Documentation
    ├── PLAN.md
    ├── STEPS.md
    └── PROGRESS.md
```

## Architecture

### Three-Phase Workflow

**Phase 1: Feature Identification**
1. Call `get_jira_data()` to retrieve all feature metadata
2. Identify which feature user is asking about (NLP)
3. Extract feature_id for subsequent tool calls

**Phase 2: Data Gathering**
1. Call `get_analysis()` for relevant analysis types
2. Call `list_docs()` and `read_doc()` for documentation
3. Large docs (>10K tokens) analyzed in sub-conversations
4. Receive concise summaries in main conversation

**Phase 3: Assessment**
1. Synthesize gathered information
2. Make production readiness decision (ready/not_ready/borderline)
3. Provide evidence-based justification
4. State confidence level

### Sub-Conversation Pattern

```python
# Automatically triggered when tool result exceeds 10K tokens
if count_tokens(tool_result) > 10000:
    # Create isolated sub-conversation
    sub_conv = SubConversationManager.analyze_in_subconversation(
        content=tool_result,
        purpose="Analyze architecture documentation",
        analysis_prompt="Extract key architectural components..."
    )

    # Returns compressed summary (targeting 10:1 ratio)
    summary = sub_conv.summary  # ~1K tokens instead of 10K

    # Main conversation receives only summary
    conversation.add_message("user", summary)
```

## Configuration

Environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |
| `MAX_TOKENS` | Max tokens per response | `4096` |
| `MAX_MESSAGES` | Context window size | `6` |
| `CONVERSATIONS_DIR` | Conversation storage | `./conversations` |
| `TRACES_DIR` | Trace storage | `./traces` |

## Development

### Running Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=investigator_agent

# Specific phase tests
uv run pytest src/investigator_agent/tools/jira_test.py -v
uv run pytest src/investigator_agent/memory/ -v
```

**Test Suite:** 160 tests passing, 72% coverage

### Running Examples

```bash
# Phase 1-3: Basic investigation
python examples/feature_investigation.py

# Phase 4: Sub-conversations
python examples/feature_investigation_phase4.py

# Phase 5: Memory system
python examples/feature_investigation_phase5.py

# Phase 6: Evaluations
python examples/run_evaluations.py
```

### Running Evaluations

```bash
# Run all 8 scenarios
python examples/run_evaluations.py

# Expected output:
# Total Scenarios: 8
# Passed: 6/8
# Pass Rate: 75.0%
# Average Scores:
#   feature_identification: 0.85
#   tool_usage: 0.72
#   decision_quality: 0.68
#   context_management: 0.90
#   overall: 0.74
```

## Technology Stack

- **Python 3.11+** - Async/await, type hints
- **Anthropic Claude** - LLM provider (Sonnet 3.5)
- **tiktoken** - Token counting (~90% accurate for Claude)
- **OpenTelemetry** - Observability and tracing
- **httpx** - Async HTTP client
- **pytest** - Testing framework (160+ tests)
- **uv** - Fast Python package manager

## Project Status

✅ **Module 8 Complete** - All 7 phases implemented:

1. ✅ Phase 1: JIRA Tool
2. ✅ Phase 2: Analysis Tool
3. ✅ Phase 3: Documentation Tools
4. ✅ Phase 4: Sub-Conversation Context Management
5. ✅ Phase 5: Memory System (File-based)
6. ✅ Phase 6: Comprehensive Evaluation System
7. ✅ Phase 7: Final Integration and Polish

See [docs/PROGRESS.md](docs/PROGRESS.md) for detailed status.

## Performance Characteristics

**Average Feature Assessment:**
- Tool Calls: 3-5 per assessment
- Tokens: 5K-15K total (with sub-conversations)
- Latency: 10-30s depending on complexity
- Sub-Conversations: 0-2 per assessment
- Cost: ~$0.05-0.15 per assessment (Sonnet 3.5 pricing)

**Context Management:**
- Main conversation: <20K tokens typical
- Sub-conversations: 10K-20K tokens each
- Summarization: 10:1 compression ratio target
- Memory: O(1) file lookup, <100ms retrieval

## Known Limitations

1. **Memory Storage:** Simple file-based (not vector search)
   - Works well for small scale (4 features in examples)
   - Could be upgraded to vector DB for larger deployments

2. **Evaluation:** Manual running (not automated CI)
   - Designed as quality measurement tool
   - Can be integrated into CI/CD if needed

3. **Token Counting:** ~90% accurate (tiktoken approximation)
   - Good enough for threshold detection
   - Actual Claude usage may vary slightly

4. **Automatic Memory Storage:** Not implemented
   - Memory infrastructure complete
   - Storing assessments currently manual (examples demonstrate)
   - Could be automated in future enhancement

## Documentation

- [Implementation Plan](docs/PLAN.md) - Detailed phase-by-phase plan
- [Implementation Steps](docs/STEPS.md) - Step-by-step guide
- [Progress Tracking](docs/PROGRESS.md) - Current status

## License

Educational project - Module 8 of AI Agent Development Course

---

**Built with Claude Code** 🤖
