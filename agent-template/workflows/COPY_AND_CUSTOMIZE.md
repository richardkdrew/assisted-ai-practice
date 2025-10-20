# Copy and Customize Workflow

**Build a production-ready AI agent in 1-2 hours**

This workflow is for when you want to move quickly using the proven template. You'll copy the starter code and customize only the 10% that's use-case-specific.

---

## Overview

**Time:** 1-2 hours
**Approach:** Copy → Find placeholders → Customize → Test → Deploy
**Best for:** Production deployments, time-sensitive projects, when you trust the architecture

---

## Prerequisites

✅ Completed [DISCOVERY_QUESTIONNAIRE.md](../DISCOVERY_QUESTIONNAIRE.md) or [DISCOVERY_CONVERSATION.md](../DISCOVERY_CONVERSATION.md)
✅ Have your agent specification ready:
  - Agent name and purpose
  - 2-5 tools defined
  - Classification system
  - 3-5 test scenarios
✅ Python 3.11+, uv package manager
✅ LLM API key (Anthropic recommended)

---

## Step-by-Step Workflow

### Phase 1: Setup (10 minutes)

#### 1.1 Copy the Template

```bash
# Navigate to where you want your project
cd ~/projects

# Copy the starter template
cp -r /path/to/agent-template/starter-template ./my-agent

# Rename the directory
mv my-agent {{your-agent-name}}

cd {{your-agent-name}}
```

#### 1.2 Rename Package Directory

```bash
# Rename the package from {{agent_name}} to your actual name
mv src/{{agent_name}} src/{{actual_agent_name}}

# Example:
# mv src/{{agent_name}} src/support_bot
```

#### 1.3 Initialize Environment

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate  # Windows

# Install dependencies
uv sync

# Verify
uv run pytest --version
```

#### 1.4 Configure API Key

```bash
# Set API key
export ANTHROPIC_API_KEY="your-api-key"

# Or create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=your-api-key-here
EOF
```

---

### Phase 2: Find All Placeholders (5 minutes)

#### 2.1 Search for Placeholders

```bash
# Find all files with placeholders
grep -r "{{" src/ evals/ *.toml *.md 2>/dev/null

# You should see placeholders in:
# - pyproject.toml
# - src/{{agent_name}}/system_prompt.py
# - src/{{agent_name}}/tools/example_tools.py
# - evals/scenarios.py
# - README.md (template)
# - examples/*.py
```

#### 2.2 Create Replacement Plan

Make a list:

```
Placeholder                    → Replacement
-------------------------------------------------
{{agent_name}}                → support_bot
{{AGENT_NAME}}                → SupportBot
{{domain}}                    → support
{{PRIMARY_PURPOSE}}           → triage support tickets
{{CLASSIFICATION_SYSTEM}}     → Priority levels
{{LEVEL_1}}                   → URGENT
{{LEVEL_2}}                   → HIGH
{{LEVEL_3}}                   → MEDIUM
{{LEVEL_4}}                   → LOW
```

---

### Phase 3: Customize Core Files (30-45 minutes)

#### 3.1 System Prompt (15 minutes)

**File:** `src/{{agent_name}}/system_prompt.py`

```python
DEFAULT_SYSTEM_PROMPT = """You are {{AGENT_NAME}}, {{ROLE_DESCRIPTION}}.

Your purpose is to {{PRIMARY_PURPOSE}}.

You have access to the following tools:
1. {{TOOL1_NAME}} - {{TOOL1_DESCRIPTION}}
2. {{TOOL2_NAME}} - {{TOOL2_DESCRIPTION}}

{{CLASSIFICATION_SYSTEM}}:
- {{LEVEL_1}}: {{CRITERIA_1}}
- {{LEVEL_2}}: {{CRITERIA_2}}
- {{LEVEL_3}}: {{CRITERIA_3}}

Always explain your reasoning and base decisions on provided data.
"""
```

**Replace with your specification:**

1. Copy your agent purpose from discovery
2. List all your tools
3. Define your classification system with criteria
4. Add behavioral guidelines
5. Set personality/tone

**Example result:**

```python
DEFAULT_SYSTEM_PROMPT = """You are SupportBot, a customer support triage agent.

Your purpose is to efficiently handle customer support tickets.

You have access to the following tools:
1. get_ticket - Retrieve ticket details
2. search_knowledge_base - Find help articles
3. update_ticket - Change ticket status
4. send_response - Reply to customer

Priority Levels:
- URGENT: System outages, data loss → Escalate immediately
- HIGH: Cannot login, payment issues → Respond within 1 hour
- MEDIUM: Feature questions → Respond within 4 hours
- LOW: General inquiries → Respond within 24 hours

Always explain your reasoning and base decisions on provided data.
"""
```

#### 3.2 Implement Tools (20-30 minutes)

**File:** `src/{{agent_name}}/tools/{{domain}}_tools.py`

For EACH tool from your discovery:

1. **Create mock data:**
```python
MOCK_{{ENTITY}}_DATA = {
    "{{id1}}": { /* realistic data */ },
    "{{id2}}": { /* realistic data */ },
}
```

2. **Implement function:**
```python
async def {{tool_name}}({{params}}) -> dict:
    """{{Description}}."""
    # Validate
    # Use mock data or call API
    # Return result
    return data
