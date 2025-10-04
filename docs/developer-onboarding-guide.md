# PdaNet Linux - Developer Onboarding Guide

## Executive Summary

Welcome to the PdaNet Linux project - a security-critical network tethering application that implements advanced carrier detection bypass techniques. This comprehensive onboarding guide will prepare you for contributing to a complex codebase involving Linux networking, iptables manipulation, GTK3 GUI development, and carrier security research.

**🚨 SECURITY NOTICE**: This project involves privileged system operations, network manipulation, and security-sensitive code. All developers must complete security training before accessing production systems.

**Project Complexity**: High - Requires expertise in Linux networking, Python development, security practices, and carrier bypass techniques.

---

## 1. Project Overview & Business Context

### What is PdaNet Linux?

PdaNet Linux is a reverse-engineered Linux client for PdaNet+ USB/WiFi tethering that provides system-wide internet connectivity through Android devices. The primary value proposition is **6-layer carrier detection bypass** that prevents mobile carriers from detecting and throttling tethered traffic.

### Core Technologies

- **Frontend**: Python 3 + PyGObject (GTK3) with cyberpunk theme
- **Backend**: iptables, redsocks, NetworkManager integration
- **Security**: Transparent proxy redirection, TTL manipulation, traffic obfuscation
- **Platform**: Linux Mint 22.2 Cinnamon (Debian/Ubuntu-based)

### Business Critical Features

1. **WiFi Tethering with Carrier Bypass** (Primary)
   - 6-layer defense against carrier detection
   - TTL normalization, IPv6 blocking, DNS leak prevention
   - Traffic shaping and OS update blocking

2. **USB Tethering Mode** (Secondary)
   - Direct USB interface detection
   - HTTP proxy validation and redirection

3. **Professional GUI** (Supporting)
   - Real-time statistics, connection management
   - System tray integration, auto-reconnect

---

## 2. Security-First Onboarding (Week 1)

### 🚨 Critical Security Training

**MANDATORY**: Complete before touching any code involving:
- `subprocess.run()` calls
- Network operations
- File system access with elevated privileges
- User input handling

#### Security Vulnerabilities Context

The project currently has **5 critical security vulnerabilities** identified in our code review:

1. **Command Injection** (`connection_manager.py:111-114`)
2. **Privilege Escalation** via hardcoded paths (`connection_manager.py:171`)
3. **Configuration Injection** (`config_manager.py:83-86`)
4. **Host Injection** in ping tests (`stats_collector.py:135`)
5. **Missing Credential Management**

#### Security Checklist

```python
# SECURITY REVIEW REQUIRED for any code containing:
SECURITY_REVIEW_PATTERNS = [
    "subprocess.run()",     # Command injection risk
    "sudo",                 # Privilege escalation
    "user input",           # Input validation needed
    "network operations",   # Protocol security
    "file system access"    # Path traversal risk
]
```

### Security Training Resources

1. **OWASP Secure Coding Practices** (2 hours)
2. **Linux Network Security** (3 hours)
3. **Python Security Best Practices** (2 hours)
4. **iptables Security Configuration** (2 hours)

### Environment Security Setup

```bash
# 1. Secure development environment setup
sudo apt update && sudo apt upgrade
sudo apt install python3-dev python3-pip python3-venv git

# 2. Install security analysis tools
pip install bandit safety semgrep

# 3. Run security audit on dependencies
safety check -r requirements.txt
bandit -r src/

# 4. Set up pre-commit security hooks
pip install pre-commit
pre-commit install
```

---

## 3. Development Environment Setup

### System Requirements

- **OS**: Linux Mint 22.2 Cinnamon or Ubuntu 22.04+
- **Python**: 3.10+
- **GTK**: GTK3 development libraries
- **Network**: Administrative privileges for iptables/NetworkManager

### Complete Setup Process

