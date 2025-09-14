# Memory Loading Implementation Examples

This document provides concrete examples of how the intelligent memory loading protocol works in practice, demonstrating the decision-making process for different types of user requests.

## Implementation Logic

### Technical Keywords Detection
```python
TECHNICAL_KEYWORDS = [
    'refactor', 'optimize', 'performance', 'architecture', 'migration', 
    'dependency', 'scaling', 'infrastructure', 'optimization', 'implement', 
    'build', 'create', 'modify', 'update', 'fix', 'debug', 'test', 'deploy',
    'api', 'database', 'service', 'component', 'model', 'repository',
    'configuration', 'endpoint', 'schema', 'validation', 'error handling'
]

def contains_technical_keywords(user_request):
    return any(keyword.lower() in user_request.lower() for keyword in TECHNICAL_KEYWORDS)
```

### File Path Pattern Matching
```python
import re

TECHNICAL_PATH_PATTERNS = [
    r'config-service/svc/(api|services|repositories|models)/',
    r'.*\.(py|ts|sql|json|toml|yml|yaml)',
    r'(pyproject\.toml|package\.json|docker-compose\.yml|vite\.config\.ts)',
    r'config-service/.*/test/',
    r'memory/(ARCHITECTURE|TECHNICAL)\.md'
]

def matches_technical_paths(user_request):
    return any(re.search(pattern, user_request) for pattern in TECHNICAL_PATH_PATTERNS)
```

### Complexity Assessment
```python
def assess_complexity(user_request):
    complexity_indicators = [
        'entire system', 'multiple', 'across', 'all', 'comprehensive',
        'full', 'complete', 'end-to-end', 'integration', 'workflow'
    ]
    return any(indicator in user_request.lower() for indicator in complexity_indicators)
```

## Detailed Examples

### Example 1: Clear Technical Request
**User Request**: "Refactor the configuration service API to improve performance"

**Analysis**:
- Technical keywords detected: `refactor`, `performance`, `API`, `service`
- File path patterns: None explicitly mentioned
- Complexity: Medium (specific component focus)

**Decision**: Load ARCHITECTURE.md and TECHNICAL.md
**Reasoning**: Clear technical modification request with performance implications

**Loading Sequence**:
1. Read `memory/ABOUT.md` (mandatory)
2. Detect technical keywords → trigger technical file loading
3. Read `memory/ARCHITECTURE.md`
4. Read `memory/TECHNICAL.md`
5. Say `[ADDITIONAL MEMORY BANK: ACTIVE]` for subsequent tool uses
6. Proceed with refactoring task

### Example 2: File-Specific Technical Request
**User Request**: "Update the application_service.py file to handle errors better"

**Analysis**:
- Technical keywords detected: `update`, `service`
- File path patterns: `application_service.py` (matches `.py` pattern)
- Complexity: Low (single file focus)

**Decision**: Load ARCHITECTURE.md and TECHNICAL.md
**Reasoning**: Specific technical file modification requiring architectural context

**Loading Sequence**:
1. Read `memory/ABOUT.md` (mandatory)
2. Detect file path pattern → trigger technical file loading
3. Read `memory/ARCHITECTURE.md`
4. Read `memory/TECHNICAL.md`
5. Say `[ADDITIONAL MEMORY BANK: ACTIVE]` for subsequent tool uses
6. Proceed with error handling implementation

### Example 3: Non-Technical Informational Request
**User Request**: "Explain the purpose of this project and what it does"

**Analysis**:
- Technical keywords detected: None
- File path patterns: None
- Complexity: Low (informational only)

**Decision**: Load only ABOUT.md
**Reasoning**: Informational request, no technical changes required

**Loading Sequence**:
1. Read `memory/ABOUT.md` (mandatory)
2. No technical indicators detected → skip technical files
3. Proceed with explanation based on ABOUT.md content

### Example 4: Complex Architectural Request
**User Request**: "Add a new feature to manage user permissions across the entire system with database schema changes"

**Analysis**:
- Technical keywords detected: `Add`, `feature`, `database`, `schema`
- File path patterns: None explicitly mentioned
- Complexity: High (`entire system`, `across`)

**Decision**: Load ARCHITECTURE.md and TECHNICAL.md
**Reasoning**: Complex architectural change affecting multiple system layers

**Loading Sequence**:
1. Read `memory/ABOUT.md` (mandatory)
2. Detect technical keywords and complexity indicators → trigger technical file loading
3. Read `memory/ARCHITECTURE.md`
4. Read `memory/TECHNICAL.md`
5. Say `[ADDITIONAL MEMORY BANK: ACTIVE]` for subsequent tool uses
6. Proceed with comprehensive feature implementation

### Example 5: Configuration File Request
**User Request**: "Modify the package.json to add a new dependency"

