---
model: claude-sonnet-4-20250514
category: documentation
priority: high
tags: ["documentation"]
description: Developer Onboarding Guide Generator
allowed-tools: Read, Write, Edit, Bash
argument-hint: [role-type] | --developer | --designer | --devops | --comprehensive | --interactive

# Enhanced Context-Aware Agent Integration
enhanced-integration:
  enabled: true
  agent-selection-criteria:
    domain-expertise: ["onboarding-design", "developer-experience", "documentation-creation"]
    complexity-factors: ["role-based-customization", "interactive-content", "learning-pathways"]
    specialized-tools: ["content-generation", "interactive-documentation", "learning-design"]
  preferred-agents:
    primary: "general-purpose"
    secondary: "content-creator"
    fallback: ["task-orchestrator"]
  tool-requirements:
    mcp-servers: ["desktop-commander", "context7", "cipher-memory"]
    specialized-functions: ["documentation-generation", "content-organization"]

# Universal Cipher Memory Integration (MANDATORY FOR ALL COMMANDS)
cipher-memory-integration:
  enabled: true
  priority: "high"
  
  # Pre-execution Memory Operations
  pre-execution-memory:
    context-search:
      - query-pattern: "onboarding-design + developer-experience + learning-pathways"
      - tools: ["mcp__cipher-memory__search_nodes", "mcp__cipher-memory__open_nodes"]
      - context-retrieval: "onboarding-patterns + developer-experience-knowledge"
    
    knowledge-preparation:
      - domain: "developer-onboarding"
      - pattern-search: "onboarding-strategies + learning-design + developer-workflows"
      - tools: ["mcp__cipher-memory__read_graph"]
  
  # Execution Memory Operations
  execution-memory:
    progress-tracking:
      - tool: "mcp__cipher-memory__add_observations"
      - capture-points: ["onboarding-analysis", "guide-creation", "content-organization"]
      - entity-updates: "real-time-progress"
    
    decision-logging:
      - tool: "mcp__cipher-memory__create_entities"
      - log-decisions: "onboarding-strategies + content-approaches + role-customization"
      - pattern-recognition: "onboarding-design-patterns"
  
  # Post-execution Memory Operations
  post-execution-memory:
    result-storage:
      - tools: ["mcp__cipher-memory__create_entities"]
      - store-patterns: ["onboarding-guides", "developer-experience-insights", "learning-strategies"]
      - knowledge-extraction: "onboarding-methodologies + developer-experience-patterns"
    
    relationship-creation:
      - tools: ["mcp__cipher-memory__create_relations"]
      - link-concepts: ["onboarding-relationships", "learning-dependencies", "role-connections"]
      - cross-reference: "related-onboarding-processes"
    
    knowledge-refinement:
      - tools: ["mcp__cipher-memory__add_observations"]
      - enrich-existing: "onboarding-knowledge + developer-experience-patterns"
      - continuous-learning: "onboarding-process-optimization"

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
    - onboarding-analysis
    - guide-creation
    - content-customization
    - role-adaptation
    - error-handling
    - completion-status
  
  # Structured Log Format
  log-structure:
    timestamp: "ISO-8601"
    command: "create-onboarding-guide"
    execution-id: "UUID"
    agent-assignments: "selected-agents-with-reasoning"
    memory-operations: "cipher-memory-transactions"
    performance-metrics: "execution-time + memory-usage + success-rate"
    outcome-summary: "onboarding-guide-results + developer-experience-insights"

# Cross-Command Learning Integration
cross-command-learning:
  enabled: true
  share-insights: ["onboarding-patterns", "developer-experience-techniques", "learning-design-methods"]
  learn-from: ["setup-development-environment", "interactive-documentation", "docs-maintenance"]
  contribute-to: "developer-experience-knowledge-base"

# Workflow Integration
workflow-integration:
  pre-execution:
    - validate-project-context
    - prepare-memory-context
    - select-optimal-agents
  
  execution:
    - parallel-guide-creation
    - continuous-memory-updates
    - real-time-content-generation
  
  post-execution:
    - comprehensive-result-storage
    - cross-reference-generation
    - onboarding-pattern-extraction
---

# Developer Onboarding Guide Generator

Create developer onboarding guide: $ARGUMENTS

## Current Team Context

- Project setup: @package.json or @requirements.txt or @Cargo.toml (detect tech stack)
- Existing docs: @docs/ or @README.md (if exists)
- Development tools: !`find . -name ".env*" -o -name "docker-compose.yml" -o -name "Makefile" | head -3`
- Team structure: @CODEOWNERS or @.github/ (if exists)
- CI/CD setup: !`find .github/workflows -name "*.yml" 2>/dev/null | head -3`

## Task

Create comprehensive onboarding experience tailored to role and project needs:

1. **Onboarding Requirements Analysis**
   - Analyze current team structure and skill requirements
   - Identify key knowledge areas and learning objectives
   - Assess current onboarding challenges and pain points
   - Define onboarding timeline and milestone expectations
   - Document role-specific requirements and responsibilities

2. **Development Environment Setup Guide**
   - Create comprehensive development environment setup instructions
   - Document required tools, software, and system requirements
   - Provide step-by-step installation and configuration guides
   - Create environment validation and troubleshooting procedures
   - Set up automated environment setup scripts and tools

3. **Project and Codebase Overview**
   - Create high-level project overview and business context
   - Document system architecture and technology stack
   - Provide codebase structure and organization guide
   - Create code navigation and exploration guidelines
   - Document key modules, libraries, and frameworks used

4. **Development Workflow Documentation**
   - Document version control workflows and branching strategies
   - Create code review process and quality standards guide
   - Document testing practices and requirements
   - Provide deployment and release process overview
   - Create issue tracking and project management workflow guide

5. **Team Communication and Collaboration**
   - Document team communication channels and protocols
   - Create meeting schedules and participation guidelines
   - Provide team contact information and org chart
   - Document collaboration tools and access procedures
   - Create escalation procedures and support contacts

6. **Learning Resources and Training Materials**
   - Curate learning resources for project-specific technologies
   - Create hands-on tutorials and coding exercises
   - Provide links to documentation, wikis, and knowledge bases
   - Create video tutorials and screen recordings
   - Set up mentoring and buddy system procedures

7. **First Tasks and Milestones**
   - Create progressive difficulty task assignments
   - Define learning milestones and checkpoints
   - Provide "good first issues" and starter projects
   - Create hands-on coding challenges and exercises
   - Set up pair programming and shadowing opportunities

8. **Security and Compliance Training**
   - Document security policies and access controls
   - Create data handling and privacy guidelines
   - Provide compliance training and certification requirements
   - Document incident response and security procedures
   - Create security best practices and guidelines

9. **Tools and Resources Access**
   - Document required accounts and access requests
   - Create tool-specific setup and usage guides
   - Provide license and subscription information
   - Document VPN and network access procedures
   - Create troubleshooting guides for common access issues

10. **Feedback and Continuous Improvement**
    - Create onboarding feedback collection process
    - Set up regular check-ins and progress reviews
    - Document common questions and FAQ section
    - Create onboarding metrics and success tracking
    - Establish onboarding guide maintenance and update procedures
    - Set up new hire success monitoring and support systems

