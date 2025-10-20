# Detective Agent - Manual Test Plan

This comprehensive test plan will guide you through testing the Detective Agent to understand how each component works. Each test includes what to do, what to observe, and what you'll learn.

## Prerequisites

1. Ensure you have your environment set up:
```bash
cd /Users/richarddrew/working/assitant-to-agentic/practice-files/assisted-ai-practice/module7
source .venv/bin/activate
```

2. Verify your API key is configured:
```bash
echo $ANTHROPIC_API_KEY
```

3. Clear any previous test data (optional):
```bash
rm -rf data/conversations/*
rm -rf data/traces/*
```

---

## Test 1: Basic Conversation Flow

**Goal:** Understand the core conversation loop and message persistence.

**What You'll Learn:**
- How the agent maintains conversation history
- How messages are structured
- How conversations are persisted to disk

### Steps:

1. **Start a new conversation:**
```bash
uv run python cli.py
```

2. **Have a simple conversation:**
```
You: Hello! What are you designed to do?
```

3. **Continue the conversation:**
```
You: Can you explain how you assess release risk?
```

4. **Exit gracefully:**
```
You: exit
```

### What to Observe:

1. **In the terminal:**
   - Note the conversation ID that's created
   - Observe the agent's responses
   - See how it introduces itself and explains its purpose

2. **In the filesystem:**
```bash
# List your conversations
ls -la data/conversations/

# View the conversation JSON (replace <id> with your conversation ID)
cat data/conversations/<conversation-id>.json | uv run python -m json.tool
```

3. **What to look for in the JSON:**
   - `conversation_id`: Unique identifier
   - `trace_id`: Links to observability traces
   - `messages`: Array of user and assistant messages
   - `created_at`, `updated_at`: Timestamps
   - Message structure: `role`, `content`, `timestamp`

### Key Learnings:
- Each conversation has a unique ID
- Messages alternate between user and assistant
- Entire conversation history is preserved
- Each conversation is linked to a trace for observability

---

## Test 2: Continuing Conversations

**Goal:** Understand conversation persistence and loading.

**What You'll Learn:**
- How to resume conversations
- How context is maintained across sessions

### Steps:

1. **List your conversations:**
```bash
uv run python cli.py list
```

2. **Continue the conversation from Test 1 (you can use just the first 8 characters):**
```bash
uv run python cli.py continue <conversation-id>
```

3. **Reference earlier context:**
```
You: Based on what you told me about your purpose, what severity levels do you use?
```

4. **Exit:**
```
You: exit
```

### What to Observe:

1. **The agent should remember your previous conversation**
2. **Check the updated conversation file:**
```bash
cat data/conversations/<conversation-id>.json | uv run python -m json.tool
```

3. **Notice:**
   - New messages appended to the same file
   - `updated_at` timestamp changed
   - `created_at` timestamp unchanged
   - All previous messages still present

### Key Learnings:
- Conversations persist across CLI sessions
- Agent has full access to conversation history
- You can pause and resume conversations anytime

---

## Test 3: Observability (Traces and Spans)

**Goal:** Understand how OpenTelemetry captures agent operations and session-based tracing.

**What You'll Learn:**
- What traces, spans, and sessions are
- How session-based tracing works across multiple CLI invocations
- How to view all traces for a conversation
- What information is captured for debugging

### Steps:

1. **Start a new conversation:**
```bash
uv run python cli.py
```

2. **Send one message:**
```
You: Explain observability to me briefly.
```

3. **Exit and view all traces for the conversation:**
```bash
# Use the new trace command (supports partial IDs)
uv run python cli.py trace <conversation-id>
```

Note: With the new session-based tracing, each CLI session creates a separate trace file, but all traces for a conversation share the same `session.id` (the conversation ID). The trace command finds all trace files for that conversation.

4. **Test multi-session tracing (continue the conversation):**
```bash
uv run python cli.py continue <conversation-id>
```

Send another message, exit, and run the trace command again. You should now see **two trace files** for the same conversation.

### What to Observe in the Trace:

