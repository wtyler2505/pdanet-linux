---
model: claude-sonnet-4-20250514
category: documentation
priority: high
tags: ["documentation", "docs"]
description: Interactive Documentation Platform
allowed-tools: Read, Write, Edit, Bash
argument-hint: [platform] | --docusaurus | --gitbook | --notion | --storybook | --jupyter | --comprehensive

# Enhanced Context-Aware Agent Integration
enhanced-integration:
  enabled: true
  agent-selection-criteria:
    domain-expertise: ["interactive-documentation", "platform-development", "user-experience"]
    complexity-factors: ["platform-integration", "interactive-features", "user-engagement"]
    specialized-tools: ["documentation-platforms", "interactive-development", "engagement-optimization"]
  preferred-agents:
    primary: "general-purpose"
    secondary: "ui-controls-architect"
    fallback: ["task-orchestrator"]
  tool-requirements:
    mcp-servers: ["context7", "desktop-commander", "cipher-memory"]
    specialized-functions: ["interactive-documentation", "platform-development"]

# Universal Cipher Memory Integration (MANDATORY FOR ALL COMMANDS)
cipher-memory-integration:
  enabled: true
  priority: "high"
  
  # Pre-execution Memory Operations
  pre-execution-memory:
    context-search:
      - query-pattern: "interactive-documentation + platform-development + user-experience"
      - tools: ["mcp__cipher-memory__search_nodes", "mcp__cipher-memory__open_nodes"]
      - context-retrieval: "documentation-patterns + platform-knowledge"
    
    knowledge-preparation:
      - domain: "interactive-documentation"
      - pattern-search: "documentation-platforms + interactive-patterns + engagement-strategies"
      - tools: ["mcp__cipher-memory__read_graph"]
  
  # Execution Memory Operations
  execution-memory:
    progress-tracking:
      - tool: "mcp__cipher-memory__add_observations"
      - capture-points: ["platform-selection", "interactive-development", "user-engagement"]
      - entity-updates: "real-time-progress"
    
    decision-logging:
      - tool: "mcp__cipher-memory__create_entities"
      - log-decisions: "platform-choices + interactive-strategies + engagement-approaches"
      - pattern-recognition: "interactive-documentation-patterns"
  
  # Post-execution Memory Operations
  post-execution-memory:
    result-storage:
      - tools: ["mcp__cipher-memory__create_entities"]
      - store-patterns: ["documentation-platforms", "interactive-insights", "engagement-techniques"]
      - knowledge-extraction: "documentation-methodologies + interactive-patterns"
    
    relationship-creation:
      - tools: ["mcp__cipher-memory__create_relations"]
      - link-concepts: ["platform-relationships", "interactive-dependencies", "engagement-connections"]
      - cross-reference: "related-documentation-processes"
    
    knowledge-refinement:
      - tools: ["mcp__cipher-memory__add_observations"]
      - enrich-existing: "documentation-knowledge + interactive-patterns"
      - continuous-learning: "documentation-platform-optimization"

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
    - platform-selection
    - interactive-development
    - user-engagement-optimization
    - content-integration
    - error-handling
    - completion-status
  
  # Structured Log Format
  log-structure:
    timestamp: "ISO-8601"
    command: "interactive-documentation"
    execution-id: "UUID"
    agent-assignments: "selected-agents-with-reasoning"
    memory-operations: "cipher-memory-transactions"
    performance-metrics: "execution-time + memory-usage + success-rate"
    outcome-summary: "documentation-platform-results + interactive-insights"

# Cross-Command Learning Integration
cross-command-learning:
  enabled: true
  share-insights: ["documentation-patterns", "interactive-techniques", "platform-development-methods"]
  learn-from: ["docs-maintenance", "create-architecture-documentation", "create-onboarding-guide"]
  contribute-to: "documentation-knowledge-base"

# Workflow Integration
workflow-integration:
  pre-execution:
    - validate-documentation-requirements
    - prepare-memory-context
    - select-optimal-agents
  
  execution:
    - parallel-platform-development
    - continuous-memory-updates
    - real-time-interactive-optimization
  
  post-execution:
    - comprehensive-result-storage
    - cross-reference-generation
    - documentation-pattern-extraction
