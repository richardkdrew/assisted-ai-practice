# Customization Guide

**Deep dive into adapting the template to your use case**

This guide explains exactly what to customize, what to leave alone, and best practices for each customization point.

---

## Table of Contents

1. [Overview: The 90/10 Rule](#overview-the-9010-rule)
2. [Customization Point 1: System Prompt](#customization-point-1-system-prompt)
3. [Customization Point 2: Tools](#customization-point-2-tools)
4. [Customization Point 3: Evaluation Scenarios](#customization-point-3-evaluation-scenarios)
5. [Customization Point 4: Project Metadata](#customization-point-4-project-metadata)
6. [Optional Customizations](#optional-customizations)
7. [What NOT to Customize](#what-not-to-customize)
8. [Testing Your Customizations](#testing-your-customizations)

---

## Overview: The 90/10 Rule

### 90% Generic Infrastructure (DO NOT MODIFY)

These files provide battle-tested, production-ready infrastructure:

```
src/{{agent_name}}/
├── agent.py              ✅ Use as-is
├── config.py             ✅ Use as-is
├── models.py             ✅ Use as-is
├── cli.py                ✅ Use as-is (or minor tweaks)
├── providers/            ✅ Use as-is
│   ├── base.py
│   └── anthropic.py
├── tools/
│   └── registry.py       ✅ Use as-is
├── context/              ✅ Use as-is
├── retry/                ✅ Use as-is
├── observability/        ✅ Use as-is
└── persistence/          ✅ Use as-is

evals/
├── evaluator.py          ✅ Use as-is
└── reporters.py          ✅ Use as-is

tests/                     ✅ Use as-is (add your own)
```

**Why not modify?**
- Proven, tested architecture
- Consistent patterns across all agents
- Easy to maintain and debug
- Updates can be applied cleanly

### 10% Use-Case-Specific (MUST CUSTOMIZE)

These files define what makes your agent unique:

```
src/{{agent_name}}/
├── system_prompt.py      ⚠️  CUSTOMIZE
└── tools/
    └── {{domain}}_tools.py  ⚠️  CUSTOMIZE

evals/
└── scenarios.py          ⚠️  CUSTOMIZE

pyproject.toml            ⚠️  CUSTOMIZE (metadata)
README.md                 ⚠️  CUSTOMIZE (documentation)
examples/                 ⚠️  CUSTOMIZE (usage examples)
```

---

## Customization Point 1: System Prompt

**File:** `src/{{agent_name}}/system_prompt.py`

**Purpose:** Define agent personality, domain knowledge, and behavior guidelines

### Template Structure

```python
DEFAULT_SYSTEM_PROMPT = """You are {{AGENT_NAME}}, {{ROLE_DESCRIPTION}}.

Your purpose is to {{PRIMARY_PURPOSE}}.

You have access to the following tools:
1. {{TOOL1_NAME}} - {{TOOL1_DESCRIPTION}}
2. {{TOOL2_NAME}} - {{TOOL2_DESCRIPTION}}

When {{SCENARIO_TYPE_1}}:
- {{ACTION_1}}
- {{ACTION_2}}

Guidelines for {{CLASSIFICATION_SYSTEM}}:
- {{LEVEL_1}}: {{CRITERIA_1}}
- {{LEVEL_2}}: {{CRITERIA_2}}
- {{LEVEL_3}}: {{CRITERIA_3}}

Always:
- {{GENERAL_GUIDELINE_1}}
- {{GENERAL_GUIDELINE_2}}
- Base decisions on provided data
- Acknowledge uncertainty when information is incomplete

You are {{PERSONALITY_TRAITS}}.
"""
```

### What to Include

#### 1. Identity and Role
```python
"""You are {{AGENT_NAME}}, {{ONE_LINE_ROLE_DESCRIPTION}}."""
```

**Examples:**
- "You are Detective Agent, part of a Release Confidence System."
- "You are SupportBot, a customer support triage specialist."
- "You are CodeReviewer, an automated code quality analyst."

#### 2. Purpose Statement
```python
"""Your purpose is to {{WHAT_YOU_DO}} by {{HOW_YOU_DO_IT}}."""
```

**Examples:**
- "Your purpose is to assess software release risk by analyzing test results and deployment metrics."
- "Your purpose is to triage customer support tickets by understanding issues and providing solutions."

#### 3. Tool Descriptions
```python
"""You have access to the following tools:
1. {{tool_name}} - {{what_it_does}}
2. {{tool_name}} - {{what_it_does}}
"""
```

**Best Practice:** List ALL tools the agent will have access to

#### 4. Behavioral Guidelines

**When to use each tool:**
```python
"""When assessing {{something}}:
- First, call {{tool1}} to gather {{data}}
- Analyze the {{results}} for {{patterns}}
- Then, call {{tool2}} to {{action}}
"""
```

**Decision criteria:**
```python
"""{{Classification}} levels:
- {{HIGH}}: {{specific_criteria}} (e.g., >5% error rate, critical failures)
- {{MEDIUM}}: {{specific_criteria}} (e.g., 2-5% error rate, minor issues)
- {{LOW}}: {{specific_criteria}} (e.g., <2% error rate, all tests passing)
"""
```

#### 5. General Principles
```python
"""Always:
- Explain your reasoning clearly
- Base assessments on provided data
- Acknowledge uncertainty when data is incomplete
- Be {{personality_trait}}  # e.g., cautious, thorough, concise
"""
```

### Best Practices

✅ **DO:**
- Be specific and concrete
- Include examples in criteria
- Use clear, unambiguous language
- List ALL tools
- Define classification levels with measurable criteria
- Specify edge case handling

❌ **DON'T:**
- Be vague ("be smart", "do the right thing")
- Assume agent knows domain concepts
- Omit tools from the description
- Use subjective criteria without examples
- Contradict yourself

### Examples by Use Case

#### Customer Support Agent
```python
DEFAULT_SYSTEM_PROMPT = """You are SupportBot, a customer support triage and response agent.

Your purpose is to efficiently handle customer support tickets by understanding issues, finding solutions, and providing helpful responses.

You have access to the following tools:
1. get_ticket - Retrieve detailed ticket information
2. search_knowledge_base - Find relevant help articles and solutions
3. update_ticket - Change ticket status and add internal notes
4. send_response - Send a response to the customer

Priority Guidelines:
- URGENT: System outages, data loss, security issues
  → Escalate immediately to on-call engineer
- HIGH: Cannot access account, payment failures, broken core features
  → Respond within 1 hour with solution or workaround
- MEDIUM: Feature questions, minor bugs, "how-to" inquiries
  → Search knowledge base, respond within 4 hours
- LOW: Feature requests, general questions, feedback
  → Acknowledge and respond within 24 hours

Always:
- Be empathetic and professional
- Search knowledge base before crafting responses
- Provide step-by-step instructions when applicable
- Escalate if issue is complex or outside your capability
- Update ticket status appropriately
- Confirm resolution when possible

You are helpful, patient, and thorough.
"""
```

#### Code Review Agent
```python
DEFAULT_SYSTEM_PROMPT = """You are CodeReviewer, an automated code quality and security analyst.

Your purpose is to review code changes for potential issues, bugs, security vulnerabilities, and style violations.

You have access to the following tools:
1. get_pull_request - Retrieve PR details and changed files
2. analyze_code_quality - Run static analysis on code
3. check_security - Scan for security vulnerabilities
4. post_review_comment - Add review comments to PR

Review Severity Levels:
- CRITICAL: Security vulnerabilities, data leaks, breaking changes
  → Block merge, require immediate fixes
- HIGH: Bugs, performance issues, bad practices
  → Request changes before merge
- MEDIUM: Code style, minor improvements, suggestions
  → Approve with recommendations
- LOW: Nits, optional optimizations
  → Approve, mention as FYI

Focus Areas:
- Security: SQL injection, XSS, authentication issues
- Bugs: Logic errors, null references, race conditions
- Performance: N+1 queries, memory leaks, inefficient algorithms
- Maintainability: Code clarity, documentation, test coverage

Always:
- Explain WHY something is an issue
- Suggest specific fixes
- Reference coding standards when applicable
- Acknowledge good practices
- Be constructive and educational

You are thorough, educational, and constructive.
"""
```

---

## Customization Point 2: Tools

**File:** `src/{{agent_name}}/tools/{{domain}}_tools.py`

**Purpose:** Implement the agent's capabilities - what it can actually DO

### Tool Implementation Pattern

For EACH tool, you need:
1. Async function implementation
2. Tool schema (for LLM)
3. Mock data (for testing)
4. Error handling

### Template for a Tool

```python
# 1. Mock data for testing
MOCK_{{ENTITY}}_DATA = {
    "{{id1}}": {
        "field1": "value1",
        "field2": "value2",
    },
    "{{id2}}": {
        "field1": "value3",
        "field2": "value4",
    },
}

# 2. Function implementation
async def {{tool_name}}({{param1}}: str, {{param2}}: int = 0) -> dict[str, Any]:
    """{{DESCRIPTION}}.

    Args:
        {{param1}}: {{param1_description}}
        {{param2}}: {{param2_description}} (optional)

    Returns:
        Dictionary containing {{return_value_description}}

    Raises:
        ValueError: If {{error_condition}}
    """
    # Validate inputs
    if not {{param1}}:
        raise ValueError("{{param1}} is required")

    # Development: Use mock data
    if {{param1}} in MOCK_{{ENTITY}}_DATA:
        return MOCK_{{ENTITY}}_DATA[{{param1}}]

    # Production: Call real API (commented out for now)
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(f"{API_URL}/{{{param1}}}")
    #     return response.json()

    # Not found
    raise ValueError(
        f"{{Entity}} '{ {{param1}} }' not found. "
        f"Available: {', '.join(MOCK_{{ENTITY}}_DATA.keys())}"
    )

# 3. Tool schema (for LLM)
{{TOOL_NAME}}_SCHEMA = {
    "type": "object",
    "properties": {
        "{{param1}}": {
            "type": "string",
            "description": "{{Description for LLM to understand when/how to use this param}}"
        },
        "{{param2}}": {
            "type": "integer",
            "description": "{{Description}}"
        }
    },
    "required": ["{{param1}}"]  # List required params
}
```

### Tool Types

#### Type 1: GET Tool (Fetch Data)

**Purpose:** Retrieve information

```python
async def get_{{entity}}({{entity}}_id: str) -> dict:
    """Retrieve {{entity}} information."""
    # Fetch and return data
    return data

GET_{{ENTITY}}_SCHEMA = {
    "type": "object",
    "properties": {
        "{{entity}}_id": {"type": "string", "description": "..."}
    },
    "required": ["{{entity}}_id"]
}
```

**Examples:**
- `get_release_summary(release_id)` - Fetch release info
- `get_ticket(ticket_id)` - Fetch support ticket
- `get_user_profile(user_id)` - Fetch user data

#### Type 2: POST/Action Tool (Submit/Modify Data)

**Purpose:** Take an action or submit information

```python
async def {{action}}_{{entity}}(
    {{entity}}_id: str,
    {{field1}}: str,
    {{field2}}: list[str]
) -> dict:
    """{{ACTION_DESCRIPTION}}."""
    # Validate
    # Process
    # Submit
    return {"status": "success", "id": "..."}

{{ACTION}}_{{ENTITY}}_SCHEMA = {
    "type": "object",
    "properties": {
        "{{entity}}_id": {"type": "string", "description": "..."},
        "{{field1}}": {"type": "string", "description": "..."},
        "{{field2}}": {"type": "array", "items": {"type": "string"}, "description": "..."}
    },
    "required": ["{{entity}}_id", "{{field1}}", "{{field2}}"]
}
```

**Examples:**
- `file_risk_report(release_id, severity, findings)` - Submit assessment
- `update_ticket(ticket_id, status, notes)` - Modify ticket
- `send_response(ticket_id, message)` - Send reply

#### Type 3: Search/Query Tool

**Purpose:** Search for relevant information

```python
async def search_{{resource}}(query: str, limit: int = 10) -> list[dict]:
    """Search for {{resource}} matching query."""
    # Perform search
    # Return ranked results
    return results

SEARCH_{{RESOURCE}}_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Search query"},
        "limit": {"type": "integer", "description": "Max results to return"}
    },
    "required": ["query"]
}
```

**Examples:**
- `search_knowledge_base(query)` - Find help articles
- `search_documentation(query)` - Find docs
- `search_similar_issues(description)` - Find similar cases

### Best Practices

✅ **DO:**
- Provide comprehensive docstrings
- Include type hints
- Validate inputs
- Use descriptive error messages
- Start with mock data
- Make schemas match function signatures exactly
- Handle edge cases (missing data, invalid inputs)

❌ **DON'T:**
- Skip error handling
- Use vague parameter names
- Forget to export schemas
- Make required params optional in schema
- Hallucinate or make up data when not found

### Mock Data Guidelines

**Make it realistic:**
```python
# ✅ Good: Realistic, varied examples
MOCK_TICKETS = {
    "T-001": {
        "subject": "Cannot login to account",
        "description": "Getting 'Invalid credentials' error when trying to log in with correct password",
        "priority": "high",
        "created_at": "2024-10-18T09:15:00Z",
        "customer": "John Doe"
    },
    "T-002": {
        "subject": "How to export my data?",
        "description": "I need to export all my data to CSV format",
        "priority": "medium",
        "created_at": "2024-10-18T14:30:00Z",
        "customer": "Jane Smith"
    },
}

# ❌ Bad: Too simple, unrealistic
MOCK_TICKETS = {
    "1": {"text": "test ticket 1"},
    "2": {"text": "test ticket 2"},
}
```

**Cover different scenarios:**
- Happy path (normal case)
- Edge cases (missing fields, unusual values)
- Error cases (for testing error handling)

---

## Customization Point 3: Evaluation Scenarios

**File:** `evals/scenarios.py`

**Purpose:** Define test cases that validate agent behavior

### Scenario Structure

```python
from evals.evaluator import Scenario

{{SCENARIO_NAME}} = Scenario(
    id="{{unique_scenario_id}}",
    description="{{Human-readable description of what this tests}}",

    # Input data (your domain-specific field name)
    {{input_data_field}}: {
        # Data that represents this test case
        "field1": "value1",
        "field2": "value2",
    },

    # Expected outcomes
    expected_{{classification_field}}: "{{expected_level}}",  # e.g., "high", "urgent", "approved"
    expected_tools=["{{tool1}}", "{{tool2}}"],  # Tools agent should call
    expected_findings_keywords=["{{keyword1}}", "{{keyword2}}"],  # Keywords in response

    # Optional metadata
    metadata={"{{key}}": {{value}}}
)
```

### Example Scenarios

```python
# High severity scenario
HIGH_RISK_RELEASE = Scenario(
    id="high_risk_critical_failures",
    description="Release with critical test failures and high error rate",
    release_data={
        "release_id": "rel-003",
        "version": "v2.3.0",
        "changes": ["Major authentication refactor"],
        "tests": {"passed": 135, "failed": 12},
        "deployment_metrics": {"error_rate": 0.065}
    },
    expected_severity="high",
    expected_tools=["get_release_summary", "file_risk_report"],
    expected_findings_keywords=["test failure", "error rate", "risk"],
)

# Medium severity scenario
MEDIUM_RISK_RELEASE = Scenario(
    id="medium_risk_minor_issues",
    description="Release with minor test failures",
    release_data={
        "release_id": "rel-004",
        "version": "v2.4.0",
        "changes": ["UI improvements"],
        "tests": {"passed": 156, "failed": 2},
        "deployment_metrics": {"error_rate": 0.028}
    },
    expected_severity="medium",
    expected_tools=["get_release_summary", "file_risk_report"],
    expected_findings_keywords=["minor", "moderate"],
)

# Edge case: Missing data
MISSING_DATA_SCENARIO = Scenario(
    id="missing_test_data",
    description="Release with incomplete information",
    release_data={
        "release_id": "rel-999",
        "version": "v3.0.0",
        # Missing test results and metrics
    },
    expected_severity="high",  # Should be cautious
    expected_tools=["get_release_summary"],
    expected_findings_keywords=["missing", "incomplete", "uncertain"],
)

# Export all scenarios
ALL_SCENARIOS = [
    HIGH_RISK_RELEASE,
    MEDIUM_RISK_RELEASE,
    MISSING_DATA_SCENARIO,
    # Add 2-3 more scenarios
]
```

### Coverage Guidelines

Create scenarios that cover:

1. **Happy Path** - Typical, expected cases
2. **Each Classification Level** - All severity/priority/status levels
3. **Edge Cases** - Missing data, boundary conditions
4. **Error Cases** - Invalid inputs, failures
5. **Complex Cases** - Conflicting signals, ambiguous situations

**Minimum:** 3-5 scenarios
**Recommended:** 5-10 scenarios
**Comprehensive:** 10+ scenarios

### Best Practices

✅ **DO:**
- Name scenarios descriptively
- Cover all classification levels
- Include edge cases
- Use realistic data
- Test both success and failure paths
- Export as `ALL_SCENARIOS`

❌ **DON'T:**
- Only test happy path
- Use unrealistic data
- Forget edge cases
- Make expected behaviors too strict
- Skip error scenarios

---

## Customization Point 4: Project Metadata

**File:** `pyproject.toml`

Replace placeholders:

```toml
[project]
name = "{{agent-name}}"  # e.g., "support-bot", "code-reviewer"
version = "0.1.0"
description = "{{DESCRIPTION}}"  # One-line description
authors = [{ name = "{{YOUR_NAME}}" }]

[project.scripts]
{{agent-name}} = "{{agent_name}}.cli:main"  # CLI entry point
```

**File:** `README.md`

Update with:
- Your agent's purpose
- Tools it provides
- How to use it
- Examples
- Configuration

---

## Optional Customizations

### 1. CLI Customization

**File:** `src/{{agent_name}}/cli.py`

**Minor tweaks you might want:**

```python
# Change welcome message
print(f"Welcome to {{AGENT_NAME}}!")

# Add custom commands
if sys.argv[1] == "my-custom-command":
    # Handle custom command
    pass
```

### 2. Configuration Customization

**File:** `src/{{agent_name}}/config.py`

**Add domain-specific config:**

```python
@dataclass
class Config:
    # Existing fields...
    api_key: str
    model: str
    # ...

    # Your custom config
    {{custom_field}}: str = "{{default_value}}"

    @classmethod
    def from_env(cls) -> "Config":
        # Load from environment
        {{custom_field}} = os.getenv("{{CUSTOM_FIELD}}", cls.{{custom_field}})
```

### 3. Adding Example Files

**Directory:** `examples/`

Create usage examples:

```python
# examples/{{use_case}}_example.py
"""Example of using {{agent_name}} for {{use_case}}."""

import asyncio
from {{agent_name}} import Agent, Config
# ... implementation ...
```

---

## What NOT to Customize

**These files are generic infrastructure - DO NOT MODIFY:**

### Core Agent Logic
- `src/{{agent_name}}/agent.py` - Conversation loop, tool execution
- `src/{{agent_name}}/models.py` - Data models

**Why:** This is the heart of the agentic system. Changes here affect all agents.

### Provider System
- `src/{{agent_name}}/providers/base.py` - Provider interface
- `src/{{agent_name}}/providers/anthropic.py` - Anthropic implementation

**Why:** Changing these breaks provider abstraction. To add providers, create NEW files.

### Infrastructure
- `src/{{agent_name}}/context/manager.py` - Context window management
- `src/{{agent_name}}/retry/strategy.py` - Retry logic
- `src/{{agent_name}}/observability/*` - Tracing
- `src/{{agent_name}}/persistence/store.py` - Storage

**Why:** Proven, tested implementations. Changing these introduces bugs.

### Evaluation Engine
- `evals/evaluator.py` - Scoring logic
- `evals/reporters.py` - Report generation

**Why:** Generic evaluation framework works for all agents.

### Test Infrastructure
- `tests/conftest.py` - Test fixtures
- `tests/*_test.py` - Generic tests

**Why:** Tests validate the infrastructure. Add YOUR tests, don't modify these.

---

## Testing Your Customizations

### Step 1: Unit Tests

Test your tools individually:

```python
# tests/{{domain}}_tools_test.py
import pytest
from {{agent_name}}.tools.{{domain}}_tools import {{tool_name}}

@pytest.mark.asyncio
async def test_{{tool_name}}():
    result = await {{tool_name}}("valid_id")
    assert result["field"] == "expected_value"

@pytest.mark.asyncio
async def test_{{tool_name}}_error():
    with pytest.raises(ValueError):
        await {{tool_name}}("invalid_id")
```

### Step 2: Integration Tests

Test full agent workflow:

```bash
uv run pytest tests/integration_test.py -v
```

### Step 3: Evaluation Suite

Run automated scenarios:

```bash
uv run python examples/run_evaluation.py
```

**Target:** >70% pass rate

### Step 4: Manual Testing

```bash
uv run python -m {{agent_name}}.cli new
```

Test realistic scenarios manually.

### Step 5: Check Observability

```bash
# Verify traces are generated
ls data/traces/

# Inspect a trace
cat data/traces/<trace-id>.json | python -m json.tool

# Check for:
# - Tool execution spans
# - API call timing
# - Token counts
```

---

## Checklist: Customization Complete?

Before considering customization done:

### System Prompt
- [ ] Agent role clearly defined
- [ ] All tools listed and described
- [ ] Classification levels with specific criteria
- [ ] Behavioral guidelines included
- [ ] Edge case handling specified
- [ ] Personality/tone appropriate

### Tools
- [ ] 2-5 tools implemented
- [ ] All tools have docstrings
- [ ] Schemas match function signatures
- [ ] Mock data provided for each tool
- [ ] Error handling for invalid inputs
- [ ] Tools registered in CLI/main

### Evaluation
- [ ] 3-5+ scenarios created
- [ ] All classification levels covered
- [ ] Edge cases included
- [ ] Realistic input data
- [ ] Expected behaviors defined
- [ ] Exported as ALL_SCENARIOS

### Project
- [ ] pyproject.toml updated
- [ ] README customized
- [ ] Examples created
- [ ] Tests passing
- [ ] Evals passing (>70%)
- [ ] Observability working

---

## Next Steps

Once customization is complete:

1. **Test thoroughly** - Unit, integration, evaluation, manual
2. **Document** - Update README, add examples
3. **Deploy** - Local, containerized, or cloud
4. **Monitor** - Check traces, track errors
5. **Iterate** - Refine based on real usage

**See:**
- [QUICKSTART.md](QUICKSTART.md) - Testing and deployment
- [FOR_AI_ASSISTANTS.md](FOR_AI_ASSISTANTS.md) - Quality checklist

---

**Happy customizing! 🎨**
