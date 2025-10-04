---
model: claude-sonnet-4-20250514
category: utilities-tools
priority: high
tags: ["utilities-tools"]
description: Project Reflection - AI Code Assistant Optimization

# Enhanced Context-Aware Agent Integration
enhanced-integration:
  enabled: true
  agent-selection-criteria:
    domain-expertise: ["project-analysis", "ai-optimization", "development-practices"]
    complexity-factors: ["codebase-introspection", "pattern-recognition", "optimization-strategies"]
    specialized-tools: ["project-analysis", "ai-assistant-optimization", "development-insights"]
  preferred-agents:
    primary: "general-purpose"
    secondary: "agent-expert"
    fallback: ["task-orchestrator"]
  tool-requirements:
    mcp-servers: ["FileScopeMCP", "clear-thought", "cipher-memory"]
    specialized-functions: ["project-analysis", "ai-optimization"]

# Universal Cipher Memory Integration (MANDATORY FOR ALL COMMANDS)
cipher-memory-integration:
  enabled: true
  priority: "critical"
  
  # Pre-execution Memory Operations
  pre-execution-memory:
    context-search:
      - query-pattern: "project-analysis + ai-optimization + development-practices"
      - tools: ["mcp__cipher-memory__search_nodes", "mcp__cipher-memory__open_nodes"]
      - context-retrieval: "project-patterns + ai-optimization-knowledge"
    
    knowledge-preparation:
      - domain: "project-reflection"
      - pattern-search: "project-structures + ai-patterns + optimization-strategies"
      - tools: ["mcp__cipher-memory__read_graph"]
  
  # Execution Memory Operations
  execution-memory:
    progress-tracking:
      - tool: "mcp__cipher-memory__add_observations"
      - capture-points: ["project-analysis", "pattern-recognition", "optimization-generation"]
      - entity-updates: "real-time-progress"
    
    decision-logging:
      - tool: "mcp__cipher-memory__create_entities"
      - log-decisions: "analysis-strategies + optimization-approaches + reflection-methodologies"
      - pattern-recognition: "project-reflection-patterns"
  
  # Post-execution Memory Operations
  post-execution-memory:
    result-storage:
      - tools: ["mcp__cipher-memory__create_entities"]
      - store-patterns: ["reflection-results", "optimization-insights", "project-analysis-techniques"]
      - knowledge-extraction: "reflection-methodologies + optimization-patterns"
    
    relationship-creation:
      - tools: ["mcp__cipher-memory__create_relations"]
      - link-concepts: ["project-relationships", "optimization-dependencies", "reflection-connections"]
      - cross-reference: "related-analysis-processes"
    
    knowledge-refinement:
      - tools: ["mcp__cipher-memory__add_observations"]
      - enrich-existing: "project-knowledge + optimization-patterns"
      - continuous-learning: "reflection-process-optimization"

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
    - project-analysis
    - pattern-recognition
    - optimization-generation
    - reflection-synthesis
    - error-handling
    - completion-status
  
  # Structured Log Format
  log-structure:
    timestamp: "ISO-8601"
    command: "project_reflection"
    execution-id: "UUID"
    agent-assignments: "selected-agents-with-reasoning"
    memory-operations: "cipher-memory-transactions"
    performance-metrics: "execution-time + memory-usage + success-rate"
    outcome-summary: "reflection-results + optimization-insights"

# Cross-Command Learning Integration
cross-command-learning:
  enabled: true
  share-insights: ["project-patterns", "optimization-techniques", "reflection-methodologies"]
  learn-from: ["initref", "directory-deep-dive", "create-architecture-documentation"]
  contribute-to: "project-optimization-knowledge-base"

# Workflow Integration
workflow-integration:
  pre-execution:
    - validate-project-state
    - prepare-memory-context
    - select-optimal-agents
  
  execution:
    - parallel-analysis-processing
    - continuous-memory-updates
    - real-time-optimization-generation
  
  post-execution:
    - comprehensive-result-storage
    - cross-reference-generation
    - reflection-pattern-extraction
---

# Project Reflection - AI Code Assistant Optimization

You are an expert in prompt engineering, specializing in optimizing AI code assistant instructions for maximum effectiveness and efficiency.

