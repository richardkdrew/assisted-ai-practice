# AI Agent Discovery Questionnaire

**Purpose:** Gather all necessary information to build a custom AI agent
**Format:** Structured checklist - user fills out, AI assistant reads
**Estimated time:** 15-30 minutes

---

## Instructions

Please answer all questions as completely as possible. The more detail you provide, the better the agent will meet your needs.

**Legend:**
- ✅ = Required (must answer)
- 💡 = Optional (helpful but not essential)
- 📝 = Provide examples when possible

---

## Section 1: Agent Identity

### 1.1 Agent Name ✅
**What should the agent be called?**

```
Agent Name: ___________________________

Example: "Detective Agent", "SupportBot", "CodeReviewer"
```

### 1.2 Agent Purpose ✅ 📝
**What is the agent's primary purpose? What problem does it solve?**

```
Purpose:
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________

Example: "Assess software release risk by analyzing test results,
deployment metrics, and code changes to identify potential issues
before production deployment."
```

### 1.3 Target Users ✅
**Who will use this agent?**

```
Primary Users: ___________________________

Example: "DevOps engineers, Release managers, QA teams"
```

---

## Section 2: Domain and Context

### 2.1 Domain ✅
**What domain does the agent operate in?**

```
Domain: ___________________________

Examples: "DevOps", "Customer Support", "Healthcare", "Finance",
"Education", "E-commerce"
```

### 2.2 Domain Knowledge 💡
**What domain-specific knowledge should the agent have?**

```
Key Concepts:
- _____________________________________________
- _____________________________________________
- _____________________________________________

Example for Release Agent:
- Understanding of CI/CD pipelines
- Test coverage and failure interpretation
- Deployment metrics (error rates, latency)
- Impact assessment for code changes
```

### 2.3 Constraints and Limitations ✅
**What should the agent NOT do? Any boundaries?**

```
Constraints:
- _____________________________________________
- _____________________________________________
- _____________________________________________

Example:
- Cannot deploy releases automatically
- Cannot modify code
- Must escalate to humans for critical decisions
```

---

## Section 3: Tools and Capabilities

### 3.1 Required Tools ✅ 📝
**What actions/capabilities must the agent have?**

For each tool, provide:
- Tool name
- Purpose
- Type (GET data, POST/submit data, other action)
- Required inputs
- Expected outputs

```
Tool 1:
  Name: ___________________________
  Purpose: ___________________________
  Type: [ ] GET  [ ] POST  [ ] Other: _______
  Inputs:
    - _____________________________________________
    - _____________________________________________
  Outputs:
    - _____________________________________________

Tool 2:
  Name: ___________________________
  Purpose: ___________________________
  Type: [ ] GET  [ ] POST  [ ] Other: _______
  Inputs:
    - _____________________________________________
  Outputs:
    - _____________________________________________

Tool 3:
  Name: ___________________________
  Purpose: ___________________________
  Type: [ ] GET  [ ] POST  [ ] Other: _______
  Inputs:
    - _____________________________________________
  Outputs:
    - _____________________________________________

[ ] Add more tools (copy format above)
```

**Example:**
```
Tool 1:
  Name: get_release_summary
  Purpose: Fetch release metadata for analysis
  Type: [✓] GET  [ ] POST  [ ] Other
  Inputs:
    - release_id (string): Unique identifier
  Outputs:
    - version, changes, test results, deployment metrics

Tool 2:
  Name: file_risk_report
  Purpose: Submit risk assessment findings
  Type: [ ] GET  [✓] POST  [ ] Other
  Inputs:
    - release_id (string)
    - severity (string): HIGH/MEDIUM/LOW
    - findings (list): Identified risks
  Outputs:
    - report_id, status, location
```

### 3.2 Data Sources ✅
**Where does the agent get its data?**

```
[ ] Mock/Static data (for testing)
[ ] REST APIs (specify endpoints)
[ ] Databases (specify type)
[ ] Files/Documents
[ ] Real-time streams
[ ] Other: ___________________________

Details:
_____________________________________________________________
_____________________________________________________________
```

### 3.3 Tool Dependencies 💡
**Do tools need to be called in a specific order?**

```
[ ] No specific order
[ ] Yes, specific sequence required

If yes, describe:
_____________________________________________________________
_____________________________________________________________

Example: "Must call get_release_summary BEFORE file_risk_report"
```

---

## Section 4: Decision Making and Classification

### 4.1 Classification System ✅ 📝
**How does the agent categorize or classify things?**

```
Classification Type: ___________________________

Levels/Categories:
  Level 1: __________ - Criteria: ___________________________
  Level 2: __________ - Criteria: ___________________________
  Level 3: __________ - Criteria: ___________________________
  [ ] Add more levels

Example for Release Risk:
  HIGH: >5% error rate, critical test failures, high-risk changes
  MEDIUM: 2-5% error rate, minor test failures, moderate changes
  LOW: <2% error rate, all tests passing, low-impact changes
```

