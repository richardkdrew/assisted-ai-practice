# Memory Loading Usage Patterns

This document provides comprehensive guidelines for implementing and using the intelligent memory loading protocol in practice.

## Quick Reference Guide

### Memory Loading Decision Matrix

| Request Type | Keywords Present | File Paths | Complexity | Files Loaded | Memory Bank Status |
|--------------|------------------|------------|------------|--------------|-------------------|
| Technical Action | ✅ | Any | Any | ABOUT + ARCH + TECH | [ADDITIONAL MEMORY BANK: ACTIVE] |
| File Modification | Any | ✅ (.py, .ts, .sql, etc.) | Any | ABOUT + ARCH + TECH | [ADDITIONAL MEMORY BANK: ACTIVE] |
| Complex Change | Any | Any | ✅ | ABOUT + ARCH + TECH | [ADDITIONAL MEMORY BANK: ACTIVE] |
| Informational | ❌ | ❌ | ❌ | ABOUT only | [MEMORY BANK: ACTIVE] |
| Memory Update | Special trigger | Any | Any | ALL FILES | [ADDITIONAL MEMORY BANK: ACTIVE] |

### Implementation Checklist

1. **Start Every Task**:
   - [ ] Analyze user request for technical indicators
   - [ ] Read `memory/ABOUT.md` (mandatory)
   - [ ] Apply intelligent loading logic
   - [ ] Load additional files if triggered
   - [ ] Set appropriate memory bank status

2. **Memory Bank Status Messages**:
   - `[MEMORY BANK: ACTIVE]` - ABOUT.md loaded only
   - `[ADDITIONAL MEMORY BANK: ACTIVE]` - Technical files also loaded

## Detailed Implementation Patterns

### Pattern 1: Standard Technical Request
```
User Request: "Optimize the database connection pooling"

Analysis Process:
1. Check for technical keywords: "optimize", "database" ✅
2. Check for file patterns: None
3. Check for complexity: Medium
4. Decision: Load technical files

Implementation:
1. read_file("memory/ABOUT.md")
2. read_file("memory/ARCHITECTURE.md") 
3. read_file("memory/TECHNICAL.md")
4. Say "[ADDITIONAL MEMORY BANK: ACTIVE]" in next tool use
5. Proceed with optimization task
```

### Pattern 2: File-Specific Request
```
User Request: "Update the application_service.py to add logging"

Analysis Process:
1. Check for technical keywords: "update" ✅
2. Check for file patterns: "application_service.py" (.py extension) ✅
3. Check for complexity: Low
4. Decision: Load technical files (file pattern match)

Implementation:
1. read_file("memory/ABOUT.md")
2. read_file("memory/ARCHITECTURE.md")
3. read_file("memory/TECHNICAL.md")
4. Say "[ADDITIONAL MEMORY BANK: ACTIVE]" in next tool use
5. Proceed with file modification
```

### Pattern 3: Informational Request
```
User Request: "What is the purpose of this configuration service?"

Analysis Process:
1. Check for technical keywords: "service" (but informational context)
2. Check for file patterns: None
3. Check for complexity: Low
4. Decision: Load only ABOUT.md

Implementation:
1. read_file("memory/ABOUT.md")
2. Say "[MEMORY BANK: ACTIVE]" in next tool use
3. Provide explanation based on ABOUT.md content
```

### Pattern 4: Complex Architectural Request
```
User Request: "Add user authentication across the entire system"

Analysis Process:
1. Check for technical keywords: "Add" ✅
2. Check for file patterns: None
3. Check for complexity: "entire system" ✅
4. Decision: Load technical files (complexity match)

Implementation:
1. read_file("memory/ABOUT.md")
2. read_file("memory/ARCHITECTURE.md")
3. read_file("memory/TECHNICAL.md")
4. Say "[ADDITIONAL MEMORY BANK: ACTIVE]" in next tool use
5. Proceed with comprehensive feature implementation
```

### Pattern 5: Memory Update Request
```
User Request: "Update memory with recent changes"

Analysis Process:
1. Special trigger detected: "update memory" ✅
2. Override normal analysis logic
3. Decision: Load ALL memory files

Implementation:
1. read_file("memory/ABOUT.md")
2. read_file("memory/ARCHITECTURE.md")
3. read_file("memory/TECHNICAL.md")
4. Say "[ADDITIONAL MEMORY BANK: ACTIVE]" in next tool use
5. Review and update memory files as needed
```

## Technical Keywords Reference

### Primary Technical Keywords (High Confidence)
```
Core Actions: refactor, optimize, implement, build, create, modify, update, fix, debug, deploy
Technical Areas: api, database, service, component, model, repository, endpoint, schema
Quality: performance, architecture, migration, dependency, scaling, infrastructure
Testing: test, validation, error handling
```

