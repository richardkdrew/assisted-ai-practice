# Integrate your learning experience with reflection

## 1. Which MCP servers did you attempt to use? Were you unsuccessful with any of them? Why?

**MCP Servers Used:**

- Context7 MCP
- Postgres MCP Pro
- Trello MCP
- Playwright MCP
- a11y
- Obsidian

Not really unsuccessful with any. Followed the demo for the first three with no problems. The last three I used for a while longer on a different home project... Very interesting seeing when Claude Code decided to leverage the tools and how much better it felt as part of a workflow where I simply wasn't needed to collect and provide feedback - now that there was a tool Claude had access to.

## 2. Did you install any local servers? Docker or on the metal? What are your reflections between the two?

**Local Installations:**

### Docker

- Postgres MCP Pro
- Trello MCP

### Bare Metal

- Playwright MCP
- a11y

Nothing really stood out, maybe speed of local vs remote? Also, a couple of the local npm install MCPs had issues with deprecated versions of dependencies and seemed to take longer to install than just spinning up Docker.

## 3. Which MCP servers do you suspect would be useful to run locally? What about remotely and/or team shared?

**Local MCP servers when:**

- Privacy and compliance requirements exist
- Security-sensitive or highly customized codebases like large monoliths
- Anything that is single user and/or needs to be close to the codebase

**Remote/Team Shared MCP servers when:**

- Team collaboration is needed
- Global access to tools is required
- Scalability and high availability for production applications - more resources required

I can imagine a shared MCP capability needing to be more of a remote install to be totally shareable. What about MCPs that train models, learn from the work they do - is that a thing? they will shurely need to be remote and require significantly more grunt!

## 4. Are there any obvious candidates for useful MCP servers in your organisation? Is this supporting an existing need, or a new opportunity?

### Existing

- **Visa API Standards MCP**
- **Visa Design System MCP**

### Being Considered (loosely)

- **Technology Radar MCP** - provides information, guidance, status and governance for technology choices
- **Meta Architecture MCP** - creates graph-based architecture metadata based on 4+1 model for existing codebase or solution design

### Crowd Sourced Ideas (from architects recently...)

- Solution discovery support - suggest design (maybe solution options) from product discovery/requirements (based on organisational technology guardrails)
- Architecture MCP that provides templating, boilerplating of 'approved' reference architectures
- Upskilling ops/support groups on release changes
- Providing architecture-specific specs and workflow templates based on product requirements
- Evaluate solution design and/or codebase to find/fix compliance/QoS gaps (TSRs, DSRs, KCs, etc...)
- Refactor stored procedures to business logic libraries with appropriate events for communication and comprehensive testing

---

**Before the next time we meet, please post a link to your repo and your reflections to Discord.**