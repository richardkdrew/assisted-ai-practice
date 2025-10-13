# SpecKit Constitution

## Philosophy

**Start small. Build fast. Learn continuously.**

SpecKit is a lightweight specification methodology that prioritizes working software over elaborate planning. It integrates seamlessly with TDD, incremental development, and the four-stage workflow process.

## Core Tenets

### 1. Minimal Viable Specification
- **Just enough to start**: Capture the essential goal and first steps only
- **No spec theater**: Skip elaborate planning documents that nobody maintains
- **Emergent detail**: Let specification emerge from building, not prediction
- **Living documents**: Specs evolve as understanding grows

### 2. Right-Sized Features
- **Small is beautiful**: Features should be completable in one focused session (2-4 hours max)
- **Clear value**: Every feature must answer "What user/business value does this deliver?"
- **Testable scope**: If you can't write tests for it, the scope is too vague
- **Time-boxed**: If it takes longer than planned, split it or re-scope it

### 3. Task Granularity
- **30-minute chunks**: Break work into tasks completable in ~30 minutes
- **Given-When-Then format**: Each task as a behavioral scenario
- **Concrete actions**: "Add GET /users/{id} endpoint" not "Design user system"
- **Test-first mindset**: Every task implies one or more tests

### 4. Progressive Specification
- **Build to learn**: Implementation reveals requirements better than speculation
- **Update as you go**: Keep specs current with reality, don't predict everything upfront
- **Embrace change**: Changing specs is success, not failure
- **Delete outdated**: Remove specs that no longer match reality

## Specification Structure

### Story Format
```markdown
# Story: [Clear, Concise Name]

**Business Value**: [One sentence: Who benefits and how?]
**Scope**: [What's in, what's out - be explicit]
**Time Estimate**: [Realistic: 2-4 hours ideal, 1 day maximum]

## Quick Tasks
1. [Concrete action with clear outcome]
2. [Concrete action with clear outcome]
3. [Concrete action with clear outcome]

## Test Strategy
- [How you'll verify it works]

## Notes
- [Any context needed to start]
```

### Task Format (Given-When-Then)
```markdown
**Task**: [Action-oriented name]
- **Given**: [Context/preconditions]
- **When**: [Action taken]
- **Then**: [Expected outcome]
- **Tests**: [Specific tests to write]
```

## Anti-Patterns (What NOT to Do)

### ❌ Over-Specification
```markdown
## User Story
AS A user
I WANT to manage my profile
SO THAT I can keep information up to date

### Acceptance Criteria (15+ items)
- GIVEN I am logged in
- WHEN I navigate to /profile
- THEN I should see...
[20 more detailed criteria]

### Technical Design (5 pages)
[Architecture diagrams, sequence diagrams, etc.]

### Tasks (3 weeks of work)
- [ ] Design database schema (2 days)
- [ ] Implement backend (3 days)
...
```

**Problems**:
- Spec is outdated before you finish reading it
- Requirements change during implementation
- Too much upfront planning = analysis paralysis
- Nobody maintains elaborate docs

### ✅ Right-Sized Specification
```markdown
# Story: Edit User Profile

**Business Value**: Users can update their name and email to keep profile current
**Scope**: Name and email only (no password, no avatar)
**Time Estimate**: 2-3 hours

## Quick Tasks
1. Add PUT /users/me endpoint with validation
2. Add edit form on /profile page
3. Show success/error messages
4. Write tests for happy path and validation errors

## Test Strategy
- Unit tests: endpoint validation logic
- Integration tests: full edit flow
- E2E tests: user can edit and see changes

## Notes
- Email validation: basic format check only
- Errors: 400 for validation, 401 for auth
```

**Why Better**:
- Clear goal achievable today
- Specific enough to start
- Room to adapt as you learn
- Tests included from the start

## Decision Framework

### Before Creating a Spec
Ask yourself:
1. **Can I build this in one session?** (If no, split it)
2. **Do I know enough to start?** (If yes, start building)
3. **What's the simplest version that delivers value?** (Build that first)
4. **Am I planning or procrastinating?** (Be honest)

### During Implementation
Ask yourself:
1. **Is the spec still accurate?** (Update it if not)
2. **Did I learn something that changes the approach?** (Adapt the spec)
3. **Is scope creeping?** (Cut scope or create new story)
4. **Can I ship this increment?** (Focus on deliverable chunks)

### Before Expanding Scope
Ask yourself:
1. **Is this necessary for the current goal?** (If no, create separate story)
2. **Does this add user value now?** (If no, defer it)
3. **Can this wait for the next iteration?** (Usually yes)
4. **Am I gold-plating?** (Probably)

## Integration with Four-Stage Workflow

### Stage 1: PLAN
**SpecKit Role**: Create minimal viable specification
- Write story with clear business value (1-2 sentences)
- Break into Given-When-Then tasks (30-minute chunks)
- Identify test strategy (not detailed test cases)
- Note file changes and dependencies
- **Stop when you have enough to start building**

### Stage 2: BUILD & ASSESS
**SpecKit Role**: Let specification emerge from implementation
- Update spec as you learn
- Add tasks discovered during build
- Remove tasks that become irrelevant
- Keep spec synchronized with reality
- **Spec evolves with the code**