```bash
# 1. Clone repository
git clone https://github.com/user/pdanet-linux.git
cd pdanet-linux

# 2. Install system dependencies
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
                 gir1.2-appindicator3-0.1 libcairo2-dev \
                 redsocks iptables-persistent

# 3. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install --break-system-packages -r requirements.txt

# 5. Install development tools
pip install black isort flake8 mypy pytest pytest-cov bandit

# 6. Verify installation
python src/pdanet_gui_v2.py --version
```

### Validation Tests

```bash
# Test 1: GUI can launch
python src/pdanet_gui_v2.py --test-mode

# Test 2: All modules import correctly
python -c "from src import *"

# Test 3: Security tools work
flake8 src/
mypy src/
bandit -r src/

# Test 4: Network tools available
which iptables && which redsocks && echo "Network tools OK"
```

### Claude Code Hooks Setup

The project includes automated quality assurance:

```json
{
  "PostToolUse": [
    {"command": "black {file}", "pattern": "**/*.py"},
    {"command": "isort {file}", "pattern": "**/*.py"},
    {"command": "flake8 {file}", "pattern": "**/*.py", "blocking": true},
    {"command": "mypy {file}", "pattern": "**/*.py", "blocking": true}
  ]
}
```

---

## 4. Architecture Deep Dive (Week 1-2)

### System Architecture Overview

```
Android Device (PdaNet+ app)
         ↓
[USB Mode] OR [WiFi Mode]
         ↓
HTTP Proxy (192.168.49.1:8000) OR WiFi Gateway
         ↓
[6-Layer Carrier Bypass - WiFi Mode Only]
         ↓
redsocks (transparent proxy, port 12345)
         ↓
iptables NAT/mangle rules
         ↓
All Linux Applications
```

### Core Modules Architecture

```python
# Module Dependencies (from least to most dependent)
logger.py              # Logging foundation
config_manager.py      # Configuration persistence
stats_collector.py     # Bandwidth/latency tracking
connection_manager.py  # State machine + auto-reconnect
theme.py              # GTK3 CSS generation
pdanet_gui_v2.py      # Main GUI (646 lines - REFACTORING NEEDED)
```

### 6-Layer Carrier Bypass (Critical Knowledge)

**Layer 1 - TTL Normalization** (MOST IMPORTANT)
```bash
# Sets all outgoing packets to TTL 65 (phone-like)
iptables -t mangle -A WIFI_STEALTH -j TTL --ttl-set 65
```

**Layer 2 - IPv6 Complete Block**
```bash
# Disable IPv6 and drop all IPv6 packets
sysctl -w net.ipv6.conf.wlan0.disable_ipv6=1
ip6tables -A OUTPUT -j DROP
```

**Layer 3 - DNS Leak Prevention**
```bash
# Redirect all DNS to gateway
iptables -t nat -A OUTPUT -p udp --dport 53 -j DNAT --to-destination 192.168.1.1:53
```

**Layer 4 - OS Update Blocking**
```bash
# Block Windows/Mac/Ubuntu update servers
iptables -A OUTPUT -d windowsupdate.com -j DROP
```

**Layer 5 - MSS/MTU Clamping**
```bash
# Match phone packet characteristics
iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
```

**Layer 6 - Traffic Shaping** (Optional)
```bash
# Currently disabled for performance
# Can limit bandwidth to appear phone-like
```

### State Machine (ConnectionManager)

```python
class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    ERROR = "error"
```

### Threading Model

```python
# CRITICAL: All UI updates must use GLib.idle_add()
def _connect_thread(self):
    # Heavy work in background thread
    result = subprocess.run(...)
    # UI update scheduled on main thread
    GLib.idle_add(self._on_connect_complete, result)
```

---

## 5. Hands-On Learning Path

### Week 1: Foundation Tasks

#### Task 1: Environment Validation (Day 1)
```bash
# Goal: Verify all systems work
python src/pdanet_gui_v2.py --test-mode
pytest tests/ -v  # Will fail - 0% coverage currently
```

