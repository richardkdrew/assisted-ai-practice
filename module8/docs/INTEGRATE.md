## 1. How do you decide when to use sub-conversations vs direct context?

**Use sub-conversations** when content would overwhelm your main conversation - in our case, documents over 3,000 tokens (my number so I can test easily). The main agent stays focused on the decision while sub-conversations handle the heavy lifting of analysing large content. There's a trade-off of some information loss (through summarisation) for the ability to process unlimited content.

**Stick with direct context** for simple back-and-forth data gathering. i.e. most JIRA calls or analysis metrics fit comfortably in the context window without needing special handling.

Key insight: sub-conversations aren't about parallelisation. They're about preventing context overflow while keeping your main agent focused on its core task.

## 2. What's the right granularity for a sub-conversation?

**One clear purpose per sub-conversation.** In practice, that means one sub-conversation per large document.

It woudl probably be a mistake to going too granular (separate sub-conversations for "extract endpoints" and "check authentication") or too broad ("analyse all documentation").

A "sweet spot" example: when the agent reads "API_SPECIFICATION.md" for example (5,175 tokens), it gets one sub-conversation with a focused purpose: "Analyse this API spec and tell me about endpoints, authentication, and potential risks, etc..."

## 3. How do summaries lose information? What mitigations exist?

Summaries drop fine details, edge cases, and attribution. That's the point - but you need to be aware of it.

**What gets lost:** Specific version numbers, unusual failure scenarios, exact ordering, who said what, etc...

**What helps:**

- Good obeservability. keep metadata about the source (document name, token count, etc...)
- Use targeted prompts ("extract security concerns") not generic "summarise this"
- Preserve originals for audit (ours are still in `incoming_data/`)

Key realisation: you only need **sufficient** preservation for the task. i.e. for production readiness, you need to know about test failures and security issues, not every single test case name.

## 4. When is memory overhead worth the benefit?

Memory mostly makes sense when history improves decisions. i.e. for software deployment, knowing "we assessed this three weeks ago and found database issues" helps you check if they're fixed.

**When it pays off:**

- Consistency across related decisions (apply same standards to similar features)
- Learning from past mistakes (remember patterns that caused problems)
- Audit trails and compliance (JSON files you can show auditors, etc...)

**AI-enhanced Cost considerations:**
File-based memory is cheap (<5ms read time, no dependencies) but you need a strategy: expire old entries, store key facts not full transcripts, upgrade to ChromaDB for semantic search at scale.

**AI-enhanced Scale guidance:**

- File-based: works great up to ~1,000 features
- ChromaDB: 10,000+ assessments with semantic search needs
- Graphiti: when you need relationship tracking and temporal patterns

For most teams starting out, file-based memory is plenty.

## 5. How do you evaluate "good enough" for an agent decision?

It depends... on what's at stake.

**Start with clear success criteria:** Define "ready for production" upfront - test coverage >80%, all critical tests passing, security review complete, stakeholder approval.

**Use automated evaluations** for objective measures. i.e. our system scores four dimensions: correct feature identification, right tool usage, right decision, proper sub-conversation use. We got 75% pass rate with 70% threshold - acceptable for prototype, not production.

**For higher-risk decisions, raise the bar:** 95%+ pass rate, human review for borderline cases, monitoring for drift, feedback loops to improve over time.

Honest answer: "good enough" is whatever lets you sleep at night. Define it based on risk tolerance, compliance requirements and cost/tolerance of being wrong.

## 6. What patterns from this module apply to your domain?

Assuming a typical enterprise software environment... obvious patterns are things like:

- Sub-conversations for scale
- Memory for consistency
- Evaluation for quality
- Observability for debugging

All foundational patterns for agentic systems that need to work reliably in production environments.