# Quick Start Guide

**Build a production-ready AI agent in under 2 hours**

---

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- LLM API key (Anthropic recommended)
- Basic understanding of AI agents and tools

---

## 30-Second Overview

1. Copy `starter-template/` to your project
2. Find all `{{PLACEHOLDERS}}` in files
3. Customize system prompt, tools, and eval scenarios
4. Run tests
5. Deploy

---

## Step-by-Step (15 minutes)

### Step 1: Copy the Template (1 min)

```bash
# Copy starter template to your project
cp -r starter-template/ my-agent/
cd my-agent/

# Create virtual environment
uv venv
source .venv/bin/activate  # On macOS/Linux
# or: .venv\Scripts\activate  # On Windows
```

### Step 2: Install Dependencies (1 min)

```bash
# Install all dependencies
uv sync

# Verify installation
uv run pytest --version
```

### Step 3: Configure API Key (1 min)

```bash
# Set your API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Or add to .env file (create it)
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Step 4: Find Placeholders (2 min)

```bash
# Search for all customization points
grep -r "{{" src/ evals/

# You should see placeholders in:
# - src/{{agent_name}}/system_prompt.py
# - src/{{agent_name}}/tools/example_tools.py
# - evals/scenarios.py
# - pyproject.toml
```

### Step 5: Customize System Prompt (5 min)

**Edit: `src/{{agent_name}}/system_prompt.py`**

```python
DEFAULT_SYSTEM_PROMPT = """You are {{AGENT_NAME}}, {{ROLE_DESCRIPTION}}.

Your purpose is to {{PRIMARY_PURPOSE}}.

You have access to the following tools:
1. {{TOOL1_NAME}} - {{TOOL1_DESCRIPTION}}
2. {{TOOL2_NAME}} - {{TOOL2_DESCRIPTION}}

Guidelines:
- {{GUIDELINE_1}}
- {{GUIDELINE_2}}
- {{GUIDELINE_3}}

{{CLASSIFICATION_SYSTEM}}:
- {{LEVEL_1}}: {{CRITERIA_1}}
- {{LEVEL_2}}: {{CRITERIA_2}}
- {{LEVEL_3}}: {{CRITERIA_3}}

Always explain your reasoning and base decisions on provided data.
"""
```

**Example (Customer Support Agent):**

```python
DEFAULT_SYSTEM_PROMPT = """You are SupportBot, a customer support triage agent.

Your purpose is to efficiently handle customer support tickets.

You have access to the following tools:
1. get_ticket - Retrieve ticket details
2. update_ticket - Change ticket status and add notes
3. send_response - Reply to customer

Guidelines:
- Be empathetic and professional
- Search for solutions before responding
- Escalate complex issues

Priority Levels:
- URGENT: System outages, data loss → Escalate immediately
- HIGH: Cannot login, payment issues → Respond within 1 hour
- MEDIUM: Feature questions → Respond within 4 hours
- LOW: General inquiries → Respond within 24 hours

Always explain your reasoning and base decisions on provided data.
"""
```

### Step 6: Implement Tools (10-30 min)

**Edit: `src/{{agent_name}}/tools/{{domain}}_tools.py`**

**Template for each tool:**

```python
async def {{tool_name}}({{param1}}: str, {{param2}}: int) -> dict:
    """{{DESCRIPTION}}

    Args:
        {{param1}}: {{param1_description}}
        {{param2}}: {{param2_description}}

    Returns:
        Dictionary containing {{return_description}}
    """
    # For development: use mock data
    if {{param1}} in MOCK_DATA:
        return MOCK_DATA[{{param1}}]

    # For production: call real API
    # response = await http_client.get(f"/api/{{{param1}}}")
    # return response.json()

    raise ValueError(f"{{Error message}}")

# Tool schema (required for LLM)
{{TOOL_NAME}}_SCHEMA = {
    "type": "object",
    "properties": {
        "{{param1}}": {
            "type": "string",
            "description": "{{Description for LLM}}"
        },
        "{{param2}}": {
            "type": "integer",
            "description": "{{Description for LLM}}"
        }
    },
    "required": ["{{param1}}", "{{param2}}"]
}
```

**Real Example:**

```python
# Mock data for testing
MOCK_TICKETS = {
    "T-001": {
        "id": "T-001",
        "subject": "Cannot login",
        "description": "Getting error when trying to log in",
        "status": "open",
        "priority": "high"
    }
}

async def get_ticket(ticket_id: str) -> dict:
    """Retrieve ticket information.

    Args:
        ticket_id: Unique ticket identifier

    Returns:
        Dictionary with ticket details
    """
    if ticket_id not in MOCK_TICKETS:
        raise ValueError(f"Ticket {ticket_id} not found")

    return MOCK_TICKETS[ticket_id]

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

### Step 7: Create Evaluation Scenarios (10 min)

**Edit: `evals/scenarios.py`**

```python
from evals.evaluator import Scenario

{{SCENARIO_1}} = Scenario(
    id="{{scenario_id}}",
    description="{{What this tests}}",
    {{data_field}}: {
        # Input data for this test
    },
    expected_{{classification}}: "{{expected_level}}",
    expected_tools=["{{tool1}}", "{{tool2}}"],
    expected_findings_keywords=["{{keyword1}}", "{{keyword2}}"],
)

# Create 3-5 scenarios covering different cases
```

**Example:**

