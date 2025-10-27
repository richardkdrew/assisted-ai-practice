# Investigator Agent - Manual Test Plan

This comprehensive test plan guides you through testing the Investigator Agent to understand how each component works. Each test includes exact commands to run, what to observe, and what you'll learn.

## Prerequisites

1. Ensure you have your environment set up:
```bash
cd module8
uv sync
```

2. Verify your API key is configured:
```bash
cat .env | grep ANTHROPIC_API_KEY
```

3. Clear any previous test data (optional):
```bash
rm -rf data/conversations/*
rm -rf data/traces/*
rm -rf data/memory/*
```

---

## Test 1: Basic Conversation Flow

**Goal:** Understand the core conversation loop and how the agent investigates features.

**What You'll Learn:**
- How the agent uses tools (JIRA, analysis, docs)
- How conversations are persisted
- How decisions are made

### Steps:

1. **Start a new conversation:**
```bash
uv run python cli.py
```

2. **Ask the agent to investigate a feature:**
```
You: Is the Maintenance Scheduling feature (FEAT-MS-001) ready for production?
```

3. **Observe the agent's behavior:**
   - Watch it call tools (get_jira_data, get_analysis)
   - See how it analyzes the data
   - Notice the decision it makes

4. **Exit gracefully:**
```
You: exit
```

### What to Observe:

1. **In the terminal:**
   - Note the conversation ID that's created (first 8 characters shown)
   - Watch tool calls happening in real-time
   - See the agent's reasoning and final decision

2. **In the filesystem:**
```bash
# List your conversations
ls -la data/conversations/

# View the conversation JSON (replace <id> with your conversation ID)
cat data/conversations/<conversation-id>.json | python3 -m json.tool
```

3. **What to look for in the JSON:**
   - `id`: Unique conversation identifier
   - `messages`: Array of user and assistant messages
   - `created_at`, `updated_at`: Timestamps
   - Tool use blocks with `type`: `tool_use`
   - Tool result blocks with `type`: `tool_result`

### Key Learnings:
- Agent automatically discovers and calls appropriate tools
- Full conversation history is preserved in JSON
- Tool calls and results are part of the message flow
- Each conversation can be resumed later

---

## Test 2: Continuing Conversations

**Goal:** Understand conversation persistence and context maintenance.

**What You'll Learn:**
- How to resume conversations
- How context carries across sessions

### Steps:

1. **List your conversations:**
```bash
uv run python cli.py list
```

2. **Continue the conversation from Test 1:**
```bash
uv run python cli.py continue <conversation-id>
```

You can use just the first 8 characters of the ID.

3. **Reference earlier context:**
```
You: What were the key factors in your assessment of FEAT-MS-001?
```

The agent should remember the previous analysis.

4. **Try another feature:**
```
You: Now check FEAT-QR-002 - is it ready?
```

5. **Exit:**
```
You: exit
```

### What to Observe:

1. **The agent remembers the previous conversation**
2. **Check the updated conversation file:**
```bash
cat data/conversations/<conversation-id>.json | python3 -m json.tool | tail -50
```

3. **Notice:**
   - New messages appended to the same file
   - `updated_at` timestamp changed
   - All previous messages and tool calls still present

### Key Learnings:
- Conversations persist across CLI sessions
- Agent has full access to conversation history
- You can pause and resume anytime
- Multiple feature assessments can happen in one conversation

---

## Test 3: Observability (Traces and Spans)

**Goal:** Understand how OpenTelemetry captures agent operations.

**What You'll Learn:**
- What traces and spans are
- How to view traces for debugging
- What performance data is captured

### Steps:

1. **Start a new conversation:**
```bash
uv run python cli.py
```

2. **Send a message:**
```
You: Quick status check on FEAT-MS-001
You: exit
```

3. **View traces:**
```bash
# List trace files
ls -la data/traces/

# View the most recent trace
ls -t data/traces/*.json | head -1 | xargs cat | python3 -m json.tool | less
```

### What to Observe in the Trace:

1. **Look for different span types:**
   - `new_conversation`: Agent initialization
   - `send_message`: Each message you send
   - `anthropic_api_call`: Calls to Claude API
   - `execute_tools`: Tool execution

2. **For each span, note:**
   - `name`: Operation name
   - `start_time`, `end_time`: Timing information
   - `duration_ms`: How long it took
   - `attributes`: Metadata about the operation

