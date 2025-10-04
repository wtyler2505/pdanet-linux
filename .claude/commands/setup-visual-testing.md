---
model: claude-sonnet-4-20250514
category: testing-quality
priority: high
tags: ["testing-quality", "testing", "setup"]
description: Setup Visual Testing
allowed-tools: Read, Write, Edit, Bash
argument-hint: [testing-scope] | --components | --pages | --responsive | --cross-browser | --accessibility

# Enhanced Context-Aware Agent Integration
enhanced-integration:
  enabled: true
  agent-selection-criteria:
    domain-expertise: ["visual-testing", "regression-detection", "accessibility-validation"]
    complexity-factors: ["visual-baseline-management", "cross-browser-testing", "responsive-validation"]
    specialized-tools: ["visual-testing-setup", "regression-analysis", "accessibility-checking"]
  preferred-agents:
    primary: "mock-test-orchestrator"
    secondary: "general-purpose"
    fallback: ["task-orchestrator"]
  tool-requirements:
    mcp-servers: ["context7", "desktop-commander", "cipher-memory"]
    specialized-functions: ["visual-testing", "accessibility-validation"]

# Universal Cipher Memory Integration (MANDATORY FOR ALL COMMANDS)
cipher-memory-integration:
  enabled: true
  priority: "high"
  
  # Pre-execution Memory Operations
  pre-execution-memory:
    context-search:
      - query-pattern: "visual-testing + regression-detection + accessibility-validation"
      - tools: ["mcp__cipher-memory__search_nodes", "mcp__cipher-memory__open_nodes"]
      - context-retrieval: "testing-patterns + visual-testing-knowledge"
    
    knowledge-preparation:
      - domain: "visual-testing"
      - pattern-search: "visual-testing-strategies + regression-patterns + accessibility-techniques"
      - tools: ["mcp__cipher-memory__read_graph"]
  
  # Execution Memory Operations
  execution-memory:
    progress-tracking:
      - tool: "mcp__cipher-memory__add_observations"
      - capture-points: ["visual-setup", "baseline-creation", "regression-configuration"]
      - entity-updates: "real-time-progress"
    
    decision-logging:
      - tool: "mcp__cipher-memory__create_entities"
      - log-decisions: "visual-testing-approaches + regression-strategies + accessibility-methods"
      - pattern-recognition: "visual-testing-patterns"
  
  # Post-execution Memory Operations
  post-execution-memory:
    result-storage:
      - tools: ["mcp__cipher-memory__create_entities"]
      - store-patterns: ["visual-testing-setups", "regression-insights", "accessibility-techniques"]
      - knowledge-extraction: "visual-testing-methodologies + regression-patterns"
    
    relationship-creation:
      - tools: ["mcp__cipher-memory__create_relations"]
      - link-concepts: ["testing-relationships", "visual-dependencies", "accessibility-connections"]
      - cross-reference: "related-testing-strategies"
    
    knowledge-refinement:
      - tools: ["mcp__cipher-memory__add_observations"]
      - enrich-existing: "visual-testing-knowledge + regression-patterns"
      - continuous-learning: "visual-testing-optimization"

# Centralized Logging Integration
logging-integration:
  enabled: true
  log-file: ".claude/command-execution.jsonl"
  
  # Comprehensive Execution Logging
  log-level: "comprehensive"
  
  capture-points:
    - command-initiation
    - agent-selection-process
    - memory-operations
    - visual-setup
    - baseline-creation
    - regression-configuration
    - accessibility-validation
    - error-handling
    - completion-status
  
  # Structured Log Format
  log-structure:
    timestamp: "ISO-8601"
    command: "setup-visual-testing"
    execution-id: "UUID"
    agent-assignments: "selected-agents-with-reasoning"
    memory-operations: "cipher-memory-transactions"
    performance-metrics: "execution-time + memory-usage + success-rate"
    outcome-summary: "visual-testing-results + regression-insights"

# Cross-Command Learning Integration
cross-command-learning:
  enabled: true
  share-insights: ["visual-testing-patterns", "regression-techniques", "accessibility-validation-methods"]
  learn-from: ["e2e-setup", "setup-comprehensive-testing", "generate-test-cases"]
  contribute-to: "testing-knowledge-base"

# Workflow Integration
workflow-integration:
  pre-execution:
    - validate-visual-testing-requirements
    - prepare-memory-context
    - select-optimal-agents
  
  execution:
    - parallel-visual-setup
    - continuous-memory-updates
    - real-time-regression-optimization
  
  post-execution:
    - comprehensive-result-storage
    - cross-reference-generation
    - visual-testing-pattern-extraction
---

# Setup Visual Testing

Setup comprehensive visual regression testing with responsive and accessibility validation: **$ARGUMENTS**

## Current Visual Testing Context

- Frontend framework: !`grep -l "react\\|vue\\|angular" package.json 2>/dev/null || echo "Detect framework"`
- UI components: !`find . -name "components" -o -name "src" | head -1 && echo "Component structure detected" || echo "Analyze structure"`
- Existing testing: !`find . -name "cypress" -o -name "playwright" -o -name "storybook" | head -1 || echo "No visual testing"`
- CI system: !`find . -name ".github" -o -name ".gitlab-ci.yml" | head -1 || echo "No CI detected"`

## Task

Implement comprehensive visual testing with regression detection and accessibility validation:

**Testing Scope**: Use $ARGUMENTS to focus on component testing, page testing, responsive testing, cross-browser testing, or accessibility testing

**Visual Testing Framework**:
1. **Tool Selection & Setup** - Choose visual testing tools (Percy, Chromatic, BackstopJS, Playwright), configure integration, setup environments
2. **Baseline Creation** - Capture visual baselines, organize screenshot structure, implement version control, optimize image management
3. **Test Scenario Design** - Create component tests, design page workflows, implement responsive breakpoints, configure browser matrix
4. **Integration Setup** - Configure CI/CD integration, setup automated execution, implement review workflows, optimize performance
5. **Regression Detection** - Configure diff algorithms, setup threshold management, implement approval workflows, optimize accuracy
6. **Advanced Testing** - Setup accessibility testing, configure cross-browser validation, implement responsive testing, design performance monitoring

**Advanced Features**: Automated visual testing, intelligent diff analysis, accessibility compliance checking, responsive design validation, performance visual metrics.

**Quality Assurance**: Test reliability, false positive reduction, maintainability optimization, execution performance.

**Output**: Complete visual testing setup with baseline management, regression detection, CI integration, and comprehensive validation workflows.