---

# Interactive Documentation Platform

Create interactive documentation with live examples: $ARGUMENTS

## Current Documentation Infrastructure

- Static site generators: !`find . -name "docusaurus.config.js" -o -name "gatsby-config.js" -o -name "_config.yml" | head -3`
- Documentation framework: @docs/ or @website/ (detect existing setup)
- Component libraries: !`find . -name "*.stories.*" | head -5` (Storybook detection)
- Interactive examples: !`find . -name "*.ipynb" -o -name "*playground*" | head -3`
- Hosting setup: @vercel.json or @netlify.toml or @.github/workflows/ (if exists)

## Task

Build comprehensive interactive documentation platform with live code examples, user engagement features, and multi-platform integration capabilities.

## Interactive Documentation Architecture

### 1. Platform Foundation and Configuration
- Documentation platform selection and optimization setup
- Theme customization and branding configuration
- Navigation structure and content organization
- Multi-language support and internationalization
- Search integration with advanced filtering and indexing

### 2. Live Code Playground Integration
- Interactive code editor with syntax highlighting
- Real-time code execution and preview capabilities
- Multi-language support and framework integration
- Error handling and debugging assistance
- Code sharing and collaboration features

### 3. API Documentation and Testing
- Interactive API endpoint exploration
- Live request/response testing capabilities
- Parameter validation and example generation
- Authentication flow integration
- Response schema visualization and validation

### 4. Interactive Tutorial System
- Step-by-step guided learning experiences
- Progress tracking and completion validation
- Hands-on coding exercises with instant feedback
- Adaptive learning paths based on user progress
- Gamification elements and achievement systems

### 5. Component Documentation Integration
- Live component playground with property controls
- Visual component gallery with interactive examples
- Design system integration and style guide generation
- Accessibility testing and compliance validation
- Cross-browser compatibility testing

### 6. User Engagement and Feedback Systems
- Rating and review collection mechanisms
- User feedback aggregation and analysis
- Community discussion and Q&A integration
- Usage analytics and behavior tracking
- Personalization and recommendation systems

### 7. Content Management and Publishing
- Version control integration with automated publishing
- Content review and approval workflows
- Multi-author collaboration and editing
- Content scheduling and automated updates
- SEO optimization and metadata management

### 8. Advanced Interactive Features
- Advanced search with faceted filtering and suggestions
- Interactive diagrams and visualization tools
- Embedded video content and multimedia integration
- Mobile-responsive design and offline capabilities
- Progressive web app features and notifications

## Implementation Requirements

### Platform Integration
- Multi-framework support (React, Vue, Angular, vanilla JS)
- Build system integration with automated deployment
- Content management system compatibility
- Third-party service integration (analytics, feedback, search)
- Performance optimization and bundle splitting

### User Experience Design
- Responsive design across all device types
- Accessibility compliance (WCAG 2.1 AA standards)
- Progressive enhancement for feature degradation
- Fast loading times and optimal Core Web Vitals
- Intuitive navigation and content discovery

### Technical Infrastructure
- Scalable hosting and CDN configuration
- Database integration for user data and analytics
- API design for external integrations
- Security implementation and user authentication
- Monitoring and error tracking systems

## Deliverables

1. **Interactive Platform Architecture**
   - Complete documentation platform setup and configuration
   - Live code playground and API testing integration
   - Interactive tutorial system with progress tracking
   - Component documentation with visual examples

2. **User Engagement Systems**
   - Feedback collection and analysis mechanisms
   - User analytics and behavior tracking implementation
   - Community features and discussion integration
   - Personalization and recommendation engines

3. **Content Management Framework**
   - Automated publishing and deployment pipelines
   - Multi-author collaboration and review workflows
   - Version control integration with change tracking
   - SEO optimization and metadata management

4. **Performance and Optimization**
   - Mobile-responsive design with offline capabilities
   - Performance monitoring and optimization implementation
   - Accessibility compliance and testing frameworks
   - Progressive web app features and service workers

## Integration Guidelines

Implement with modern documentation platforms and development workflows. Ensure scalability for large content repositories and team collaboration while maintaining optimal performance and user experience across all devices and platforms.