```

3. **Define schema:**
```python
{{TOOL_NAME}}_SCHEMA = {
    "type": "object",
    "properties": { /* match params */ },
    "required": [ /* required params */ ]
}
```

**Example:**

```python
# Mock data
MOCK_TICKETS = {
    "T-001": {
        "id": "T-001",
        "subject": "Cannot login",
        "description": "Getting invalid credentials error",
        "priority": "high",
        "status": "open",
        "created_at": "2024-10-18T09:00:00Z"
    }
}

# Tool implementation
async def get_ticket(ticket_id: str) -> dict:
    """Retrieve support ticket information.

    Args:
        ticket_id: Unique ticket identifier

    Returns:
        Dictionary with ticket details
    """
    if ticket_id not in MOCK_TICKETS:
        raise ValueError(f"Ticket {ticket_id} not found")
    return MOCK_TICKETS[ticket_id]

# Schema
GET_TICKET_SCHEMA = {
    "type": "object",
    "properties": {
        "ticket_id": {
            "type": "string",
            "description": "Unique identifier for the support ticket"
        }
    },
    "required": ["ticket_id"]
}
```

Repeat for each tool (2-5 tools total).

#### 3.3 Create Evaluation Scenarios (10 minutes)

**File:** `evals/scenarios.py`

For EACH test scenario from your discovery:

```python
from evals.evaluator import Scenario

{{SCENARIO_NAME}} = Scenario(
    id="{{scenario_id}}",
    description="{{description}}",
    {{input_field}}: { /* test data */ },
    expected_{{classification}}: "{{level}}",
    expected_tools=["{{tool1}}", "{{tool2}}"],
    expected_findings_keywords=["{{kw1}}", "{{kw2}}"],
)
```

**Example:**

```python
URGENT_TICKET_SCENARIO = Scenario(
    id="urgent_system_outage",
    description="Critical system outage requiring immediate escalation",
    ticket_data={
        "id": "T-999",
        "subject": "Production down - 500 errors",
        "description": "All users seeing 500 errors since 2pm",
        "created_at": "2024-10-18T14:05:00Z"
    },
    expected_priority="urgent",
    expected_tools=["get_ticket", "update_ticket"],
    expected_findings_keywords=["escalate", "urgent", "outage"],
)

MEDIUM_TICKET_SCENARIO = Scenario(
    id="feature_question",
    description="User asking about feature functionality",
    ticket_data={
        "id": "T-100",
        "subject": "How to export data?",
        "description": "I need to export my data to CSV",
        "created_at": "2024-10-18T10:30:00Z"
    },
    expected_priority="medium",
    expected_tools=["get_ticket", "search_knowledge_base", "send_response"],
    expected_findings_keywords=["export", "instructions"],
)