1. **Multiple trace files per conversation:**
   - Each CLI session creates a new trace file with a unique `trace_id`
   - All traces share the same `session.id` (the conversation ID)
   - This follows OpenTelemetry best practices for long-lived sessions

2. **Look for different span types:**
   - `new_conversation`: Agent initialization (first session only)
   - `send_message`: Each message you send
   - `anthropic_api_call`: Calls to Claude API

3. **For each span, note:**
   - `name`: Operation name
   - `start_time`, `end_time`: Timing information
   - `duration_ns`: How long it took (in nanoseconds)
   - `attributes`: Metadata about the operation

4. **Look for these attributes:**
   - `session.id`: The conversation ID (links all traces together)
   - `model`: Which Claude model was used
   - `input_tokens`: Tokens sent to the API
   - `output_tokens`: Tokens in the response
   - `message_count`: Number of messages in context

### Key Learnings:
- Every agent operation is instrumented
- Multiple CLI sessions = multiple trace files (linked by session.id)
- Session-based tracing follows OpenTelemetry best practices
- Traces show timing and performance data
- You can debug issues by examining traces
- Token usage is tracked for cost monitoring
- Traces are human-readable JSON files
- Use `uv run python cli.py trace <id>` to view all traces for a conversation

---

## Test 4: Context Window Management

**Goal:** See truncation in action when conversation history grows.

**What You'll Learn:**
- How the agent manages limited context windows
- Which messages are kept vs. discarded
- How to verify truncation occurred

### Steps:

1. **Start a new conversation:**
```bash
uv run python cli.py
```

2. **Send 10 short messages** (one at a time):
```
You: Message 1
You: Message 2
You: Message 3
You: Message 4
You: Message 5
You: Message 6
You: Message 7
You: Message 8
You: Message 9
You: Message 10
```

3. **Exit and examine:**
```bash
cat data/conversations/<conversation-id>.json | uv run python -m json.tool
```

### What to Observe:

1. **Count the messages:**
   - You sent 10 user messages
   - Agent sent ~10 assistant messages
   - Total: ~20 messages in conversation JSON

2. **Check the trace for truncation using the trace command:**
```bash
uv run python cli.py trace <conversation-id> | grep "context\."
```

Or view all traces with context details:
```bash
uv run python cli.py trace <conversation-id> | grep -A 3 "was_truncated"
```

3. **Look for these attributes in the trace output:**
   - `context.was_truncated`: `true` (should happen after 6 messages)
   - `context.messages_dropped`: How many messages were removed
   - `context.total_messages`: Total in conversation

**Example output (from a conversation with 10 exchanges):**
```
"context.total_messages": 3,
"context.was_truncated": false,
--
"context.total_messages": 7,
"context.was_truncated": true,
"context.messages_dropped": 1,
--
"context.total_messages": 17,
"context.was_truncated": true,
"context.messages_dropped": 11,
```

**What this means:**

- **Early messages (1-3):** No truncation - under the 6 message limit
- **Message 4:** First truncation - 7 total messages, dropped 1, kept 6
- **Message 9:** Heavy truncation - 17 total messages, dropped 11, kept 6

Note: The context window is set to max 6 messages (configurable via MAX_MESSAGES). You'll see `was_truncated: false` for the first few exchanges, then `true` as the conversation grows.

### Experiment:

**Test that the agent can't remember early messages:**

1. **Continue the conversation:**

```bash
uv run python cli.py continue <conversation-id>
```

2. **Ask about early message content:**

```
You: What was message 1 about?
```

Or ask a specific factual question about an early message:

```
You: What number did I mention in my first message?
```

3. **Expected behavior:**

- The agent should either say it doesn't have that information, OR
- Give an incorrect/generic answer (if hallucinating)
- It will NOT accurately recall the specific early message content

4. **Test with recent message (should work):**

```
You: What number did I just mention?
```

- The agent SHOULD be able to answer this correctly since recent messages are in the context window

**Note:** The Detective Agent's system prompt focuses on release assessment, so it may give role-specific responses. For clearer testing of context limits, use specific factual questions rather than generic meta-questions like "what did I say?"