#### Task 2: Code Analysis (Day 2-3)
- Read and understand `connection_manager.py`
- Identify all `subprocess.run()` calls
- Document security vulnerabilities found

#### Task 3: First Security Fix (Day 4-5)
**SAFE TASK**: Add input validation to `config_manager.py`

```python
# Before (vulnerable)
def set(self, key, value):
    self.config[key] = value

# After (secure) - YOUR TASK
def set(self, key, value):
    # Add validation here
    self._validate_config_key_value(key, value)
    self.config[key] = value
```

### Week 2: Architecture Tasks

#### Task 4: GTK3 Theme Customization
- Modify cyberpunk theme colors in `theme.py`
- Add new UI element with proper CSS
- **CONSTRAINT**: No emoji, professional only

#### Task 5: Statistics Enhancement
- Add new metric to `stats_collector.py`
- Implement rolling window calculation
- Update GUI to display new metric

#### Task 6: State Machine Enhancement
- Add new connection state
- Implement proper state transitions
- Add unit tests for state machine

### Week 3-4: Advanced Tasks

#### Task 7: Security Hardening
- Implement proper input validation framework
- Add secure credential storage
- Replace hardcoded paths with dynamic resolution

#### Task 8: God Object Refactoring
**MAJOR TASK**: Break down 646-line `PdaNetGUI` class
```python
# Current (problematic)
class PdaNetGUI(Gtk.Window):  # 646 lines

# Target (refactored)
class PdaNetGUI(Gtk.Window):       # ~200 lines
class UIController:                # ~150 lines
class SystemTrayManager:           # ~100 lines
class SettingsDialog(Gtk.Dialog):  # ~150 lines
```

#### Task 9: Test Infrastructure
**CRITICAL**: Build comprehensive test suite (currently 0% coverage)

```python
# Target test coverage
pytest tests/ --cov=src --cov-report=html
# Goal: 85% overall, 100% for security functions
```

---

## 6. Domain Knowledge Training

### Networking Fundamentals (Required)

1. **TCP/IP Stack** (8 hours)
   - Packet flow, routing, NAT
   - IPv4/IPv6 differences
   - DNS resolution process

2. **iptables Mastery** (12 hours)
   - Tables: filter, nat, mangle, raw
   - Transparent proxy setup
   - Packet marking and routing

3. **Carrier Detection Methods** (6 hours)
   - TTL decrement analysis
   - Traffic pattern recognition
   - DPI (Deep Packet Inspection)
   - Machine learning detection (2024-2025)

### Python/GTK3 Development (As Needed)

1. **PyGObject/GTK3** (10 hours)
   - Widget system, signals/callbacks
   - Threading with GLib.idle_add()
   - CSS styling limitations

2. **Python Security** (8 hours)
   - Input validation patterns
   - Subprocess security
   - Credential management

### Security Mindset Training (Required)

1. **Threat Modeling** (4 hours)
   - Network security threats
   - Privilege escalation vectors
   - Input validation requirements

2. **Secure Coding** (6 hours)
   - OWASP Top 10 for Python
   - Command injection prevention
   - Path traversal prevention

---

## 7. Development Workflow & Standards

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/security-input-validation

# 2. Make changes with frequent commits
git add src/config_manager.py
git commit -m "Add input validation to config_manager

- Implement ALLOWED_CONFIG_KEYS whitelist
- Add type checking for all config values
- Add IP address validation for proxy_ip
- Add port range validation for proxy_port

Fixes: Command injection vulnerability in config system"

# 3. Run quality checks (automated via hooks)
black src/
isort src/
flake8 src/
mypy src/
pytest tests/

