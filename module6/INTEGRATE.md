# Integrating learning experience with reflection

## 1. How did you find starting with questions and putting yourself in the perspective of the agent (in terms of what it might need to perform its duties)? Or do you find it more natural to be exhaustive in data collection and then explore what might be derived from it?

I worked on the assumption that custom errors and error fields would be the most important piece of information for an agent with the autonomy to decide whether to try something again or not. I used an older version of the config service from Module 4 - I had already started capturing some performance metrics there, so I added to that observability solution by adding tracing, spans, custom fields for `request.payload`, `error.type`, `error.stack`, etc...

## 2. How did you find working through the sequence (structured data → query → decision) with your AI assistant? Did they seem to understand your intent and implementation?

My assistant seemed to really grasp the concept and went to work planning a true feat in over-engineering. I used the example prompts as a reference point and asked questions around the scope of the plan, the complexity and effort of the feature above and beyond what was in the prompt. We eventually settled on a compromise ;) - in the end the solution is still a bit over-engineered, but the back and forth strengthened the result and I learned a bit about observability primitives along the way.

## 3. What are some details we can capture to determine if a service/feature/investment is fulfilling its destiny? What are some questions we can ask ourselves (and assumptions we can discuss) during the initial planning phases about what success looks like? What do we need to capture to quantify it?

May have misunderstood the question...

### Details we can capture

- Usage Metrics
- Performance Metrics
- Business Impact Metrics
- User Experience Metrics

### Key Questions we could ask

- What specific problem is this feature solving?
- Which stakeholders are most affected by this problem?
- How are users/systems currently working around this problem?
- What quantitative improvements would make this investment worthwhile?
- What timeframe is appropriate to measure success of the investment (immediate, short-term, long-term)?

### What we need to capture

We probably need some metrics around:

- Error recovery success rates
- Reduction in manual interventions (linked to improvments in auto-recovery)
- System uptime improvements
- General usage patterns

## 4. From the following list, which would have the biggest impact from agentic automation in your org? (no need to over-share, the benefit is in the reflection, don't rush it)

- fault finding/troubleshooting

Given the volume of trace information collected just by enabling middleware and adding some simple custom trace attributes, I suspect that being able to look both proactively and retroactively would provide all sorts of insights into potential future sources of pain and the source of problems we have experienced.

---

**Before the next time we meet, please post a link to your repo and your reflections to Discord.**