### Secondary Technical Keywords (Medium Confidence)
```
Development: configuration, integration, workflow, automation, monitoring
Architecture: microservice, container, deployment, environment
Data: query, transaction, connection, pooling, caching
Security: authentication, authorization, encryption, validation
```

### File Pattern Matching
```
Backend Files: *.py, *.sql
Frontend Files: *.ts, *.js, *.html, *.css
Configuration: *.json, *.toml, *.yml, *.yaml
Build Files: package.json, pyproject.toml, docker-compose.yml, vite.config.ts
Test Files: *test*, *spec*
```

### Complexity Indicators
```
Scope: entire system, multiple, across, all, comprehensive, full, complete
Integration: end-to-end, integration, workflow, pipeline
Architecture: refactor, redesign, restructure, migrate, scale
```

## Common Usage Scenarios

### Scenario 1: Bug Fix Request
```
Request: "Fix the error handling in the configuration API"
Keywords: "fix", "error handling", "API" → Technical loading ✅
Files: ABOUT.md + ARCHITECTURE.md + TECHNICAL.md
Reasoning: Bug fixes require understanding of technical implementation
```

### Scenario 2: Feature Addition
```
Request: "Add pagination to the configuration list endpoint"
Keywords: "Add", "endpoint" → Technical loading ✅
Files: ABOUT.md + ARCHITECTURE.md + TECHNICAL.md
Reasoning: Feature additions require architectural context
```

### Scenario 3: Documentation Request
```
Request: "Create user documentation for the API"
Keywords: "API" → Technical loading ✅
Files: ABOUT.md + ARCHITECTURE.md + TECHNICAL.md
Reasoning: API documentation requires technical understanding
```

### Scenario 4: Project Explanation
```
Request: "Explain what this project does for new team members"
Keywords: None → Informational loading ✅
Files: ABOUT.md only
Reasoning: General explanation doesn't require technical details
```

### Scenario 5: Performance Analysis
```
Request: "Analyze the current performance bottlenecks"
Keywords: "performance" → Technical loading ✅
Files: ABOUT.md + ARCHITECTURE.md + TECHNICAL.md
Reasoning: Performance analysis requires deep technical knowledge
```

## Best Practices

### 1. Always Start with Analysis
- Never skip the request analysis step
- Consider context, not just keywords
- When in doubt, load technical files (better safe than sorry)

### 2. Memory Bank Status Consistency
- Always include memory bank status in tool uses
- Use correct status based on files loaded
- Maintain status throughout the session

### 3. Session Management
- Technical files loaded once per session
- Status persists until session ends
- Re-evaluate for new conversations

### 4. Error Handling
- If analysis is unclear, ask for clarification
- Default to loading technical files for ambiguous requests
- Log loading decisions for improvement

### 5. Efficiency Considerations
- Don't load unnecessary files for simple requests
- Balance completeness with efficiency
- Monitor false positive/negative rates

## Troubleshooting Guide

### Issue: False Positive Loading
**Symptom**: Technical files loaded for informational requests
**Cause**: Keywords detected without context consideration
**Solution**: Implement context-aware keyword detection

### Issue: False Negative Loading
**Symptom**: Technical files not loaded for technical requests
**Solution**: Expand keyword list or adjust complexity thresholds

### Issue: Inconsistent Memory Bank Status
**Symptom**: Wrong memory bank status messages
**Solution**: Ensure status matches files actually loaded

### Issue: Performance Impact
**Symptom**: Slow response due to unnecessary file loading
**Solution**: Refine detection algorithms to reduce false positives

## Monitoring and Metrics

### Key Metrics to Track
1. **Loading Accuracy**: Percentage of correct loading decisions
2. **False Positive Rate**: Technical loading when not needed
3. **False Negative Rate**: Missing technical loading when needed
4. **User Satisfaction**: Feedback on context appropriateness
5. **Performance Impact**: Time spent on file loading

### Improvement Process
1. Collect usage data and user feedback
2. Analyze patterns in false positives/negatives
3. Adjust keywords, patterns, and thresholds
4. Test changes with validation scenarios
5. Deploy improvements incrementally

## Future Enhancements

### Short-term Improvements
- Context-aware keyword detection
- Enhanced complexity assessment
- User feedback integration

### Long-term Vision
- Machine learning-based request analysis
- Adaptive thresholds based on usage patterns
- Integration with project change tracking
- Personalized loading preferences

## Conclusion

The intelligent memory loading protocol provides a sophisticated yet practical approach to context management. By following these usage patterns and best practices, the system can efficiently provide appropriate context for any type of request while maintaining optimal performance.

The key to success is consistent application of the analysis process and continuous refinement based on real-world usage patterns and user feedback.
