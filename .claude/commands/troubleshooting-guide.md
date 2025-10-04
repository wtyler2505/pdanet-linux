---
model: claude-sonnet-4-20250514
category: utilities-tools
priority: high
tags: ["utilities-tools", "debugging", "troubleshooting", "system-diagnosis", "problem-solving"]
description: Comprehensive troubleshooting guide generation with universal memory integration and intelligent diagnostic pattern recognition

# Enhanced Context-Aware Agent Integration with Universal Memory
agent-selection:
  type: "context-aware"
  domain-hints: ["troubleshooting", "system-diagnosis", "problem-solving", "debugging", "system-administration"]
  complexity-level: "complex"
  
  # Enhanced selection criteria for troubleshooting guide with memory integration
  selection-criteria:
    keyword-match: 0.95       # Strong troubleshooting/debugging patterns
    argument-analysis: 0.85   # System component context critical
    project-context: 0.90     # Infrastructure type affects troubleshooting approach
    error-context: 0.95       # Primary use case - system issues
  
  # Specialized troubleshooting agents with memory capabilities
  preferred-agents: ["general-purpose", "rust-async-specialist", "serial-hardware-specialist"]
  fallback-agents: ["general-purpose"]
  confidence-threshold: 0.85

# Enhanced Tool Selection with Universal Memory Integration
tool-selection:
  type: "intelligent-troubleshooting-workflow"
  
  base-tools:
    - "mcp__desktop-commander__start_process"  # Run diagnostic commands
    - "mcp__FileScopeMCP__find_important_files"  # Analyze system components
    - "mcp__cipher-memory__search_nodes"  # Universal memory integration
  
  conditional-tools:
    system-diagnosis:
      - "mcp__desktop-commander__start_process"  # System diagnostic tools
      - "mcp__context7__get-library-docs"  # System administration docs
      - "mcp__cipher-memory__open_nodes"  # Load troubleshooting patterns
    
    application-troubleshooting:
      - "mcp__FileScopeMCP__recalculate_importance"  # Critical application files
      - "mcp__cipher-memory__create_entities"  # Store troubleshooting insights
      - "mcp__desktop-commander__search_code"  # Search for error patterns
    
    infrastructure-analysis:
      - "mcp__cipher-memory__add_observations"  # Store infrastructure insights
      - "mcp__desktop-commander__start_process"  # Infrastructure diagnostic tools
      - "mcp__cipher-memory__create_relations"  # Connect infrastructure patterns
    
    problem-resolution:
      - "mcp__perplexity-ask__perplexity_ask"  # Research complex issues
      - "mcp__cipher-memory__create_entities"  # Store resolution patterns
      - "mcp__taskmaster-ai__add_task"  # Create resolution tasks

# Universal Cipher Memory Integration (MANDATORY FOR ALL COMMANDS)
cipher-memory-integration:
  enabled: true
  priority: "critical"
  pre-execution-memory:
    troubleshooting-patterns-search:
      - query-pattern: "troubleshooting + system-diagnosis + ${system_component}-issues"
      - tools: ["mcp__cipher-memory__search_nodes"]
    diagnostic-procedures:
      - query-pattern: "diagnostic-procedures + problem-solving + ${infrastructure_type}"
      - tools: ["mcp__cipher-memory__open_nodes"]
    resolution-strategies:
      - tools: ["mcp__cipher-memory__read_graph"]
      - filter: "troubleshooting-related"
  execution-memory:
    guide-progress-tracking:
      - tool: "mcp__cipher-memory__add_observations"
      - trigger: "troubleshooting-section-completion"
    pattern-identification:
      - tool: "mcp__cipher-memory__create_relations"
      - trigger: "effective-diagnostic-identified"
    solution-learning:
      - tool: "mcp__cipher-memory__create_entities"
      - trigger: "comprehensive-solution-documented"
  post-execution-memory:
    guide-methodology-storage:
      - tools: ["mcp__cipher-memory__create_entities"]
      - content: "complete-troubleshooting-guide-session-pattern"
    diagnostic-pattern-mapping:
      - tools: ["mcp__cipher-memory__create_relations"]
      - relationships: ["issue-type-to-solution", "diagnostic-to-resolution", "system-to-troubleshooting"]
    knowledge-enhancement:
      - tools: ["mcp__cipher-memory__add_observations"]
      - content: "troubleshooting-insights + diagnostic-strategies + resolution-optimization"

