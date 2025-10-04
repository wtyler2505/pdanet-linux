---
model: claude-sonnet-4-20250514
category: architecture-design
priority: high
tags: ["architecture-design"]
description: System Behavior Simulator

# Enhanced Context-Aware Agent Integration
enhanced-integration:
  enabled: true
  agent-selection-criteria:
    domain-expertise: ["system-simulation", "behavior-modeling", "performance-analysis"]
    complexity-factors: ["load-modeling", "bottleneck-analysis", "capacity-planning"]
    specialized-tools: ["system-simulation", "performance-modeling", "capacity-analysis"]
  preferred-agents:
    primary: "general-purpose"
    secondary: "performance-optimizer"
    fallback: ["task-orchestrator"]
  tool-requirements:
    mcp-servers: ["clear-thought", "perplexity-ask", "cipher-memory"]
    specialized-functions: ["system-simulation", "performance-analysis"]

# Universal Cipher Memory Integration (MANDATORY FOR ALL COMMANDS)
cipher-memory-integration:
  enabled: true
  priority: "high"
  
  # Pre-execution Memory Operations
  pre-execution-memory:
    context-search:
      - query-pattern: "system-simulation + behavior-modeling + performance-analysis"
      - tools: ["mcp__cipher-memory__search_nodes", "mcp__cipher-memory__open_nodes"]
      - context-retrieval: "simulation-patterns + performance-knowledge"
    
    knowledge-preparation:
      - domain: "system-simulation"
      - pattern-search: "simulation-strategies + behavior-patterns + performance-modeling"
      - tools: ["mcp__cipher-memory__read_graph"]
  
  # Execution Memory Operations
  execution-memory:
    progress-tracking:
      - tool: "mcp__cipher-memory__add_observations"
      - capture-points: ["simulation-modeling", "behavior-analysis", "performance-optimization"]
      - entity-updates: "real-time-progress"
    
    decision-logging:
      - tool: "mcp__cipher-memory__create_entities"
      - log-decisions: "simulation-strategies + modeling-approaches + performance-techniques"
      - pattern-recognition: "system-simulation-patterns"
  
  # Post-execution Memory Operations
  post-execution-memory:
    result-storage:
      - tools: ["mcp__cipher-memory__create_entities"]
      - store-patterns: ["simulation-results", "behavior-insights", "performance-techniques"]
      - knowledge-extraction: "simulation-methodologies + behavior-patterns"
    
    relationship-creation:
      - tools: ["mcp__cipher-memory__create_relations"]
      - link-concepts: ["simulation-relationships", "behavior-dependencies", "performance-connections"]
      - cross-reference: "related-simulation-processes"
    
    knowledge-refinement:
      - tools: ["mcp__cipher-memory__add_observations"]
      - enrich-existing: "simulation-knowledge + behavior-patterns"
      - continuous-learning: "simulation-process-optimization"

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
    - simulation-modeling
    - behavior-analysis
    - performance-optimization
    - capacity-planning
    - error-handling
    - completion-status
  
  # Structured Log Format
  log-structure:
    timestamp: "ISO-8601"
    command: "system-behavior-simulator"
    execution-id: "UUID"
    agent-assignments: "selected-agents-with-reasoning"
    memory-operations: "cipher-memory-transactions"
    performance-metrics: "execution-time + memory-usage + success-rate"
    outcome-summary: "simulation-results + behavior-insights"

# Cross-Command Learning Integration
cross-command-learning:
  enabled: true
  share-insights: ["simulation-patterns", "behavior-modeling-techniques", "performance-analysis-methods"]
  learn-from: ["simulation-calibrator", "architecture-scenario-explorer", "system-dynamics-modeler"]
  contribute-to: "simulation-knowledge-base"

# Workflow Integration
workflow-integration:
  pre-execution:
    - validate-system-requirements
    - prepare-memory-context
    - select-optimal-agents
  
  execution:
    - parallel-simulation-modeling
    - continuous-memory-updates
    - real-time-behavior-analysis
  
  post-execution:
    - comprehensive-result-storage
    - cross-reference-generation
    - simulation-pattern-extraction