3. **Look for these attributes:**
   - `session.id`: The conversation ID
   - `model`: Which Claude model was used
   - `input_tokens`: Tokens sent to the API
   - `output_tokens`: Tokens in the response
   - `tool.*.called`: Which tools were used

### Experiment:

**Search for specific information in traces:**
```bash
# Find all tool calls
grep -r "tool\." data/traces/*.json

# Find token usage
grep -r "tokens" data/traces/*.json | head -10

# Find slow operations (>1000ms)
python3 -c "
import json
from pathlib import Path
for f in Path('data/traces').glob('*.json'):
    spans = json.load(open(f))
    for span in spans:
        if span.get('duration_ms', 0) > 1000:
            print(f'{f.name}: {span[\"name\"]} took {span[\"duration_ms\"]:.0f}ms')
"
```

### Key Learnings:
- Every agent operation is instrumented
- Traces show timing and performance data
- You can debug issues by examining traces
- Token usage is tracked for cost monitoring
- Traces are human-readable JSON files

---

## Test 4: Context Management (Sub-conversations)

**Goal:** See sub-conversations in action for large documents.

**What You'll Learn:**
- When sub-conversations are created
- How they help manage large content
- How summaries work

### Steps:

1. **Start a new conversation:**
```bash
uv run python cli.py
```

2. **Request documentation review (triggers large doc read):**
```
You: Review the architecture documentation for FEAT-MS-001 and summarize the key design decisions.
```

3. **Observe:**
   - The agent will list docs, then read them
   - If docs are large enough (>3K tokens), sub-conversations are created
   - You'll see the agent provide a summary
   - The API_SPECIFICATION.md (5,175 tokens) will trigger a sub-conversation

4. **Exit and inspect:**
```
You: exit
```

```bash
cat data/conversations/<conversation-id>.json | python3 -m json.tool | grep -A 5 "sub_conversations"
```

### What to Observe:

1. **In the conversation JSON, look for:**
   - `sub_conversations` array
   - Each sub-conversation has:
     - `id`: Unique identifier
     - `purpose`: Why it was created
     - `summary`: Condensed results
     - `messages`: The full analysis (truncated in main context)

2. **Token management:**
   - Main conversation stays under token limits
   - Large tool results analyzed in isolated sub-conversations
   - Summaries included in main context instead of full content

### Experiment:

**Compare message count:**
```bash
# Count messages in main conversation
python3 -c "
import json
conv = json.load(open('data/conversations/<conversation-id>.json'))
print(f'Main conversation messages: {len(conv[\"messages\"])}')
if conv.get('sub_conversations'):
    for i, sub in enumerate(conv['sub_conversations']):
        print(f'Sub-conversation {i+1}: {len(sub[\"messages\"])} messages')
        print(f'  Purpose: {sub[\"purpose\"]}')
        print(f'  Summary length: {len(sub[\"summary\"])} chars')
"
```

### Key Learnings:
- Sub-conversations keep main context manageable
- Large tool results (docs, analysis) trigger sub-conversations
- Summaries preserve key information while reducing tokens
- This pattern scales to unlimited content

---

## Test 5: File-Based Memory

**Goal:** Test storing and retrieving memories without Docker.

**What You'll Learn:**
- How memory stores past assessments
- How to query memories
- Performance characteristics

### Steps:

1. **Check memory configuration:**
```bash
cat .env | grep MCP_MEMORY_BACKEND
# Should show: MCP_MEMORY_BACKEND=file
# Or be commented out (file is default)
```

2. **Run the agent with memory:**
```bash
uv run python cli.py
```

3. **Make an assessment:**
```
You: Assess FEAT-MS-001 for production readiness.
```

*Note: The current agent implementation doesn't automatically store to memory in the CLI. This tests the memory store capability directly.*

4. **For this test, we'll inspect the memory system:**
```bash
# Check if memory directory exists
ls -la data/memory/

# Memory files are JSON
ls data/memory/*.json 2>/dev/null || echo "No memory files yet"
```

### Understanding Memory:

The memory system stores assessment decisions as Memory objects:
- `feature_id`: Which feature was assessed
- `decision`: ready/not_ready/borderline
- `justification`: Why
- `key_findings`: Important data points
- `timestamp`: When

