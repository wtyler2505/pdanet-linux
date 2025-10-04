---
model: claude-sonnet-4-20250514
category: documentation
priority: high
tags: ["documentation", "docs"]
description: Documentation Maintenance & Quality Assurance
allowed-tools: Read, Write, Edit, Bash, Grep
argument-hint: [maintenance-type] | --audit | --update | --validate | --optimize | --comprehensive

# Enhanced Context-Aware Agent Integration
enhanced-integration:
  enabled: true
  agent-selection-criteria:
    domain-expertise: ["documentation-maintenance", "quality-assurance", "content-optimization"]
    complexity-factors: ["documentation-auditing", "content-validation", "maintenance-automation"]
    specialized-tools: ["documentation-analysis", "quality-checking", "content-optimization"]
  preferred-agents:
    primary: "general-purpose"
    secondary: "content-creator"
    fallback: ["task-orchestrator"]
  tool-requirements:
    mcp-servers: ["desktop-commander", "FileScopeMCP", "cipher-memory"]
    specialized-functions: ["documentation-maintenance", "quality-assurance"]

# Universal Cipher Memory Integration (MANDATORY FOR ALL COMMANDS)
cipher-memory-integration:
  enabled: true
  priority: "high"
  
  # Pre-execution Memory Operations
  pre-execution-memory:
    context-search:
      - query-pattern: "documentation-maintenance + quality-assurance + content-optimization"
      - tools: ["mcp__cipher-memory__search_nodes", "mcp__cipher-memory__open_nodes"]
      - context-retrieval: "documentation-patterns + quality-assurance-knowledge"
    
    knowledge-preparation:
      - domain: "documentation-maintenance"
      - pattern-search: "maintenance-strategies + quality-patterns + content-optimization"
      - tools: ["mcp__cipher-memory__read_graph"]
  
  # Execution Memory Operations
  execution-memory:
    progress-tracking:
      - tool: "mcp__cipher-memory__add_observations"
      - capture-points: ["maintenance-analysis", "quality-assessment", "optimization-implementation"]
      - entity-updates: "real-time-progress"
    
    decision-logging:
      - tool: "mcp__cipher-memory__create_entities"
      - log-decisions: "maintenance-strategies + quality-approaches + optimization-techniques"
      - pattern-recognition: "documentation-maintenance-patterns"
  
  # Post-execution Memory Operations
  post-execution-memory:
    result-storage:
      - tools: ["mcp__cipher-memory__create_entities"]
      - store-patterns: ["maintenance-results", "quality-insights", "optimization-techniques"]
      - knowledge-extraction: "documentation-methodologies + quality-patterns"
    
    relationship-creation:
      - tools: ["mcp__cipher-memory__create_relations"]
      - link-concepts: ["maintenance-relationships", "quality-dependencies", "optimization-connections"]
      - cross-reference: "related-documentation-processes"
    
    knowledge-refinement:
      - tools: ["mcp__cipher-memory__add_observations"]
      - enrich-existing: "documentation-knowledge + maintenance-patterns"
      - continuous-learning: "maintenance-process-optimization"

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
    - maintenance-analysis
    - quality-assessment
    - content-optimization
    - validation-execution
    - error-handling
    - completion-status
  
  # Structured Log Format
  log-structure:
    timestamp: "ISO-8601"
    command: "docs-maintenance"
    execution-id: "UUID"
    agent-assignments: "selected-agents-with-reasoning"
    memory-operations: "cipher-memory-transactions"
    performance-metrics: "execution-time + memory-usage + success-rate"
    outcome-summary: "maintenance-results + quality-insights"

# Cross-Command Learning Integration
cross-command-learning:
  enabled: true
  share-insights: ["documentation-patterns", "maintenance-techniques", "quality-assurance-methods"]
  learn-from: ["interactive-documentation", "update-docs", "create-onboarding-guide"]
  contribute-to: "documentation-knowledge-base"

