# AI Agent Template System

**Build production-quality AI agents in hours, not days**

A comprehensive, battle-tested template for building agentic AI systems with tool calling, observability, evaluation, and robust error handling.

---

## What is This?

This is a **complete framework** for building AI agents that:
- ✅ Use tools to accomplish tasks (agentic behavior)
- ✅ Handle errors gracefully (retry with exponential backoff)
- ✅ Manage context windows (conversation truncation)
- ✅ Provide full observability (OpenTelemetry traces)
- ✅ Persist conversations (filesystem storage)
- ✅ Include automated evaluation (quality assurance)
- ✅ Achieve 90%+ test coverage (production-ready)

## Why Use This Template?

### 90% of Every Agent is the Same

**Generic Infrastructure (included):**
- Conversation management
- Provider abstraction (LLM APIs)
- Tool execution framework
- Context window handling
- Retry mechanisms
- Observability and tracing
- Persistence layer
- Evaluation framework

**Your Customization (10% of work):**
- System prompt (agent personality)
- Domain-specific tools (2-5 tools)
- Evaluation scenarios (test cases)
- Mock data for testing

### Proven Architecture

Based on the **Detective Agent** - a production-grade release risk assessment system built through 8 complete implementation phases:
- 1,340 lines of code
- 91 tests with 91% coverage
- Complete documentation
- Real-world validation

---

## Quick Start

### For AI Assistants

**Building an agent for a user?**

1. Read: [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md) - comprehensive guide
2. Run discovery: [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md) or [DISCOVERY_CONVERSATION.md](DISCOVERY_CONVERSATION.md)
3. Choose workflow: [workflows/COPY_AND_CUSTOMIZE.md](workflows/COPY_AND_CUSTOMIZE.md)
4. Follow customization guide: [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)

**Total time: 1-2 hours to production-ready agent**

### For Developers

**Want to build an agent yourself?**

1. Copy `starter-template/` to your project
2. Search for `{{PLACEHOLDERS}}` in files
3. Customize 3 files:
   - `system_prompt.py` - Define agent personality
   - `tools/{{domain}}_tools.py` - Implement your tools
   - `evals/scenarios.py` - Create test scenarios
4. Run tests: `uv run pytest`
5. Run evals: `uv run python examples/run_evaluation.py`

**See:** [QUICKSTART.md](QUICKSTART.md) for detailed instructions

---

## What's Included

### Documentation

| File | Purpose |
|------|---------|
| [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md) | Complete guide for AI assistants |
| [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md) | Structured requirements gathering |
| [DISCOVERY_CONVERSATION.md](DISCOVERY_CONVERSATION.md) | Interactive discovery script |
| [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) | Deep dive on customization |
| [QUICKSTART.md](QUICKSTART.md) | Get started in 15 minutes |
| [workflows/COPY_AND_CUSTOMIZE.md](workflows/COPY_AND_CUSTOMIZE.md) | Fast template-based workflow |
| [workflows/BUILD_FROM_SCRATCH.md](workflows/BUILD_FROM_SCRATCH.md) | Educational step-by-step |

### Starter Template

```
starter-template/
├── src/{{agent_name}}/
│   ├── agent.py              # ✅ Generic - Core agent with tool loop
│   ├── config.py             # ✅ Generic - Configuration
│   ├── models.py             # ✅ Generic - Data models
│   ├── cli.py                # ✅ Generic - Command-line interface
│   ├── system_prompt.py      # ⚠️  CUSTOMIZE - Agent personality
│   ├── providers/            # ✅ Generic - LLM provider abstraction
│   ├── tools/
│   │   ├── registry.py      # ✅ Generic - Tool framework
│   │   └── example_tools.py # ⚠️  CUSTOMIZE - Your domain tools
│   ├── context/             # ✅ Generic - Context management
│   ├── retry/               # ✅ Generic - Error handling
│   ├── observability/       # ✅ Generic - Tracing
│   └── persistence/         # ✅ Generic - Storage
├── evals/
│   ├── evaluator.py         # ✅ Generic - Evaluation engine
│   ├── reporters.py         # ✅ Generic - Report generation
│   └── scenarios.py         # ⚠️  CUSTOMIZE - Test cases
├── tests/                    # ✅ Generic - Test infrastructure
├── examples/                 # ⚠️  CUSTOMIZE - Usage examples
└── pyproject.toml            # ⚠️  CUSTOMIZE - Project metadata
```

**Legend:**
- ✅ Generic - Use as-is (90% of code)
- ⚠️  CUSTOMIZE - Adapt to your use case (10% of code)

### Reference Implementation

The `reference-implementation/` folder links to the **Detective Agent** as a complete working example showing how all pieces fit together.

---

## Features

### 🤖 Agentic Tool Execution

Agents autonomously call tools in multi-turn loops:
```python
# Agent automatically:
# 1. Calls tool to get data
# 2. Analyzes results
# 3. Calls tool to submit findings
# 4. Returns comprehensive response
```

### 📊 Complete Observability

OpenTelemetry tracing captures everything:
- API call timing and token counts
- Tool execution spans
- Context window management
- Retry attempts
- Saved as human-readable JSON

### 🔄 Robust Error Handling

Exponential backoff with jitter:
- Automatic retry on rate limits (429)
- Retry on server errors (500, 502, 503)
- Fail fast on auth/validation errors
- Configurable max attempts and delays

