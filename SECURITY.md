# Security Policy

## Overview

This document outlines the security model, threat analysis, and disclosure policy for PdaNet Linux. We take security seriously and have implemented multiple layers of protection to ensure safe operation.

**Security Principles:**
- Defense in depth
- Principle of least privilege
- Secure by default
- Fail securely
- Complete mediation

## Reporting Security Vulnerabilities

### Responsible Disclosure

We encourage responsible disclosure of security vulnerabilities. If you discover a security issue, please report it privately before public disclosure.

**How to Report:**
1. **Email:** Send details to [security@pdanet-linux.org](mailto:security@pdanet-linux.org)
2. **Subject:** Use "SECURITY:" prefix in subject line
3. **Content:** Include:
   - Detailed description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fix (if any)
   - Your contact information

**What to Expect:**
- Initial response within 48 hours
- Status updates every 5-7 days
- Coordinated disclosure timeline (typically 90 days)
- Credit in security advisories (if desired)

**Please DO NOT:**
- Publicly disclose the vulnerability before coordinated release
- Exploit the vulnerability beyond proof-of-concept
- Access or modify data belonging to others
- Perform DoS attacks or resource exhaustion

### Bug Bounty

Currently, we do not offer a bug bounty program. However, we greatly appreciate responsible disclosure and will publicly credit researchers who follow our disclosure policy.

## Security Model

### Threat Model

**Assets We Protect:**
1. **WiFi Credentials** - SSIDs and passwords
2. **Network Traffic** - User's internet activity
3. **System Integrity** - Protection against malicious commands
4. **Privacy** - Connection metadata and usage patterns

**Trust Boundaries:**
1. User → Application (trusted)
2. Application → System (requires privilege escalation)
3. Application → Network (untrusted)
4. Application → Scripts (requires validation)

**Threat Actors:**
1. **Local Attacker** - Unprivileged user on same system
2. **Network Attacker** - Person on same network
3. **ISP/Carrier** - Mobile carrier attempting to detect tethering
4. **Malware** - Malicious software on user's system

### Security Controls

#### Authentication & Access Control

**Privilege Escalation:**
- Uses PolicyKit (pkexec) for privilege escalation
- Requires user authentication for privileged operations
- No silent sudo fallback (explicit failure)
- All privileged operations are logged

**Single Instance Enforcement:**
- XDG-compliant lockfile location (~/.cache or $XDG_RUNTIME_DIR)
- Atomic lockfile creation with O_EXCL
- Restrictive permissions (0600)
- Stale lock detection and cleanup
- PID validation for crashed instances

#### Cryptography & Secret Storage

**WiFi Password Storage:**
- Prefer system keyring (Secret Service/libsecret) when available
- Fallback to file-based storage with:
  - Restrictive permissions (0600)
  - XDG-compliant location (~/.config/pdanet-linux)
  - Clear warning to user about plaintext storage
- Automatic migration from plaintext to keyring
- Secure deletion on removal

**No Encryption of Network Traffic:**
- PdaNet Linux does NOT encrypt your network traffic
- For encryption, use a VPN service (recommended)
- Stealth mode only obfuscates metadata, not content

#### Input Validation

**Comprehensive Validation:**
- All user inputs validated before use
- SSID validation (length, character whitelist)
- Password validation (length, shell-unsafe character blocking)
- IP address validation (format, type checking)
- Port validation (range checking)
- Hostname validation (RFC 1123 compliance)
- Interface name validation (Linux naming rules)
- Subprocess argument validation (type, null byte checking)

**Attack Prevention:**
- Command injection blocked (no shell=True)
- Path traversal blocked (.. detection)
- SQL injection N/A (no SQL database)
- XSS N/A (no web interface)

#### Process & Network Security

**Subprocess Execution:**
- All subprocess calls use list-based arguments (no shell=True)
- Command arguments validated before execution
- Timeouts on all subprocess calls
- Proper error handling and logging

**Network Operations:**
- Proxy validation before use
- Interface detection with retries
- Connection state machine with transition validation
- Automatic reconnection with exponential backoff

#### Stealth Mode Security

**What Stealth Mode Does:**
- TTL normalization to hide hop count
- IPv6 blocking (carrier fingerprinting prevention)
- DNS request routing (prevents carrier DNS analysis)
- OS update blocking (prevents carrier pattern detection)

**What Stealth Mode Does NOT Do:**
- Encrypt your traffic (use VPN for encryption)
- Make you completely undetectable (carriers have ML-based detection)
- Protect against deep packet inspection of encrypted protocols
- Hide your overall data usage patterns

**Stealth Mode Levels:**
1. **Level 1 (Basic)** - TTL normalization only
2. **Level 2 (Moderate)** - + IPv6 blocking + DNS routing
3. **Level 3 (Aggressive)** - + OS update blocking (may break updates)

