# Investigator Agent - Feature Readiness Assessment

[![Module 8](https://img.shields.io/badge/module-8-blue.svg)](docs/PROGRESS.md)
[![Tests](https://img.shields.io/badge/tests-160%2B-green.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-72%25-yellow.svg)](#testing)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](#prerequisites)

An advanced agentic AI system for assessing software feature production readiness. Built with sophisticated context management, memory capabilities, MCP integration, and comprehensive evaluation.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Features](#features)
- [CLI Usage](#cli-usage)
- [API Reference](#api-reference)
- [MCP Integration](#mcp-integration)
- [Architecture](#architecture)
- [Testing & Evaluation](#testing--evaluation)
- [Documentation](#documentation)
- [Development](#development)

## Overview

The Investigator Agent analyzes feature metadata, test results, and documentation to determine if features are ready for production deployment. It intelligently manages context through sub-conversations, learns from past assessments via memory, and provides evidence-based recommendations.

### Key Capabilities

- 🔍 **Feature Investigation** - JIRA metadata, analysis data, and documentation tools
- 🧠 **Sub-Conversation Management** - Intelligent context handling for large documents
- 💾 **Memory Systems** - File-based and MCP-backed (ChromaDB, Graphiti) memory stores
- 📊 **Comprehensive Evaluation** - 8 test scenarios with multi-dimensional scoring
- 🤖 **Agentic Execution** - Multi-turn reasoning with automatic tool orchestration
- 📈 **Full Observability** - OpenTelemetry tracing for all operations
- 🔄 **Resilient Retry** - Exponential backoff with jitter for API calls
- 🔌 **MCP Protocol** - Interchangeable knowledge backends via Model Context Protocol

### Module 8 Status

✅ **Complete** - All 7 phases implemented:
1. ✅ JIRA Tool Integration
2. ✅ Analysis Tool Integration
3. ✅ Documentation Tools
4. ✅ Sub-Conversation Context Management
5. ✅ Memory System (File-based + MCP)
6. ✅ Comprehensive Evaluation System
7. ✅ Final Integration and Polish

## Quick Start

### Prerequisites

- **Python 3.11 or higher**
- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **Anthropic API key** - Get yours at [console.anthropic.com](https://console.anthropic.com/settings/keys)

### Installation

```bash
# Navigate to module8
cd module8

# Install dependencies with uv
uv sync

# Activate virtual environment (optional)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Configuration

Create a `.env` file from the example:

```bash
# Copy example configuration
cp .env.example .env

# Edit .env and add your API key
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### First Conversation

Start the interactive CLI:

```bash
# Start a new conversation
uv run python cli.py

# Ask about a feature
You: Is the Maintenance Scheduling feature (FEAT-MS-001) ready for production?

# The agent will:
# 1. Call get_jira_data() to retrieve feature metadata
# 2. Call get_analysis() for test coverage and metrics
# 3. Read documentation (using sub-conversations for large docs)
# 4. Provide a production readiness assessment

# Exit when done
You: exit
```

### Basic Python Usage

```python
import asyncio
from pathlib import Path
from investigator_agent import Agent, AnthropicProvider, Config, ConversationStore
from investigator_agent.tools import get_jira_data, get_analysis, list_docs, read_doc
from investigator_agent.tools.registry import ToolRegistry

async def main():
    # Setup configuration
    config = Config.from_env()
    provider = AnthropicProvider(config.api_key, config.model)
    store = ConversationStore(Path("data/conversations"))

    # Register tools
    tool_registry = ToolRegistry()
    tool_registry.register("get_jira_data", "Get JIRA feature metadata",
                          {"type": "object", "properties": {}}, get_jira_data)
    tool_registry.register("get_analysis", "Get analysis data",
                          {"type": "object", "properties": {"feature_id": {"type": "string"}}},
                          get_analysis)

    # Create agent
    agent = Agent(provider, store, config, tool_registry=tool_registry)

    # Start conversation
    conversation = agent.new_conversation()
    response = await agent.send_message(
        conversation,
        "Is the Maintenance Scheduling feature ready for production?"
    )

    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

See [examples/](examples/) for complete working examples.

## Features

### 🔍 Feature Investigation Tools

The agent uses three categories of tools to gather comprehensive information:

#### 1. JIRA Metadata (`get_jira_data`)
Returns metadata for all features in the system:
- `feature_id` - Unique identifier
- `name` - Feature name
- `status` - Current status (In Progress, Testing, etc.)
- `data_quality` - Quality score of available data

**Usage:** No parameters - returns complete feature list

#### 2. Analysis Data (`get_analysis`)
Provides detailed metrics and reviews:
- **Metrics:** test_coverage, unit_tests, pipeline_results, performance, security_scans
- **Reviews:** security_review, stakeholder_approvals, uat_results

**Usage:** Parameterized by `feature_id` and `analysis_type`

#### 3. Documentation (`list_docs`, `read_doc`)
Access to planning and technical documents:
- Lists available documents for a feature
- Reads architecture, design, deployment plans
- Automatically triggers sub-conversations for large documents (>3K tokens)

### 🧠 Sub-Conversation Context Management

Large documents are analyzed in isolated sub-conversations to prevent context overflow:

```
Main Conversation (Decision Making)
├── Phase 1: Feature Identification → get_jira_data()
├── Phase 2: Analysis Gathering → get_analysis()
├── Phase 3: Documentation Review
│   ├── read_doc("ARCHITECTURE.md") → [5KB, triggers sub-conversation]
│   │   └── Sub-Conversation: Analyze architecture
│   │       ├── Specialized analysis prompt
│   │       ├── Claude-based summarization (~3:1 compression)
│   │       └── Returns: Concise summary with key points
│   └── Main receives summary (not full 5KB)
└── Phase 4: Final Assessment → Production readiness decision
```

**Benefits:**
- ✅ Main conversation stays under token limits
- ✅ Can analyze unlimited documentation
- ✅ Preserves critical information via intelligent summarization
- ✅ Uses tiktoken for accurate token counting (~90% accuracy)

**Configuration:**
```python
# In .env or Config
SUB_CONVERSATION_THRESHOLD=3000  # Tokens before triggering sub-conversation
```

### 💾 Memory System

Optional memory for learning from past assessments with multiple backend options:

#### File-Based Memory (Default)
```python
from investigator_agent.memory import FileMemoryStore

memory_store = FileMemoryStore(Path("data/memory"))
agent = Agent(..., memory_store=memory_store)
```

**Features:**
- JSON file storage in `data/memory/` directory
- No external dependencies (Docker-free)
- Fast operations (<5ms read/write)
- Suitable for development and small-scale deployments

#### MCP-Backed Memory (Production)
See [MCP Integration](#mcp-integration) section for ChromaDB and Graphiti options.

### 📊 Evaluation System

Comprehensive evaluation across 8 test scenarios with multi-dimensional scoring:

```bash
# Run full evaluation suite
uv run python examples/run_evaluations.py

# Save results as baseline
uv run python examples/run_evaluations.py --baseline v1.0

# Compare against baseline
uv run python examples/run_evaluations.py --compare v1.0
```

**Evaluation Dimensions:**
- **Feature Identification (20%)** - Correct feature from natural language query
- **Tool Usage (30%)** - Expected tools called (F1 score)
- **Decision Quality (40%)** - Correct readiness decision + justification
- **Context Management (10%)** - Proper sub-conversation usage

**Pass Threshold:** 70% overall score

**Example Output:**
```
✅ Scenario 1: feature_ready_all_green - Score: 0.85 (PASSED)
✅ Scenario 2: feature_not_ready_test_failures - Score: 0.78 (PASSED)
⚠️  Scenario 3: feature_borderline_partial_approval - Score: 0.65 (FAILED)

Overall Results:
  Total: 8 scenarios
  Passed: 6/8 (75.0%)
  Average Overall Score: 0.74
```

See [Testing & Evaluation](#testing--evaluation) for details.

## CLI Usage

The CLI provides an interactive interface for feature assessment:

### Commands

```bash
# Start new conversation
uv run python cli.py

# Continue existing conversation
uv run python cli.py continue <conversation-id>

# List all conversations
uv run python cli.py list

# Delete a conversation
uv run python cli.py delete <conversation-id>
```

### Interactive Mode

```
$ uv run python cli.py

🤖 Investigator Agent - Feature Readiness Assessment
📝 Conversation ID: abc123de

You: Is FEAT-MS-001 ready for production?

🔍 Calling tool: get_jira_data
✓ Found feature: Maintenance Scheduling (FEAT-MS-001)

🔍 Calling tool: get_analysis (feature_id=FEAT-MS-001)
✓ Retrieved analysis data

Agent: Based on my analysis of FEAT-MS-001 (Maintenance Scheduling):

**Assessment: READY for production** ✅

Key findings:
- Test coverage: 92% (exceeds 80% threshold)
- All unit tests passing (45/45)
- UAT completed with stakeholder approval
- Security review: No critical issues
- Performance within acceptable range

Confidence: High

You: exit
👋 Goodbye!
```

### Conversation Management

```bash
# List conversations with timestamps
$ uv run python cli.py list

Recent Conversations:
  abc123de - 2024-10-27 14:32:15 (3 messages)
  def456gh - 2024-10-27 13:15:42 (7 messages)

# Continue previous conversation
$ uv run python cli.py continue abc123de

📂 Loaded conversation abc123de
💬 3 messages in history

You: What about FEAT-QR-002?
```

## API Reference

### Core Classes

#### Agent

Main agent class that orchestrates conversations and tool execution.

```python
from investigator_agent import Agent

agent = Agent(
    provider: BaseProvider,
    store: ConversationStore,
    config: Config,
    tool_registry: ToolRegistry | None = None,
    memory_store: MemoryStore | None = None
)
```

**Methods:**

- **`new_conversation() -> Conversation`**
  - Creates a new conversation with unique ID
  - Returns: Conversation object

- **`async send_message(conversation: Conversation, user_message: str) -> str`**
  - Sends message and gets agent response
  - Handles tool loop automatically
  - Returns: Agent's final response text

- **`load_conversation(conversation_id: str) -> Conversation`**
  - Loads saved conversation from store
  - Raises: `FileNotFoundError` if not found

- **`list_conversations() -> list[tuple[str, str]]`**
  - Lists all saved conversations
  - Returns: List of (conversation_id, timestamp) tuples

#### Config

Configuration management with environment variable support.

```python
from investigator_agent import Config

# Load from environment
config = Config.from_env()

# Or create manually
config = Config(
    api_key="your-key",
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    max_messages=6,
    conversations_dir=Path("./data/conversations")
)
```

**Environment Variables:**
- `ANTHROPIC_API_KEY` (required)
- `ANTHROPIC_MODEL` (default: claude-3-5-sonnet-20241022)
- `MAX_TOKENS` (default: 4096)
- `MAX_MESSAGES` (default: 6)
- `CONVERSATIONS_DIR` (default: ./data/conversations)

#### ToolRegistry

Manages tool registration and execution.

```python
from investigator_agent.tools.registry import ToolRegistry

registry = ToolRegistry()

# Register a tool
registry.register(
    name="get_jira_data",
    description="Retrieves JIRA feature metadata",
    input_schema={"type": "object", "properties": {}},
    handler=async_function
)

# Execute tool
result = await registry.execute(tool_call)

# Get definitions for API
tools = registry.get_tool_definitions()
```

### Providers

#### AnthropicProvider

Claude implementation of the provider interface.

```python
from investigator_agent.providers.anthropic import AnthropicProvider

provider = AnthropicProvider(
    api_key="your-key",
    model="claude-3-5-sonnet-20241022"
)

# Send message with tools
response = await provider.send_message(
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=4096,
    system="You are a helpful assistant",
    tools=tool_definitions
)
```

### Memory System

#### FileMemoryStore

Simple file-based memory storage (no dependencies).

```python
from investigator_agent.memory.file_store import FileMemoryStore
from investigator_agent.memory.protocol import Memory

store = FileMemoryStore(Path("data/memory"))

# Store memory
memory = Memory(
    feature_id="FEAT-MS-001",
    decision="ready",
    justification="All tests passing",
    key_findings=["92% coverage", "UAT approved"],
    timestamp=datetime.now()
)
await store.store(memory)

# Retrieve memories
memories = await store.retrieve(query="maintenance", limit=5)
```

### Sub-Conversation Manager

```python
from investigator_agent.context.subconversation import SubConversationManager

manager = SubConversationManager(
    provider=provider,
    config=config,
    threshold_tokens=3000
)

# Analyze large content
summary = await manager.analyze_in_subconversation(
    content=large_document,
    purpose="Analyze architecture documentation",
    analysis_prompt="Extract key components and risks..."
)
```

## MCP Integration

The Investigator Agent supports the **Model Context Protocol (MCP)** for connecting to external knowledge backends like vector databases and knowledge graphs.

### Why MCP?

- **Interchangeable Backends** - Switch between ChromaDB, Graphiti, Neo4j without code changes
- **Standard Protocol** - Industry-standard communication with AI tool servers
- **Separation of Concerns** - Memory logic separate from storage implementation
- **Future-Proof** - Easy to add new backends as MCP servers become available

### Supported Backends

| Backend | Type | Use Case | Docker |
|---------|------|----------|--------|
| **File** | JSON Files | Development, no dependencies | No |
| **ChromaDB** | Vector Database | Semantic search over memories | Yes |
| **Graphiti** | Knowledge Graph | Temporal relationships, entity extraction | Yes |

### Quick Setup

#### 1. Start MCP Services

```bash
# Start ChromaDB MCP server
docker-compose up -d chroma-mcp chroma

# Or start Graphiti (includes Neo4j)
docker-compose --profile graphiti up -d

# Verify services
docker-compose ps
curl http://localhost:8001/health  # ChromaDB MCP
curl http://localhost:8000/health  # Graphiti MCP (if running)
```

#### 2. Configure Environment

```bash
# Add to .env
MCP_ENABLED=true
MCP_MEMORY_BACKEND=chroma  # Options: file, chroma, graphiti, none

# ChromaDB Configuration
MCP_CHROMA_ENABLED=true
MCP_CHROMA_URL=http://localhost:8001/sse
MCP_CHROMA_TRANSPORT=sse
MCP_CHROMA_COLLECTION=agent_memories

# OpenAI API key (for embeddings)
OPENAI_API_KEY=your-openai-key
```

#### 3. Use MCP Memory

```python
from investigator_agent.mcp import setup_mcp_tools
from investigator_agent.memory.mcp_store import MCPChromaMemoryStore

# Setup MCP tools
mcp_adapter = await setup_mcp_tools(
    tool_registry,
    chroma_url="http://localhost:8001/sse"
)

# Create MCP-backed memory
memory_store = MCPChromaMemoryStore(mcp_adapter.clients["chroma"])
await memory_store.initialize()

# Use with agent
agent = Agent(..., memory_store=memory_store)
```

### ChromaDB Backend

Vector database for semantic search over memories.

**Features:**
- Semantic similarity search using embeddings
- Scalable to 100K+ memories
- Natural language queries
- Metadata filtering

**Performance:**
- Store: ~50ms per memory
- Retrieve: ~100ms for semantic search
- Suitable for: Production deployments with semantic search needs

**Example:**

```python
from investigator_agent.memory.mcp_store import MCPChromaMemoryStore

memory_store = MCPChromaMemoryStore(chroma_client)
await memory_store.initialize()

# Semantic search
memories = await memory_store.retrieve(
    query="features with test coverage issues",
    limit=5
)
```

### Graphiti Backend

Temporal knowledge graph with automatic entity extraction.

**Features:**
- Entity and relationship extraction
- Temporal reasoning (time-based queries)
- Graph traversal for complex queries
- Automatic fact extraction from text

**Performance:**
- Store: ~200ms per memory (includes entity extraction)
- Retrieve: ~300ms for graph queries
- Suitable for: Complex relationship tracking, temporal analysis

**Requires:**
- OpenAI API key (for entity extraction)
- Neo4j database

**Example:**

```python
from investigator_agent.memory.mcp_store import MCPGraphitiMemoryStore

memory_store = MCPGraphitiMemoryStore(graphiti_client)

# Stores automatically extract entities
await memory_store.store(memory)

# Query with temporal context
memories = await memory_store.retrieve(
    query="features assessed in last week"
)
```

### Backend Comparison

| Feature | File | ChromaDB | Graphiti |
|---------|------|----------|----------|
| Setup | None | Docker | Docker + OpenAI |
| Storage | JSON files | Vector DB | Knowledge Graph |
| Search | Exact match | Semantic | Semantic + Graph |
| Scale | <1K | 100K+ | 10K+ |
| Speed | <5ms | ~100ms | ~300ms |
| Best For | Development | Production semantic search | Relationship tracking |

### Example: MCP Integration

See [examples/mcp_integration.py](examples/mcp_integration.py) for a complete example.

```bash
# Run MCP integration example
docker-compose up -d chroma-mcp chroma
uv run python examples/mcp_integration.py
```

## Architecture

### Project Structure

```
module8/
├── src/investigator_agent/          # Main package
│   ├── agent.py                    # Core agent with sub-conversations
│   ├── config.py                   # Configuration management
│   ├── models.py                   # Data models (Conversation, Message, etc.)
│   ├── system_prompt.py            # Agent instructions
│   ├── providers/                  # LLM providers
│   │   ├── base.py                # Provider interface
│   │   └── anthropic.py           # Claude implementation
│   ├── tools/                      # Tool system
│   │   ├── registry.py            # Tool registration & execution
│   │   ├── jira.py                # JIRA metadata tool
│   │   ├── analysis.py            # Analysis data tool
│   │   └── docs.py                # Documentation tools
│   ├── context/                    # Context management
│   │   ├── subconversation.py     # Sub-conversation manager
│   │   └── tokens.py              # Token counting (tiktoken)
│   ├── memory/                     # Memory system
│   │   ├── protocol.py            # Memory interface
│   │   ├── file_store.py          # File-based implementation
│   │   └── mcp_store.py           # MCP-backed implementations
│   ├── mcp/                        # MCP integration
│   │   ├── client.py              # MCP client
│   │   ├── config.py              # MCP configuration
│   │   └── adapter.py             # Tool adapter
│   ├── evaluations/                # Evaluation system
│   │   ├── scenarios.py           # Test scenarios
│   │   └── evaluator.py           # Scoring engine
│   ├── observability/              # OpenTelemetry tracing
│   ├── persistence/                # Conversation storage
│   └── retry/                      # Retry mechanism
├── examples/                        # Usage examples
│   ├── basic_usage.py             # Simple getting started
│   ├── feature_investigation.py   # Full investigation workflow
│   ├── mcp_integration.py         # MCP backends
│   └── run_evaluations.py         # Evaluation runner
├── tests/                           # 160+ tests (72% coverage)
├── incoming_data/                   # Test data (4 features)
│   ├── feature1/                   # FEAT-MS-001 (ready)
│   ├── feature2/                   # FEAT-QR-002 (not ready)
│   ├── feature3/                   # FEAT-RS-003 (borderline)
│   └── feature4/                   # FEAT-CT-004 (incomplete)
├── data/                            # Runtime data
│   ├── conversations/              # Saved conversations
│   ├── traces/                     # OpenTelemetry traces
│   ├── memory/                     # File-based memory
│   └── baselines/                  # Evaluation baselines
├── docs/                            # Documentation
│   ├── DESIGN.md                  # Architecture & design decisions
│   ├── INTEGRATE.md               # Integration patterns
│   ├── EXERCISE.md                # Learning exercises
│   ├── MANUAL_TEST_PLAN.md        # Comprehensive testing guide
│   ├── PLAN.md                    # Project plan
│   ├── PROGRESS.md                # Development progress
│   └── STEPS.md                   # Implementation steps
├── cli.py                           # Interactive CLI
├── docker-compose.yml              # MCP services
└── pyproject.toml                  # Dependencies
```

### Three-Phase Workflow

**Phase 1: Feature Identification**
1. User asks about a feature in natural language
2. Agent calls `get_jira_data()` to retrieve all feature metadata
3. Uses NLP to identify which feature is being discussed
4. Extracts `feature_id` for subsequent tool calls

**Phase 2: Data Gathering**
1. Calls `get_analysis()` for relevant analysis types (metrics, reviews)
2. Calls `list_docs()` and `read_doc()` for documentation
3. Large documents (>3K tokens) automatically trigger sub-conversations
4. Receives concise summaries in main conversation

**Phase 3: Assessment**
1. Synthesizes all gathered information
2. Makes production readiness decision: `ready`, `not_ready`, or `borderline`
3. Provides evidence-based justification with specific findings
4. States confidence level (Low/Medium/High)

### Sub-Conversation Pattern

When tool results exceed the token threshold (default: 3000 tokens), a sub-conversation is automatically created:

```python
# Automatic sub-conversation trigger
if count_tokens(tool_result) > threshold:
    # Create isolated sub-conversation
    summary = await manager.analyze_in_subconversation(
        content=tool_result,
        purpose="Analyze API specification",
        analysis_prompt="Extract key endpoints, auth requirements, and risks..."
    )

    # Summary replaces full content in main conversation
    # Typical compression: 5KB document → 1.5KB summary
    return summary
```

**Key Benefits:**
- ✅ Prevents context window overflow
- ✅ Enables analysis of arbitrarily large documents
- ✅ Preserves critical information via Claude-based summarization
- ✅ Main conversation remains focused on decision-making

## Testing & Evaluation

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov=investigator_agent --cov-report=html

# Run specific test file
uv run pytest tests/agent_test.py -v

# Run specific test
uv run pytest tests/agent_test.py::test_send_message -v
```

**Test Suite:**
- 160+ tests covering all components
- 72% code coverage
- Unit tests for all tools, memory, context management
- Integration tests for full workflows
- Evaluation tests for quality measurement

### Running Evaluations

The evaluation system measures agent quality across 8 test scenarios:

```bash
# Run evaluation suite
uv run python examples/run_evaluations.py

# Save as baseline
uv run python examples/run_evaluations.py --baseline v1.0

# Compare to baseline
uv run python examples/run_evaluations.py --compare v1.0
```

**Evaluation Scenarios:**

1. **Feature Ready (All Green)** - All metrics passing, full approval
2. **Feature Not Ready (Test Failures)** - Critical test failures
3. **Feature Borderline (Partial Approval)** - Mixed signals
4. **Feature Incomplete Data** - Missing critical information
5. **Feature Ready (Edge Case)** - Minimal passing thresholds
6. **Feature Not Ready (Security Issues)** - Security blockers
7. **Feature Ready (High Confidence)** - Strong signals
8. **Feature Borderline (Performance Issues)** - Performance concerns

**Scoring:**
- **Feature Identification (20%)** - Correct feature from NL query
- **Tool Usage (30%)** - Expected tools called (F1 score)
- **Decision Quality (40%)** - Correct decision + justification
- **Context Management (10%)** - Sub-conversation usage

**Pass Threshold:** 70% overall score

### Manual Testing

For hands-on testing and learning, use the comprehensive manual test plan:

```bash
# Follow the interactive test plan
cat docs/MANUAL_TEST_PLAN.md

# Tests include:
# 1. Basic Conversation Flow
# 2. Continuing Conversations
# 3. Observability (Traces)
# 4. Context Management (Sub-conversations)
# 5. File-Based Memory
# 6. Graphiti Memory (Docker)
# 7. Evaluation System
# 8. Multi-Feature Workflow
```

See [docs/MANUAL_TEST_PLAN.md](docs/MANUAL_TEST_PLAN.md) for detailed step-by-step instructions.

## Documentation

### Core Documentation

- **[DESIGN.md](docs/DESIGN.md)** - Architecture and design decisions
  - System architecture
  - Component design
  - Technology choices
  - Trade-offs and rationale

- **[INTEGRATE.md](docs/INTEGRATE.md)** - Integration patterns
  - How to integrate the agent into your systems
  - API usage patterns
  - Customization guide
  - Extension points

- **[EXERCISE.md](docs/EXERCISE.md)** - Learning exercises
  - Hands-on coding exercises
  - Understanding sub-conversations
  - Memory system exploration
  - Evaluation framework

- **[MANUAL_TEST_PLAN.md](docs/MANUAL_TEST_PLAN.md)** - Comprehensive testing guide
  - 8 manual test scenarios
  - Step-by-step instructions
  - What to observe and learn
  - Troubleshooting

### Project Planning

- **[PLAN.md](docs/PLAN.md)** - Detailed phase-by-phase plan
- **[STEPS.md](docs/STEPS.md)** - Implementation steps
- **[PROGRESS.md](docs/PROGRESS.md)** - Current status and completion

## Development

### Technology Stack

- **Python 3.11+** - Modern async/await, type hints
- **Anthropic Claude** - LLM provider (Sonnet 3.5)
- **tiktoken** - Token counting (~90% accurate for Claude)
- **OpenTelemetry** - Observability and tracing
- **FastMCP** - MCP protocol implementation
- **httpx** - Async HTTP client
- **pytest** - Testing framework
- **uv** - Fast Python package manager

### Performance Characteristics

**Average Feature Assessment:**
- Tool Calls: 3-5 per assessment
- Tokens: 5K-15K total (with sub-conversations)
- Latency: 10-30s depending on complexity
- Sub-Conversations: 0-2 per assessment
- Cost: ~$0.05-0.15 per assessment (Sonnet 3.5 pricing)

**Context Management:**
- Main conversation: <20K tokens typical
- Sub-conversations: 5K-10K tokens each
- Summarization: ~3:1 compression ratio
- Memory: O(1) file lookup, <100ms retrieval

**MCP Memory Performance:**
- File-based: <5ms read/write
- ChromaDB: ~50ms store, ~100ms semantic search
- Graphiti: ~200ms store (with entity extraction), ~300ms graph queries

### Known Limitations

1. **Token Counting Accuracy** - ~90% accurate (tiktoken approximation)
   - Actual Claude API usage may vary slightly
   - Good enough for threshold detection

2. **File-Based Memory Scalability** - Simple storage, not vector search
   - Works well for small scale (<1K features)
   - Use ChromaDB MCP backend for larger deployments

3. **Automatic Memory Storage** - Not implemented by default
   - Memory infrastructure complete
   - Storing assessments currently explicit (see examples)
   - Can be automated in agent post-processing

4. **Evaluation Automation** - Manual running (not CI integrated)
   - Designed as quality measurement tool
   - Can be integrated into CI/CD pipelines if needed

### Contributing

This is an educational project from Module 8 of the AI Agent Development Course. Feel free to:

- Explore the code and experiment
- Try different models or providers
- Add new tools for your domain
- Extend the memory system
- Create new evaluation scenarios

### Local Development

```bash
# Install development dependencies
uv sync --all-extras

# Run tests with coverage
uv run pytest --cov=investigator_agent

# Run linting
uv run ruff check src/

# Run type checking
uv run mypy src/
```

## License

Educational project - Module 8 of AI Agent Development Course

---

**Built with Claude Code** 🤖

For questions or issues, see the [comprehensive documentation](docs/) or run the [manual test plan](docs/MANUAL_TEST_PLAN.md).