# Centralized Logging Integration (MANDATORY FOR ALL COMMANDS)
logging-integration:
  enabled: true
  log-file: ".claude/logs/command-execution.jsonl"
  log-level: "comprehensive"
  
  log-phases:
    pre-execution:
      - command-metadata
      - troubleshooting-scope-analysis
      - diagnostic-pattern-search
      - memory-pattern-analysis
    
    execution:
      - system-analysis-results
      - diagnostic-procedure-creation
      - solution-documentation
      - guide-structure-generation
      - cross-reference-creation
    
    post-execution:
      - guide-completion-summary
      - diagnostic-effectiveness-assessment
      - memory-operations
      - troubleshooting-recommendations
  
  structured-metadata:
    command-id: "troubleshooting-guide"
    session-id: "${session_timestamp}"
    user-context: "${user_request}"
    project-context: "${project_type}"
    agent-assigned: "${selected_agent}"
    tools-used: "${tool_list}"
    memory-operations: "${cipher_memory_ops}"
    system-component: "${troubleshooting_scope}"
    guide-sections-created: "${guide_sections_count}"
    diagnostic-procedures: "${diagnostic_procedures_count}"
    solutions-documented: "${solutions_count}"
    cross-references: "${cross_reference_count}"
    execution-time: "${duration_ms}"
    guide-quality-score: "${troubleshooting_effectiveness}"

# Enhanced workflow configuration
tool-chain: "universal-troubleshooting-workflow"
auto-deploy: true
parallel-execution: false
memory-persistence: true
cross-command-learning: true
troubleshooting-pattern-recognition: true

allowed-tools: Read, Write, Edit, Bash, mcp__desktop-commander__*, mcp__FileScopeMCP__*, mcp__context7__*, mcp__cipher-memory__*, mcp__perplexity-ask__*, mcp__taskmaster-ai__*

argument-hint: [system-component] | --application | --database | --network | --deployment | --comprehensive | --interactive

pre-execution:
  validate-tools: true
  load-context: true
  analyze-system-architecture: true
  search-troubleshooting-patterns: true
  log-session-start: true

post-execution:
  store-results: true
  update-learning: true
  generate-report: true
  persist-troubleshooting-knowledge: true
  log-session-complete: true
  update-knowledge-graph: true
---

# Troubleshooting Guide Generator (Universal Integration)

Generate comprehensive troubleshooting documentation with universal memory integration and intelligent diagnostic pattern recognition: $ARGUMENTS

**ENHANCED WORKFLOW**: This command utilizes specialized troubleshooting agents (rust-async-specialist, serial-hardware-specialist) with complete Cipher Memory integration for troubleshooting pattern recognition, diagnostic optimization, and resolution methodology persistence.

## Enhanced Pre-Execution Memory Analysis
Before guide generation, the system will:
1. **Search troubleshooting patterns**: Query Cipher Memory for effective diagnostic procedures and resolution strategies
2. **Load system knowledge**: Retrieve system administration best practices and infrastructure troubleshooting patterns
3. **Analyze diagnostic strategies**: Understanding problem-solving methodologies and systematic diagnosis approaches
4. **Connect resolution knowledge**: Access comprehensive troubleshooting resolution and prevention patterns

## Current System Context

- System architecture: @docker-compose.yml or @k8s/ or detect deployment type
- Log locations: !`find . -name "*log*" -type d | head -3`
- Monitoring setup: !`grep -r "prometheus\|grafana\|datadog" . 2>/dev/null | wc -l` monitoring references
- Error patterns: !`find . -name "*.log" | head -3` recent logs
- Health endpoints: !`grep -r "health\|status" src/ 2>/dev/null | head -3`

## Task

Create comprehensive troubleshooting guide with systematic diagnostic procedures: $ARGUMENTS

1. **System Overview and Architecture**
   - Document the system architecture and components
   - Map out dependencies and integrations
   - Identify critical paths and failure points
   - Create system topology diagrams
   - Document data flow and communication patterns

2. **Common Issues Identification**
   - Collect historical support tickets and issues
   - Interview team members about frequent problems
   - Analyze error logs and monitoring data
   - Review user feedback and complaints
   - Identify patterns in system failures

3. **Troubleshooting Framework**
   - Establish systematic diagnostic procedures
   - Create problem isolation methodologies
   - Document escalation paths and procedures
   - Set up logging and monitoring checkpoints
   - Define severity levels and response times

4. **Diagnostic Tools and Commands**
   
   ```markdown
   ## Essential Diagnostic Commands
   
   ### System Health
   ```bash
   # Check system resources
   top                    # CPU and memory usage
   df -h                 # Disk space
   free -m               # Memory usage
   netstat -tuln         # Network connections
   
   # Application logs
   tail -f /var/log/app.log
   journalctl -u service-name -f
   
   # Database connectivity
   mysql -u user -p -e "SELECT 1"
   psql -h host -U user -d db -c "SELECT 1"
   ```
   ```