### 💾 Conversation Persistence

Conversations saved to filesystem:
- Resume conversations across sessions
- Full history preserved
- Linked to traces via trace_id

### 📏 Context Window Management

Automatic truncation:
- Keeps last N messages (configurable)
- Preserves system prompt
- Tracks truncation in traces

### ✅ Automated Evaluation

Built-in quality assurance:
- Tool usage validation
- Decision quality scoring
- Regression tracking
- Machine-readable reports

---

## Use Cases

Perfect for building agents that:

- **Assess and Analyze** - Risk assessment, content moderation, data analysis
- **Triage and Route** - Customer support, ticket routing, inquiry classification
- **Research and Summarize** - Document analysis, research assistance, information gathering
- **Monitor and Alert** - System monitoring, anomaly detection, alerting
- **Assist and Guide** - Onboarding, troubleshooting, step-by-step guidance

---

## Technology Stack

- **Python 3.11+** with async/await
- **Anthropic Claude** (default, extensible to other providers)
- **OpenTelemetry** for observability
- **pytest** for testing
- **uv** for package management

---

## Project Structure

This repository contains:

```
agent-template/
├── README.md                    # This file
├── FOR_AI_ASSISTANTS.md        # Comprehensive AI assistant guide
├── QUICKSTART.md               # Fast-track for developers
├── DISCOVERY_QUESTIONNAIRE.md  # Requirements gathering (checklist)
├── DISCOVERY_CONVERSATION.md   # Requirements gathering (interactive)
├── CUSTOMIZATION_GUIDE.md      # Deep dive on customization
├── starter-template/           # Working code template
├── workflows/                  # Implementation approaches
└── reference-implementation/   # Detective Agent example
```

---

## Examples

### Example 1: Release Risk Assessment (Detective Agent)

**Purpose:** Assess software release risk

**Tools:**
- `get_release_summary` - Fetch release data
- `file_risk_report` - Submit assessment

**Classification:** HIGH / MEDIUM / LOW risk

**See:** `reference-implementation/` for complete code

### Example 2: Customer Support Agent

**Purpose:** Triage support tickets

**Tools:**
- `get_ticket` - Fetch ticket details
- `search_knowledge_base` - Find solutions
- `update_ticket` - Change status
- `send_response` - Reply to customer

**Classification:** URGENT / HIGH / MEDIUM / LOW priority

**See:** [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md) - Customer Support Example

---

## Getting Started

### 1. Choose Your Path

**Option A: Use Template (Fast)**
- Copy `starter-template/`
- Customize 3 files
- Deploy in hours
- **See:** [workflows/COPY_AND_CUSTOMIZE.md](workflows/COPY_AND_CUSTOMIZE.md)

**Option B: Build from Scratch (Educational)**
- Learn architecture deeply
- Build incrementally over 8 phases
- Takes 1-2 days but you'll understand everything
- **See:** [workflows/BUILD_FROM_SCRATCH.md](workflows/BUILD_FROM_SCRATCH.md)

**Option C: AI Assistant Builds for You**
- Share your requirements
- AI follows the template
- Review and approve plan
- AI implements and tests
- **See:** [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md)

### 2. Read the Guides

**If you're an AI assistant:**
→ Start with [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md)

**If you're a developer:**
→ Start with [QUICKSTART.md](QUICKSTART.md)

**If you need to gather requirements:**
→ Use [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md) or [DISCOVERY_CONVERSATION.md](DISCOVERY_CONVERSATION.md)

---

## Quality Standards

All agents built from this template should have:

- ✅ Clear system prompt defining role and capabilities
- ✅ 2-5 well-defined tools with schemas
- ✅ Comprehensive evaluation scenarios
- ✅ 90%+ test coverage
- ✅ 70%+ evaluation pass rate
- ✅ Full observability (traces for all operations)
- ✅ Error handling and retry logic
- ✅ Documentation (README, API docs, examples)

---

## Philosophy

### 1. Don't Reinvent the Wheel

90% of agent infrastructure is identical across use cases. Reuse it.

### 2. Focus on Your Domain

Spend your time on what makes your agent unique:
- System prompt (personality and knowledge)
- Tools (capabilities)
- Evaluation (quality criteria)

### 3. Production-Ready from Day One

Include observability, error handling, and testing from the start. Not as afterthoughts.

### 4. Evaluation Drives Quality

You can't improve what you don't measure. Automated evaluation ensures agents work correctly.

### 5. Simplicity Over Cleverness

Clear, maintainable code beats clever abstractions. KISS principle throughout.

---

## Contributing

Improvements welcome! If you:
- Find bugs or issues
- Have suggestions for better patterns
- Want to add provider support (OpenAI, etc.)
- Have ideas for additional features

Please open an issue or PR.

---

## License

[Specify your license]

---

## Support

- **Documentation:** Start with [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md)
- **Examples:** See `reference-implementation/` (Detective Agent)
- **Issues:** Open a GitHub issue
- **Questions:** Check the guides first, then ask

---

## Acknowledgments

This template is based on practical experience building the **Detective Agent** through a structured, incremental approach. Special thanks to the Claude Code assistant for helping refine the architecture and documentation.

---

**Ready to build your agent? Start here:**
- **AI Assistants:** [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md)
- **Developers:** [QUICKSTART.md](QUICKSTART.md)
- **Planning:** [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md)

**Happy Building! 🤖**
