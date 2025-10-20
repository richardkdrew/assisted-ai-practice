# Reference Implementation: Detective Agent

This directory contains a symbolic link to the **Detective Agent** - a complete, production-ready AI agent that demonstrates how all components of the template work together.

## About Detective Agent

**Purpose:** Assess software release risk by analyzing test results, deployment metrics, and code changes.

**Domain:** DevOps / Release Management

**Tools:**
- `get_release_summary` - Fetch release metadata
- `file_risk_report` - Submit risk assessment

**Classification:** HIGH / MEDIUM / LOW severity

**Stats:**
- 1,340 lines of production code
- 91 tests with 91% coverage
- 8 implementation phases completed
- Fully documented and working

## How to Use This Reference

### 1. See the Complete Architecture

Navigate to the Detective Agent:
```bash
cd detective-agent
```

Explore the structure:
```bash
tree -L 3 -I '__pycache__|*.pyc|.venv'
```

### 2. Study the Customization Points

**System Prompt:**
```bash
cat detective-agent/src/detective_agent/system_prompt.py
```

**Tools:**
```bash
cat detective-agent/src/detective_agent/tools/release_tools.py
```

**Evaluation Scenarios:**
```bash
cat detective-agent/evals/scenarios.py
```

### 3. See Generic Infrastructure

**Agent Core:**
```bash
cat detective-agent/src/detective_agent/agent.py
```

**Provider Abstraction:**
```bash
cat detective-agent/src/detective_agent/providers/base.py
cat detective-agent/src/detective_agent/providers/anthropic.py
```

**Tool Registry:**
```bash
cat detective-agent/src/detective_agent/tools/registry.py
```

**Observability:**
```bash
cat detective-agent/src/detective_agent/observability/tracer.py
```

### 4. Run the Detective Agent

```bash
cd detective-agent
source .venv/bin/activate
export ANTHROPIC_API_KEY="your-key"

# Start a conversation
uv run python -m detective_agent.cli new

# Try: "Please assess release rel-003"
```

### 5. Compare to Your Agent

Use Detective Agent as a reference when building your own:

**When customizing system prompt:**
→ See how Detective Agent defines severity levels

**When implementing tools:**
→ See how `get_release_summary` and `file_risk_report` are structured

**When creating scenarios:**
→ See how Detective Agent covers HIGH/MEDIUM/LOW risk cases

## Key Files to Study

| File | What to Learn |
|------|---------------|
| `src/detective_agent/system_prompt.py` | How to write effective system prompts |
| `src/detective_agent/tools/release_tools.py` | Tool implementation patterns |
| `evals/scenarios.py` | Comprehensive evaluation scenarios |
| `src/detective_agent/agent.py` | How tool loop works |
| `tests/tool_integration_test.py` | How to test tool workflows |
| `docs/DESIGN.md` | Architecture decisions |
| `docs/PROGRESS.md` | Implementation journey |
| `README.md` | Complete documentation |

## Documentation

The Detective Agent has extensive documentation:

- `docs/DESIGN.md` - Architecture and design decisions
- `docs/PLAN.md` - Detailed implementation plan
- `docs/PROGRESS.md` - Development history
- `docs/STEPS.md` - Implementation guide
- `docs/API.md` - API reference
- `docs/MANUAL_TEST_PLAN.md` - Manual testing guide
- `README.md` - Complete project overview

## Run Tests

```bash
cd detective-agent

# All tests
uv run pytest

# With coverage
uv run pytest --cov=src/detective_agent --cov-report=term-missing

# Specific test
uv run pytest tests/tool_integration_test.py -v
```

## Run Evaluation

```bash
cd detective-agent
uv run python examples/run_evaluation.py
```

Expected: 90-100% pass rate

## Inspect Traces

```bash
cd detective-agent

# Run a conversation to generate traces
uv run python -m detective_agent.cli new
# (have a conversation, then exit)

# View traces
ls data/traces/
cat data/traces/<trace-id>.json | python -m json.tool
```

## Side-by-Side Comparison

| Aspect | Detective Agent | Your Agent |
|--------|-----------------|------------|
| **Purpose** | Release risk assessment | {{Your purpose}} |
| **Domain** | DevOps | {{Your domain}} |
| **Tools** | get_release_summary, file_risk_report | {{Your tools}} |
| **Classification** | HIGH/MEDIUM/LOW severity | {{Your classification}} |
| **Scenarios** | 5 scenarios (risk levels + edge cases) | {{Your scenarios}} |
| **System Prompt** | Detective agent, cautious approach | {{Your personality}} |

## Questions to Ask While Studying

1. **System Prompt:** How does Detective Agent describe its purpose and guidelines?
2. **Tools:** How are mock data and real API calls structured?
3. **Tool Schemas:** How do schemas match function signatures?
4. **Scenarios:** What makes a good evaluation scenario?
5. **Error Handling:** How are edge cases handled?
6. **Observability:** What information is captured in traces?
7. **Testing:** How are tools and workflows tested?

## Applying What You Learn

**Pattern:** See how Detective Agent does X, then adapt to your use case

**Examples:**

**Detective Agent defines severity:**
```python
- HIGH: >5% error rate, critical test failures
- MEDIUM: 2-5% error rate, minor failures
- LOW: <2% error rate, all tests passing
```

**Your agent defines priority:**
```python
- URGENT: System outages, data loss
- HIGH: Cannot login, payment issues
- MEDIUM: Feature questions
- LOW: General inquiries
```

**Detective Agent tool:**
```python
async def get_release_summary(release_id: str) -> dict:
    """Retrieve release information."""
    if release_id in MOCK_RELEASES:
        return MOCK_RELEASES[release_id]
    raise ValueError(f"Release {release_id} not found")
```

**Your agent tool:**
```python
async def get_ticket(ticket_id: str) -> dict:
    """Retrieve ticket information."""
    if ticket_id in MOCK_TICKETS:
        return MOCK_TICKETS[ticket_id]
    raise ValueError(f"Ticket {ticket_id} not found")
```

Same pattern, different domain!

## Summary

The Detective Agent is your **living example** of:
- ✅ How to structure an agent project
- ✅ How to write effective system prompts
- ✅ How to implement tools properly
- ✅ How to create comprehensive evaluations
- ✅ How to achieve 90%+ test coverage
- ✅ How to document thoroughly

**Use it as a guide when building your own agent!**

---

## Need Help?

- **Understand a component?** Read the Detective Agent's implementation
- **Stuck on customization?** See how Detective Agent did it
- **Want examples?** Detective Agent has them all
- **Need test patterns?** Study Detective Agent's test suite

**The Detective Agent is your reference manual.** 📚