5. **Issue Categories and Solutions**

   **Performance Issues:**
   ```markdown
   ### Slow Response Times
   
   **Symptoms:**
   - API responses > 5 seconds
   - User interface freezing
   - Database timeouts
   
   **Diagnostic Steps:**
   1. Check system resources (CPU, memory, disk)
   2. Review application logs for errors
   3. Analyze database query performance
   4. Check network connectivity and latency
   
   **Common Causes:**
   - Database connection pool exhaustion
   - Inefficient database queries
   - Memory leaks in application
   - Network bandwidth limitations
   
   **Solutions:**
   - Restart application services
   - Optimize database queries
   - Increase connection pool size
   - Scale infrastructure resources
   ```

6. **Error Code Documentation**
   
   ```markdown
   ## Error Code Reference
   
   ### HTTP Status Codes
   - **500 Internal Server Error**
     - Check application logs for stack traces
     - Verify database connectivity
     - Check environment variables
   
   - **404 Not Found**
     - Verify URL routing configuration
     - Check if resources exist
     - Review API endpoint documentation
   
   - **503 Service Unavailable**
     - Check service health status
     - Verify load balancer configuration
     - Check for maintenance mode
   ```

7. **Environment-Specific Issues**
   - Document development environment problems
   - Address staging/testing environment issues
   - Cover production-specific troubleshooting
   - Include local development setup problems

8. **Database Troubleshooting**
   
   ```markdown
   ### Database Connection Issues
   
   **Symptoms:**
   - "Connection refused" errors
   - "Too many connections" errors
   - Slow query performance
   
   **Diagnostic Commands:**
   ```sql
   -- Check active connections
   SHOW PROCESSLIST;
   
   -- Check database size
   SELECT table_schema, 
          ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) AS 'DB Size in MB' 
   FROM information_schema.tables 
   GROUP BY table_schema;
   
   -- Check slow queries
   SHOW VARIABLES LIKE 'slow_query_log';
   ```
   ```

9. **Network and Connectivity Issues**
   
   ```markdown
   ### Network Troubleshooting
   
   **Basic Connectivity:**
   ```bash
   # Test basic connectivity
   ping example.com
   telnet host port
   curl -v https://api.example.com/health
   
   # DNS resolution
   nslookup example.com
   dig example.com
   
   # Network routing
   traceroute example.com
   ```
   
   **SSL/TLS Issues:**
   ```bash
   # Check SSL certificate
   openssl s_client -connect example.com:443
   curl -vI https://example.com
   ```
   ```

10. **Application-Specific Troubleshooting**
    
    **Memory Issues:**
    ```markdown
    ### Out of Memory Errors
    
    **Java Applications:**
    ```bash
    # Check heap usage
    jstat -gc [PID]
    jmap -dump:format=b,file=heapdump.hprof [PID]
    
    # Analyze heap dump
    jhat heapdump.hprof
    ```
    
    **Node.js Applications:**
    ```bash
    # Monitor memory usage
    node --inspect app.js
    # Use Chrome DevTools for memory profiling
    ```
    ```

11. **Security and Authentication Issues**
    
    ```markdown
    ### Authentication Failures
    
    **Symptoms:**
    - 401 Unauthorized responses
    - Token validation errors
    - Session timeout issues
    
    **Diagnostic Steps:**
    1. Verify credentials and tokens
    2. Check token expiration
    3. Validate authentication service
    4. Review CORS configuration
    
    **Common Solutions:**
    - Refresh authentication tokens
    - Clear browser cookies/cache
    - Verify CORS headers
    - Check API key permissions
    ```

12. **Deployment and Configuration Issues**
    
    ```markdown
    ### Deployment Failures
    
    **Container Issues:**
    ```bash
    # Check container status
    docker ps -a
    docker logs container-name
    
    # Check resource limits
    docker stats
    
    # Debug container
    docker exec -it container-name /bin/bash
    ```
    
    **Kubernetes Issues:**
    ```bash
    # Check pod status
    kubectl get pods
    kubectl describe pod pod-name
    kubectl logs pod-name
    
    # Check service connectivity
    kubectl get svc
    kubectl port-forward pod-name 8080:8080
    ```
    ```

13. **Monitoring and Alerting Setup**
    - Configure health checks and monitoring
    - Set up log aggregation and analysis
    - Implement alerting for critical issues
    - Create dashboards for system metrics
    - Document monitoring thresholds