# 4. Create pull request
git push origin feature/security-input-validation
# Open PR with security review template
```

### Code Review Process

**MANDATORY**: All security-sensitive code requires two-person review:

1. **Author**: Fills out security checklist
2. **Reviewer 1**: Security-focused review
3. **Reviewer 2**: Architecture/functionality review

#### Security Review Checklist

```markdown
- [ ] No hardcoded credentials or paths
- [ ] All user input validated
- [ ] No command injection vectors
- [ ] Proper error handling
- [ ] Logging does not expose sensitive data
- [ ] Tests include security test cases
```

### Testing Standards

```python
# Example security test
def test_config_injection_prevention():
    config = ConfigManager()

    # Test malicious input rejection
    with pytest.raises(ValueError):
        config.set("proxy_ip", "192.168.1.1; rm -rf /")

    # Test invalid key rejection
    with pytest.raises(ValueError):
        config.set("invalid_key", "value")
```

### Performance Standards

- **Connection Time**: < 5 seconds
- **Memory Usage**: < 50MB steady state
- **CPU Usage**: < 5% during normal operation
- **Test Coverage**: 85% overall, 100% security functions

---

## 8. Team Communication & Support

### Communication Channels

1. **Daily Standup**: 9:00 AM EST (remote-friendly)
2. **Architecture Reviews**: Wednesdays 2:00 PM EST
3. **Security Reviews**: As needed (blocking for security changes)
4. **Sprint Planning**: Bi-weekly Mondays 10:00 AM EST

### Team Structure

```
Project Lead (wtyler)
├── Security Architect (TBD)
├── Network Engineer (TBD)
├── Python Developers (2-3)
└── Quality Assurance (1)
```

### Escalation Procedures

1. **Technical Issues**: Ask in team chat first
2. **Security Concerns**: Immediate escalation to Security Architect
3. **Network Issues**: Escalate to Network Engineer
4. **Architectural Decisions**: Schedule architecture review

### Support Resources

- **Internal Wiki**: `/docs/` directory
- **Architecture Docs**: `/ref/` directory
- **Code Examples**: `/examples/` directory
- **Troubleshooting**: `/docs/troubleshooting.md`

---

## 9. First 30-60-90 Day Milestones

### 30-Day Goals

**Week 1: Foundation**
- ✅ Complete security training
- ✅ Environment setup and validation
- ✅ Architecture understanding verified
- ✅ First security fix merged

**Week 2: Integration**
- ✅ GTK3 theme customization completed
- ✅ Statistics enhancement delivered
- ✅ Code review participation (2+ reviews)
- ✅ Pair programming sessions (5+ hours)

**Week 3-4: Contribution**
- ✅ State machine enhancement
- ✅ Test infrastructure contribution
- ✅ Security vulnerability fix
- ✅ Documentation improvement

### 60-Day Goals

- ✅ Independent feature ownership (medium complexity)
- ✅ God object refactoring contribution
- ✅ Security review certification
- ✅ Mentoring new team member

### 90-Day Goals

- ✅ Architecture review participation
- ✅ Complex feature delivery (carrier bypass enhancement)
- ✅ Technical debt reduction leadership
- ✅ Process improvement proposal

---

## 10. Tools & Resources Access

### Required Accounts & Access

```bash
# Development Tools
GitHub: pdanet-linux repository access
Docker: For testing environments
VPN: For secure testing networks

# Security Tools
Bandit: Python security linter
Safety: Dependency vulnerability scanner
OWASP ZAP: Security testing

# Monitoring & Analytics
Wireshark: Network packet analysis
htop/iotop: System monitoring
iptables-save: Network rule analysis
```

### License & Subscription Information

- **GitHub**: Open source repository
- **PyGObject**: LGPL (compatible)
- **Security Tools**: Open source (free)
- **Development IDE**: VS Code (free) or PyCharm Community

### Network Access Procedures

```bash
# VPN Setup for secure testing
sudo apt install openvpn
# Configure with team-provided certificates