### 4.2 Decision Criteria ✅
**What factors should the agent consider when making decisions?**

```
Key Factors:
1. _____________________________________________ (Weight: High/Med/Low)
2. _____________________________________________ (Weight: High/Med/Low)
3. _____________________________________________ (Weight: High/Med/Low)
4. _____________________________________________ (Weight: High/Med/Low)

Example:
1. Test failure rate (Weight: High)
2. Error rate in production metrics (Weight: High)
3. Scope of code changes (Weight: Medium)
4. Historical release success (Weight: Low)
```

### 4.3 Edge Cases ✅ 📝
**What unusual situations might the agent encounter?**

```
Edge Case 1: ___________________________
  How to handle: ___________________________

Edge Case 2: ___________________________
  How to handle: ___________________________

Edge Case 3: ___________________________
  How to handle: ___________________________

Example:
Edge Case 1: Missing test data
  How to handle: Treat as HIGH risk (cautious approach)

Edge Case 2: Conflicting signals (tests pass but high error rate)
  How to handle: Prioritize production metrics over tests
```

---

## Section 5: Agent Personality and Behavior

### 5.1 Tone and Style ✅
**How should the agent communicate?**

```
Select all that apply:
[ ] Professional
[ ] Casual/Friendly
[ ] Technical/Precise
[ ] Empathetic
[ ] Concise
[ ] Detailed/Explanatory
[ ] Other: ___________________________
```

### 5.2 Response Format 💡
**Any specific format for responses?**

```
[ ] Plain text explanations
[ ] Structured/bulleted lists
[ ] JSON/Data format
[ ] Markdown formatting
[ ] Tables or charts
[ ] Other: ___________________________
```

### 5.3 Personality Traits 💡
**What personality should the agent have?**

```
Adjectives (pick 3-5):
[ ] Helpful      [ ] Cautious     [ ] Proactive    [ ] Analytical
[ ] Direct       [ ] Patient      [ ] Thorough     [ ] Efficient
[ ] Transparent  [ ] Confident    [ ] Humble       [ ] Curious

Other traits:
_____________________________________________________________
```

---

## Section 6: Success Criteria and Evaluation

### 6.1 Success Definition ✅
**How do you know the agent is working correctly?**

```
Success means:
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

Example:
1. Correctly identifies high-risk releases (>90% accuracy)
2. Provides actionable findings
3. Doesn't miss critical issues
```

### 6.2 Test Scenarios ✅ 📝
**Describe 3-5 test scenarios the agent should handle correctly**

```
Scenario 1: [Typical/Happy Path]
  Input: ___________________________
  Expected Behavior: ___________________________
  Expected Output/Classification: ___________________________

Scenario 2: [Edge Case]
  Input: ___________________________
  Expected Behavior: ___________________________
  Expected Output/Classification: ___________________________

Scenario 3: [Error/Failure Case]
  Input: ___________________________
  Expected Behavior: ___________________________
  Expected Output/Classification: ___________________________

Scenario 4: [Complex Case]
  Input: ___________________________
  Expected Behavior: ___________________________
  Expected Output/Classification: ___________________________

Scenario 5: [Your Choice]
  Input: ___________________________
  Expected Behavior: ___________________________
  Expected Output/Classification: ___________________________
```

**Example:**
```
Scenario 1: [Low Risk Release]
  Input: All tests passing, 0.5% error rate, minor UI changes
  Expected Behavior: Call get_release_summary, analyze data, call file_risk_report
  Expected Output: LOW severity with positive findings

Scenario 2: [Missing Data]
  Input: Release with no test results available
  Expected Behavior: Acknowledge missing data, be cautious
  Expected Output: HIGH severity due to uncertainty

Scenario 3: [High Risk Release]
  Input: 15 test failures, 8% error rate, authentication changes
  Expected Behavior: Identify critical risks, recommend delay
  Expected Output: HIGH severity with specific risk findings
```

### 6.3 Failure Modes ✅
**What would indicate the agent is failing?**

```
Failure indicators:
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

Example:
1. Classifies high-risk release as low-risk
2. Fails to use tools when needed
3. Hallucinates data instead of acknowledging missing info
```

---

## Section 7: Technical Requirements

### 7.1 LLM Provider ✅
**Which LLM provider should the agent use?**

```
Provider Preference:
[ ] Anthropic (Claude) - Recommended
[ ] OpenAI (GPT)
[ ] OpenRouter (multi-provider)
[ ] Other: ___________________________

Model Preference (if specific):
___________________________

Example: "claude-3-5-sonnet-20241022"
```