#### Audit & Logging

**What We Log:**
- Privileged command executions
- Connection state changes
- Authentication attempts (keyring access)
- Configuration changes
- Error conditions

**What We Don't Log:**
- WiFi passwords (never logged)
- Network traffic content
- Visited websites or IPs
- DNS query contents
- Personal identifiable information

**Log Storage:**
- Logs stored in ~/.config/pdanet-linux/logs/
- Rotating log files (configurable size limit)
- Restrictive permissions (0600)
- Optional systemd journal integration

## Known Security Limitations

### By Design

1. **Carrier Detection Risk**
   - Stealth mode is not foolproof
   - Carriers may use ML-based detection
   - Deep packet inspection can reveal tethering patterns
   - Long-term high data usage may trigger investigation

2. **No Traffic Encryption**
   - PdaNet Linux does not encrypt your traffic
   - Unencrypted HTTP traffic is visible to network observers
   - Use HTTPS and VPN for sensitive activities

3. **Requires Root Privileges**
   - Network configuration requires root access
   - PolicyKit authentication required
   - Risk of privilege escalation bugs (mitigated by validation)

### Implementation Limitations

1. **Plaintext Password Fallback**
   - If keyring is unavailable, passwords stored in plaintext file
   - File has restrictive permissions (0600) but readable by root
   - Users should install keyring support

2. **Race Conditions**
   - Theoretical race conditions in state machine transitions
   - Mitigated by locks but not formally verified
   - Low probability in single-user scenario

3. **Dependency Vulnerabilities**
   - We depend on system libraries (GTK3, NetworkManager, etc.)
   - Keep your system updated to get security patches
   - Run `pip-audit` to check Python dependencies

## Security Best Practices for Users

### Setup

1. **Install Keyring Support:**
   ```bash
   sudo apt-get install python3-keyring gnome-keyring
   ```

2. **Verify Installations:**
   ```bash
   python3 -m src.migrate_passwords --dry-run
   ```

3. **Review Permissions:**
   ```bash
   ls -la ~/.config/pdanet-linux/
   # All files should be 0600 (rw-------)
   ```

### Operational Security

1. **Use VPN:** Always use a VPN service for encryption
2. **HTTPS Only:** Only visit HTTPS websites when tethering
3. **Monitor Usage:** Check data usage to avoid carrier scrutiny
4. **Update Regularly:** Keep PdaNet Linux and system packages updated
5. **Limit Exposure:** Don't tether for extended periods continuously

### Network Safety

1. **Don't Use Public WiFi** as your tether source (man-in-the-middle risk)
2. **Verify Connection** before transmitting sensitive data
3. **Use Stealth Level 2** as default (Level 3 may break updates)
4. **Monitor Logs** for connection issues or anomalies

## Security Audits & Testing

### Completed

- ✅ Comprehensive code quality audit (2025-10-13)
- ✅ Static security analysis (bandit)
- ✅ Dependency vulnerability scan (pip-audit)
- ✅ Input validation testing
- ✅ Privilege escalation review

### Ongoing

- Regular dependency updates
- Continuous static analysis
- User-reported vulnerability assessment

### Planned

- Third-party security audit (pending funding)
- Fuzzing of input validators
- Formal verification of state machine
- Penetration testing

## Security Updates

### Versioning

We use semantic versioning with security implications:
- **MAJOR.MINOR.PATCH**
- Security fixes always result in at least a PATCH version bump
- Critical vulnerabilities may result in out-of-band releases

### Update Notifications

Security updates are announced via:
1. GitHub Security Advisories
2. Release notes
3. In-app notifications (if enabled)

### Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | ✅ Yes             |
| 1.x     | ⚠️ Security fixes only |
| < 1.0   | ❌ No              |

## Compliance

### Legal Considerations

**Important:** Check your carrier's terms of service regarding tethering.
- Tethering may violate your service agreement
- Some carriers allow tethering, others prohibit it
- Legal implications vary by jurisdiction
- Use at your own risk

**Privacy Laws:**
- PdaNet Linux collects no personal data
- All data stored locally
- No telemetry or analytics
- GDPR compliant (no data processing)

## Security Contacts

- **Security Issues:** security@pdanet-linux.org
- **General Contact:** support@pdanet-linux.org
- **GitHub Issues:** https://github.com/pdanet-linux/pdanet-linux/issues (for non-security bugs only)

## Acknowledgments

We thank the security research community for responsible disclosure and testing:
- *(List of credited researchers will be added here)*

## Changelog

| Date       | Version | Description |
|------------|---------|-------------|
| 2025-10-13 | 2.0.0   | Initial SECURITY.md, comprehensive security hardening |

---

*Last Updated: 2025-10-13*
*Version: 1.0*