# Test Network Access
ping test-carrier-bypass-server.internal
curl -v https://security-testing-api.internal/status
```

### Troubleshooting Common Access Issues

1. **iptables Permission Denied**
   ```bash
   # Add user to sudo group
   sudo usermod -aG sudo $USER
   # Verify sudoers entry exists
   sudo cat /etc/sudoers.d/pdanet-linux
   ```

2. **GTK3 Import Errors**
   ```bash
   # Install missing GTK3 development packages
   sudo apt install python3-gi-dev libgirepository1.0-dev
   ```

3. **redsocks Service Issues**
   ```bash
   # Check service status
   sudo systemctl status redsocks
   # Verify configuration
   sudo cat /etc/redsocks.conf
   ```

---

## 11. Learning Resources & Training Materials

### Project-Specific Documentation

1. **Architecture Deep Dive**: `/ref/architecture.md`
2. **Carrier Bypass Guide**: `/ref/carrier-bypass.md`
3. **iptables Configuration**: `/ref/iptables-redsocks.md`
4. **Python GUI Guide**: `/ref/python-gui.md`
5. **Connection Scripts**: `/ref/connection-scripts.md`

### External Learning Resources

#### Network Security (CRITICAL)
- **Book**: "Network Security with iptables" by Steve Suehring
- **Course**: Linux Network Administration (Linux Academy)
- **Guide**: OWASP Network Security Testing Guide

#### Python Security
- **Book**: "Serious Python" by Julien Danjou
- **Course**: Secure Python Development (SANS)
- **Guide**: Python Security Best Practices (PyPA)

#### GTK3 Development
- **Documentation**: PyGObject API Reference
- **Tutorial**: GTK3 Python Tutorial (gnome.org)
- **Examples**: GTK3 Application Examples

### Hands-On Tutorials

#### Tutorial 1: iptables Transparent Proxy
```bash
# Goal: Understand packet redirection
# Location: /tutorials/iptables-transparent-proxy.md
# Duration: 2 hours
# Prerequisites: Basic networking knowledge
```

#### Tutorial 2: GTK3 Threading
```python
# Goal: Master UI threading patterns
# Location: /tutorials/gtk3-threading.md
# Duration: 3 hours
# Prerequisites: Python basics, GTK3 installation
```

#### Tutorial 3: Carrier Bypass Testing
```bash
# Goal: Test bypass effectiveness
# Location: /tutorials/carrier-bypass-testing.md
# Duration: 4 hours
# Prerequisites: Network analysis tools
```

### Video Training Series

1. **PdaNet Architecture Overview** (30 min)
2. **Security Vulnerability Deep Dive** (45 min)
3. **Carrier Detection Methods** (60 min)
4. **Python GTK3 Best Practices** (45 min)
5. **iptables for Developers** (90 min)

---

## 12. Mentoring & Buddy System

### Mentor Assignment Process

**Week 1**: Assigned primary mentor (senior developer)
**Week 2**: Assigned secondary mentor (security specialist)
**Week 4**: Begin reverse mentoring (teach concepts to newer developers)

### Mentoring Schedule

```
Monday: Architecture review with Senior Developer
Tuesday: Code review session with mentor
Wednesday: Security discussion with Security Specialist
Thursday: Independent work with Q&A support
Friday: Weekly retrospective and planning
```

### Reverse Mentoring Opportunities

- Document learning journey for future developers
- Create tutorials for complex topics
- Mentor next new hire (after 30 days)
- Present learnings to team (after 60 days)

---

## 13. Quality Assurance & Testing

### Test Pyramid Strategy

```
              Unit Tests (85% coverage target)
                     /\
            Integration Tests (Key workflows)
                   /    \
         System Tests (Full carrier bypass)
              /          \
    Manual Security Tests (Penetration testing)
```

### Testing Environments

1. **Local Development**: Safe testing without network effects
2. **Isolated VM**: Network manipulation testing
3. **Staging Network**: Carrier bypass validation
4. **Production**: Never test here - read-only monitoring only

### Continuous Integration

```yaml
# .github/workflows/quality-check.yml
name: Quality Assurance
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Security Scan
        run: |
          bandit -r src/
          safety check -r requirements.txt

  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Code Quality
        run: |
          flake8 src/
          mypy src/
          pytest --cov=src --cov-fail-under=85