### 7.2 Performance Requirements 💡
**Any specific performance needs?**

```
Response Time: ___________________________ (e.g., <2 seconds)
Throughput: ___________________________ (e.g., 100 requests/min)
Availability: ___________________________ (e.g., 99.9%)

[ ] No specific requirements
```

### 7.3 Cost Constraints 💡
**Budget or cost considerations?**

```
[ ] Minimize token usage
[ ] Standard usage acceptable
[ ] No constraints

Notes:
_____________________________________________________________
```

---

## Section 8: Deployment and Integration

### 8.1 Deployment Environment ✅
**Where will the agent run?**

```
[ ] Local development only
[ ] Cloud deployment (specify: _______________)
[ ] On-premise servers
[ ] Containerized (Docker/Kubernetes)
[ ] Serverless (Lambda, Cloud Functions)
[ ] Other: ___________________________
```

### 8.2 Integration Points 💡
**What systems does it need to integrate with?**

```
Systems to integrate:
1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

APIs/Services:
_____________________________________________________________
```

### 8.3 Data Persistence ✅
**How should conversations be stored?**

```
[ ] Local filesystem (default)
[ ] Database (specify: _______________)
[ ] Cloud storage (S3, GCS, etc.)
[ ] No persistence needed
[ ] Other: ___________________________
```

---

## Section 9: Observability and Monitoring

### 9.1 Monitoring Needs 💡
**What should be monitored?**

```
[ ] Conversation traces (included by default)
[ ] Tool execution timing
[ ] Token usage and costs
[ ] Error rates
[ ] User satisfaction
[ ] Custom metrics: ___________________________
```

### 9.2 Alerting 💡
**When should alerts be triggered?**

```
Alert on:
[ ] Error rate > ___%
[ ] Response time > ___ seconds
[ ] Tool failure
[ ] Classification errors
[ ] Other: ___________________________
```

---

## Section 10: Additional Context

### 10.1 Similar Systems 💡
**Are there existing systems this should be similar to?**

```
Reference systems:
_____________________________________________________________
_____________________________________________________________

Example: "Similar to GitHub Copilot but for release assessment"
```

### 10.2 Unique Requirements 💡
**Anything unusual or special about this use case?**

```
Special requirements:
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
```

### 10.3 Timeline 💡
**When do you need this?**

```
[ ] ASAP (use copy-and-customize)
[ ] 1-2 weeks (can build from scratch)
[ ] Flexible timeline
```

### 10.4 Questions for AI Assistant 💡
**Anything you're unsure about or want advice on?**

```
Questions:
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
```

---

## Section 11: Review Checklist

Before submitting, verify you've provided:

- [ ] Agent name and purpose
- [ ] Domain and target users
- [ ] At least 2-3 tools with descriptions
- [ ] Classification system with criteria
- [ ] 3-5 test scenarios
- [ ] Success criteria
- [ ] LLM provider preference
- [ ] Deployment environment

---

## Submission

**You're done!** Share this completed questionnaire with your AI assistant to begin building your agent.

**Next steps:**
1. AI assistant will review your answers
2. AI will ask clarifying questions if needed
3. AI will create an implementation plan
4. You'll review and approve the plan
5. AI will build the agent based on your specifications

---

## Example: Completed Questionnaire (Detective Agent)

**For reference, here's what a completed questionnaire looks like:**

```markdown
1.1 Agent Name: Detective Agent

1.2 Purpose: Assess software release risk by analyzing test results,
deployment metrics, and code changes to identify potential issues
before production deployment.

1.3 Target Users: DevOps engineers, Release managers, QA teams

2.1 Domain: DevOps / Release Management

3.1 Tools:
  Tool 1:
    Name: get_release_summary
    Purpose: Fetch release metadata for analysis
    Type: GET
    Inputs: release_id (string)
    Outputs: version, changes, test results, metrics

  Tool 2:
    Name: file_risk_report
    Purpose: Submit risk assessment findings
    Type: POST
    Inputs: release_id, severity, findings list
    Outputs: report_id, status

4.1 Classification:
  HIGH: >5% error rate, critical test failures
  MEDIUM: 2-5% error rate, minor failures
  LOW: <2% error rate, all tests passing

6.2 Test Scenarios:
  Scenario 1: Low risk - all tests pass, 0.8% error rate
  Scenario 2: High risk - 12 test failures, 6.5% error rate
  Scenario 3: Missing data - no test results available

7.1 Provider: Anthropic (Claude 3.5 Sonnet)

8.1 Deployment: Local development, future cloud
```

---

**Need help filling this out? See [DISCOVERY_CONVERSATION.md](DISCOVERY_CONVERSATION.md) for an interactive approach!**