### Key Learnings:
- Context window has limits (6 messages in this implementation)
- Old messages are automatically truncated
- System prompt is always preserved
- Recent messages are kept for coherence
- Truncation is tracked in observability

---

## Test 5: Retry Mechanism

**Goal:** Understand how the agent handles API failures.

**What You'll Learn:**
- How retries work with exponential backoff
- Which errors are retried vs. fail fast
- How to observe retries in traces

### Steps:

**Note:** This test requires simulating failures. We'll use the test suite to demonstrate retry behavior.

1. **Review the retry configuration:**
```bash
cat src/detective_agent/config.py | grep -A 10 "class RetryConfig"
```

2. **Run the retry tests to see behavior:**
```bash
uv run pytest tests/retry_test.py -v
```

3. **Observe the test output:**

The tests verify retry behavior programmatically. You'll see tests like:
   - `test_retryable_error_triggers_retry`: Verifies 429 errors are retried
   - `test_exponential_backoff`: Validates exponential delay growth
   - `test_non_retryable_error_fails_fast`: Confirms 401 fails immediately
   - `test_max_retries_exhausted`: Checks giving up after max attempts

All tests should pass, confirming the retry mechanism works correctly.

**To see the retry logic implementation:**
```bash
cat src/detective_agent/retry/strategy.py
```

This shows the `with_retry` decorator and `is_retryable_error` function that implement the retry behavior.

### Understanding Retry Behavior:

**Retryable errors (will retry):**
- 429 (Rate Limit)
- 500, 502, 503 (Server Errors)
- Network timeouts

**Non-retryable errors (fail fast):**
- 401 (Authentication)
- 400 (Bad Request)
- 404 (Not Found)

**Retry strategy:**
- Base delay: 1 second
- Exponential backoff: delay = base * (2 ^ attempt)
- Jitter: Random variation ±25% to prevent thundering herd
- Max attempts: 3 by default

### Manual Test (Optional):

**If you want to see real retries, you can temporarily cause rate limits:**

1. **Send many requests quickly:**
```bash
for i in {1..10}; do
  echo "Test message $i" | uv run python cli.py &
done
wait
```

2. **Check traces for retry spans:**
```bash
grep -r "retry_attempt" data/traces/*.json
```

### Key Learnings:
- Not all errors should be retried
- Exponential backoff prevents overwhelming the API
- Jitter prevents synchronized retries
- Retry attempts are visible in traces
- Configuration is tunable for different needs

---

## Test 6: System Prompt Engineering

**Goal:** Understand how the system prompt shapes agent behavior.

**What You'll Learn:**
- What the system prompt contains
- How it affects agent responses
- How to customize it

### Steps:

1. **View the default system prompt:**
```bash
cat src/detective_agent/system_prompt.py
```

2. **Test default behavior:**
```bash
uv run python cli.py
```

```
You: What is your role?
You: What severity levels do you use?
You: exit
```

3. **Create a custom system prompt:**
```bash
export SYSTEM_PROMPT="You are a friendly coding assistant who loves emojis and speaks casually. Always be enthusiastic!"
```

4. **Test custom behavior:**
```bash
uv run python cli.py
```

```
You: What is your role?
You: exit
```

5. **Unset custom prompt:**
```bash
unset SYSTEM_PROMPT
```

### What to Observe:

**Default system prompt includes:**
- Agent identity (Detective Agent)
- Purpose (Release Confidence System)
- Severity levels (HIGH, MEDIUM, LOW)
- Risk assessment criteria
- Tool usage instructions

**With custom prompt:**
- Different personality
- Different response style
- Different domain expertise

### Key Learnings:
- System prompt defines agent personality and capabilities
- Easily configurable via environment variable
- Critical for setting agent behavior
- Should include tool usage instructions
- Shapes every response the agent gives

---

## Test 7: Tool Usage (The Agentic Loop)

**Goal:** See the agent use tools to accomplish tasks.

**What You'll Learn:**
- How the agentic tool loop works
- How tools are called and results processed
- How multi-step reasoning happens

### Steps:

