# AI Agent Discovery - Conversational Script

**Purpose:** Interactive conversation flow for gathering agent requirements
**Format:** AI assistant asks questions, user answers conversationally
**Estimated time:** 20-30 minutes

---

## How to Use This Script

**For AI Assistants:**
1. Follow the conversation flow below
2. Ask questions naturally (don't read verbatim)
3. Listen for key information in responses
4. Ask follow-up questions based on answers
5. Summarize understanding periodically
6. Confirm all required information collected before proceeding

**For Users:**
- Answer naturally - no need to be formal
- Provide examples when you can
- Ask for clarification if questions are unclear
- It's okay to say "I'm not sure" - we'll figure it out together

---

## Conversation Flow

### Opening

**AI:** "I'm going to help you build a custom AI agent! I'll ask you some questions to understand what you need. This should take about 20-30 minutes. Sound good?"

**[Wait for confirmation]**

**AI:** "Great! Let's start with the basics..."

---

### Phase 1: The Big Picture (5 min)

#### Q1: Agent Purpose

**AI:** "What problem are you trying to solve with this agent? What should it do?"

**Listen for:**
- Clear problem statement
- Desired outcomes
- User pain points

**Follow-ups:**
- "Can you give me an example of when you'd use this?"
- "What happens today without this agent?"
- "Who would use this?"

**Capture:**
```
Purpose: [1-2 sentence description]
Use Case Example: [concrete scenario]
Target Users: [who will use it]
```

#### Q2: Domain

**AI:** "What domain or industry does this relate to?"

**Examples to help them:**
- DevOps/Software Development
- Customer Support
- Healthcare
- Finance/Banking
- E-commerce
- Education
- Other

**Listen for:** Domain-specific terminology they use naturally

**Capture:**
```
Domain: [domain name]
Key Terms: [domain vocabulary they used]
```

#### Q3: Scope and Boundaries

**AI:** "What should the agent NOT do? Any guardrails or limitations?"

**Listen for:**
- Safety concerns
- Things that need human oversight
- Out-of-scope functionality

**Follow-ups:**
- "Should it be able to make decisions autonomously or always check with humans?"
- "Are there any risky actions it should avoid?"

**Capture:**
```
Boundaries: [list of limitations]
Human Oversight: [when needed]
```

---

### Phase 2: Tools and Actions (10 min)

**AI:** "Now let's talk about what the agent needs to DO. Agents accomplish tasks by using 'tools' - think of these as capabilities or actions."

#### Q4: Core Capabilities

**AI:** "Walk me through a typical scenario. What steps would the agent take?"

**Prompt them to think through the workflow:**
1. What information does it need first?
2. What does it do with that information?
3. What does it produce or output?

**Example:**
- User: "Well, it would need to get the release information..."
- AI: "Great! So one tool is 'get release information'. What else?"

**For each tool they describe, capture:**

**Tool Discovery Template:**
```
AI: "Let me make sure I understand this tool..."

Tool Name: [suggest a name] - "Does '{tool_name}' sound right?"
Purpose: "So this tool [restate purpose], correct?"
Type: "Is this fetching/reading data or taking an action/writing data?"
Inputs: "What information does it need?" [list parameters]
Outputs: "What does it return?" [describe result]
```

**Continue until they've described all tools (usually 2-5 tools)**

**AI:** "Let me summarize the tools we've identified:
1. {Tool 1} - {purpose}
2. {Tool 2} - {purpose}
...

Does that cover everything, or are we missing any capabilities?"

#### Q5: Data Sources

**AI:** "Where will this data come from? Do you have APIs, databases, or should we use mock data for now?"

**Listen for:**
- Existing APIs or services
- Databases
- File systems
- Need for mock/test data

**Capture:**
```
Data Sources:
- [API/DB/File/Mock] - [details]
```

**Follow-up:**
"For development and testing, should I create mock data, or do you have test environments?"

---

### Phase 3: Decision Making (8 min)

#### Q6: Classification/Assessment

**AI:** "It sounds like the agent needs to make judgments or assessments. How should it categorize things?"

**Examples to help:**
- "HIGH/MEDIUM/LOW risk?"
- "URGENT/NORMAL/LOW priority?"
- "APPROVED/NEEDS_REVIEW/REJECTED?"

**User:** [describes their classification system]

**AI (for each level):** "What makes something {LEVEL}? What criteria?"

**Capture:**
```
Classification System: [name the levels]

Level 1 ({name}):
  Criteria: [what qualifies]
  Examples: [concrete examples]

Level 2 ({name}):
  Criteria: [what qualifies]
  Examples: [concrete examples]

...
```

#### Q7: Decision Factors

**AI:** "What factors should the agent weigh when making these decisions?"

**Prompt:** "Think about what you'd consider if YOU were making this assessment..."

**Listen for:**
- Metrics or measurements
- Qualitative factors
- Priorities or weights

**AI:** "Which of these factors are most important? Rank them for me."

**Capture:**
```
Decision Factors:
1. [Factor] - Weight: HIGH/MEDIUM/LOW
2. [Factor] - Weight: HIGH/MEDIUM/LOW
...
```

#### Q8: Edge Cases

**AI:** "What tricky situations might the agent encounter? What could go wrong?"

**Prompts:**
- "What if data is missing?"
- "What if signals conflict?"
- "What if it's unsure?"

**For each edge case:**

**AI:** "If {edge case happens}, what should the agent do?"

**Capture:**
```
Edge Cases:
- [Situation]: [How to handle]
- [Situation]: [How to handle]
```

---

### Phase 4: Personality and Style (3 min)

#### Q9: Communication Style

**AI:** "How should the agent communicate? Formal and professional, or casual and friendly?"

**Offer choices:**
- Technical and precise
- Friendly and approachable
- Concise and efficient
- Detailed and explanatory

**AI:** "Should it explain its reasoning, or just give the answer?"

**Capture:**
```
Tone: [description]
Verbosity: [concise/detailed]
Explain Reasoning: [yes/no]
```

---

### Phase 5: Success and Testing (5 min)

#### Q10: Success Definition

**AI:** "How will we know the agent is working correctly?"

**Listen for:** Success metrics, quality indicators

**Follow-up:** "What would make you confident to use this in production?"

**Capture:**
```
Success Criteria:
- [Criterion 1]
- [Criterion 2]
...
```

#### Q11: Test Scenarios

**AI:** "Let's define some test cases. I need scenarios that cover different situations the agent will face."

**Ask for 3-5 scenarios:**

**For each scenario:**
```
AI: "Describe a {typical/edge case/error} scenario..."

User: [describes situation]

AI: "What's the input data for this test?"
User: [provides example data]

AI: "What should the agent do?"
User: [describes expected behavior]

AI: "What classification/output should it produce?"
User: [expected result]
```

**Capture:**
```
Test Scenarios:
1. [Name] - Input: [data] | Expected: [behavior + output]
2. [Name] - Input: [data] | Expected: [behavior + output]
...
```

**AI:** "Perfect! These scenarios will be used for automated testing."

---

### Phase 6: Technical Preferences (2 min)

#### Q12: LLM Provider

**AI:** "Which AI model provider do you prefer? I recommend Anthropic's Claude for reliability and tool use, but we can use OpenAI or others."

**Capture:**
```
Provider: [Anthropic/OpenAI/Other]
Specific Model: [if they have preference]
```

#### Q13: Deployment

**AI:** "Where will this run? Local development, cloud, both?"

**Capture:**
```
Environment: [local/cloud/containerized/etc.]
```

---

### Recap and Confirmation

**AI:** "Great! Let me summarize what we've discussed. Please let me know if I got anything wrong or if we need to add anything."

**AI provides structured summary:**

```
AGENT SPECIFICATION SUMMARY
===========================

NAME: [agent name]

PURPOSE: [1-2 sentences]

DOMAIN: [domain]

TARGET USERS: [who uses it]

TOOLS:
1. {tool_name} - {purpose}
   - Inputs: {params}
   - Outputs: {results}
2. {tool_name} - {purpose}
   - Inputs: {params}
   - Outputs: {results}
[...]

CLASSIFICATION SYSTEM:
- {LEVEL1}: {criteria}
- {LEVEL2}: {criteria}
- {LEVEL3}: {criteria}

DECISION FACTORS:
1. {factor} (weight: {HIGH/MED/LOW})
2. {factor} (weight: {HIGH/MED/LOW})
[...]

AGENT PERSONALITY:
- Tone: {description}
- Style: {characteristics}

SUCCESS CRITERIA:
- {criterion 1}
- {criterion 2}

TEST SCENARIOS:
1. {scenario name}: {brief description}
2. {scenario name}: {brief description}
[...]

TECHNICAL:
- Provider: {LLM provider}
- Environment: {deployment context}

CONSTRAINTS:
- {limitation 1}
- {limitation 2}
```

**AI:** "Does this look correct? Anything to change or add?"

**[Wait for confirmation and address any corrections]**

---

### Next Steps

**AI:** "Perfect! Now I need to ask: do you want to learn how everything works as we build it (takes 1-2 days), or do you want me to move quickly using the template (takes 1-2 hours)?"

**Options:**
- **BUILD FROM SCRATCH**: Educational, step-by-step, understand architecture
- **COPY AND CUSTOMIZE**: Fast, template-based, production-ready quickly
- **HYBRID**: Copy template but explain components along the way

**[User chooses approach]**

**AI:** "Excellent! I have everything I need. Let me create an implementation plan based on what you've told me. I'll show you the plan and get your approval before writing any code. Give me just a moment..."

**[AI creates detailed implementation plan based on gathered information]**

---

## Tips for AI Assistants

### Active Listening
- Repeat back what you heard
- Ask for examples
- Clarify ambiguities immediately
- Don't assume - confirm

### Guide, Don't Dictate
- User knows their domain better than you
- Your job: translate their knowledge into agent architecture
- Suggest options but let them decide
- Be flexible with terminology

### Manage Scope
- If they describe 10+ tools, gently suggest starting smaller
- "That's comprehensive! Should we start with the 3 most critical tools and add more later?"
- Prevent scope creep while capturing their vision

### Spot Gaps
- Missing edge case handling? Ask about it
- Unclear classification criteria? Dig deeper
- Vague success metrics? Get specific

### Build Confidence
- "This is a really clear use case for an agent"
- "These tools will work well together"
- "Your classification system makes sense"

### Document as You Go
- Keep notes in structured format
- Easy to reference during implementation
- Becomes part of project documentation

---

## Example Conversation Excerpts

### Good Discovery

**AI:** "What problem are you trying to solve?"

**User:** "We deploy releases but don't know if they're risky until after deployment. By then it's too late."

**AI:** "So you want to assess risk BEFORE deployment. What information do you look at to judge risk?"

**User:** "Test results, error rates, what changed..."

**AI:** "Perfect. So the agent needs to get release information - tests, metrics, changes. Then what?"

**User:** "Analyze it and tell us if it's safe to deploy."

**AI:** "Got it. And 'safe' means what? All tests passing? Low error rate? How do you define safe vs. risky?"

**[This leads to classification criteria discussion]**

### Handling Uncertainty

**User:** "I'm not sure what tools it needs..."

**AI:** "Let's think through a scenario together. Imagine a release is ready. What's the first thing you'd want to know about it?"

**User:** "Um, what changed?"

**AI:** "Great! So one tool could be 'get changes' or 'get release summary'. What would you do with that information?"

**User:** "Check if tests passed..."

**AI:** "Would that be part of the release summary, or a separate tool?"

**[This scaffolds the tool discovery process]**

### Clarifying Vague Requirements

**User:** "It should be smart about assessing risk."

**AI:** "Help me understand 'smart' - what specific factors should it weigh?"

**User:** "Well, if lots of tests fail, that's risky..."

**AI:** "Absolutely. What's 'lots'? More than 5? More than 10? A percentage?"

**User:** "Maybe like, more than 5% of tests failing?"

**AI:** "Perfect! So >5% test failure rate = high risk. What else indicates high risk?"

**[This converts vague to concrete criteria]**

---

## Post-Discovery Checklist

Before proceeding to implementation, verify you have:

- [ ] Clear agent purpose and use case
- [ ] 2-5 well-defined tools with inputs/outputs
- [ ] Classification system with specific criteria
- [ ] Decision factors with relative importance
- [ ] 3-5 concrete test scenarios
- [ ] Edge case handling approach
- [ ] Success criteria
- [ ] Agent personality/style preferences
- [ ] Technical preferences (provider, deployment)
- [ ] Summary confirmed by user

**If any item is missing or unclear, go back and ask follow-up questions!**

---

## Next: Create Implementation Plan

Once discovery is complete:

1. Synthesize all information into structured specification
2. Choose appropriate template workflow
3. Create detailed implementation plan
4. Get user approval on plan
5. Begin implementation

**See:** [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for next steps

---

**Remember: Good discovery makes everything else easier. Invest the time upfront!**
