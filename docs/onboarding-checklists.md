# PdaNet Linux - Role-Specific Onboarding Checklists

## Developer Role-Specific Materials

This document provides targeted onboarding checklists for different developer roles joining the PdaNet Linux project.

---

## 🔒 Security-Focused Developer Onboarding

**Background**: Understands networking and security principles but new to carrier bypass techniques.

### Week 1: Security Foundation
- [ ] **Day 1**: Complete mandatory security training (OWASP, network security)
- [ ] **Day 1**: Review all 5 critical security vulnerabilities in code review report
- [ ] **Day 2**: Analyze command injection vulnerabilities in `connection_manager.py:111-114`
- [ ] **Day 2**: Understand privilege escalation risks in hardcoded sudo paths
- [ ] **Day 3**: Deep dive into carrier detection methods and bypass techniques
- [ ] **Day 3**: Study 6-layer defense system architecture
- [ ] **Day 4**: Set up security testing environment (bandit, safety, semgrep)
- [ ] **Day 5**: Complete first security fix: input validation in `config_manager.py`

### Week 2: Advanced Security
- [ ] **Day 6-7**: Implement secure credential management system
- [ ] **Day 8-9**: Create security testing framework for carrier bypass
- [ ] **Day 10**: Develop threat model for PdaNet Linux architecture

### Security Specialist Resources
- **Primary Focus**: `/ref/carrier-bypass.md` - Carrier detection and bypass techniques
- **Security Docs**: OWASP Network Security Testing Guide
- **Tools**: Wireshark, nmap, custom traffic analysis scripts
- **Mentor**: Security Architect (2 hours/week dedicated time)

### Security Tasks Progression
1. **Week 1**: Fix existing vulnerabilities (guided)
2. **Week 2**: Security test development
3. **Week 3**: Advanced bypass technique research
4. **Week 4**: Security architecture review participation

---

## 🖥️ Python GUI Developer Onboarding

**Background**: Experienced with Python and GTK3 but new to network programming.

### Week 1: GUI Foundation
- [ ] **Day 1**: Study cyberpunk theme constraints (no emoji, monospaced fonts, pure black)
- [ ] **Day 1**: Understand GTK3 CSS limitations (no text-transform, letter-spacing)
- [ ] **Day 2**: Analyze god object anti-pattern in `pdanet_gui_v2.py` (646 lines)
- [ ] **Day 2**: Review threading model with `GLib.idle_add()` pattern
- [ ] **Day 3**: Study observer pattern implementation in connection callbacks
- [ ] **Day 4**: Create first theme modification (safe UI change)
- [ ] **Day 5**: Implement new statistics display widget

### Week 2: Advanced GUI Development
- [ ] **Day 6-7**: Contribute to god object refactoring plan
- [ ] **Day 8-9**: Implement system tray functionality improvements
- [ ] **Day 10**: Add real-time network statistics visualization

### GUI Developer Resources
- **Primary Focus**: `/ref/python-gui.md` - GTK3 implementation details
- **GUI Docs**: PyGObject API Reference, GTK3 Application Examples
- **Design Guide**: Cyberpunk theme specification in `theme.py`
- **Mentor**: Senior Python Developer (focus on architecture patterns)

### GUI Development Path
```python
# Week 1: Theme and widgets
class ThemeCustomization:
    def modify_colors(self): pass      # Safe first task
    def add_widget(self): pass         # Learn widget system

# Week 2: Architecture
class RefactoredGUI:
    def separate_concerns(self): pass   # Break down god object
    def implement_mvc(self): pass       # Proper architecture
```

---

## 🌐 Linux Network Engineer Onboarding

**Background**: Expert in iptables and Linux networking but new to Python development.

### Week 1: Network Deep Dive
- [ ] **Day 1**: Analyze transparent proxy architecture (redsocks + iptables)
- [ ] **Day 1**: Study NAT table redirection rules for traffic interception
- [ ] **Day 2**: Understand mangle table TTL manipulation for carrier bypass
- [ ] **Day 2**: Review IPv6 blocking implementation and DNS leak prevention
- [ ] **Day 3**: Test carrier bypass effectiveness with different carriers
- [ ] **Day 4**: Optimize iptables rules for performance
- [ ] **Day 5**: Create network troubleshooting documentation

### Week 2: Python Integration
- [ ] **Day 6-7**: Learn Python subprocess security for iptables calls
- [ ] **Day 8-9**: Implement dynamic iptables rule generation
- [ ] **Day 10**: Create network monitoring and alerting system

### Network Engineer Resources
- **Primary Focus**: `/ref/iptables-redsocks.md` - Complete iptables configuration
- **Network Docs**: Advanced Linux Networking Guide
- **Tools**: tcpdump, iptables-save, netstat, ss
- **Mentor**: Network Architect (focus on carrier bypass techniques)