# Workflow Integration
workflow-integration:
  pre-execution:
    - validate-documentation-structure
    - prepare-memory-context
    - select-optimal-agents
  
  execution:
    - parallel-maintenance-analysis
    - continuous-memory-updates
    - real-time-quality-assessment
  
  post-execution:
    - comprehensive-result-storage
    - cross-reference-generation
    - maintenance-pattern-extraction
---

# Documentation Maintenance & Quality Assurance

Implement comprehensive documentation maintenance system: $ARGUMENTS

## Current Documentation Health

- Documentation files: !`find . -name "*.md" -o -name "*.mdx" | wc -l` files
- Last updates: !`find . -name "*.md" -exec stat -f "%m %N" {} \; | sort -n | tail -5`
- External links: !`grep -r "http" --include="*.md" . | wc -l` links to validate
- Image references: !`grep -r "!\[.*\]" --include="*.md" . | wc -l` images to check
- Documentation structure: @docs/ or detect documentation directories

## Task

Create systematic documentation maintenance framework with automated quality assurance, comprehensive validation, content optimization, and regular update procedures.

## Documentation Maintenance Framework

### 1. Content Quality Audit System
- Comprehensive file discovery and categorization
- Content freshness analysis and aging detection
- Word count, readability, and structure assessment
- Missing sections and incomplete documentation identification
- TODO/FIXME marker tracking and resolution planning

### 2. Link and Reference Validation
- External link health monitoring with retry logic
- Internal link validation and broken reference detection
- Image reference verification and missing asset identification
- Cross-reference consistency checking
- Automated link correction suggestions

### 3. Style and Consistency Checking
- Markdown syntax validation and formatting standards
- Heading hierarchy and structure consistency
- List formatting and emphasis style uniformity
- Code block formatting and language specification
- Accessibility compliance (alt text, descriptive links)

### 4. Content Optimization and Enhancement
- Table of contents generation for long documents
- Metadata updating and frontmatter management
- Common formatting issue correction
- Spelling and grammar validation
- Readability analysis and improvement suggestions

### 5. Automated Synchronization System
- Git-based change tracking and documentation updates
- Version control integration with branch management
- Automated commit generation with detailed change logs
- Merge conflict resolution strategies
- Rollback procedures for failed updates

### 6. Quality Assurance Reporting
- Comprehensive audit reports with severity classifications
- Issue categorization and prioritization systems
- Progress tracking and maintenance metrics
- Automated notification systems for critical issues
- Dashboard creation for ongoing monitoring

## Implementation Requirements

### Audit Configuration
- Configurable quality thresholds and validation rules
- Custom style guide integration and enforcement
- Platform-specific optimization settings
- Team collaboration workflow integration
- Automated scheduling and recurring maintenance

### Validation Processes
- Multi-level validation with error categorization
- Batch processing for large documentation sets
- Performance optimization for comprehensive scans
- Integration with existing CI/CD pipelines
- Real-time monitoring and alerting systems

### Reporting and Analytics
- Detailed maintenance reports with actionable insights
- Historical trend analysis and improvement tracking
- Team productivity metrics and documentation health scores
- Integration with project management tools
- Automated stakeholder communication

## Deliverables

1. **Maintenance System Architecture**
   - Automated audit and validation framework
   - Content optimization and enhancement tools
   - Quality assurance reporting infrastructure
   - Version control integration and synchronization

2. **Validation and Quality Tools**
   - Link checking and reference validation systems
   - Style consistency and accessibility compliance tools
   - Content freshness and completeness analyzers
   - Automated correction and enhancement utilities

3. **Reporting and Monitoring**
   - Comprehensive audit reports with prioritized recommendations
   - Real-time monitoring dashboards and alert systems
   - Progress tracking and maintenance history documentation
   - Integration with team communication and project tools

4. **Documentation and Procedures**
   - Implementation guidelines and configuration instructions
   - Team workflow integration and collaboration procedures
   - Troubleshooting guides and maintenance best practices
   - Automated scheduling and recurring maintenance setup

## Integration Guidelines

Implement with existing documentation platforms and development workflows. Ensure scalability for large documentation sets and team collaboration while maintaining quality standards and accessibility compliance.

