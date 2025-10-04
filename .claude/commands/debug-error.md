---
model: claude-sonnet-4-20250514
category: utilities-tools
priority: critical
tags: ["utilities-tools", "debugging", "error-analysis", "troubleshooting"]
description: Deep-dive debugging with root cause analysis and universal memory integration

# Enhanced Context-Aware Agent Integration with Universal Memory
agent-selection:
  type: "context-aware"
  domain-hints: ["debugging", "error-analysis", "troubleshooting", "rust-debugging", "async-debugging"]
  complexity-level: "complex"
  
  # Enhanced selection criteria for debugging with memory integration
  selection-criteria:
    keyword-match: 0.95       # Strong debugging/error patterns
    argument-analysis: 0.9    # Error context critical for agent selection
    project-context: 0.85     # Project type affects debugging approach
    error-context: 0.95       # Primary use case - error debugging
  
  # Specialized debugging agents with memory capabilities
  preferred-agents: ["rust-async-specialist", "rust-performance-monitor", "general-purpose"]
  fallback-agents: ["general-purpose"]
  confidence-threshold: 0.90

# Enhanced Tool Selection with Universal Memory Integration
tool-selection:
  type: "intelligent-debugging-workflow"
  
  base-tools:
    - "mcp__desktop-commander__start_process"  # For running debug commands
    - "mcp__FileScopeMCP__find_important_files"  # Locate error-related files
    - "mcp__cipher-memory__search_nodes"  # Universal memory integration
  
  conditional-tools:
    rust-debugging:
      - "mcp__desktop-commander__start_process"  # cargo check, clippy, test
      - "mcp__context7__get-library-docs"  # Rust error documentation
      - "mcp__cipher-memory__open_nodes"  # Load similar error patterns
      - "mcp__taskmaster-ai__add_task"  # Create debugging tasks
    
    async-debugging:
      - "mcp__desktop-commander__start_process"  # tokio debugging tools
      - "mcp__cipher-memory__create_relations"  # Connect async patterns
      - "mcp__context7__get-library-docs"  # async/await documentation
    
    performance-debugging:
      - "mcp__desktop-commander__start_process"  # profiling tools
      - "mcp__cipher-memory__add_observations"  # Store performance insights
      - "mcp__FileScopeMCP__recalculate_importance"  # Find perf-critical files
    
    error-pattern-analysis:
      - "mcp__cipher-memory__search_nodes"  # Find similar historical errors
      - "mcp__cipher-memory__create_entities"  # Store new error patterns
      - "mcp__perplexity-ask__perplexity_ask"  # Research unknown errors

# Universal Cipher Memory Integration (MANDATORY FOR ALL COMMANDS)
cipher-memory-integration:
  enabled: true
  priority: "critical"
  pre-execution-memory:
    error-pattern-search:
      - query-pattern: "debug-error + ${error_type} + ${technology_stack}"
      - tools: ["mcp__cipher-memory__search_nodes"]
    historical-debugging:
      - query-pattern: "debugging-methodology + error-resolution + troubleshooting"
      - tools: ["mcp__cipher-memory__open_nodes"]
    knowledge-synthesis:
      - tools: ["mcp__cipher-memory__read_graph"]
      - filter: "debugging-related"
  execution-memory:
    investigation-tracking:
      - tool: "mcp__cipher-memory__add_observations"
      - trigger: "debugging-step-completion"
    pattern-discovery:
      - tool: "mcp__cipher-memory__create_relations"
      - trigger: "error-cause-identified"
    solution-learning:
      - tool: "mcp__cipher-memory__create_entities"
      - trigger: "successful-fix-implemented"
  post-execution-memory:
    debugging-workflow-storage:
      - tools: ["mcp__cipher-memory__create_entities"]
      - content: "complete-debugging-session-pattern"
    error-solution-mapping:
      - tools: ["mcp__cipher-memory__create_relations"]
      - relationships: ["error-type-to-solution", "debugging-tool-to-outcome", "fix-to-prevention"]
    knowledge-enhancement:
      - tools: ["mcp__cipher-memory__add_observations"]
      - content: "debugging-insights + prevention-strategies + tool-effectiveness"