### Network Tasks Progression
```bash
# Week 1: Analysis and optimization
iptables -t nat -L REDSOCKS -v -n     # Understand current rules
iptables -t mangle -L WIFI_STEALTH    # Study TTL manipulation

# Week 2: Python integration
python -c "import subprocess; subprocess.run(['iptables', '-L'])"  # Learn secure subprocess
```

---

## 🔧 Junior Developer Onboarding

**Background**: Limited experience in networking, Python, and security. Requires comprehensive foundation.

### Week 1: Foundation Building
- [ ] **Day 1**: Complete Python basics review (data types, functions, classes)
- [ ] **Day 1**: Install and configure development environment
- [ ] **Day 2**: Linux networking fundamentals training (4 hours)
- [ ] **Day 2**: Basic iptables concepts and hands-on practice
- [ ] **Day 3**: GTK3 introduction and simple widget creation
- [ ] **Day 3**: Security awareness training (OWASP basics)
- [ ] **Day 4**: Study PdaNet Linux architecture overview
- [ ] **Day 5**: Complete first documentation fix (safe, guided task)

### Week 2: Guided Development
- [ ] **Day 6-7**: Pair programming sessions (4 hours total)
- [ ] **Day 8-9**: Shadow network configuration tasks
- [ ] **Day 10**: Complete guided bug fix with extensive mentoring

### Week 3: Independent Practice
- [ ] **Day 11-13**: Implement simple feature with mentor review
- [ ] **Day 14-15**: Create comprehensive test for implemented feature

### Junior Developer Resources
- **Learning Path**: Progressive difficulty from documentation to code changes
- **Tutorials**: `/tutorials/` directory with hands-on exercises
- **Mentoring**: Daily check-ins for first 2 weeks
- **Pair Programming**: 2 hours/day with different team members

### Junior Development Progression
```python
# Week 1: Basics
def hello_pdanet():
    """First function - learn project structure"""
    return "Understanding PdaNet Linux"

# Week 2: Simple changes
def update_config_value(key, value):
    """Guided task - learn config system"""
    # Add validation here (mentor helps)

# Week 3: Feature implementation
class SimpleStatsWidget:
    """Independent task - real contribution"""
    def __init__(self): pass
    def update_display(self): pass
```

---

## 🏗️ DevOps/Infrastructure Engineer Onboarding

**Background**: Expert in deployment and infrastructure but new to GUI applications and network security.

### Week 1: Infrastructure Analysis
- [ ] **Day 1**: Analyze current deployment process (`install.sh`, `uninstall.sh`)
- [ ] **Day 1**: Review sudoers configuration and security implications
- [ ] **Day 2**: Study systemd service integration (redsocks, iptables-persistent)
- [ ] **Day 2**: Understand Claude Code hooks and CI/CD integration
- [ ] **Day 3**: Set up automated testing infrastructure
- [ ] **Day 4**: Create deployment validation scripts
- [ ] **Day 5**: Design monitoring and alerting for production systems

### Week 2: Advanced Infrastructure
- [ ] **Day 6-7**: Implement automated security scanning in CI/CD
- [ ] **Day 8-9**: Create container-based testing environment
- [ ] **Day 10**: Develop rollback procedures for failed deployments

### DevOps Engineer Resources
- **Primary Focus**: Infrastructure automation and deployment security
- **Tools**: Docker, systemd, iptables-persistent, GitHub Actions
- **Security**: Automated vulnerability scanning, deployment verification
- **Mentor**: Infrastructure Architect (focus on secure deployment)

### Infrastructure Tasks
```bash
# Week 1: Analysis
systemctl status redsocks                    # Service management
cat /etc/sudoers.d/pdanet-linux             # Security configuration
iptables-save > /tmp/current-rules.txt      # Rule persistence

# Week 2: Automation
docker build -t pdanet-test .               # Containerization
pytest --cov=src --cov-fail-under=85        # CI/CD integration
```

---

## 📊 Quality Assurance Engineer Onboarding

**Background**: Testing expertise but new to network applications and security testing.

### Week 1: Testing Foundation
- [ ] **Day 1**: Understand current test coverage (0% - critical issue)
- [ ] **Day 1**: Study security vulnerabilities that need test coverage
- [ ] **Day 2**: Learn network testing techniques for carrier bypass
- [ ] **Day 2**: Set up security testing tools (OWASP ZAP, custom scripts)
- [ ] **Day 3**: Create test plan for 6-layer carrier bypass system
- [ ] **Day 4**: Implement first unit tests for `config_manager.py`
- [ ] **Day 5**: Create integration test for connection state machine

### Week 2: Advanced Testing
- [ ] **Day 6-7**: Develop security test suite for all vulnerabilities
- [ ] **Day 8-9**: Create automated carrier bypass effectiveness tests
- [ ] **Day 10**: Implement performance benchmarking suite

