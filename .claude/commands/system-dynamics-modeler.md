---
model: claude-sonnet-4-20250514
category: architecture-design
priority: high
tags: ["architecture-design"]
description: System Dynamics Modeler
allowed-tools: Read, Write, Edit, WebSearch
argument-hint: [system-type] | --business-ecosystem | --organizational-dynamics | --market-evolution | --feedback-loops

# Enhanced Context-Aware Agent Integration
enhanced-integration:
  enabled: true
  agent-selection-criteria:
    domain-expertise: ["system-modeling", "dynamics-analysis", "feedback-systems"]
    complexity-factors: ["system-boundary-definition", "feedback-loop-modeling", "emergent-behavior-analysis"]
    specialized-tools: ["system-modeling", "dynamics-simulation", "behavior-analysis"]
  preferred-agents:
    primary: "general-purpose"
    secondary: "system-behavior-simulator"
    fallback: ["task-orchestrator"]
  tool-requirements:
    mcp-servers: ["clear-thought", "perplexity-ask", "cipher-memory"]
    specialized-functions: ["system-modeling", "dynamics-analysis"]

# Universal Cipher Memory Integration (MANDATORY FOR ALL COMMANDS)
cipher-memory-integration:
  enabled: true
  priority: "high"
  
  # Pre-execution Memory Operations
  pre-execution-memory:
    context-search:
      - query-pattern: "system-modeling + dynamics-analysis + feedback-systems"
      - tools: ["mcp__cipher-memory__search_nodes", "mcp__cipher-memory__open_nodes"]
      - context-retrieval: "system-patterns + dynamics-knowledge"
    
    knowledge-preparation:
      - domain: "system-dynamics"
      - pattern-search: "modeling-strategies + dynamics-patterns + feedback-analysis"
      - tools: ["mcp__cipher-memory__read_graph"]
  
  # Execution Memory Operations
  execution-memory:
    progress-tracking:
      - tool: "mcp__cipher-memory__add_observations"
      - capture-points: ["system-modeling", "dynamics-analysis", "behavior-prediction"]
      - entity-updates: "real-time-progress"
    
    decision-logging:
      - tool: "mcp__cipher-memory__create_entities"
      - log-decisions: "modeling-strategies + dynamics-approaches + feedback-techniques"
      - pattern-recognition: "system-dynamics-patterns"
  
  # Post-execution Memory Operations
  post-execution-memory:
    result-storage:
      - tools: ["mcp__cipher-memory__create_entities"]
      - store-patterns: ["dynamics-models", "system-insights", "feedback-techniques"]
      - knowledge-extraction: "dynamics-methodologies + system-patterns"
    
    relationship-creation:
      - tools: ["mcp__cipher-memory__create_relations"]
      - link-concepts: ["system-relationships", "dynamics-dependencies", "feedback-connections"]
      - cross-reference: "related-modeling-processes"
    
    knowledge-refinement:
      - tools: ["mcp__cipher-memory__add_observations"]
      - enrich-existing: "system-knowledge + dynamics-patterns"
      - continuous-learning: "dynamics-modeling-optimization"

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
    - system-modeling
    - dynamics-analysis
    - feedback-identification
    - behavior-prediction
    - error-handling
    - completion-status
  
  # Structured Log Format
  log-structure:
    timestamp: "ISO-8601"
    command: "system-dynamics-modeler"
    execution-id: "UUID"
    agent-assignments: "selected-agents-with-reasoning"
    memory-operations: "cipher-memory-transactions"
    performance-metrics: "execution-time + memory-usage + success-rate"
    outcome-summary: "dynamics-modeling-results + system-insights"

# Cross-Command Learning Integration
cross-command-learning:
  enabled: true
  share-insights: ["system-patterns", "dynamics-techniques", "modeling-methodologies"]
  learn-from: ["system-behavior-simulator", "simulation-calibrator", "architecture-scenario-explorer"]
  contribute-to: "system-modeling-knowledge-base"

# Workflow Integration
workflow-integration:
  pre-execution:
    - validate-system-requirements
    - prepare-memory-context
    - select-optimal-agents
  
  execution:
    - parallel-system-analysis
    - continuous-memory-updates
    - real-time-dynamics-modeling
  
  post-execution:
    - comprehensive-result-storage
    - cross-reference-generation
    - system-pattern-extraction
---

# System Dynamics Modeler

Model complex system dynamics with comprehensive feedback analysis and emergent behavior prediction: **$ARGUMENTS**

## Current System Context

- System type: Based on $ARGUMENTS (business ecosystem, organizational dynamics, market evolution, feedback loops)
- System boundaries: Components, stakeholders, and environmental factors included in the model
- Key variables: Stock and flow variables, feedback mechanisms, and delay structures
- Behavior patterns: Current system performance and historical dynamics

## Task

Build comprehensive system dynamics model with feedback loops and emergent behavior analysis:

**System Type**: Use $ARGUMENTS to model business ecosystems, organizational dynamics, market evolution, or feedback loop systems

**System Dynamics Framework**:
1. **System Architecture** - Stock and flow identification, causal loop mapping, and boundary definition
2. **Feedback Structure** - Reinforcing loops, balancing loops, and delay modeling with policy resistance analysis
3. **Dynamic Simulation** - Time-based behavior analysis, scenario testing, and sensitivity analysis
4. **Emergent Behavior** - Non-linear effects, unintended consequences, and system archetypes identification
5. **Policy Testing** - Intervention analysis, leverage point identification, and strategy optimization
6. **Learning Laboratory** - What-if experimentation, mental model testing, and insight generation

**Advanced Features**: Nonlinear modeling, stochastic elements, multi-level hierarchy modeling, and behavioral dynamics integration.

**Strategic Applications**: Policy design, organizational change, strategic planning, and complex problem solving with systems thinking.

**Output**: Complete system dynamics model with causal structure, simulation results, policy recommendations, and strategic insights for complex system optimization and management.