```

---

## 14. Feedback & Continuous Improvement

### Feedback Collection Process

#### Week 1 Check-in
```markdown
1. Was security training sufficient?
2. Any environment setup blockers?
3. Architecture complexity manageable?
4. Mentor relationship effective?
5. Documentation clarity rating (1-10)
```

#### 30-Day Retrospective
```markdown
1. Most challenging technical concept?
2. Best learning resource discovered?
3. Suggested onboarding improvements?
4. Team integration satisfaction?
5. Confidence level with security practices?
```

#### 90-Day Assessment
```markdown
1. Ready for independent feature development?
2. Security mindset fully developed?
3. Architecture decision participation ready?
4. Mentoring others capability?
5. Overall onboarding effectiveness (1-10)
```

### Success Metrics & KPIs

#### Developer Velocity
- **Time to First Commit**: Target < 3 days
- **Time to First Security Fix**: Target < 10 days
- **Time to Independent Feature**: Target < 30 days
- **Time to Architecture Participation**: Target < 90 days

#### Code Quality
- **Code Review Comments**: Decreasing trend expected
- **Security Issues Introduced**: Target = 0
- **Test Coverage Contribution**: Target > 5% increase
- **Documentation Quality**: Peer review score > 8/10

#### Team Integration
- **Mentor Satisfaction**: Target > 8/10
- **Peer Review Quality**: Target > 7/10
- **Knowledge Sharing**: Target 2+ presentations/90 days
- **Process Improvement**: Target 1+ suggestion/30 days

### Onboarding Guide Maintenance

#### Quarterly Updates (Required)
- Security threat landscape changes
- New developer feedback integration
- Technology stack updates
- Process improvement integration

#### Annual Review (Required)
- Complete guide effectiveness assessment
- Industry best practice alignment
- Tool and resource updates
- Success metric calibration

---

## 15. Emergency Procedures & Incident Response

### Security Incident Response

**IMMEDIATE ACTIONS** if security vulnerability discovered:

1. **STOP**: Do not commit or deploy affected code
2. **ISOLATE**: Remove affected systems from network if needed
3. **ESCALATE**: Contact Security Architect immediately
4. **DOCUMENT**: Record all details of vulnerability
5. **REMEDIATE**: Follow security patch process

### Network Incident Response

**CARRIER BYPASS DETECTION** procedure:

1. **DETECT**: Monitor for unusual throttling or blocking
2. **ANALYZE**: Check which bypass layers may have failed
3. **ADJUST**: Modify stealth levels or techniques
4. **TEST**: Verify bypass effectiveness restored
5. **DOCUMENT**: Update bypass technique documentation

### Development Environment Issues

**CRITICAL SYSTEM ACCESS LOST**:

```bash
# Recovery procedures
sudo usermod -aG sudo $USER          # Restore sudo access
sudo systemctl restart redsocks     # Restart proxy service
sudo iptables-restore < /etc/iptables/rules.v4  # Restore network rules
```

---

## Conclusion

This comprehensive onboarding guide establishes the foundation for successful contribution to the PdaNet Linux project. The security-first approach, progressive skill building, and comprehensive support system ensure that new developers can safely and effectively contribute to this complex, security-critical codebase.

**Remember**: This project requires a security mindset from day one. When in doubt about security implications, always escalate rather than risk introducing vulnerabilities.

**Success Path**: Follow the progressive milestones, engage actively with mentors, and maintain focus on both technical excellence and security best practices.

---

**Document Metadata**
- **Created**: October 4, 2025
- **Framework Used**: 90-day structured onboarding with security-first approach
- **Research Base**: 2024-2025 developer onboarding best practices, Azure portal extension onboarding methodology
- **Target Audience**: Python developers, network engineers, security specialists joining PdaNet Linux project
- **Update Schedule**: Quarterly review with annual major revision