### QA Engineer Resources
- **Primary Focus**: Building comprehensive test coverage from 0%
- **Testing Strategy**: Security-first, network-aware testing
- **Tools**: pytest, unittest.mock, Wireshark, custom traffic generators
- **Mentor**: QA Lead + Security Architect (joint mentoring)

### Testing Progression
```python
# Week 1: Foundation tests
def test_config_validation():
    """Security-focused unit tests"""
    assert config.validate_ip("192.168.1.1") == True
    assert config.validate_ip("invalid") == False

# Week 2: Integration tests
def test_carrier_bypass_effectiveness():
    """Network-aware integration tests"""
    assert bypass.ttl_manipulation_active() == True
    assert bypass.ipv6_blocked() == True
```

---

## 🎯 Milestone Checklists by Role

### 30-Day Checkpoint - All Roles

#### Security Developer
- [ ] Fixed 2+ security vulnerabilities
- [ ] Created security testing framework
- [ ] Completed threat model review
- [ ] Mentored team on security practices

#### GUI Developer
- [ ] Contributed to god object refactoring
- [ ] Implemented 2+ UI improvements
- [ ] Mastered GTK3 threading patterns
- [ ] Created reusable UI components

#### Network Engineer
- [ ] Optimized iptables performance
- [ ] Enhanced carrier bypass effectiveness
- [ ] Created network monitoring tools
- [ ] Documented troubleshooting procedures

#### Junior Developer
- [ ] Completed foundational training
- [ ] Made 5+ successful code contributions
- [ ] Demonstrated security awareness
- [ ] Ready for independent tasks

#### DevOps Engineer
- [ ] Automated deployment process
- [ ] Implemented security scanning
- [ ] Created monitoring/alerting
- [ ] Established rollback procedures

#### QA Engineer
- [ ] Achieved 50%+ test coverage
- [ ] Created security test suite
- [ ] Implemented CI/CD testing
- [ ] Documented testing procedures

### 90-Day Goals - All Roles

#### Technical Mastery
- [ ] **Architecture Participation**: Contributing to design decisions
- [ ] **Independent Delivery**: Owning complete features
- [ ] **Quality Leadership**: Setting standards in area of expertise
- [ ] **Knowledge Sharing**: Teaching others in your domain

#### Team Integration
- [ ] **Mentoring Others**: Guiding new team members
- [ ] **Process Improvement**: Suggesting workflow enhancements
- [ ] **Cross-Functional Work**: Collaborating outside primary role
- [ ] **Technical Leadership**: Leading discussions in your area

---

## 📋 Daily/Weekly Routine Checklists

### Daily Routine (All Roles)
- [ ] **Security Review**: Check for new vulnerabilities in changed code
- [ ] **Quality Check**: Run automated linting and testing
- [ ] **Knowledge Update**: 15 minutes reading security/networking news
- [ ] **Team Communication**: Participate in standup and discussions

### Weekly Routine (All Roles)
- [ ] **Architecture Review**: Participate in design discussions
- [ ] **Security Assessment**: Review code changes for security implications
- [ ] **Learning Goal**: Complete 1 training module or tutorial
- [ ] **Documentation**: Update/improve 1 documentation section
- [ ] **Mentoring**: Give or receive mentoring session

### Monthly Review (All Roles)
- [ ] **Skill Assessment**: Evaluate progress against role expectations
- [ ] **Goal Adjustment**: Update learning and contribution goals
- [ ] **Team Feedback**: Provide input on team processes and culture
- [ ] **Career Development**: Discuss growth opportunities with manager

---

## 🚨 Emergency Response by Role

### Security Incident - Security Developer Lead
1. **Immediate**: Isolate affected systems
2. **Assessment**: Determine vulnerability scope and impact
3. **Communication**: Alert team and stakeholders
4. **Remediation**: Lead patch development and deployment
5. **Documentation**: Create incident report and lessons learned

### Network Incident - Network Engineer Lead
1. **Detection**: Identify carrier bypass failure or network issues
2. **Analysis**: Determine which bypass layers have failed
3. **Workaround**: Implement temporary mitigation
4. **Resolution**: Restore full bypass functionality
5. **Prevention**: Update monitoring and detection systems

### Quality Incident - QA Engineer Lead
1. **Triage**: Assess severity and user impact
2. **Regression**: Identify root cause and when introduced
3. **Testing**: Create test cases that would have caught the issue
4. **Validation**: Verify fix doesn't introduce new problems
5. **Process**: Update testing procedures to prevent recurrence

---

**Document Metadata**
- **Created**: October 4, 2025
- **Target**: Role-specific onboarding for PdaNet Linux project
- **Framework**: Progressive skill building with role-specific focus
- **Update**: Quarterly review based on team feedback and role evolution