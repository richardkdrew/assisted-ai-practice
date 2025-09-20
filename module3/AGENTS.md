# AI Assistant Context Management System

## Overview

This document defines a comprehensive context management system for AI assistants working with Claude Code. The system ensures consistent, reliable project understanding through structured memory loading protocols and context validation procedures.

## Core Philosophy

**Context Before Action**: AI assistants must establish complete project context before executing any tasks. This prevents context drift, ensures consistent decision-making, and maintains project coherence across sessions.

## Memory Bank Architecture

### Mandatory Memory Loading Protocol

**CRITICAL REQUIREMENT**: At the start of EVERY session, the assistant MUST load ALL memory files in the specified order:

1. **`memory/ABOUT.md`** - **PRIMARY CONTEXT** - Project purpose, vision, and core objectives
2. **`memory/ARCHITECTURE.md`** - System design, patterns, and technical architecture
3. **`memory/IMPLEMENTATION.md`** - Current implementation state, decisions, and progress
4. **`memory/ENV_SCRIPTS.md`** - Environment setup, scripts, and development workflows
5. **`memory/WORKFLOW_STATUS.md`** - Current tasks, status, and next steps

### Context Hierarchy

The memory system follows a layered approach:

- **Level 1 - Project Identity**: `ABOUT.md` establishes fundamental project understanding
- **Level 2 - Technical Foundation**: `ARCHITECTURE.md` defines system structure and design
- **Level 3 - Current State**: `IMPLEMENTATION.md` provides current development progress
- **Level 4 - Development Environment**: `ENV_SCRIPTS.md` defines setup and workflow tools
- **Level 5 - Active Status**: `WORKFLOW_STATUS.md` tracks current tasks and priorities

## Session Management

### Startup Checklist

Every assistant session MUST follow this sequence:

1. **Read Primary Documents**:
   - Load `CLAUDE.md` for project overview
   - Process `AGENTS.md` (this document) for context protocols

2. **Execute Memory Loading Protocol**:
   - Load all memory files in specified order
   - Validate memory file accessibility
   - Confirm understanding of current project state

3. **Environment Validation**:
   - Check `.claude/settings.local.json` for permissions
   - Verify development environment status
   - Review recent git history for changes

4. **Context Confirmation**:
   - Acknowledge project objectives from `ABOUT.md`
   - Confirm current development state
   - Identify any missing or outdated context

### Context Validation Checkpoints

The assistant should validate context at these points:

- **Session Start**: Complete memory loading protocol
- **Task Transition**: Before switching between major tasks
- **After Breaks**: When resuming work after interruptions
- **Before Major Changes**: Prior to significant code modifications
- **Context Doubt**: Whenever uncertain about project state

## Memory File Management

### File Organization Standards

- **Atomic Content**: Each memory file focuses on a specific domain
- **Actionable Information**: Content provides clear, implementable guidance
- **Current State**: Files reflect the most recent project understanding
- **Cross-Reference Links**: Files reference related files with specific line numbers
- **Version Awareness**: Content includes timestamps or version indicators

### Update Protocols

Memory files should be updated:

- **After Major Decisions**: Capture architectural or design choices
- **Following Implementation**: Document completed features or changes
- **During Planning**: Record planned approaches or constraints
- **Context Evolution**: When project understanding changes significantly

### Content Guidelines

- **Specificity**: Use precise, technical language
- **Completeness**: Provide sufficient detail for full understanding
- **Clarity**: Structure content for easy scanning and reference
- **Relevance**: Focus on information that affects development decisions
- **Timeliness**: Ensure content reflects current project state

## Context Drift Prevention

### Recognition Patterns

Signs of context drift include:

- Inconsistent architectural decisions
- Deviation from established patterns
- Contradictory implementation approaches
- Confusion about project objectives
- Uncertainty about current system state

### Recovery Procedures

When context drift is detected:

1. **Immediate Stop**: Halt current task execution
2. **Memory Reload**: Re-execute complete memory loading protocol
3. **State Verification**: Confirm current project understanding
4. **Gap Analysis**: Identify missing or outdated context
5. **Memory Update**: Refresh memory files as needed
6. **Resume Safely**: Continue with validated context

## Integration with Claude Code

### Permission Management

The context system integrates with Claude Code permissions:

- Memory files are granted automatic read access
- Context validation commands are pre-approved
- Memory update operations require appropriate write permissions

### Hook Integration

Leverage Claude Code hooks for context management:

- **SessionStart**: Trigger automatic memory loading
- **PreToolUse**: Validate context before major operations
- **PostToolUse**: Update memory files after significant changes

### Tool Coordination

Context management coordinates with Claude Code tools:

- **Read Tool**: Primary mechanism for memory file loading
- **Write/Edit Tools**: Update memory files when context evolves
- **Bash Tool**: Execute context validation commands
- **TodoWrite Tool**: Track context-related tasks

## Best Practices

### For Assistant Behavior

- **Always Load First**: Never begin tasks without complete context loading
- **Validate Regularly**: Confirm context understanding throughout sessions
- **Update Promptly**: Refresh memory files when project state changes
- **Reference Specifically**: Use file paths and line numbers when citing context
- **Acknowledge Gaps**: Identify and address missing context immediately

### For Memory Content

- **Keep Current**: Update files to reflect latest project state
- **Be Specific**: Provide actionable, implementable guidance
- **Cross-Reference**: Link related concepts across memory files
- **Use Structure**: Organize content for easy scanning and reference
- **Include Examples**: Provide concrete examples where helpful

### For Context Validation

- **Systematic Approach**: Follow established protocols consistently
- **Document Changes**: Record context updates in memory files
- **Verify Understanding**: Confirm context comprehension before proceeding
- **Handle Conflicts**: Resolve contradictory information immediately
- **Maintain Coherence**: Ensure consistent understanding across all memory files

## Error Handling

### Context Loading Failures

If memory files cannot be loaded:

1. **Identify Missing Files**: Determine which files are inaccessible
2. **Request Creation**: Ask for missing memory files to be created
3. **Partial Context**: Proceed with available context, noting limitations
4. **Document Gaps**: Record missing context for future resolution

### Context Inconsistencies

When memory files contain conflicting information:

1. **Flag Conflicts**: Identify specific contradictions
2. **Seek Clarification**: Request resolution from project stakeholders
3. **Document Uncertainty**: Note unresolved conflicts in memory files
4. **Proceed Cautiously**: Make conservative decisions until conflicts resolve

### Context Obsolescence

When memory files appear outdated:

1. **Validate Currency**: Check file timestamps and project history
2. **Request Updates**: Ask for memory file refreshes
3. **Note Staleness**: Document potentially outdated information
4. **Conservative Approach**: Favor established patterns over uncertain changes

## System Evolution

This context management system should evolve with project needs:

- **Feedback Integration**: Incorporate lessons learned from context management
- **Process Refinement**: Improve protocols based on experience
- **Tool Enhancement**: Leverage new Claude Code capabilities
- **Scale Adaptation**: Adjust for project size and complexity changes

The goal is maintaining optimal assistant performance through robust, reliable context management that scales with project complexity and team needs.