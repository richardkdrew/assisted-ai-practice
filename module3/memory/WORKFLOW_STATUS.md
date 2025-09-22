# Workflow & Status

## Overview

This document establishes a rigorous four-stage development process that ensures consistent, high-quality software delivery. Every work item must progress through all stages sequentially, with explicit user approval required for stage transitions.

## Four-Stage Development Process

### Stage 1: PLAN

**Purpose**: Establish clear direction and success criteria before any implementation begins.

**Activities**:
- **Story Planning**: Define complete feature scope with business value statement
- **Task Planning**: Break down into Given-When-Then acceptance criteria scenarios
- **Failure Mode Planning**: Anticipate common failure modes and integration issues
- **Validation Strategy**: Include end-to-end validation approach in initial plan
- **Test Strategy**: Identify testing approach and coverage requirements
- **File Change Identification**: Map which files will be modified or created
- **Branch Creation**: Create feature branch following naming conventions
- **Plan Commitment**: Lock in the plan before proceeding

**Completion Criteria**:
- [ ] Story has clear business value statement
- [ ] All tasks defined with Given-When-Then format
- [ ] Test strategy documented for each task
- [ ] File changes identified and validated
- [ ] Feature branch created and checked out
- [ ] Working document created and committed
- [ ] **USER APPROVAL REQUIRED** to advance to Stage 2

**Quality Gate**: Plan must be complete, coherent, and committed before implementation begins.

---

### Stage 2: BUILD & ASSESS

**Purpose**: Implement the planned solution while continuously validating quality and requirements.

**Activities**:
- **Implementation Loop**: Write code according to planned file changes
- **Testing Loop**: Create and execute tests for each Given-When-Then scenario
- **End-to-End Validation**: Test integration points and full system functionality
- **Quality Validation**: Run complete quality suite after each significant change
- **Assessment**: Validate implementation against acceptance criteria
- **Cleanup**: Remove temporary/debug code before stage completion
- **Iteration**: Refine implementation until all criteria are satisfied

**Completion Criteria**:
- [ ] All planned file changes implemented
- [ ] All Given-When-Then scenarios pass
- [ ] **MANDATORY**: 100% E2E test pass rate for all frontend components
- [ ] **MANDATORY**: Backend dependency services (API, database) must be available for E2E tests
- [ ] **MANDATORY**: Full-stack integration testing with UI server + backend stack
- [ ] Quality validation passes cleanly (no warnings)
- [ ] Code coverage meets requirements
- [ ] Implementation matches planned scope exactly
- [ ] **USER APPROVAL REQUIRED** to advance to Stage 3

**Quality Gate**: All tests pass, quality validation is clean, acceptance criteria are fully satisfied, and **E2E tests achieve 100% pass rate**.

**Critical Protocol**:
- Quality validation must pass **without warnings**
- **E2E tests are MANDATORY and must achieve 100% pass rate**
- Any E2E test failures must be resolved before stage completion
- Backend services (API, database, observability) must be running and healthy for E2E test execution
- UI server integration must be verified and working

---

### Stage 3: REFLECT & ADAPT

**Purpose**: Capture learnings and optimize future development cycles.

**Activities**:
- **Process Assessment**: Evaluate what worked well and what didn't
- **Critical Gap Resolution**: Address any critical issues identified during implementation
- **Improvement Identification**: Document specific process enhancements
- **Future Task Review**: Assess remaining tasks for priority and approach
- **Documentation Update**: Record lessons learned and best practices
- **Adaptation Planning**: Prepare process adjustments for next iteration

**Completion Criteria**:
- [ ] Process assessment completed and documented
- [ ] Improvement opportunities identified
- [ ] Future tasks reviewed and prioritized
- [ ] Lessons learned captured in working document
- [ ] Process adaptations planned for next cycle
- [ ] **USER APPROVAL REQUIRED** to advance to Stage 4

**Quality Gate**: Reflection is thorough and actionable improvements are identified.

---

### Stage 4: COMMIT & PICK NEXT

**Purpose**: Finalize current work and transition smoothly to the next development cycle.

**Activities**:
- **Final Production Readiness Review**: Ensure all components are production-ready
- **Commit Creation**: Create conventional commit with clear, descriptive message
- **Branch Management**: Merge feature branch and clean up
- **Next Task Selection**: Choose next task based on priority and dependencies
- **Status Update**: Update working document and project status
- **Cycle Transition**: Prepare for next PLAN stage

**Completion Criteria**:
- [ ] Conventional commit created with proper format
- [ ] Feature branch merged to main/develop
- [ ] Local branches cleaned up
- [ ] Next task selected and documented
- [ ] Working document updated with progress
- [ ] **USER APPROVAL REQUIRED** to begin next cycle