### Stage 3: REFLECT & ADAPT
**SpecKit Role**: Capture specification learnings
- What spec details were wrong?
- What did we learn about sizing?
- What would we specify differently next time?
- **Improve specification practices**

### Stage 4: COMMIT & PICK NEXT
**SpecKit Role**: Finalize specification for historical record
- Ensure spec reflects what was actually built
- Archive completed spec with accurate final state
- Use learnings to improve next spec
- **Spec becomes accurate historical record**

## Specification Sizing Guide

### Too Small (Rare Problem)
- Takes < 30 minutes total
- Single function change
- **Solution**: Combine with related changes or just do it

### Just Right (Target)
- 2-4 hours of focused work
- 3-6 concrete tasks
- Clear value delivery
- **This is the sweet spot**

### Too Large (Common Problem)
- > 1 day of work
- Vague or numerous tasks
- Unclear how to start
- **Solution**: Split into multiple stories

## Real Examples

### Example 1: API Endpoint (Good)
```markdown
# Story: Get Configuration by ID

**Business Value**: API clients can retrieve specific configurations for runtime use
**Scope**: Single config retrieval only (no bulk operations)
**Time Estimate**: 2 hours

## Quick Tasks
1. Add GET /api/v1/configurations/{id} endpoint
2. Return 404 if config not found
3. Add validation for ULID format
4. Write integration tests

## Test Strategy
- Happy path: valid ID returns config
- Error path: invalid ULID returns 400
- Error path: missing config returns 404
```

### Example 2: UI Component (Good)
```markdown
# Story: Application List Component

**Business Value**: Admins can view all applications in a clean, responsive table
**Scope**: Display only (no edit/delete in this story)
**Time Estimate**: 3 hours

## Quick Tasks
1. Create ApplicationList web component
2. Fetch applications from API
3. Display in responsive table (name, created date)
4. Show loading state and error handling
5. Write unit tests for component
6. Add E2E test for list display

## Test Strategy
- Unit: component renders correctly with data
- Unit: error handling displays message
- E2E: navigate to apps page, see list
```

### Example 3: Database Migration (Good)
```markdown
# Story: Add Configuration Versioning

**Business Value**: Track configuration changes over time for audit and rollback
**Scope**: Schema and migration only (no UI or API changes)
**Time Estimate**: 1.5 hours

## Quick Tasks
1. Create migration 004_add_config_versions.sql
2. Add config_versions table with foreign key
3. Add trigger to auto-version on updates
4. Test migration up and down
5. Update repository tests

## Test Strategy
- Migration runs successfully
- Trigger creates version on update
- Foreign key constraints work
```

## Quality Integration

### SpecKit Quality Standards
Every specification must:
- [ ] Have clear business value statement
- [ ] Be completable in one session (2-4 hours)
- [ ] Include concrete Given-When-Then tasks
- [ ] Specify test strategy upfront
- [ ] Fit on one screen (no scrolling)

### SpecKit + TDD Integration
1. **Spec defines behavior** → Write failing test (Red)
2. **Build minimal solution** → Make test pass (Green)
3. **Update spec with learnings** → Refactor and adapt
4. **Repeat for next task**

### SpecKit + Quality Gates
Before proposing commit:
- [ ] Spec matches what was actually built
- [ ] All tests specified in spec are written and passing
- [ ] Scope stayed within spec boundaries (or spec was updated)
- [ ] Working document reflects final accurate state

## Common Pitfalls

### Pitfall 1: Spec Grows During Build
**Symptom**: "Just one more small feature..."
**Solution**: Create new story, finish current one first

### Pitfall 2: Spec Becomes Outdated
**Symptom**: Code and spec diverge
**Solution**: Update spec immediately when you learn something new

### Pitfall 3: Tasks Too Vague
**Symptom**: "Implement user management"
**Solution**: Break into concrete 30-minute chunks with clear outcomes

### Pitfall 4: Premature Detail
**Symptom**: Specifying implementation details before building
**Solution**: Specify behavior and outcomes, let implementation emerge

### Pitfall 5: Skipping Test Strategy
**Symptom**: "We'll figure out tests later"
**Solution**: Always include test strategy in initial spec

## Success Metrics

Track these to improve specification practices:

1. **Spec Accuracy Rate**: % of stories where final code matches initial spec direction
2. **Story Cycle Time**: Average time from spec to completion (target: 2-4 hours)
3. **Scope Creep Rate**: % of stories that exceed initial scope
4. **Spec Update Frequency**: How often specs are updated during build (healthy: 2-3 times)
5. **Split Rate**: % of stories that need splitting (target: < 20%)

## Remember

**SpecKit Mantras**:
- "Specify just enough to start, learn the rest by building"
- "A spec that fits on one screen beats a 10-page design doc"
- "Changing your spec is learning, not failure"
- "If you can't build it in one session, split it"
- "Tests are part of the spec, not an afterthought"

**The SpecKit Promise**:
Follow these principles and you'll:
- ✅ Ship working features faster
- ✅ Reduce wasted planning time
- ✅ Keep specs synchronized with reality
- ✅ Build exactly what's needed (no more, no less)
- ✅ Learn and adapt continuously

---

*"The best specification is working code with tests. Everything else is just a sketch to get you started."*

---

**Version**: 1.0
**Last Updated**: 2025-10-11
**Status**: Active
