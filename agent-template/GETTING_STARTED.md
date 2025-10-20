# Getting Started with the AI Agent Template

**Welcome! This template will help you build production-quality AI agents quickly.**

---

## Choose Your Path

### 🤖 I'm an AI Assistant building an agent for a user
→ Start with [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md)
- Comprehensive guide for AI assistants
- Discovery process
- Implementation workflows
- Quality standards

### 👨‍💻 I'm a developer building my own agent
→ Start with [QUICKSTART.md](QUICKSTART.md)
- Fast-track guide
- Step-by-step instructions
- Get running in 15 minutes

### 📋 I need to gather requirements first
→ Use discovery tools:
- [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md) - Structured checklist
- [DISCOVERY_CONVERSATION.md](DISCOVERY_CONVERSATION.md) - Interactive script

---

## Quick Overview

### What is This?

A complete template system for building AI agents with:
- ✅ Tool calling (agentic behavior)
- ✅ Observability (OpenTelemetry)
- ✅ Error handling (retry logic)
- ✅ Context management
- ✅ Conversation persistence
- ✅ Automated evaluation
- ✅ 90%+ test coverage

### The 90/10 Rule

**90% of the code is generic** (included in template):
- Agent core, providers, observability
- Retry logic, context management
- Tool registry, persistence
- Evaluation framework

**10% is use-case-specific** (you customize):
- System prompt (personality and domain)
- Tools (2-5 capabilities)
- Evaluation scenarios (test cases)

### Time to Build

- **Copy and customize:** 1-2 hours
- **Build from scratch:** 1-2 days (educational)
- **AI assistant builds:** Variable (with guidance)

---

## Documentation Map

### Core Guides

| Document | For Whom | Purpose |
|----------|----------|---------|
| [README.md](README.md) | Everyone | Project overview |
| [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md) | AI Assistants | Complete implementation guide |
| [QUICKSTART.md](QUICKSTART.md) | Developers | Fast-track tutorial |
| [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) | Everyone | Deep dive on customization |

### Discovery Tools

| Document | Format | Time |
|----------|--------|------|
| [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md) | Structured checklist | 15-30 min |
| [DISCOVERY_CONVERSATION.md](DISCOVERY_CONVERSATION.md) | Interactive script | 20-30 min |

### Workflows

| Document | Approach | Time |
|----------|----------|------|
| [workflows/COPY_AND_CUSTOMIZE.md](workflows/COPY_AND_CUSTOMIZE.md) | Fast, template-based | 1-2 hours |
| [workflows/BUILD_FROM_SCRATCH.md](workflows/BUILD_FROM_SCRATCH.md) | Educational, step-by-step | 1-2 days |

### Reference

| Resource | What It Shows |
|----------|---------------|
| [reference-implementation/](reference-implementation/) | Complete working example (Detective Agent) |
| `starter-template/` | Template code with placeholders |

---

## Recommended Workflows

### Scenario 1: AI Assistant Building for User

1. ✅ Read [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md)
2. ✅ Run discovery ([DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md) or [DISCOVERY_CONVERSATION.md](DISCOVERY_CONVERSATION.md))
3. ✅ Follow [workflows/COPY_AND_CUSTOMIZE.md](workflows/COPY_AND_CUSTOMIZE.md)
4. ✅ Refer to [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) as needed
5. ✅ Check [reference-implementation/](reference-implementation/) for examples

### Scenario 2: Developer Building Own Agent (Fast)

1. ✅ Skim [README.md](README.md)
2. ✅ Follow [QUICKSTART.md](QUICKSTART.md)
3. ✅ Use [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) for details
4. ✅ Reference Detective Agent when stuck

### Scenario 3: Learning Agent Architecture

1. ✅ Read [reference-implementation/README.md](reference-implementation/README.md)
2. ✅ Study Detective Agent code
3. ✅ Follow [workflows/BUILD_FROM_SCRATCH.md](workflows/BUILD_FROM_SCRATCH.md)
4. ✅ Build incrementally, understanding each piece

### Scenario 4: Planning a Project

1. ✅ Use [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md)
2. ✅ Review [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)
3. ✅ Check [reference-implementation/](reference-implementation/) for patterns
4. ✅ Create implementation plan
5. ✅ Follow [workflows/COPY_AND_CUSTOMIZE.md](workflows/COPY_AND_CUSTOMIZE.md)

---

## What's Included

### Documentation (9 comprehensive guides)

```
agent-template/
├── README.md                           ← Start here (overview)
├── GETTING_STARTED.md                  ← You are here!
├── FOR_AI_ASSISTANTS.md               ← Comprehensive AI assistant guide
├── QUICKSTART.md                       ← Fast-track for developers
├── CUSTOMIZATION_GUIDE.md             ← Deep dive on customization
├── DISCOVERY_QUESTIONNAIRE.md         ← Requirements gathering (checklist)
├── DISCOVERY_CONVERSATION.md          ← Requirements gathering (interactive)
└── workflows/
    ├── COPY_AND_CUSTOMIZE.md          ← Fast workflow (1-2 hours)
    └── BUILD_FROM_SCRATCH.md          ← Educational workflow (1-2 days)
```

### Code Template