**Quality Gate**: Work is properly committed and next iteration is clearly defined.

---

## Critical Process Rules

### Non-Negotiable Protocols

1. **Explicit Stage Approval Required**: Only the user can advance between stages. The assistant **must** wait for explicit "approved to move to stage X" before proceeding. Never assume approval or move stages automatically.

2. **Complete Stage Completion**: All completion criteria must be satisfied before stage transition. No partial completions allowed.

3. **Quality Validation Requirement**: Quality checks must pass **cleanly without warnings** before advancing from Stage 2.

4. **Sequential Processing**: Stages must be completed in order. No skipping or parallel processing.

5. **Documentation Integrity**: Working document must accurately reflect current status and be updated at each stage transition.

### Stage Transition Protocol

**Assistant Responsibilities**:
- Complete all activities for current stage
- Validate all completion criteria
- Present stage summary to user
- **Request explicit permission** to advance

**User Responsibilities**:
- Review stage completion summary
- Validate quality and completeness
- **Explicitly approve** stage advancement
- Provide guidance for process improvements

---

## Work Item Structure & Organization

### Story
- **Definition**: Complete feature that delivers business value to users
- **Scope**: End-to-end functionality that can be demonstrated and validated
- **Composition**: Contains 1-N tasks that collectively implement the feature
- **Acceptance**: Must satisfy business requirements and user needs
- **Storage**: Stored as markdown files in `changes/` directory

### Task
- **Definition**: Single Given-When-Then scenario within a story
- **Scope**: Atomic unit of work that can be completed in one development cycle
- **Format**: Structured as behavioral specification with clear success criteria
- **Validation**: Must be testable and demonstrable
- **Tracking**: Tracked within parent story document with individual status

### Working Document Pattern
- **Purpose**: Real-time tracking and status management for AI assistant guidance
- **Structure**: Template-based with consistent sections for clarity and support
- **Content**: Current status, completion criteria, notes, context, and history
- **Location**: Stored in `changes/` directory with descriptive filenames
- **Assistant Support**: Provides sufficient context for AI to maintain focus and direction

### Changes Directory Structure
```
changes/
├── 001-story-user-authentication.md       # Numbered story files
├── 002-story-dashboard-redesign.md        # Sequential numbering
├── 003-story-api-rate-limiting.md         # One file per story
└── archived/                              # Completed stories
    ├── 001-story-login-system.md          # Moved after completion
    └── 002-story-user-profile.md          # Maintains numbering
```

### File Naming Convention
- **Format**: `[XXX]-story-[descriptive-name].md` (where XXX is a 3-digit number)
- **Examples**: 
  - `001-story-user-authentication.md`
  - `002-story-payment-integration.md`
  - `003-story-dashboard-redesign.md`
- **Numbering**: Sequential 3-digit numbers (001, 002, 003, etc.)
- **Rationale**: Numbered sequence provides chronological order, clear searchability, and AI-friendly naming that promotes understanding of work progression

---

## Development Commands

### Quality Validation Suite
```bash
# Backend validation
make test                    # Run backend tests with coverage
make lint                    # Backend code linting
make format                  # Backend code formatting

# Frontend validation
make ui-test                 # Run UI unit tests
make ui-lint                 # UI code linting
make ui-format               # UI code formatting

# MANDATORY E2E Testing (Stage 2 Requirement)
make backend-up              # Start backend stack (API + DB + observability)
make ui-dev                  # Start UI development server
make ui-test-e2e             # Run E2E tests (MUST achieve 100% pass rate)

# Complete quality validation
make quality                 # Run complete validation suite (backend + UI + E2E)
```

### E2E Testing Requirements (MANDATORY for Stage 2)
```bash
# CRITICAL: E2E tests require full-stack environment
1. Backend stack must be running: make backend-up
2. UI server must be running: make ui-dev
3. All services must be healthy before E2E execution
4. 100% E2E test pass rate required for Stage 2 completion
5. Any E2E failures block Stage 2 → Stage 3 advancement
```

### Branch and Commit Workflow
```bash
# Story setup
git checkout main
git pull origin main
git checkout -b feature/story-name
git push -u origin feature/story-name

# Task iteration
git add .
git commit -m "feat: implement task description"
git push

# Story completion
git checkout main
git merge feature/story-name
git push origin main
git branch -d feature/story-name
git push origin --delete feature/story-name
```

### Conventional Commit Format
```bash
# Format: type(scope): description
feat(auth): add user authentication system
fix(api): resolve null pointer in user service
docs(readme): update installation instructions
test(utils): add unit tests for validation helpers
```

---

## Current Status