# Must export ALL_SCENARIOS
ALL_SCENARIOS = [
    URGENT_TICKET_SCENARIO,
    MEDIUM_TICKET_SCENARIO,
    # ... add 1-3 more scenarios
]
```

Create 3-5 scenarios minimum.

---

### Phase 4: Update Project Metadata (5 minutes)

#### 4.1 Update pyproject.toml

```toml
[project]
name = "{{your-agent-name}}"  # e.g., "support-bot"
version = "0.1.0"
description = "{{Your description}}"
authors = [{ name = "{{Your name}}" }]

[project.scripts]
{{your-agent-name}} = "{{your_agent_package}}.cli:main"
```

#### 4.2 Update README.md

Replace the template content with:
- Your agent's purpose
- Your tools
- How to use it
- Your examples

#### 4.3 Update Examples (Optional)

**Files:** `examples/basic_usage.py`, `examples/run_evaluation.py`

Replace `{{agent_name}}` with your actual package name.

---

### Phase 5: Test Everything (15-20 minutes)

#### 5.1 Run Unit Tests

```bash
# Run all tests
uv run pytest

# Expected: Most generic tests should pass
# Add tests for your custom tools if needed
```

#### 5.2 Run Evaluation Suite

```bash
# Run automated evaluation
uv run python examples/run_evaluation.py

# Check results
cat eval_results.json | python -m json.tool

# Target: >70% pass rate
```

If pass rate is low:
- Refine system prompt (make criteria clearer)
- Adjust expected behaviors in scenarios
- Check tool implementations

#### 5.3 Manual Testing

```bash
# Start CLI
uv run python -m {{your_agent_package}}.cli new

# Test a conversation
You: [Test your agent with realistic input]

# Verify:
# 1. Agent calls correct tools
# 2. Makes appropriate decisions
# 3. Provides useful responses
```

#### 5.4 Check Observability

```bash
# List traces
ls data/traces/

# View a trace
cat data/traces/<trace-id>.json | python -m json.tool

# Verify:
# - Tool execution captured
# - API calls traced
# - Token counts present
```

---

### Phase 6: Polish and Document (10 minutes)

#### 6.1 Final Code Review

```bash
# Search for any remaining placeholders
grep -r "{{" src/ evals/ *.toml

# Should return nothing or only comments
```

#### 6.2 Update Documentation

- [ ] README explains your agent
- [ ] Tools are documented
- [ ] Usage examples included
- [ ] Configuration documented

#### 6.3 Git Init (Optional)

```bash
git init
git add .
git commit -m "Initial commit: {{Agent Name}} implementation"
```

---

### Phase 7: Deploy (Variable time)

Choose your deployment:

#### Option A: Local Development

```bash
# Run directly
uv run python -m {{agent_package}}.cli new
```

#### Option B: Install as Package

```bash
# Install locally
uv pip install -e .

# Run from anywhere
{{your-agent-name}}
```

#### Option C: Containerize

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install uv && uv sync

CMD ["uv", "run", "python", "-m", "{{agent_package}}.cli", "new"]
```

```bash
docker build -t {{your-agent-name}} .
docker run -it -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY {{your-agent-name}}
```

#### Option D: Cloud Deployment

Follow your cloud provider's deployment guide for Python apps.

---

## Troubleshooting

### Issue: Tests Failing

**Symptom:** Many tests failing after customization