---

----|
| Normal Load | 500 RPS | 200ms | 0.1% | 60% CPU |
| Peak Load | 1000 RPS | 800ms | 2.5% | 85% CPU |
| Stress Test | 1500 RPS | 2000ms | 15% | 95% CPU |

### Bottleneck Analysis
- Primary Bottleneck: [most limiting performance factor]
- Secondary Bottlenecks: [additional constraints affecting performance]
- Cascade Effects: [how bottlenecks impact other system components]
- Resolution Priority: [recommended order of bottleneck addressing]

### Optimization Recommendations

#### Immediate Optimizations (0-30 days):
- Quick Wins: [low-effort, high-impact improvements]
- Configuration Tuning: [parameter adjustments and settings optimization]
- Query Optimization: [database and application query improvements]
- Caching Implementation: [strategic caching layer additions]

#### Medium-term Optimizations (1-6 months):
- Architecture Changes: [structural improvements and scaling strategies]
- Infrastructure Upgrades: [hardware and platform enhancements]
- Code Refactoring: [application optimization and efficiency improvements]
- Monitoring Enhancement: [observability and alerting system improvements]

#### Long-term Optimizations (6+ months):
- Technology Migration: [platform or framework modernization]
- System Redesign: [fundamental architecture improvements]
- Capacity Expansion: [infrastructure scaling and geographic distribution]
- Innovation Integration: [new technology adoption and competitive advantage]

### Capacity Planning
- Current Capacity: [existing system limits and headroom]
- Growth Accommodation: [resource scaling for projected demand]
- Cost Implications: [budget requirements for capacity increases]
- Timeline Requirements: [implementation schedule for capacity improvements]

### Monitoring and Alerting Strategy
- Key Performance Indicators: [critical metrics for ongoing monitoring]
- Alert Thresholds: [performance degradation warning levels]
- Escalation Procedures: [response protocols for performance issues]
- Regular Review Schedule: [ongoing optimization and capacity assessment]
```

### 9. Continuous Performance Learning

**Establish ongoing simulation refinement and system optimization:**

#### Performance Validation
- Real-world performance comparison to simulation predictions
- Optimization effectiveness measurement and validation
- User experience correlation with system performance metrics
- Business impact assessment of performance improvements

#### Model Enhancement
- Simulation accuracy improvement based on actual system behavior
- Load pattern refinement and user behavior modeling
- Bottleneck prediction enhancement and early warning systems
- Optimization strategy effectiveness tracking and improvement

## Usage Examples

```bash
# Web application performance simulation
/performance:system-behavior-simulator Simulate e-commerce platform performance under Black Friday traffic with 10x normal load

# API service scaling analysis
/performance:system-behavior-simulator Model REST API performance for mobile app with 1M+ daily active users and geographic distribution

# Database performance optimization
/performance:system-behavior-simulator Simulate database performance for analytics workload with real-time reporting requirements

# Microservices capacity planning
/performance:system-behavior-simulator Model microservices mesh performance under various failure scenarios and auto-scaling conditions
```

## Quality Indicators

- **Green**: Comprehensive load modeling, validated bottleneck analysis, quantified optimization strategies
- **Yellow**: Good load coverage, basic bottleneck identification, estimated optimization benefits
- **Red**: Limited load scenarios, unvalidated bottlenecks, qualitative-only optimization suggestions

## Common Pitfalls to Avoid

- Load unrealism: Testing with artificial patterns that don't match real usage
- Bottleneck tunnel vision: Focusing on single constraints while ignoring others
- Optimization premature: Optimizing for problems that don't exist yet
- Capacity under-planning: Not accounting for growth and traffic spikes
- Monitoring blindness: Not establishing ongoing performance visibility
- Cost ignorance: Optimizing performance without considering budget constraints

Transform system performance from reactive firefighting into proactive, data-driven optimization through comprehensive behavior simulation and capacity planning.