```
starter-template/                       ← Copy this to start
├── src/{{agent_name}}/                ← Your agent code
├── evals/                             ← Evaluation scenarios
├── tests/                             ← Test suite
├── examples/                          ← Usage examples
└── pyproject.toml                     ← Project configuration
```

### Reference Implementation

```
reference-implementation/
└── detective-agent/                   ← Complete working example
    ├── README.md                      ← Detective Agent docs
    └── [full implementation]          ← Study this!
```

---

## Key Concepts

### Agent = Infrastructure + Domain Logic

**Infrastructure (90%)** - Provided by template:
- Conversation management
- LLM provider abstraction
- Tool execution framework
- Observability and tracing
- Error handling and retry
- Context window management
- Persistence layer
- Evaluation system

**Domain Logic (10%)** - You customize:
- System prompt
- Tools (2-5)
- Evaluation scenarios

### Three Customization Points

1. **System Prompt** (`system_prompt.py`)
   - Agent personality
   - Domain knowledge
   - Decision criteria
   - Behavioral guidelines

2. **Tools** (`tools/{{domain}}_tools.py`)
   - What the agent can DO
   - Your domain-specific capabilities
   - 2-5 async functions with schemas

3. **Evaluation Scenarios** (`evals/scenarios.py`)
   - Test cases
   - Quality assurance
   - Regression prevention

---

## Common Use Cases

Perfect for agents that:

- **Assess and Analyze** - Risk assessment, content moderation, data analysis
- **Triage and Route** - Support tickets, inquiry classification, task routing
- **Research and Summarize** - Document analysis, information gathering
- **Monitor and Alert** - System monitoring, anomaly detection
- **Assist and Guide** - Onboarding, troubleshooting, step-by-step help

---

## Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- LLM API key (Anthropic recommended)
- Basic understanding of async Python
- Familiarity with AI agents and tools (helpful but not required)

---

## Quick Start (3 Steps)

### 1. Choose Your Approach

- **Fast:** Copy template, customize 3 files (1-2 hours)
- **Learn:** Build from scratch, understand architecture (1-2 days)
- **AI-assisted:** Let AI assistant build with guidance

### 2. Gather Requirements

Answer these 6 questions:
1. What is the agent's purpose?
2. What domain does it operate in?
3. What tools/capabilities does it need?
4. How does it classify/assess things?
5. What defines success?
6. What test scenarios should it pass?

Use [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md) to structure your answers.

### 3. Follow Your Workflow

- **Fast track:** [QUICKSTART.md](QUICKSTART.md) or [workflows/COPY_AND_CUSTOMIZE.md](workflows/COPY_AND_CUSTOMIZE.md)
- **Educational:** [workflows/BUILD_FROM_SCRATCH.md](workflows/BUILD_FROM_SCRATCH.md)
- **AI-assisted:** Share [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md) with your AI assistant

---

## Examples

### Example 1: Detective Agent (Reference Implementation)

**Purpose:** Assess software release risk
**Tools:** get_release_summary, file_risk_report
**Classification:** HIGH / MEDIUM / LOW
**Time to build:** 8 phases (already done!)

See [reference-implementation/](reference-implementation/)

### Example 2: Customer Support Bot

**Purpose:** Triage support tickets
**Tools:** get_ticket, search_knowledge_base, update_ticket, send_response
**Classification:** URGENT / HIGH / MEDIUM / LOW
**Time to build:** 1-2 hours using template

See [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md) - Customer Support Example

---

## What You'll Build

Following this template, you'll create an agent with:

✅ **Tool Calling** - Agent autonomously uses tools to accomplish tasks
✅ **Multi-Turn Loops** - Handles complex workflows requiring multiple steps
✅ **Observability** - Every operation traced with OpenTelemetry
✅ **Error Handling** - Automatic retry with exponential backoff
✅ **Context Management** - Smart truncation for long conversations
✅ **Persistence** - Conversations saved and resumable
✅ **Evaluation** - Automated quality testing
✅ **90%+ Test Coverage** - Production-ready quality
✅ **Documentation** - README, examples, API docs

---

## Support and Resources

### Documentation
- Start with [README.md](README.md)
- AI Assistants → [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md)
- Developers → [QUICKSTART.md](QUICKSTART.md)
- Customization → [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)

### Examples
- Complete agent → [reference-implementation/](reference-implementation/)
- Code patterns → [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)

### Help
- Check troubleshooting in guides
- Study Detective Agent implementation
- Review test suite for patterns

---

## What's Next?

### Choose Your Starting Point:

**🎯 I want to build FAST**
→ [QUICKSTART.md](QUICKSTART.md)

**🤖 I'm an AI assistant**
→ [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md)

**📚 I want to LEARN**
→ [reference-implementation/README.md](reference-implementation/README.md)

**📋 I need to PLAN**
→ [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md)

**🔧 I'm CUSTOMIZING**
→ [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)

---

## Philosophy

1. **Don't Reinvent the Wheel** - 90% is the same across agents
2. **Focus on Your Domain** - Spend time on what's unique
3. **Production-Ready from Day One** - Include quality from the start
4. **Evaluation Drives Quality** - Test behavior, not just code
5. **Keep It Simple** - Clear beats clever

---

**Ready to build your agent? Pick your path above and let's go!** 🚀