**Common causes:**
1. Modified generic infrastructure (shouldn't have)
2. Tool schemas don't match functions
3. Import errors (package renamed incorrectly)

**Fix:**
```bash
# Check what was modified
git diff src/{{agent_name}}/agent.py  # Should show minimal changes

# Verify imports
python -c "from {{agent_package}} import Agent, Config"

# Verify tool schemas
python -c "from {{agent_package}}.tools.{{tools}} import *"
```

### Issue: Low Evaluation Pass Rate

**Symptom:** <70% scenarios passing

**Common causes:**
1. System prompt unclear about criteria
2. Expected behaviors too strict
3. Tool implementations incomplete

**Fix:**
1. Review failed scenarios:
```bash
cat eval_results.json | jq '.scenarios[] | select(.passed == false)'
```

2. Refine system prompt or expected behaviors

3. Re-run evaluation

### Issue: Agent Not Using Tools

**Symptom:** Agent responds but doesn't call tools

**Checklist:**
- [ ] Tools registered in CLI? (Check `cli.py`)
- [ ] Tools mentioned in system prompt?
- [ ] Schemas valid?
- [ ] Task clear enough?

**Fix:** Make system prompt more directive about tool usage

### Issue: Missing Placeholders

**Symptom:** Some `{{PLACEHOLDERS}}` still in code

**Fix:**
```bash
# Find remaining placeholders
grep -r "{{" src/ evals/

# Replace manually or use sed
sed -i 's/{{PLACEHOLDER}}/replacement/g' file.py
```

---

## Quality Checklist

Before considering the agent "done":

### Code Quality
- [ ] No `{{placeholders}}` remaining
- [ ] All imports working
- [ ] System prompt complete and clear
- [ ] All tools implemented with schemas
- [ ] Mock data realistic
- [ ] Error handling present

### Testing
- [ ] Unit tests passing
- [ ] Evaluation pass rate >70%
- [ ] Manual testing successful
- [ ] Observability verified (traces generated)

### Documentation
- [ ] README updated
- [ ] Tools documented
- [ ] Examples provided
- [ ] Configuration explained

### Production Readiness
- [ ] API keys via environment (not hardcoded)
- [ ] Error messages user-friendly
- [ ] Graceful degradation on failures
- [ ] Retry mechanism configured
- [ ] Conversation persistence working

---

## Timeline Breakdown

| Phase | Task | Time |
|-------|------|------|
| 1 | Setup | 10 min |
| 2 | Find placeholders | 5 min |
| 3 | Customize system prompt | 15 min |
| 3 | Implement tools | 20-30 min |
| 3 | Create eval scenarios | 10 min |
| 4 | Update metadata | 5 min |
| 5 | Test | 15-20 min |
| 6 | Polish | 10 min |
| **Total** | **Ready to deploy** | **90-105 min** |

Add deployment time as needed.

---

## Next Steps

Once your agent is working:

### Short Term
1. **Add more scenarios** - Improve evaluation coverage
2. **Refine system prompt** - Based on real usage
3. **Add more tools** - Expand capabilities
4. **Monitor usage** - Check traces, track errors

### Medium Term
1. **Switch to real APIs** - Replace mock data
2. **Add authentication** - Secure your agent
3. **Improve error handling** - Edge cases
4. **Optimize performance** - Token usage, latency

### Long Term
1. **Multi-agent workflows** - Coordinate multiple agents
2. **Advanced evaluation** - A/B testing, LLM-as-judge
3. **User feedback loops** - Learn from usage
4. **Scale deployment** - Handle production load

---

## Resources

- [CUSTOMIZATION_GUIDE.md](../CUSTOMIZATION_GUIDE.md) - Deep dive on customization
- [FOR_AI_ASSISTANTS.md](../FOR_AI_ASSISTANTS.md) - Comprehensive guide
- [QUICKSTART.md](../QUICKSTART.md) - Alternative quick start
- [reference-implementation/](../reference-implementation/) - Detective Agent example

---

## Summary

**You just built a production-ready AI agent in ~2 hours!**

What you accomplished:
✅ Complete agentic system with tool calling
✅ Full observability and tracing
✅ Robust error handling
✅ Automated evaluation
✅ 90%+ test coverage
✅ Production-ready architecture

**Amazing work! Now go deploy and iterate based on real usage.** 🚀