### Performance Test:

```bash
# If memory files exist, check retrieval speed
python3 -c "
import time
from pathlib import Path
from investigator_agent.memory.file_store import FileMemoryStore

store = FileMemoryStore(Path('data/memory'))
start = time.time()
memories = store.retrieve()
elapsed = (time.time() - start) * 1000

print(f'Retrieved {len(memories)} memories in {elapsed:.2f}ms')
"
```

### Key Learnings:
- File-based memory is simple and fast (<5ms operations)
- No Docker required
- Stores as JSON files in data/memory/
- Good for single-machine deployments
- Easy to inspect and backup

---

## Test 6: Graphiti Memory (Temporal Graph)

**Goal:** Test advanced memory with temporal queries and entity extraction.

**What You'll Learn:**
- How Graphiti builds knowledge graphs
- Entity and relationship extraction
- Temporal queries

### Prerequisites:

```bash
# Requires Docker and OpenAI API key
docker-compose up -d neo4j graphiti-mcp

# Wait for services to be healthy
sleep 10
docker-compose ps

# Set OpenAI key in .env
echo "OPENAI_API_KEY=your-key-here" >> .env
echo "MCP_ENABLED=true" >> .env
echo "MCP_MEMORY_BACKEND=graphiti" >> .env
echo "MCP_GRAPHITI_ENABLED=true" >> .env
```

### Steps:

1. **Test Graphiti connection:**
```bash
# Check Neo4j is running
curl -I http://localhost:7474

# Check Graphiti MCP server
curl http://localhost:8000/health
```

2. **Run agent with Graphiti:**
```bash
uv run python cli.py
```

3. **Make assessments that build entity relationships:**
```
You: Assess FEAT-MS-001 for production readiness.
(wait for response)

You: Assess FEAT-QR-002. Are there any similarities to FEAT-MS-001?
(wait for response)

You: exit
```

4. **View the knowledge graph:**
```bash
# Open Neo4j browser
open http://localhost:7474

# Or query via CLI
docker exec -it module8-neo4j-1 cypher-shell -u neo4j -p password123 \
  "MATCH (n) RETURN n LIMIT 25;"
```

### What to Observe:

1. **Entities extracted:**
   - Features (FEAT-MS-001, FEAT-QR-002)
   - Components (authentication, QR scanner)
   - Quality metrics (test coverage, UAT status)

2. **Relationships:**
   - FEAT-MS-001 `ASSESSED_AS` ready
   - FEAT-QR-002 `HAS_ISSUE` test failures
   - Features `SIMILAR_TO` each other

3. **Temporal queries:**
   - "What was assessed recently?"
   - "What changed between assessments?"
   - "What issues were found over time?"

### Advanced Graphiti Features:

```bash
# Query for features assessed as "ready"
# (Via Graphiti MCP tools if integrated)

# Query for temporal patterns
# "Show me features assessed in the last week"

# Entity extraction
# Graphiti automatically extracts entities from conversations
```

### Key Learnings:
- Graphiti builds structured knowledge from conversations
- Enables temporal and relational queries
- Requires OpenAI for entity extraction
- More complex setup but more powerful queries
- Good for tracking changes over time

---

## Test 7: Evaluation System

**Goal:** Understand how agent quality is measured.

**What You'll Learn:**
- Automated testing of agent behavior
- How evaluations score decisions
- Regression tracking

### Steps:

1. **Check evaluation scenarios:**
```bash
cat src/investigator_agent/evaluations/scenarios.py | less
```

Notice the structure:
- `id`: Scenario identifier
- `query`: User question
- `expected_decision`: What agent should decide
- `expected_tools`: Tools it should use

