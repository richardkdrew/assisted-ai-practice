# AI Agent Template System - Guide for AI Assistants

**Version:** 1.0
**Last Updated:** 2025-10-18
**Purpose:** Comprehensive guide for AI assistants to build production-quality agentic systems

---

## Table of Contents

1. [Overview](#overview)
2. [When to Use This Template](#when-to-use-this-template)
3. [Template Architecture](#template-architecture)
4. [Quick Decision Tree](#quick-decision-tree)
5. [Discovery Phase](#discovery-phase)
6. [Implementation Approaches](#implementation-approaches)
7. [Generic vs Use-Case-Specific](#generic-vs-use-case-specific)
8. [Step-by-Step Workflow](#step-by-step-workflow)
9. [Common Patterns](#common-patterns)
10. [Quality Checklist](#quality-checklist)
11. [Troubleshooting](#troubleshooting)

---

## Overview

### What is This?

This is a **production-ready template system** for building AI agents with:
- ✅ Tool calling capabilities (agentic behavior)
- ✅ Complete observability (OpenTelemetry)
- ✅ Robust error handling (retry with exponential backoff)
- ✅ Context window management
- ✅ Conversation persistence
- ✅ Automated evaluation framework
- ✅ 90%+ test coverage

### Key Insight

**90% of any AI agent is generic infrastructure**. Only ~10% is use-case-specific:
- System prompt (agent personality and domain)
- Tools (domain-specific capabilities)
- Evaluation scenarios (test cases)
- Mock data (for testing)

This template provides the 90% so you can focus on the 10%.

### Based On

This template is extracted from the **Detective Agent** (a release risk assessment system) built through 8 complete implementation phases with:
- 1,340 lines of production code
- 91 passing tests with 91% coverage
- Full documentation and examples
- Proven architecture patterns

---

## When to Use This Template

### ✅ Perfect For:

1. **AI agents that need tools** - Agents that call functions/APIs to accomplish tasks
2. **Production deployments** - Need observability, error handling, evaluation
3. **Domain-specific tasks** - Where you customize behavior through system prompts and tools
4. **Multi-turn conversations** - Agents that maintain context across interactions
5. **Quality-critical applications** - Where testing and evaluation matter

### ❌ Not Ideal For:

1. **Simple chatbots** - If you just need basic Q&A without tools
2. **Single-shot completions** - No conversation state needed
3. **Prototype/throwaway code** - This is production-grade infrastructure
4. **Non-Python projects** - Template is Python-specific (but architecture applies elsewhere)

---

## Template Architecture

### Core Components (All Generic - DO NOT Modify)

```
src/{{agent_name}}/
├── agent.py              # Core agent with tool loop
├── config.py             # Configuration management
├── models.py             # Data models (Message, Conversation, etc.)
├── cli.py                # Command-line interface
├── providers/
│   ├── base.py          # Provider abstraction
│   └── anthropic.py     # Anthropic/Claude implementation
├── tools/
│   └── registry.py      # Tool registration and execution
├── context/
│   └── manager.py       # Context window management
├── retry/
│   └── strategy.py      # Retry with exponential backoff
├── observability/
│   ├── tracer.py        # OpenTelemetry tracing
│   └── exporter.py      # File-based trace export
└── persistence/
    └── store.py         # Conversation storage
```

### Customization Points (Use-Case-Specific - MUST Customize)

```
src/{{agent_name}}/
├── system_prompt.py     # ⚠️ CUSTOMIZE: Agent personality and instructions
└── tools/
    └── {{domain}}_tools.py  # ⚠️ CUSTOMIZE: Your domain-specific tools

evals/
└── scenarios.py         # ⚠️ CUSTOMIZE: Your test scenarios
```

---

## Quick Decision Tree

```
START: User asks you to build an AI agent

│
├─ Does it need tools/capabilities?
│  ├─ NO → Use simpler chatbot template
│  └─ YES → Continue ↓
│
├─ Do they want production-quality?
│  ├─ NO → Consider simpler approach
│  └─ YES → Use this template ↓
│
├─ Which workflow should you use?
│  ├─ User wants to learn → BUILD FROM SCRATCH workflow
│  ├─ User wants speed → COPY AND CUSTOMIZE workflow
│  └─ Unsure → Ask: "Do you want to learn the architecture or build quickly?"
│
└─ Start Discovery Phase →
```

---

## Discovery Phase

### CRITICAL: Always Start Here

Before writing ANY code, you MUST understand the use case. Use one of these approaches:

#### Option A: Structured Checklist
Direct user to fill out: [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md)

**When to use:** User has time, wants to think through requirements, prefers structured format.

#### Option B: Conversational Discovery
Follow the script in: [DISCOVERY_CONVERSATION.md](DISCOVERY_CONVERSATION.md)

**When to use:** Interactive session, user wants guidance, exploring ideas together.

### Required Information

You MUST gather these before proceeding:

1. **Agent Purpose** - What is the agent's primary role?
2. **Domain** - What domain does it operate in?
3. **Tools Needed** - What capabilities/actions must it perform?
4. **Classification System** - How does it categorize/assess things? (HIGH/MEDIUM/LOW, etc.)
5. **Success Criteria** - How do you know it's working correctly?
6. **Evaluation Scenarios** - What test cases should it pass?

### Example: Detective Agent

```markdown
Purpose: Assess software release risk
Domain: DevOps / Release Management
Tools:
  - get_release_summary (fetch release data)
  - file_risk_report (submit assessment)
Classification: HIGH / MEDIUM / LOW severity
Success: Correctly identifies high-risk releases based on test failures and metrics
Scenarios: High risk (many failures), Medium risk (some failures), Low risk (all passing)
```

---

## Implementation Approaches

### Approach 1: Copy and Customize (Recommended for Speed)

**Time: 1-2 hours**
**Best for:** Production deployment, time-sensitive projects

1. Copy `starter-template/` to new project
2. Search for all `{{PLACEHOLDERS}}`
3. Customize 3 files (system prompt, tools, scenarios)
4. Run tests
5. Deploy

**See:** [workflows/COPY_AND_CUSTOMIZE.md](workflows/COPY_AND_CUSTOMIZE.md)

### Approach 2: Build from Scratch (Recommended for Learning)

**Time: 1-2 days**
**Best for:** Educational purposes, understanding architecture

1. Phase 0: Project setup
2. Phase 1: Basic conversation
3. Phase 2: Add observability
4. Phase 3: Context management
5. Phase 4: Retry mechanism
6. Phase 5: System prompt
7. Phase 6: Tool abstraction
8. Phase 7: Evaluation
9. Phase 8: Documentation

**See:** [workflows/BUILD_FROM_SCRATCH.md](workflows/BUILD_FROM_SCRATCH.md)

### Hybrid Approach

Start with copy-and-customize, but explain each component as you go. Best of both worlds.

---

## Generic vs Use-Case-Specific

### The 90/10 Rule

| Component | % of Code | Generic | Use-Case |
|-----------|-----------|---------|----------|
| Core Infrastructure | ~90% | ✅ Reuse as-is | |
| Domain Logic | ~10% | | ⚠️ Must customize |

### Generic Infrastructure (DO NOT MODIFY)

**Purpose:** Foundational capabilities that ALL agents need

| Component | What It Does | Why It's Generic |
|-----------|--------------|------------------|
| `agent.py` | Conversation loop, tool execution | Same for all agents |
| `providers/*` | LLM API abstraction | Provider-agnostic |
| `models.py` | Data structures | Universal models |
| `observability/*` | Tracing and monitoring | Same instrumentation needs |
| `retry/*` | Error handling | Same retry logic |
| `context/*` | Token management | Same windowing strategy |
| `persistence/*` | Save/load conversations | Same storage needs |
| `tools/registry.py` | Tool framework | Same execution pattern |
| `evals/evaluator.py` | Evaluation engine | Same scoring approach |

**If you modify these:** You're diverging from the proven architecture. Only do this if you have a very specific reason and understand the tradeoffs.

### Use-Case-Specific (MUST CUSTOMIZE)

**Purpose:** Define what makes your agent unique

| File | What to Customize | Example (Detective Agent) |
|------|-------------------|---------------------------|
| `system_prompt.py` | Agent role, domain knowledge, guidelines | "You are a Detective Agent for release risk..." |
| `{{domain}}_tools.py` | Tool implementations | `get_release_summary()`, `file_risk_report()` |
| `evals/scenarios.py` | Test cases | High/medium/low risk releases |
| Mock data | Sample data for testing | Mock release data (tests, metrics) |

---

## Step-by-Step Workflow

### Phase 1: Discovery & Planning

1. ✅ **Run Discovery** - Use questionnaire or conversation
2. ✅ **Validate Requirements** - Ensure you have all 6 required pieces
3. ✅ **Create Plan** - Document what you'll build
4. ✅ **Get User Approval** - Confirm plan before coding

### Phase 2: Setup

1. ✅ **Choose Workflow** - Build from scratch or copy template?
2. ✅ **Create Project** - Set up folder structure
3. ✅ **Install Dependencies** - `uv sync`
4. ✅ **Verify Environment** - Run tests (should see generic tests pass)

### Phase 3: Customization

1. ✅ **System Prompt** - Define agent personality
   ```python
   DEFAULT_SYSTEM_PROMPT = """You are {{AGENT_NAME}}, designed to {{PURPOSE}}.

   Your responsibilities:
   - {{RESPONSIBILITY_1}}
   - {{RESPONSIBILITY_2}}

   Guidelines:
   - {{GUIDELINE_1}}
   - {{GUIDELINE_2}}
   """
   ```

2. ✅ **Tools** - Implement domain capabilities
   ```python
   async def {{tool_name}}({{params}}) -> dict:
       """{{TOOL_DESCRIPTION}}"""
       # Implementation
       return result

   # Tool schema
   {{TOOL_NAME}}_SCHEMA = {
       "type": "object",
       "properties": { {{PARAMETERS}} },
       "required": [{{REQUIRED_PARAMS}}]
   }
   ```

3. ✅ **Evaluation Scenarios** - Define test cases
   ```python
   HIGH_SEVERITY_SCENARIO = Scenario(
       id="{{scenario_id}}",
       description="{{what_you're_testing}}",
       input_data={{test_input}},
       expected_behavior={{what_should_happen}},
   )
   ```

### Phase 4: Testing

1. ✅ **Unit Tests** - Test tool functions
2. ✅ **Integration Tests** - Test full workflows
3. ✅ **Evaluation Suite** - Run automated scenarios
4. ✅ **Manual Testing** - Try realistic conversations

### Phase 5: Validation

1. ✅ **Run Full Test Suite** - `pytest tests/`
2. ✅ **Check Coverage** - Should be 90%+
3. ✅ **Run Evals** - All scenarios should pass
4. ✅ **Manual Validation** - Test with real use cases

### Phase 6: Documentation

1. ✅ **Update README** - Project-specific info
2. ✅ **Document Tools** - What each tool does
3. ✅ **Usage Examples** - Show how to use
4. ✅ **Configuration Guide** - Environment variables

---

## Common Patterns

### Pattern 1: Simple GET Tool

**Use Case:** Fetch data from an API or database

```python
async def get_{{entity}}({{entity}}_id: str) -> dict:
    """Retrieve {{entity}} information."""
    # Option A: Real API call
    response = await http_client.get(f"/api/{{entities}}/{{{entity}}_id}")
    return response.json()

    # Option B: Mock data (for testing)
    return MOCK_{{ENTITIES}}[{{entity}}_id]

# Schema
GET_{{ENTITY}}_SCHEMA = {
    "type": "object",
    "properties": {
        "{{entity}}_id": {
            "type": "string",
            "description": "Unique identifier for the {{entity}}"
        }
    },
    "required": ["{{entity}}_id"]
}
```

### Pattern 2: POST/Action Tool

**Use Case:** Submit data, trigger actions

```python
async def {{action}}_{{entity}}(
    {{entity}}_id: str,
    {{field1}}: str,
    {{field2}}: list[str]
) -> dict:
    """{{ACTION_DESCRIPTION}}."""
    # Validate inputs
    if {{field1}} not in VALID_VALUES:
        raise ValueError(f"Invalid {{field1}}: {{{field1}}}")

    # Create payload
    payload = {
        "{{entity}}_id": {{entity}}_id,
        "{{field1}}": {{field1}},
        "{{field2}}": {{field2}},
        "timestamp": datetime.now().isoformat()
    }

    # Save/send
    # Option A: Real API
    response = await http_client.post("/api/{{entities}}", json=payload)

    # Option B: Save to file (for testing)
    save_to_file(payload)

    return {"status": "success", "{{entity}}_id": {{entity}}_id}
```

### Pattern 3: System Prompt Structure

```python
DEFAULT_SYSTEM_PROMPT = """You are {{AGENT_NAME}}, {{ROLE_DESCRIPTION}}.

Your purpose is to {{PRIMARY_PURPOSE}}.

You have access to the following tools:
1. {{TOOL1_NAME}} - {{TOOL1_DESCRIPTION}}
2. {{TOOL2_NAME}} - {{TOOL2_DESCRIPTION}}

When {{SCENARIO_1}}:
- {{ACTION_1}}
- {{ACTION_2}}

Guidelines for {{CLASSIFICATION_SYSTEM}}:
- {{LEVEL_1}}: {{CRITERIA_1}}
- {{LEVEL_2}}: {{CRITERIA_2}}
- {{LEVEL_3}}: {{CRITERIA_3}}

Always:
- {{GENERAL_GUIDELINE_1}}
- {{GENERAL_GUIDELINE_2}}
- Base decisions on data provided
- Acknowledge uncertainty when information is incomplete

You are {{PERSONALITY_TRAIT}}.
"""
```

### Pattern 4: Evaluation Scenario

```python
{{SCENARIO_NAME}} = Scenario(
    id="{{scenario_id}}",
    description="{{what_this_tests}}",
    {{input_data_field}}: {
        "{{field1}}": {{value1}},
        "{{field2}}": {{value2}},
        # Data that represents this test case
    },
    expected_{{classification}}: "{{expected_result}}",
    expected_tools: ["{{tool1}}", "{{tool2}}"],
    expected_findings_keywords: ["{{keyword1}}", "{{keyword2}}"],
    metadata: {"{{meta_key}}": {{meta_value}}}
)
```

---

## Quality Checklist

Before considering the agent "done", verify:

### Code Quality
- [ ] All generic infrastructure unchanged (or changes documented)
- [ ] System prompt clearly defines agent role and capabilities
- [ ] All tools have clear docstrings and type hints
- [ ] Tool schemas match function signatures
- [ ] Error handling for tool failures
- [ ] Configuration via environment variables

### Testing
- [ ] Unit tests for all custom tools
- [ ] Integration test for full workflow
- [ ] Evaluation scenarios cover success and failure cases
- [ ] Test coverage >90%
- [ ] All tests passing
- [ ] Evaluation pass rate >70%

### Observability
- [ ] Traces generated for all conversations
- [ ] Tool executions visible in traces
- [ ] Token counts tracked
- [ ] Retry attempts logged
- [ ] Context truncation tracked

### Documentation
- [ ] README explains what the agent does
- [ ] Environment variables documented
- [ ] Tool usage examples provided
- [ ] Evaluation results documented
- [ ] Architecture explained (or reference this template)

### Production Readiness
- [ ] API keys managed securely (env vars, not hardcoded)
- [ ] Error messages user-friendly
- [ ] Graceful degradation on tool failures
- [ ] Retry mechanism configured appropriately
- [ ] Conversation persistence working
- [ ] CLI tested end-to-end

---

## Troubleshooting

### Problem: Tests Failing After Customization

**Symptom:** Generic tests fail after adding custom tools

**Likely Cause:** Modified generic infrastructure

**Solution:**
1. Check git diff - what changed?
2. Revert changes to generic files
3. Put customizations in the right place (system_prompt.py, {{domain}}_tools.py)

### Problem: Agent Not Using Tools

**Symptom:** Agent responds but doesn't call tools

**Possible Causes:**
1. Tools not registered in CLI/main
2. System prompt doesn't mention tools
3. Tool schemas invalid
4. Agent doesn't understand when to use tools

**Solution:**
1. Check tool registration in agent initialization
2. Add tool descriptions to system prompt
3. Validate schemas match Anthropic format
4. Make system prompt more directive about tool usage

### Problem: Evaluation Scenarios Failing

**Symptom:** Agent makes wrong decisions in evals

**Possible Causes:**
1. System prompt unclear about criteria
2. Expected behavior unrealistic
3. Agent needs more context
4. Evaluation scoring too strict

**Solution:**
1. Refine system prompt guidelines
2. Adjust expected_behavior to match reality
3. Add more detail to scenario input data
4. Lower pass threshold if criteria too stringent

### Problem: Context Window Issues

**Symptom:** Errors about token limits

**Solution:**
1. Check MAX_MESSAGES configuration
2. Increase context window size if needed
3. Verify truncation is working (check traces)
4. Consider summarization for very long conversations

### Problem: Retry Not Working

**Symptom:** Fails immediately on transient errors

**Solution:**
1. Check error type - is it retryable?
2. Verify retry config (max_attempts, delays)
3. Check traces - are retries being attempted?
4. Add error type to retryable list if needed

---

## Advanced Customization

### Adding New LLM Providers

If you need OpenAI, OpenRouter, etc.:

1. Create `src/{{agent_name}}/providers/{{provider}}.py`
2. Implement `Provider` interface from `base.py`
3. Handle provider-specific tool formatting
4. Add provider-specific dependencies to `pyproject.toml`
5. Update config to support provider selection

**Reference:** See `providers/anthropic.py` as example

### Custom Context Strategies

If truncation isn't enough:

1. Extend `ContextManager` in `context/manager.py`
2. Implement summarization strategy
3. Use embedding-based importance scoring
4. Preserve key messages (system prompt, tool results)

**Note:** This is advanced - only do if truncation insufficient

### Custom Evaluation Metrics

If tool usage + decision quality isn't enough:

1. Extend `Evaluator` in `evals/evaluator.py`
2. Add new scoring dimension
3. Create evaluation function
4. Update pass threshold calculation
5. Add to reports

**Examples:** Response time, token efficiency, conversation quality

---

## Best Practices

### 1. Start Simple, Iterate

- Begin with 2-3 basic tools
- Add complexity only when needed
- Validate each addition with tests

### 2. System Prompt is Critical

- Spend time crafting clear instructions
- Include examples in the prompt
- Test different phrasings
- Reference tool capabilities explicitly

### 3. Mock Data for Development

- Use mock data during development
- Switch to real APIs for production
- Keep mocks realistic (based on real data)
- Use mocks in evaluation scenarios

### 4. Evaluation Drives Quality

- Write scenarios BEFORE implementing
- Cover happy path AND edge cases
- Include error scenarios
- Regression test after changes

### 5. Observability is Non-Negotiable

- Always check traces when debugging
- Monitor token usage for cost control
- Track tool execution patterns
- Use traces to understand agent decisions

---

## Example: Building a Customer Support Agent

Let's walk through how you'd use this template:

### 1. Discovery

**User says:** "I want to build an agent that helps with customer support tickets."

**You gather:**
- Purpose: Triage and respond to customer support tickets
- Domain: Customer support / Help desk
- Tools needed:
  - `get_ticket` - Fetch ticket details
  - `search_knowledge_base` - Find relevant articles
  - `update_ticket` - Add notes, change status
  - `send_response` - Reply to customer
- Classification: URGENT / HIGH / MEDIUM / LOW priority
- Success: Correctly prioritizes tickets, provides relevant solutions
- Scenarios: Urgent (system down), High (can't login), Medium (how-to question), Low (feature request)

### 2. Choose Workflow

Fast deployment needed → **Copy and Customize**

### 3. Customize System Prompt

```python
DEFAULT_SYSTEM_PROMPT = """You are SupportBot, a customer support triage and response agent.

Your purpose is to efficiently handle customer support tickets by:
1. Understanding the customer's issue
2. Searching for relevant solutions
3. Providing helpful responses
4. Escalating when necessary

You have access to:
- get_ticket: Retrieve ticket details
- search_knowledge_base: Find help articles
- update_ticket: Update ticket status and add notes
- send_response: Reply to the customer

Priority Guidelines:
- URGENT: System outages, data loss, security issues → Escalate immediately
- HIGH: Cannot access account, payment failures → Respond within 1 hour
- MEDIUM: Feature questions, minor bugs → Respond within 4 hours
- LOW: Feature requests, general questions → Respond within 24 hours

Always:
- Be empathetic and professional
- Search knowledge base before responding
- Provide step-by-step instructions
- Escalate if issue is complex or unclear
- Update ticket status appropriately
"""
```

### 4. Implement Tools

```python
async def get_ticket(ticket_id: str) -> dict:
    """Retrieve ticket information."""
    return MOCK_TICKETS[ticket_id]  # or real API call

async def search_knowledge_base(query: str) -> list[dict]:
    """Search help articles."""
    # Implementation
    pass

async def update_ticket(
    ticket_id: str,
    status: str,
    notes: str
) -> dict:
    """Update ticket status and add internal notes."""
    # Implementation
    pass

async def send_response(
    ticket_id: str,
    message: str
) -> dict:
    """Send response to customer."""
    # Implementation
    pass
```

### 5. Create Evaluation Scenarios

```python
URGENT_SCENARIO = Scenario(
    id="urgent_system_outage",
    description="System outage ticket requiring immediate escalation",
    ticket_data={
        "ticket_id": "T-12345",
        "subject": "Cannot access application - Error 500",
        "description": "All users getting 500 errors since 10am",
        "customer": "BigCorp Inc",
        "created_at": "2024-10-18T10:05:00Z"
    },
    expected_priority="urgent",
    expected_tools=["get_ticket", "update_ticket"],
    expected_findings_keywords=["escalate", "urgent", "outage"],
)
```

### 6. Test and Deploy

```bash
uv run pytest  # All tests pass
uv run python examples/run_evaluation.py  # 90% pass rate
uv run python -m support_agent.cli new  # Manual testing
```

**Total time: ~2 hours from start to working agent**

---

## Summary: Your Role as AI Assistant

When a user asks you to build an agent:

1. ✅ **Recognize the opportunity** - "This matches the agent template!"
2. ✅ **Run discovery** - Gather the 6 required pieces
3. ✅ **Choose workflow** - Build from scratch or copy-customize
4. ✅ **Guide customization** - Help with system prompt, tools, scenarios
5. ✅ **Ensure quality** - Run tests, validate evaluation, check observability
6. ✅ **Document** - Explain what you built and how to use it

**Remember:** You're building production-quality software. Take time to do it right. The template gives you 90% for free - focus on making the 10% (system prompt, tools, scenarios) excellent.

---

## Additional Resources

- [DISCOVERY_QUESTIONNAIRE.md](DISCOVERY_QUESTIONNAIRE.md) - Structured requirements gathering
- [DISCOVERY_CONVERSATION.md](DISCOVERY_CONVERSATION.md) - Interactive discovery script
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Detailed implementation steps
- [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) - Deep dive on customization points
- [workflows/BUILD_FROM_SCRATCH.md](workflows/BUILD_FROM_SCRATCH.md) - Educational approach
- [workflows/COPY_AND_CUSTOMIZE.md](workflows/COPY_AND_CUSTOMIZE.md) - Fast approach
- [reference-implementation/](reference-implementation/) - Detective Agent example

---

**Good luck building amazing agents! 🤖**