# Centralized Logging Integration (MANDATORY FOR ALL COMMANDS)
logging-integration:
  enabled: true
  log-file: ".claude/logs/command-execution.jsonl"
  log-level: "comprehensive"
  
  log-phases:
    pre-execution:
      - command-metadata
      - error-context-analysis
      - debugging-strategy-selection
      - memory-pattern-analysis
    
    execution:
      - debugging-step-execution
      - tool-invocation-results
      - hypothesis-testing
      - root-cause-investigation
      - solution-implementation
    
    post-execution:
      - debugging-session-summary
      - fix-validation-results
      - memory-operations
      - prevention-recommendations
  
  structured-metadata:
    command-id: "debug-error"
    session-id: "${session_timestamp}"
    user-context: "${user_request}"
    project-context: "${project_type}"
    agent-assigned: "${selected_agent}"
    tools-used: "${tool_list}"
    memory-operations: "${cipher_memory_ops}"
    error-context: "${error_description}"
    debugging-tools: "${debug_tools_used}"
    root-cause: "${identified_cause}"
    solution-type: "${fix_category}"
    prevention-measures: "${preventive_actions}"
    execution-time: "${duration_ms}"
    success-metrics: "${debugging_effectiveness}"

# Enhanced workflow configuration
tool-chain: "universal-debugging-workflow"
auto-deploy: true
parallel-execution: false
memory-persistence: true
cross-command-learning: true
error-pattern-recognition: true

pre-execution:
  validate-tools: true
  load-context: true
  analyze-arguments: true
  detect-project-state: true
  search-error-patterns: true
  log-session-start: true

post-execution:
  store-results: true
  update-learning: true
  generate-report: true
  persist-debugging-knowledge: true
  log-session-complete: true
  update-knowledge-graph: true
---

# Systematically Debug and Fix Errors (Universal Integration)

Systematically debug and fix errors with intelligent pattern recognition, historical error analysis, and persistent learning

**ENHANCED WORKFLOW**: This command utilizes specialized debugging agents (rust-async-specialist, rust-performance-monitor) with complete Cipher Memory integration for error pattern recognition, solution learning, and debugging methodology persistence.

## Enhanced Pre-Execution Memory Analysis
Before debugging, the system will:
1. **Search error patterns**: Query Cipher Memory for similar historical errors and solutions
2. **Load debugging methodology**: Retrieve successful debugging approaches and tools
3. **Analyze error context**: Understanding error types, stack traces, and failure patterns
4. **Connect debugging knowledge**: Access comprehensive troubleshooting patterns

## Instructions

Follow this comprehensive debugging methodology enhanced with universal memory integration to resolve: **$ARGUMENTS**

1. **Error Information Gathering**
   - Collect the complete error message, stack trace, and error code
   - Note when the error occurs (timing, conditions, frequency)
   - Identify the environment where the error happens (dev, staging, prod)
   - Gather relevant logs from before and after the error

2. **Reproduce the Error**
   - Create a minimal test case that reproduces the error consistently
   - Document the exact steps needed to trigger the error
   - Test in different environments if possible
   - Note any patterns or conditions that affect error occurrence

3. **Stack Trace Analysis**
   - Read the stack trace from bottom to top to understand the call chain
   - Identify the exact line where the error originates
   - Trace the execution path leading to the error
   - Look for any obvious issues in the failing code

4. **Code Context Investigation**
   - Examine the code around the error location
   - Check recent changes that might have introduced the bug
   - Review variable values and state at the time of error
   - Analyze function parameters and return values

5. **Hypothesis Formation**
   - Based on evidence, form hypotheses about the root cause
   - Consider common causes:
     - Null pointer/undefined reference
     - Type mismatches
     - Race conditions
     - Resource exhaustion
     - Logic errors
     - External dependency failures