2. **Run evaluation suite:**
```bash
# Run all evaluations
PYTHONPATH=. uv run python -c "
import asyncio
from pathlib import Path
from investigator_agent import Agent, Config
from investigator_agent.providers.anthropic import AnthropicProvider
from investigator_agent.persistence.store import ConversationStore
from investigator_agent.tools.registry import ToolRegistry
from investigator_agent.tools.jira import get_jira_data
from investigator_agent.tools.analysis import get_analysis
from investigator_agent.evaluations.evaluator import InvestigatorEvaluator
from investigator_agent.evaluations.scenarios import EVALUATION_SCENARIOS

async def run_eval():
    config = Config()
    provider = AnthropicProvider(config.api_key, config.model)
    store = ConversationStore(Path('./data/eval_conversations'))

    registry = ToolRegistry()
    registry.register('get_jira_data', 'Get JIRA data',
                     {'type': 'object', 'properties': {'feature_id': {'type': 'string'}}},
                     get_jira_data)
    registry.register('get_analysis', 'Get analysis',
                     {'type': 'object', 'properties': {'feature_id': {'type': 'string'}}},
                     get_analysis)

    agent = Agent(provider, store, config, tool_registry=registry)
    evaluator = InvestigatorEvaluator(pass_threshold=0.7)

    # Run first 4 scenarios (faster)
    results = await evaluator.run_suite(agent, EVALUATION_SCENARIOS[:4])

    print(f'\nOverall Performance:')
    print(f'  Pass Rate: {results.pass_rate:.1%}')
    print(f'  Avg Overall Score: {results.avg_scores[\"overall\"]:.2f}')
    print(f'  Duration: {results.duration:.1f}s')

    for result in results.scenario_results:
        status = '✅' if result.passed else '❌'
        print(f'\n{status} {result.scenario_id}: {result.scores[\"overall\"]:.2f}')

asyncio.run(run_eval())
"
```

### What to Observe:

**Console output shows:**
- Each scenario being tested
- Pass/fail status
- Scores for different metrics:
  - `feature_identification`: Did it find the right feature?
  - `tool_usage`: Did it use the right tools?
  - `decision_quality`: Did it make the right decision?
  - `overall`: Composite score

### Understanding the Scoring:

**Metrics (0-1.0 scale):**
- **Feature ID**: 1.0 if correct feature mentioned, 0.0 if not
- **Tool Usage** (F1 score):
  - 1.0 if used exactly expected tools
  - 0.5-0.9 if used some expected tools
  - 0.0 if used wrong tools
- **Decision Quality**: 1.0 if correct decision, 0.0 if wrong
- **Overall**: Weighted average of all metrics

**Pass Threshold:**
- Overall score ≥ 0.7 (70%) required to pass

### Key Learnings:
- Automated evaluation validates agent behavior
- Multiple dimensions are scored
- Regression tracking prevents quality degradation
- Evaluation is essential for production agents

---

## Test 8: Multi-Feature Workflow

**Goal:** Experience a realistic end-to-end workflow.

**What You'll Learn:**
- How all components work together
- Real-world usage patterns
- Performance characteristics

### Steps:

1. **Start a fresh conversation:**
```bash
uv run python cli.py
```

2. **Have a realistic multi-feature conversation:**

```
You: Hi! I need to assess several features for our upcoming release.

You: First, can you check FEAT-MS-001 - is it ready for production?
(observe response)

You: What about FEAT-QR-002?
(observe response)

You: Can you compare these two features and tell me which poses more risk?
(observe how agent uses prior context)

You: Finally, check FEAT-RS-003 and give me a summary of all three assessments.
(observe multi-feature summary)

You: Thank you!
You: exit
```

### Comprehensive Analysis:

After the conversation, examine all components:

1. **Conversation:**
```bash
cat data/conversations/<conversation-id>.json | python3 -m json.tool | less
```

Look for:
- Multiple feature assessments
- Tool usage across all features
- Sub-conversations if docs were read
- Context building across queries

2. **Traces:**
```bash
ls -t data/traces/*.json | head -1 | xargs cat | python3 -m json.tool | less
```

Count operations:
```bash
python3 -c "
import json
from pathlib import Path

trace_file = sorted(Path('data/traces').glob('*.json'), key=lambda p: p.stat().st_mtime)[-1]
spans = json.load(open(trace_file))

tool_calls = sum(1 for s in spans if 'tool' in s.get('name', '').lower())
api_calls = sum(1 for s in spans if 'anthropic' in s.get('name', '').lower())
duration = sum(s.get('duration_ms', 0) for s in spans) / 1000

print(f'Tool executions: {tool_calls}')
print(f'API calls: {api_calls}')
print(f'Total duration: {duration:.1f}s')
"
```