1. **Start a new conversation:**
```bash
uv run python cli.py
```

2. **Request a release assessment:**
```
You: Please assess the risk for release v2.5.0
```

### What to Observe in Real-Time:

The agent should:
1. **First tool call:** Call `get_release_summary` to fetch release data
2. **Process the data:** Analyze tests, metrics, changes
3. **Second tool call:** Call `file_risk_report` with severity and findings
4. **Final response:** Confirm the assessment was filed

**Watch for:**
- "Calling tool: get_release_summary..."
- The agent processing the response
- "Calling tool: file_risk_report..."
- Multi-turn reasoning

### Detailed Examination:

1. **Exit and view the conversation:**
```bash
cat data/conversations/<conversation-id>.json | uv run python -m json.tool
```

2. **Look for tool-related content blocks:**

**Tool use block:**
```json
{
  "type": "tool_use",
  "id": "toolu_...",
  "name": "get_release_summary",
  "input": {
    "release_id": "v2.5.0"
  }
}
```

**Tool result block:**
```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_...",
  "content": "{ ... release data ... }"
}
```

3. **Examine the trace:**
```bash
cat data/traces/<trace-id>.json | uv run python -m json.tool | grep -A 10 "execute_tool"
```

### Experiment:

**Try different release scenarios:**

```
You: Assess release v1.0.0  # Should be low risk
You: Assess release v3.0.0  # Should be high risk (if exists in mock data)
```

### Key Learnings:
- Agent decides which tools to call
- Tools are called in sequence (not all at once)
- Tool results influence next decisions
- Agent can call multiple tools per task
- Tool loop continues until task is complete
- All tool calls are preserved in history

---

## Test 8: Complete Release Assessment Workflow

**Goal:** Experience the full end-to-end workflow the agent was designed for.

**What You'll Learn:**
- How all components work together
- Real-world usage pattern
- Complete observability from start to finish

### Steps:

1. **Start a fresh conversation:**
```bash
uv run python cli.py
```

2. **Have a realistic conversation:**

```
You: Hi! I need your help assessing a release.
You: I want to assess release v2.5.0. Can you help?
You: What were the key risk factors you identified?
You: Would you recommend this release go to production?
You: Thank you!
You: exit
```

### Comprehensive Analysis:

After the conversation, examine every component:

1. **Conversation persistence:**
```bash
cat data/conversations/<conversation-id>.json | uv run python -m json.tool | less
```

2. **Trace analysis (view all traces for the conversation):**
```bash
uv run python cli.py trace <conversation-id> | less
```

3. **Count the operations across all traces:**
```bash
# Count API calls across all traces for this conversation
uv run python cli.py trace <conversation-id> 2>&1 | grep '"name".*anthropic' | wc -l

# Count tool execution spans across all traces
uv run python cli.py trace <conversation-id> 2>&1 | grep '"name".*execute_tools' | wc -l
```

### Key Learnings:
- All components work together seamlessly
- Full observability from start to finish
- Conversation is natural and coherent
- Tools enable real capabilities
- System is production-ready

---

## Test 9: Evaluation System

**Goal:** Understand how agent quality is measured.

**What You'll Learn:**
- Automated testing of agent behavior
- How evaluations score agent decisions
- Regression tracking over time

### Steps:

1. **Run the evaluation suite:**
```bash
PYTHONPATH=. uv run python examples/run_evaluation.py
```

### What to Observe:

**Console output shows:**
- Each test scenario being run
- Pass/fail status
- Scores for tool usage and decision quality
- Overall summary statistics

2. **Examine a scenario:**
```bash
cat evals/scenarios.py | grep -A 30 "HIGH_RISK_SCENARIO"
```

**Note the structure:**
- `id`: Scenario identifier
- `description`: What's being tested
- `user_message`: Input to agent
- `mock_data`: Simulated tool response
- `expected_behavior`: What the agent should do

3. **Check evaluation results:**
```bash
cat eval_results.json | uv run python -m json.tool
```

**Look for:**
- `overall_score`: Composite score (0-1.0)
- `pass_rate`: Percentage of scenarios passed
- `scenarios`: Individual results