6. **Debugging Tools Setup**
   - Set up appropriate debugging tools for the technology stack
   - Use debugger, profiler, or logging as needed
   - Configure breakpoints at strategic locations
   - Set up monitoring and alerting if not already present

7. **Systematic Investigation**
   - Test each hypothesis methodically
   - Use binary search approach to isolate the problem
   - Add strategic logging or print statements
   - Check data flow and transformations step by step

8. **Data Validation**
   - Verify input data format and validity
   - Check for edge cases and boundary conditions
   - Validate assumptions about data state
   - Test with different data sets to isolate patterns

9. **Dependency Analysis**
   - Check external dependencies and their versions
   - Verify network connectivity and API availability
   - Review configuration files and environment variables
   - Test database connections and query execution

10. **Memory and Resource Analysis**
    - Check for memory leaks or excessive memory usage
    - Monitor CPU and I/O resource consumption
    - Analyze garbage collection patterns if applicable
    - Check for resource deadlocks or contention

11. **Concurrency Issues Investigation**
    - Look for race conditions in multi-threaded code
    - Check synchronization mechanisms and locks
    - Analyze async operations and promise handling
    - Test under different load conditions

12. **Root Cause Identification**
    - Once the cause is identified, understand why it happened
    - Determine if it's a logic error, design flaw, or external issue
    - Assess the scope and impact of the problem
    - Consider if similar issues exist elsewhere

13. **Solution Implementation**
    - Design a fix that addresses the root cause
    - Consider multiple solution approaches and trade-offs
    - Implement the fix with appropriate error handling
    - Add validation and defensive programming where needed

14. **Testing the Fix**
    - Test the fix against the original error case
    - Test edge cases and related scenarios
    - Run regression tests to ensure no new issues
    - Test under various load and stress conditions

15. **Prevention Measures**
    - Add appropriate unit and integration tests
    - Improve error handling and logging
    - Add input validation and defensive checks
    - Update documentation and code comments

16. **Monitoring and Alerting**
    - Set up monitoring for similar issues
    - Add metrics and health checks
    - Configure alerts for error thresholds
    - Implement better observability

17. **Documentation**
    - Document the error, investigation process, and solution
    - Update troubleshooting guides
    - Share learnings with the team
    - Update code comments with context

18. **Post-Resolution Review**
    - Analyze why the error wasn't caught earlier
    - Review development and testing processes
    - Consider improvements to prevent similar issues
    - Update coding standards or guidelines if needed

Remember to maintain detailed notes throughout the debugging process and consider the wider implications of both the error and the fix.

## Universal Memory Integration Outcomes

### Debugging Knowledge Storage
This command will automatically:
- **Store successful debugging sessions** in Cipher Memory for error pattern recognition
- **Create relationships** between error types, debugging tools, and solution effectiveness
- **Document debugging methodologies** and troubleshooting best practices
- **Build knowledge graph** of error-solution mappings and prevention strategies

### Cross-Command Learning Enhancement
Debugging patterns will improve:
- Future error resolution through shared debugging knowledge
- Development commands via error prevention pattern recognition
- Testing commands through documented failure mode analysis
- Monitoring commands via established error signature patterns

### Advanced Debugging Intelligence
- **Error Pattern Recognition**: Automatic identification of similar historical errors
- **Solution Recommendation**: Intelligent suggestions based on successful past fixes  
- **Tool Selection Optimization**: Smart debugging tool selection based on error context
- **Prevention Strategy Generation**: Automated recommendations for preventing similar errors

### Centralized Debugging Logging
All debugging operations logged to `.claude/logs/command-execution.jsonl` including:
- Complete debugging session workflow and tool usage
- Root cause analysis results and solution implementation
- Memory operations for error pattern capture and learning
- Fix validation results and prevention measure effectiveness

**Next Commands**: Enhanced debugging patterns will automatically improve commands like `code-review`, `generate-tests`, `setup-monitoring-observability`, and `test-coverage`.