## Core Objective
Analyze the current project state, codebase patterns, and development practices to generate optimized instructions for AI code assistants working on this project.

## Analysis Process

### 1. Project Context Analysis
- **Architecture Review**: Examine the overall architecture and design patterns
- **Technology Stack**: Identify all technologies, frameworks, and libraries in use
- **Code Conventions**: Detect coding standards, naming conventions, and style guides
- **Directory Structure**: Map the project organization and module boundaries
- **Development Workflow**: Understand git workflow, CI/CD, and deployment processes

### 2. Codebase Pattern Recognition
- **Common Patterns**: Identify recurring design patterns and implementation approaches
- **Anti-patterns**: Detect areas that need improvement or refactoring
- **Technical Debt**: Assess accumulated debt and its impact
- **Quality Metrics**: Evaluate test coverage, documentation, and code quality
- **Performance Characteristics**: Understand performance requirements and optimizations

### 3. Development Practice Assessment
- **Testing Strategy**: Review unit, integration, and e2e testing approaches
- **Documentation Standards**: Assess inline comments, README files, and API docs
- **Error Handling**: Examine error handling patterns and logging practices
- **Security Practices**: Review authentication, authorization, and data protection
- **Dependency Management**: Analyze dependency health and update strategies

### 4. AI Assistant Optimization
Generate specific recommendations for AI assistants working on this project:

#### Context Awareness
- Key files and modules to understand first
- Critical dependencies and their relationships
- Domain-specific terminology and concepts
- Project-specific conventions and rules

#### Task Execution Guidelines
- Preferred implementation patterns for common tasks
- Testing requirements for different types of changes
- Documentation standards to maintain
- Performance considerations to keep in mind
- Security requirements to enforce

#### Common Pitfalls to Avoid
- Known issues and workarounds
- Deprecated patterns to avoid
- Performance bottlenecks to watch for
- Security vulnerabilities to prevent
- Breaking changes to be careful about

### 5. Generated Instructions
Create a comprehensive CLAUDE.md update with:

```markdown
## Project-Specific AI Assistant Instructions

### Quick Context
[Brief project overview and key technologies]

### Critical Files
[List of essential files to understand]

### Implementation Guidelines
[Specific patterns and practices to follow]

### Testing Requirements
[What tests to write/run for different changes]

### Common Tasks
[Step-by-step guides for frequent operations]

### Warnings & Pitfalls
[Things to avoid or be careful about]

### Performance Considerations
[Key performance requirements and optimizations]

### Security Requirements
[Security practices that must be followed]
```

## Execution Steps

1. **Scan Project Structure**
   - Read package.json/Cargo.toml for dependencies
   - Analyze directory structure
   - Review configuration files

2. **Sample Code Analysis**
   - Read 5-10 representative source files
   - Identify coding patterns and conventions
   - Note testing approaches

3. **Documentation Review**
   - Check README.md and other docs
   - Review existing CLAUDE.md if present
   - Examine inline code comments

4. **Workflow Analysis**
   - Review .github/workflows if present
   - Check build/deployment scripts
   - Understand development commands

5. **Generate Optimizations**
   - Create targeted instructions
   - Include specific examples
   - Provide clear do's and don'ts

6. **Output Results**
   - Present findings in structured format
   - Provide actionable recommendations
   - Suggest CLAUDE.md updates

## Output Format

Present findings as:

```
# Project Reflection Analysis

## ðŸ“Š Project Overview
[High-level summary]

## ðŸ—ï¸ Architecture Insights
[Key architectural findings]

## ðŸ“ Code Patterns Detected
[Common patterns and practices]

## âš ï¸ Areas for Improvement
[Technical debt and issues]

## ðŸ¤– AI Assistant Optimization
[Specific instructions for AI assistants]

## ðŸ“‹ Recommended CLAUDE.md Updates
[Proposed additions/changes to CLAUDE.md]

## âœ… Action Items
[Concrete next steps]
```

## Usage
Run this command periodically to keep AI assistant instructions optimized as the project evolves. Especially useful after:
- Major refactoring
- Technology stack changes
- New team members joining
- Significant feature additions
- Architecture updates


