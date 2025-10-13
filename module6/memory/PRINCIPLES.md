# Engineering Principles

## Core Development Philosophy

**Start simple. Prove it works. Then discuss evolution.**

## The Golden Rules

### 1. Test-First Development
- **Red → Green → Refactor**: Write failing test, make it pass, clean up
- **No code without a test**: If it's not tested, it doesn't exist
- **Tests document behavior**: Your tests are your specification
- **Test files live next to code**: `feature.py` → `test_feature.py`

### 2. Start with Single-File Architecture
- **One file until it hurts**: Keep everything in one file until complexity demands separation
- **Pain-driven refactoring**: Only split when maintaining becomes difficult
- **Progressive enhancement**: Discuss before restructuring, not after
- **Modules emerge naturally**: Let patterns reveal themselves through usage

### 3. Simplicity Over Engineering
- **YAGNI (You Aren't Gonna Need It)**: Build what you need today, not what you might need tomorrow
- **No premature abstraction**: Concrete before abstract, always
- **Obvious over clever**: Code should be boring and predictable
- **Delete before adding**: Can you solve this by removing code?

### 4. Collaborative Evolution
- **Discuss before major changes**: Architecture shifts need conversation
- **Show, don't tell**: Working code beats design documents
- **Incremental improvement**: Small steps, frequent validation
- **Question complexity**: "Why is this complex?" should always have a good answer

### 5. Feature Discipline (Spec Kit Integration)
- **Keep features small**: If you can't implement in one session, it's too big
- **Minimal specification**: Just enough to start - spec emerges from building
- **No spec theater**: Skip elaborate planning docs that nobody maintains
- **Tasks match reality**: Break work into 30-minute chunks, not multi-day epics
- **Specification evolution**: Update specs as you learn, don't predict everything upfront

### 6. Commit Discipline
- **Discuss before commit**: Every commit proposal needs human approval
- **Full quality gate**: All tests pass, no exceptions
- **Documentation in sync**: If code changes, docs change with it
- **Working state only**: Never commit broken code, even to a branch
- **Feature completeness**: Each commit represents a complete, tested, documented unit of work

## Feature Workflow (Spec Kit Compatible)

### 1. Start Small
- **One clear goal**: "Add API endpoint to get user by ID"
- **Not**: "Build user management system with auth, CRUD, and admin panel"
- **Time-box**: If it takes more than 2-4 hours, split it

### 2. Minimal Planning
```
Feature: Get user by ID
- Add GET /users/{id} endpoint
- Return 404 if not found
- Add tests
```

**That's it.** No elaborate diagrams, acceptance criteria matrices, or design docs.

### 3. Build (TDD)
```bash
# 1. Write a failing test
make test  # RED - test fails

# 2. Write minimal code to pass
make test  # GREEN - test passes

# 3. Clean up (if needed)
make test  # GREEN - still passes
```

### 4. Quality Gate (Before Commit Discussion)
Run the full quality check:
```bash
make test              # All tests must pass
make lint              # Code quality checks
make type-check        # Type validation (if applicable)
```

**Update documentation** - If you changed behavior, update:
- README examples
- API documentation
- Code comments (only where necessary)

### 5. Discuss Commit
- Show what was built
- Confirm tests pass
- Verify docs are updated
- Get approval to commit

### 6. Commit (After Approval Only)
```bash
git add .
git commit -m "Add GET /users/{id} endpoint with tests"
```

**Never commit without**:
- ✅ All tests passing
- ✅ Documentation updated
- ✅ Human approval
- ✅ Quality checks clean

## Architecture Evolution Pattern

### Stage 1: Single File (Start Here)
```
service.py              # Everything in one file
test_service.py         # Tests right next to it
```

**When to stay**: < 500 lines, clear sections, easy to navigate

### Stage 2: Logical Separation (Move here when needed)
```
service/
├── __init__.py        # Public interface
├── core.py            # Main logic
├── models.py          # Data structures
└── tests/             # Test organization mirrors code
    ├── test_core.py
    └── test_models.py
```

**When to move**: File > 500 lines, distinct responsibilities emerge, team asks "where is X?"

### Stage 3: Feature Modules (Rare, needs discussion)
```
service/
├── features/
│   ├── auth/
│   ├── api/
│   └── data/
└── shared/
```

**When to move**: Multiple features, different teams, clear bounded contexts

## Spec Kit Anti-Patterns (What NOT to Do)

### ❌ Over-Specification
```markdown
## User Story
AS A user
I WANT to be able to manage my profile
SO THAT I can keep my information up to date

### Acceptance Criteria
- GIVEN I am logged in
- WHEN I navigate to /profile
- THEN I should see my profile information
- AND I should be able to edit my name
- AND I should be able to edit my email
- AND changes should be validated
- AND validation errors should be displayed
- AND successful saves should show a message
...15 more criteria...

### Technical Design
[5 pages of architecture diagrams]

### Tasks
- [ ] Design database schema (2 days)
- [ ] Implement backend API (3 days)
- [ ] Create frontend components (3 days)
- [ ] Add validation logic (1 day)
...20 more tasks...
```

**Problem**: By the time you finish this spec, the requirements changed.

### ✅ Right-Sized Specification
```markdown
## Feature: Edit user profile

Add ability to update name and email on profile page.

### Quick tasks
- Add PUT /users/me endpoint
- Add form on /profile page
- Validate email format
- Show success/error messages
- Tests

Estimate: 2-3 hours
```

**Why better**: Clear goal, buildable today, tests included, room to adapt.

## Decision Framework

Before adding complexity, ask:

1. **Is there a test that proves we need this?**
2. **Can we solve this with what we already have?**
3. **Will this be easier to understand in 6 months?**
4. **Have we discussed this approach?**

If any answer is "no", pause and discuss.

Before over-specifying, ask:

1. **Can we start building with what we know?**
2. **What's the smallest version that delivers value?**
3. **Will this spec be outdated before we finish reading it?**
4. **Are we planning or procrastinating?**

## Red Flags

- Adding abstraction layers "for future flexibility"
- Creating interfaces with only one implementation
- Splitting files before reaching 300-500 lines
- Patterns from other projects that "might be useful"
- Code that requires explanation in comments

## Green Flags

- Tests that read like documentation
- Functions under 20 lines
- Files that fit on one screen (mostly)
- Obvious file/function names
- Deleting code as features evolve

## Example: Good vs Over-Engineered

### ❌ Over-Engineered (Don't start here)
```python
# config_service.py
from abc import ABC, abstractmethod

class ConfigRepository(ABC):
    @abstractmethod
    def get(self, key: str) -> Any: pass

class PostgresConfigRepository(ConfigRepository):
    def get(self, key: str) -> Any:
        return self.db.query(...)

class ConfigService:
    def __init__(self, repo: ConfigRepository):
        self.repo = repo
```

### ✅ Simple (Start here)
```python
# config.py
import psycopg2

def get_config(key: str) -> dict:
    """Get configuration value by key."""
    conn = get_connection()
    result = conn.execute("SELECT value FROM configs WHERE key = %s", [key])
    return result.fetchone()

# test_config.py
def test_get_config():
    result = get_config("api_timeout")
    assert result["timeout"] == 30
```

**Evolution path**: If you need multiple storage backends (Redis, file, etc.), *then* discuss abstractions.

## When to Refactor (The "Three Strikes" Rule)

1. **First time**: Write it simply
2. **Second time**: Notice the duplication, but leave it
3. **Third time**: Now refactor - you understand the pattern

## Commands Should Be Simple

```bash
make test              # Run all tests
make run               # Start the service
make check             # Verify everything works
```

If you need a manual to run tests, the workflow is too complex.

## Quality Gate Checklist

Before proposing a commit, verify:

### Code Quality
- [ ] All tests pass (`make test`)
- [ ] No linting errors (`make lint` if available)
- [ ] Type checks pass (if applicable)
- [ ] No commented-out code left behind
- [ ] No debug print statements or console.logs

### Documentation
- [ ] README updated if behavior changed
- [ ] API docs updated if endpoints changed
- [ ] Code comments added only where necessary (prefer self-documenting code)
- [ ] Examples updated if API changed

### Testing
- [ ] New features have tests
- [ ] Bug fixes have regression tests
- [ ] Edge cases covered
- [ ] Tests are clear and maintainable

### Completeness
- [ ] Feature is fully working (not partially done)
- [ ] No "TODO" comments for core functionality
- [ ] Error handling in place
- [ ] Happy path and error paths both work

### Discussion
- [ ] Human has reviewed the changes
- [ ] Approach was discussed if non-trivial
- [ ] Commit message is clear
- [ ] Ready for approval

**If any checkbox is unchecked, don't propose the commit yet.**

## Remember

- **Start with the test** - What behavior do we need?
- **Start with one file** - Where's the pain point that needs separation?
- **Start with discussion** - Why are we changing this?
- **Start simple** - Can we delete our way to a solution?
- **End with quality** - All tests pass, docs updated, human approved

> "Simplicity is prerequisite for reliability." - Edsger Dijkstra

> "The best code is no code at all." - Jeff Atwood

> "Make it work, make it right, make it fast - in that order." - Kent Beck