14. **Escalation Procedures**
    
    ```markdown
    ## Escalation Matrix
    
    ### Severity Levels
    
    **Critical (P1):** System down, data loss
    - Immediate response required
    - Escalate to on-call engineer
    - Notify management within 30 minutes
    
    **High (P2):** Major functionality impaired
    - Response within 2 hours
    - Escalate to senior engineer
    - Provide hourly updates
    
    **Medium (P3):** Minor functionality issues
    - Response within 8 hours
    - Assign to appropriate team member
    - Provide daily updates
    ```

15. **Recovery Procedures**
    - Document system recovery steps
    - Create data backup and restore procedures
    - Establish rollback procedures for deployments
    - Document disaster recovery processes
    - Test recovery procedures regularly

16. **Preventive Measures**
    - Implement monitoring and alerting
    - Set up automated health checks
    - Create deployment validation procedures
    - Establish code review processes
    - Document maintenance procedures

17. **Knowledge Base Integration**
    - Link to relevant documentation
    - Reference API documentation
    - Include links to monitoring dashboards
    - Connect to team communication channels
    - Integrate with ticketing systems

18. **Team Communication**
    
    ```markdown
    ## Communication Channels
    
    ### Immediate Response
    - Slack: #incidents channel
    - Phone: On-call rotation
    - Email: alerts@company.com
    
    ### Status Updates
    - Status page: status.company.com
    - Twitter: @company_status
    - Internal wiki: troubleshooting section
    ```

19. **Documentation Maintenance**
    - Regular review and updates
    - Version control for troubleshooting guides
    - Feedback collection from users
    - Integration with incident post-mortems
    - Continuous improvement processes

20. **Self-Service Tools**
    - Create diagnostic scripts and tools
    - Build automated recovery procedures
    - Implement self-healing systems
    - Provide user-friendly diagnostic interfaces
    - Create chatbot integration for common issues

**Advanced Troubleshooting Techniques:**

**Log Analysis:**
```bash
# Search for specific errors
grep -i "error" /var/log/app.log | tail -50

# Analyze log patterns
awk '{print $1}' access.log | sort | uniq -c | sort -nr

# Monitor logs in real-time
tail -f /var/log/app.log | grep -i "exception"
```

**Performance Profiling:**
```bash
# System performance
iostat -x 1
sar -u 1 10
vmstat 1 10

# Application profiling
strace -p [PID]
perf record -p [PID]
```

Remember to:
- Keep troubleshooting guides up-to-date
- Test all documented procedures regularly
- Collect feedback from users and improve guides
- Include screenshots and visual aids where helpful
- Make guides searchable and well-organized

## Universal Memory Integration Outcomes

### Troubleshooting Knowledge Storage
This command will automatically:
- **Store comprehensive troubleshooting guide sessions** in Cipher Memory for diagnostic pattern recognition
- **Create relationships** between problem types, diagnostic procedures, and resolution effectiveness
- **Document troubleshooting methodologies** and system diagnosis best practices
- **Build knowledge graph** of issue-resolution mappings and diagnostic optimization strategies

### Cross-Command Learning Enhancement
Troubleshooting patterns will improve:
- Future debugging commands through established diagnostic procedure patterns
- System monitoring commands via documented troubleshooting and resolution insights
- Setup commands through troubleshooting prevention integration
- Maintenance commands via proven problem resolution methodologies

### Advanced Troubleshooting Intelligence
- **Diagnostic Optimization**: Automatic identification of optimal diagnostic procedures based on system characteristics
- **Resolution Prediction**: Intelligent resolution recommendations based on successful troubleshooting patterns
- **Problem Prevention**: Smart prevention strategies using proven troubleshooting and system hardening patterns
- **Escalation Intelligence**: Automated escalation procedure recommendations based on issue complexity and resolution patterns

### Intelligent Guide Enhancement Features
- **System-Specific Troubleshooting**: Tailored troubleshooting approaches based on infrastructure type and system characteristics
- **Context-Aware Diagnostics**: Smart diagnostic procedure recommendations considering system complexity and issue patterns
- **Progressive Troubleshooting Learning**: Each guide generation improves future troubleshooting through pattern accumulation
- **Cross-System Troubleshooting Knowledge**: Shared troubleshooting insights across different systems and infrastructure types

### Centralized Troubleshooting Logging
All troubleshooting guide operations logged to `.claude/logs/command-execution.jsonl` including:
- Complete guide generation methodology and diagnostic procedure creation tracking
- Resolution documentation results and cross-reference validation
- Memory operations for troubleshooting pattern capture and learning
- Guide effectiveness assessment and diagnostic optimization recommendations

**Next Commands**: Enhanced troubleshooting patterns will automatically improve commands like `debug-error`, `setup-monitoring-observability`, `project-health-check`, and `system-behavior-simulator`.