**Analysis**:
- Technical keywords detected: `modify`, `dependency`
- File path patterns: `package.json` (matches configuration file pattern)
- Complexity: Low (single file focus)

**Decision**: Load ARCHITECTURE.md and TECHNICAL.md
**Reasoning**: Configuration file changes can have architectural implications

**Loading Sequence**:
1. Read `memory/ABOUT.md` (mandatory)
2. Detect configuration file pattern → trigger technical file loading
3. Read `memory/ARCHITECTURE.md`
4. Read `memory/TECHNICAL.md`
5. Say `[ADDITIONAL MEMORY BANK: ACTIVE]` for subsequent tool uses
6. Proceed with dependency modification

### Example 6: Testing Request
**User Request**: "Run the existing tests to make sure everything works"

**Analysis**:
- Technical keywords detected: `test`
- File path patterns: None explicitly mentioned
- Complexity: Low (execution only, no changes)

**Decision**: Load ARCHITECTURE.md and TECHNICAL.md
**Reasoning**: Testing requires understanding of technical architecture

**Loading Sequence**:
1. Read `memory/ABOUT.md` (mandatory)
2. Detect technical keyword `test` → trigger technical file loading
3. Read `memory/ARCHITECTURE.md`
4. Read `memory/TECHNICAL.md`
5. Say `[ADDITIONAL MEMORY BANK: ACTIVE]` for subsequent tool uses
6. Proceed with test execution

### Example 7: Documentation Request
**User Request**: "Create documentation for the API endpoints"

**Analysis**:
- Technical keywords detected: `API`
- File path patterns: None explicitly mentioned
- Complexity: Medium (requires technical understanding)

**Decision**: Load ARCHITECTURE.md and TECHNICAL.md
**Reasoning**: API documentation requires detailed technical knowledge

**Loading Sequence**:
1. Read `memory/ABOUT.md` (mandatory)
2. Detect technical keyword `API` → trigger technical file loading
3. Read `memory/ARCHITECTURE.md`
4. Read `memory/TECHNICAL.md`
5. Say `[ADDITIONAL MEMORY BANK: ACTIVE]` for subsequent tool uses
6. Proceed with documentation creation

## Edge Cases and Special Scenarios

### Edge Case 1: Ambiguous Request
**User Request**: "Make it better"

**Analysis**:
- Technical keywords detected: None clearly
- File path patterns: None
- Complexity: Unclear

**Decision**: Load only ABOUT.md initially, ask for clarification
**Reasoning**: Insufficient context to determine technical requirements

### Edge Case 2: Mixed Request
**User Request**: "Explain the project architecture and then optimize the database queries"

**Analysis**:
- Technical keywords detected: `architecture`, `optimize`, `database`
- File path patterns: None explicitly mentioned
- Complexity: High (mixed informational and technical)

**Decision**: Load ARCHITECTURE.md and TECHNICAL.md
**Reasoning**: Contains both informational and technical components

### Edge Case 3: Memory Update Request
**User Request**: "Update memory with recent changes"

**Analysis**:
- Special trigger: `update memory`
- Requires reading ALL memory files regardless of other indicators

**Decision**: Load ALL memory files (ABOUT.md, ARCHITECTURE.md, TECHNICAL.md)
**Reasoning**: Memory update requires comprehensive review

## Implementation Workflow

```python
def determine_memory_loading_strategy(user_request):
    # Special case: memory update
    if "update memory" in user_request.lower():
        return ["ABOUT.md", "ARCHITECTURE.md", "TECHNICAL.md"]
    
    # Always load core file
    files_to_load = ["ABOUT.md"]
    
    # Check for technical indicators
    if (contains_technical_keywords(user_request) or 
        matches_technical_paths(user_request) or 
        assess_complexity(user_request)):
        files_to_load.extend(["ARCHITECTURE.md", "TECHNICAL.md"])
    
    return files_to_load

def load_memory_files(files_to_load):
    for file in files_to_load:
        content = read_file(f"memory/{file}")
        process_memory_content(content)
    
    if len(files_to_load) > 1:
        print("[ADDITIONAL MEMORY BANK: ACTIVE]")
```

## Benefits of This Approach

1. **Contextual Relevance**: Only loads technical details when needed
2. **Efficiency**: Reduces unnecessary file reading for simple requests
3. **Comprehensive Coverage**: Ensures technical context for technical tasks
4. **Flexibility**: Adapts to various request types automatically
5. **Transparency**: Clear decision-making process with examples
6. **Maintainability**: Easy to extend with new patterns and keywords

## Monitoring and Adjustment

The system should track:
- Loading decisions made
- User satisfaction with loaded context
- False positives/negatives in detection
- Performance impact of loading strategies

This data can be used to refine the detection algorithms and improve accuracy over time.