3. **Performance metrics:**
```bash
# Token usage across conversation
python3 -c "
import json
from pathlib import Path

trace_file = sorted(Path('data/traces').glob('*.json'), key=lambda p: p.stat().st_mtime)[-1]
spans = json.load(open(trace_file))

total_input = sum(s.get('attributes', {}).get('input_tokens', 0) for s in spans)
total_output = sum(s.get('attributes', {}).get('output_tokens', 0) for s in spans)

print(f'Input tokens: {total_input:,}')
print(f'Output tokens: {total_output:,}')
print(f'Total tokens: {total_input + total_output:,}')
print(f'Estimated cost (Claude Sonnet): ${(total_input * 0.003 + total_output * 0.015) / 1000:.4f}')
"
```

### Key Learnings:
- Agent handles multi-feature workflows naturally
- Context builds across queries
- Tool usage adapts to needs
- Performance scales with conversation length
- Full observability from start to finish

---

## Summary: Key Concepts Demonstrated

After completing these tests, you should understand:

### 1. **Context Engineering**
- How sub-conversations manage large content
- Token limits and truncation strategies
- When to create sub-conversations

### 2. **Sub-Conversation Patterns**
- Automatically triggered for large tool results
- Summaries preserve key information
- Scales to unlimited content

### 3. **Information Synthesis**
- Agent combines multiple data sources (JIRA + analysis + docs)
- Makes decisions based on synthesized information
- Provides justifications

### 4. **Memory Integration**
- File-based: Simple, fast, no Docker
- Graphiti: Temporal graph, entity extraction, requires Docker + OpenAI
- Trade-offs between simplicity and query power

### 5. **Comprehensive Evaluation**
- Automated quality measurement
- Multiple scoring dimensions
- Regression tracking

### 6. **Real-world Agent Design**
- Tool orchestration
- Error handling
- Observability
- Production-ready patterns

---

## Reflection Questions

As you work through the tests, consider these questions:

### Context Engineering
1. **When did sub-conversations get created?** What was the token threshold?
2. **How much information was lost in summaries?** Could you still make decisions?
3. **What would happen with even larger documents?**

### Sub-Conversation Patterns
1. **What's the right granularity?** One per tool result? One per feature?
2. **How do you decide when to use sub-conversations vs direct context?**
3. **What patterns from this apply to your domain?**

### Information Synthesis
1. **How did the agent combine JIRA + analysis + docs?**
2. **What's the difference between having all context vs summarized context?**
3. **When is "good enough" actually good enough?**

### Memory Systems
1. **When is file-based memory sufficient?**
2. **When do you need Graphiti's temporal/relational queries?**
3. **What's the overhead cost vs benefit trade-off?**

### Evaluation
1. **What does "good enough" mean for your use case?**
2. **How would you define pass criteria for your domain?**
3. **What metrics matter most?**

### Production Readiness
1. **What would you need to deploy this?**
2. **How would you monitor it in production?**
3. **What failure modes concern you most?**

---

## Next Steps

After completing this manual test plan:

1. **Experiment with modifications:**
   - Change memory backends (file vs Graphiti)
   - Try different features
   - Add custom tools

2. **Read the code:**
```bash
# Core agent logic
cat src/investigator_agent/agent.py

# Sub-conversation manager
cat src/investigator_agent/context/subconversation.py

# Memory stores
cat src/investigator_agent/memory/file_store.py
cat src/investigator_agent/memory/mcp_store.py

# Evaluation system
cat src/investigator_agent/evaluations/evaluator.py
```

3. **Review architecture:**
```bash
cat docs/INTEGRATE.md
cat docs/EXERCISE.md
```

4. **Apply to your domain:**
   - What features would you assess?
   - What tools would you need?
   - What memory strategy fits your needs?

---

## Troubleshooting

**If something doesn't work:**

1. **Check your environment:**
```bash
which python
python --version
cat .env | grep ANTHROPIC_API_KEY
```

2. **Verify installation:**
```bash
uv sync
uv run python -c "import investigator_agent; print('OK')"
```

3. **Check Docker (if using Graphiti):**
```bash
docker-compose ps
docker-compose logs graphiti-mcp
```

4. **Run unit tests:**
```bash
uv run pytest tests/ -v
```

5. **Check data directories:**
```bash
ls -la data/conversations/
ls -la data/traces/
ls -la data/memory/
```

---

**Happy Testing!**

This manual test plan gives you hands-on experience with the Investigator Agent. Take your time with each test and explore freely!