### Understanding the Scoring:

**Tool Usage Scoring (0-1.0):**
- 1.0: Called all expected tools
- 0.5: Called some expected tools
- 0.0: Called wrong tools or none

**Decision Quality Scoring (0-1.0):**
- 1.0: Correct severity assessment
- 0.0: Incorrect severity assessment

**Pass Threshold:**
- Overall score ≥ 0.7 (70%)

### Key Learnings:
- Automated evaluation validates agent behavior
- Multiple dimensions are scored (tools + decisions)
- Regression tracking prevents quality degradation
- Evaluation is essential for production agents
- Results are machine-readable for CI/CD

---

## Test 10: Exploring the Codebase

**Goal:** Understand the implementation by reading key files.

### Recommended Reading Order:

1. **Start with data models:**
```bash
cat src/detective_agent/models.py
cat src/detective_agent/config.py
```

2. **Provider abstraction:**
```bash
cat src/detective_agent/providers/base.py
cat src/detective_agent/providers/anthropic.py
```

3. **Core agent logic:**
```bash
cat src/detective_agent/agent.py
```

4. **Tool system:**
```bash
cat src/detective_agent/tools/registry.py
cat src/detective_agent/tools/release_tools.py
```

5. **Observability:**
```bash
cat src/detective_agent/observability/tracer.py
cat src/detective_agent/observability/exporter.py
```

6. **Supporting systems:**
```bash
cat src/detective_agent/context/manager.py
cat src/detective_agent/config.py  # Contains RetryConfig
cat src/detective_agent/persistence/store.py
```

### Questions to Answer While Reading:

- How are messages structured?
- How does the provider abstraction work?
- Where is the tool loop implemented?
- How are traces generated and exported?
- How does context truncation work?
- How are retries handled?

---

## Summary: Key Concepts Demonstrated

After completing these tests, you should understand:

### 1. **Conversation Management**
- Message structure and persistence
- Loading and continuing conversations
- Context history maintenance

### 2. **Provider Abstraction**
- How to separate LLM logic from implementation
- Supporting multiple providers
- API call handling

### 3. **Observability**
- Traces and spans
- Operation timing
- Token usage tracking
- Debugging with traces

### 4. **Context Window Management**
- Token limits
- Message truncation
- Preserving important context

### 5. **Retry Mechanisms**
- Error classification
- Exponential backoff
- Jitter for load distribution

### 6. **System Prompt Engineering**
- Defining agent behavior
- Tool usage instructions
- Customization

### 7. **Tool Abstraction**
- Tool registration
- Tool loop execution
- Multi-turn reasoning
- Agentic behavior

### 8. **Evaluation**
- Automated quality assessment
- Regression tracking
- Production readiness validation

### 9. **Error Handling**
- Graceful degradation
- User-friendly messages
- Avoiding hallucinations

### 10. **Production Readiness**
- Full observability
- Robust error handling
- Configurable behavior
- Comprehensive testing

---

## Next Steps

After completing this manual test plan:

1. **Experiment with modifications:**
   - Change the system prompt
   - Adjust context window size
   - Add new tools
   - Modify retry configuration

2. **Read the code:**
   - Follow the execution flow
   - Understand design patterns
   - See how components interact

3. **Review the architecture:**
```bash
cat docs/DESIGN.md
cat docs/API.md
```

4. **Try building your own agent:**
   - Start with a different use case
   - Reuse the framework components
   - Apply the patterns you learned

---

## Troubleshooting

**If something doesn't work:**

1. **Check your environment:**
```bash
which python
python --version
echo $ANTHROPIC_API_KEY
```

2. **Review logs:**
```bash
# Most recent conversation
ls -lt data/conversations/ | head -5

# Most recent trace
ls -lt data/traces/ | head -5
```

3. **Run tests to verify setup:**
```bash
uv run pytest tests/test_agent.py -v
```

---

**Happy Testing!**

This manual test plan should give you a comprehensive understanding of how agentic systems work. Take your time with each test and experiment freely!