### Active Work Status
**Status**: 🟢 **ACTIVE** - Admin UI Implementation Build & Assess
**Active Work Item**: [`003-story-admin-ui-implementation.md`](changes/003-story-admin-ui-implementation.md)
**Current Task**: Completing Stage 2 BUILD & ASSESS - fixing remaining 5 e2e test failures for clean quality validation
**Current Stage**: Stage 2: BUILD & ASSESS - NEAR COMPLETION 🚀
**AI Context**: 34/39 tests passing, core CRUD flows working, need to fix edit form population & delete confirmation flows
**Last Updated**: 2025-09-22

### Status Update Protocol

**When Starting Work**:
1. Create working document in `changes/` directory using numbered naming convention
2. Update status to ACTIVE with file link
3. Set current task and stage to "Stage 1: PLAN"
4. Provide AI context summary for assistant guidance

**During Development**:
1. Update current stage and AI context as you progress
2. Update last modified timestamp
3. Keep task description and context current
4. Ensure assistant has sufficient information to maintain direction

**When Completing Work**:
1. Update status to INACTIVE
2. Clear active work item details
3. Move completed story to `changes/archived/` directory (maintaining number)
4. Update process learnings for future AI guidance

### Working Document Template
```markdown
# Story: [Story Name]

**File**: `changes/[XXX]-story-[descriptive-name].md`
**Business Value**: [Clear statement of user/business value]
**Current Status**: [Stage 1: PLAN | Stage 2: BUILD & ASSESS | Stage 3: REFLECT & ADAPT | Stage 4: COMMIT & PICK NEXT]

## AI Context & Guidance
**Current Focus**: [What the AI should be focusing on right now]
**Key Constraints**: [Important limitations or requirements to remember]
**Next Steps**: [Clear guidance for what comes next]
**Quality Standards**: [Specific quality criteria for this story]

## Tasks
1. **Task 1**: Given [context] When [action] Then [outcome]
   - **Status**: [Not Started | In Progress | Complete]
   - **Notes**: [Any specific guidance or context]
2. **Task 2**: Given [context] When [action] Then [outcome]
   - **Status**: [Not Started | In Progress | Complete]
   - **Notes**: [Any specific guidance or context]

## Technical Context
**Files to Modify**: [List of files that will be changed]
**Test Strategy**: [How this will be tested]
**Dependencies**: [What this depends on or what depends on this]

## Progress Log
- [Timestamp] - [Stage] - [Activity completed] - [AI guidance notes]

## Quality & Learning Notes
**Quality Reminders**: [Specific quality standards for this work]
**Process Learnings**: [What we're learning about the process]
**AI Support Notes**: [What helps the AI stay on track]

## Reflection & Adaptation
**What's Working**: [Process elements that are effective]
**Improvement Opportunities**: [What could work better]
**Future Considerations**: [Things to consider for next iterations]
```

---

## Process Discipline & Quality Assurance

### Core Values: Quality, Learning, and Flow

**Quality First**: Every stage includes quality gates that ensure high standards are maintained. Clean quality validation prevents technical debt and production issues.

**Continuous Learning**: The reflection stage captures insights and improvements, creating a learning organization that evolves and improves over time.

**Optimal Flow**: The four-stage process creates predictable rhythm and removes blockers, enabling sustainable development velocity.

**AI Assistant Support**: Comprehensive documentation and context ensure AI assistants have sufficient guidance to maintain focus and provide consistent support throughout the development cycle.

### Why These Protocols Matter

**Rigor Prevents Technical Debt**: Structured planning and quality gates prevent shortcuts that create future maintenance burdens.

**User Control Ensures Alignment**: Human oversight at each stage ensures work stays aligned with business objectives and quality standards.

**Documentation Enables Scalability**: Comprehensive tracking allows teams to scale processes and onboard new members effectively.

**Quality Gates Protect Production**: Clean quality validation prevents defects from reaching production environments.

**AI Context Maintains Direction**: Rich contextual information helps AI assistants provide consistent, focused support without losing track of objectives.

**Learning Loops Improve Process**: Regular reflection and adaptation ensure the process evolves and improves based on real experience.

### Success Metrics

- **Quality Score**: Percentage of cycles that complete without quality issues
- **Learning Velocity**: Rate of process improvements implemented and adopted
- **Flow Efficiency**: Cycle time from story planning to production deployment
- **Process Adherence**: Percentage of work items that follow complete four-stage process
- **AI Effectiveness**: How well AI assistants maintain context and provide useful guidance
- **Team Satisfaction**: Developer experience and confidence in the process

---

*Last Updated: [Timestamp will be maintained when status changes]*

**Remember**: This process is designed for **discipline and quality**. Follow it rigorously, and it will deliver consistent, high-quality results. Skip steps or rush through stages, and you compromise the entire development cycle.