```python
URGENT_TICKET = Scenario(
    id="urgent_login_issue",
    description="High-priority login failure",
    ticket_data={
        "id": "T-001",
        "subject": "Cannot login",
        "description": "All users unable to authenticate",
        "status": "open"
    },
    expected_priority="urgent",
    expected_tools=["get_ticket", "update_ticket"],
    expected_findings_keywords=["urgent", "escalate", "authentication"],
)

MEDIUM_TICKET = Scenario(
    id="medium_feature_question",
    description="Feature inquiry ticket",
    ticket_data={
        "id": "T-002",
        "subject": "How do I export data?",
        "description": "User asking about export functionality",
        "status": "open"
    },
    expected_priority="medium",
    expected_tools=["get_ticket", "send_response"],
    expected_findings_keywords=["export", "instructions"],
)

# Export all scenarios
ALL_SCENARIOS = [URGENT_TICKET, MEDIUM_TICKET, ...]
```

### Step 8: Update Project Metadata (2 min)

**Edit: `pyproject.toml`**

Replace placeholders:
```toml
[project]
name = "{{agent-name}}"  # e.g., "support-bot"
description = "{{DESCRIPTION}}"  # e.g., "Customer support triage agent"
```

### Step 9: Test Everything (5 min)

```bash
# Run unit tests
uv run pytest

# Should see generic tests passing
# Add your own tool tests as needed

# Run evaluation suite
uv run python examples/run_evaluation.py

# Check pass rate (should be >70%)
```

### Step 10: Manual Testing (10 min)

```bash
# Start CLI
uv run python -m {{agent_name}}.cli new

# Test a conversation
You: {{Test your agent here}}

# Verify it:
# 1. Calls the right tools
# 2. Makes correct decisions
# 3. Provides good responses

# Check traces
cat data/traces/<trace-id>.json | python -m json.tool

# Verify observability working
```

---

## Verification Checklist

Before considering it done:

- [ ] System prompt defines agent role clearly
- [ ] All tools implemented and tested
- [ ] Tool schemas match function signatures
- [ ] Mock data provided for testing
- [ ] 3-5 evaluation scenarios created
- [ ] Tests passing (`pytest`)
- [ ] Evaluations passing (>70% pass rate)
- [ ] Manual testing confirms agent works
- [ ] Traces generated (check `data/traces/`)
- [ ] README updated with your agent details

---

## Common Customizations

### Adding a New Tool

1. **Implement the function** in `tools/{{domain}}_tools.py`:
```python
async def my_new_tool(param: str) -> dict:
    """Description."""
    return {"result": "success"}
```

2. **Define the schema**:
```python
MY_NEW_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "param": {"type": "string", "description": "..."}
    },
    "required": ["param"]
}
```

3. **Register it** in CLI or main:
```python
registry.register(
    name="my_new_tool",
    description="What it does",
    input_schema=MY_NEW_TOOL_SCHEMA,
    handler=my_new_tool
)
```

4. **Update system prompt** to mention the new tool

5. **Add test scenario** using the new tool

### Changing Classification System

If you need different levels (not HIGH/MEDIUM/LOW):

1. **Update system prompt** with new levels
2. **Update evaluation scenarios** `expected_{{classification}}`
3. **Update evaluator** if needed (usually works as-is)

### Using Real APIs Instead of Mocks

Replace mock data with real API calls:

```python
async def get_data(id: str) -> dict:
    # Old: mock version
    # return MOCK_DATA[id]

    # New: real API
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/data/{id}")
        return response.json()
```

---

## Troubleshooting

### Tests Fail After Customization

**Problem:** Generic tests failing

**Solution:** You probably modified generic infrastructure. Revert changes to:
- `agent.py`, `config.py`, `models.py`
- `providers/*`, `tools/registry.py`
- `context/*`, `retry/*`, `observability/*`

Only customize: `system_prompt.py`, `{{domain}}_tools.py`, `scenarios.py`

### Agent Doesn't Use Tools

**Problem:** Agent responds but doesn't call tools

**Check:**
1. Tools registered? (see CLI/main)
2. System prompt mentions tools?
3. Tool schemas valid?
4. Is agent's task clear?

**Fix:** Make system prompt more directive about when to use tools

### Evaluation Scenarios Fail

**Problem:** Low pass rate

**Check:**
1. Are expected behaviors realistic?
2. Is system prompt clear about criteria?
3. Do scenarios have enough input data?

**Fix:** Refine system prompt or adjust expected behaviors

---

## Next Steps

### Option 1: Deploy Locally

```bash
# Run as service
uv run python -m {{agent_name}}.cli new

# Or import in your code
from {{agent_name}} import Agent, Config
# ... use programmatically
```

### Option 2: Containerize

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install uv && uv sync
CMD ["uv", "run", "python", "-m", "{{agent_name}}.cli", "new"]
```

### Option 3: Add More Features

- Additional tools
- Better error handling
- Custom context strategies
- Additional LLM providers
- Web interface
- API endpoint

### Option 4: Production Hardening

- [ ] Environment variable validation
- [ ] Secrets management (not hardcoded keys)
- [ ] Rate limiting
- [ ] Logging and monitoring
- [ ] Error alerting
- [ ] Cost tracking
- [ ] Performance optimization

---

## Learn More

- [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md) - Comprehensive guide
- [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) - Deep dive on customization
- [workflows/COPY_AND_CUSTOMIZE.md](workflows/COPY_AND_CUSTOMIZE.md) - Detailed workflow
- [reference-implementation/](reference-implementation/) - Detective Agent example

---

## Support

- **Stuck?** Check [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md) troubleshooting section
- **Need examples?** See `reference-implementation/`
- **Have questions?** Open an issue

---

**You're ready! Start customizing and build your agent.** 🚀
