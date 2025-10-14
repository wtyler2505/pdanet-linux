# Shell Script Analysis & Security Audit

## Overview
Analysis of all bash scripts in PdaNet Linux for security, reliability, and best practices.

---

## 📁 Scripts Analyzed

1. `/app/install.sh` (206 lines)
2. `/app/uninstall.sh` (123 lines)
3. `/app/scripts/wifi-stealth.sh` (239 lines)
4. `/app/scripts/stealth-mode.sh` (134 lines)
5. `/app/config/iptables-rules.sh` (107 lines)

**Total:** 809 lines of shell code

---

## 🔍 DETAILED FINDINGS

### 1. install.sh Analysis

#### ✅ Strengths
- Proper error handling (`set -e`)
- Root privilege check
- OS detection and validation
- Backup of existing configs
- Colored output for better UX
- Incremental progress indicators

#### ⚠️ Weaknesses

**Critical:**
1. **Hardcoded Path** (Line 16)
   ```bash
   PROJECT_DIR="/home/wtyler/pdanet-linux"
   ```
   - ❌ Not portable - assumes specific user
   - ❌ Breaks for other users/installations
   - ✅ **Fix:** Use `SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)`

2. **No Rollback on Failure**
   - If installation fails mid-way, system left in inconsistent state
   - No automatic cleanup
   - ✅ **Fix:** Add trap handler for cleanup

3. **Dependency Version Not Checked**
   - Installs any version of packages
   - No minimum version validation
   - Potential incompatibility issues

**Medium:**
4. **Sudo User Detection Fallback** (Line 112)
   ```bash
   if [ -z "$REAL_USER" ]; then
       REAL_USER="wtyler"  # Fallback to current user
   fi
   ```
   - ❌ Hardcoded username fallback
   - ✅ **Fix:** Fail with error message instead

5. **No Pre-installation Checks**
   - Doesn't verify disk space
   - Doesn't check Python version
   - Doesn't validate NetworkManager availability

6. **Silent Failures with `|| true`**
   - Many commands have `|| true` suppressing errors
   - May hide real problems
   - Example: Line 162 `update-desktop-database ... || true`

**Low:**
7. **Missing Installation Verification**
   - Doesn't test if installation actually works
   - No post-install validation
   - User must manually verify

8. **Package Installation Not Atomic**
   - Installs packages one by one
   - If one fails mid-way, partial installation

#### 🛠️ Recommended Improvements

```bash
#!/bin/bash
# Improved install.sh

set -euo pipefail  # Add -u for unset variables, -o pipefail for pipe errors

# Dynamic project directory detection
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_DIR="$SCRIPT_DIR"

# Cleanup trap
cleanup() {
    if [ $? -ne 0 ]; then
        echo "Installation failed! Rolling back changes..."
        # Rollback logic here
    fi
}
trap cleanup EXIT

# Pre-installation checks
check_requirements() {
    # Check Python version
    if ! python3 --version | grep -qE "Python 3\.(8|9|10|11|12)"; then
        echo "Error: Python 3.8+ required"
        exit 1
    fi
    
    # Check disk space (need at least 100MB)
    FREE_SPACE=$(df -m "$PROJECT_DIR" | awk 'NR==2 {print $4}')
    if [ "$FREE_SPACE" -lt 100 ]; then
        echo "Error: Insufficient disk space (need 100MB, have ${FREE_SPACE}MB)"
        exit 1
    fi
    
    # Check NetworkManager
    if ! systemctl is-active --quiet NetworkManager; then
        echo "Error: NetworkManager is not running"
        exit 1
    fi
}

# Detect real user (with validation)
get_real_user() {
    local user="${SUDO_USER:-$USER}"
    if [ -z "$user" ] || [ "$user" = "root" ]; then
        echo "Error: Cannot determine non-root user"
        echo "Please run with: sudo -u USERNAME $0"
        exit 1
    fi
    echo "$user"
}

# Atomic package installation
install_packages() {
    local packages=("$@")
    
    # Check all packages first
    local missing=()
    for pkg in "${packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            missing+=("$pkg")
        fi
    done
    
    # Install all missing packages at once (atomic)
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Installing: ${missing[*]}"
        DEBIAN_FRONTEND=noninteractive apt-get install -y "${missing[@]}"
    fi
}

# Post-installation verification
verify_installation() {
    echo "Verifying installation..."
    
    # Check if commands are accessible
    local commands=("pdanet-connect" "pdanet-disconnect" "pdanet-gui-v2")
    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            echo "Error: Command $cmd not found in PATH"
            return 1
        fi
    done
    
    # Check if GUI can import GTK
    if ! python3 -c "import gi; gi.require_version('Gtk', '3.0')" 2>/dev/null; then
        echo "Error: GTK3 Python bindings not working"
        return 1
    fi
    
    echo "✓ Installation verified"
}
```

---

### 2. wifi-stealth.sh Analysis

#### ✅ Strengths
- Well-documented bypass layers
- Incremental stealth levels (1-3)
- Comprehensive carrier bypass techniques
- Color-coded output
- Good error handling with `|| true`

#### ⚠️ Weaknesses

**Critical:**
1. **No State Tracking**
   - Doesn't track which rules were actually applied
   - Cleanup may miss rules if enable partially failed
   - Can lead to orphaned iptables rules

2. **Race Condition in enable/disable**
   - No locking mechanism
   - Multiple processes could conflict
   - ✅ **Fix:** Use flock for mutual exclusion

3. **Dangerous String Matching** (Lines 103-112)
   ```bash
   iptables -A OUTPUT -m string --string "windowsupdate" --algo bm -j DROP
   ```
   - ❌ Can match ANY packet containing string (even encrypted)
   - ❌ May block legitimate traffic
   - ❌ HTTPS encrypted, won't match anyway
   - ✅ **Fix:** Use DNS-based blocking or SNI inspection

**Medium:**
4. **No Validation of Interface**
   - Doesn't check if `$WIFI_INTERFACE` exists
   - May apply rules to non-existent interface
   - ✅ **Fix:** Validate interface with `ip link show`

5. **Gateway Detection Can Fail** (Line 79)
   ```bash
   GATEWAY=$(ip route | grep "default.*$WIFI_INTERFACE" | awk '{print $3}')
   ```
   - No error handling if gateway not found
   - DNS redirect fails silently
   - ✅ **Fix:** Check if GATEWAY is non-empty

6. **IPv6 Blocking Too Aggressive** (Lines 63-65)
   ```bash
   ip6tables -P INPUT DROP
   ip6tables -P FORWARD DROP
   ip6tables -P OUTPUT DROP
   ```
   - Blocks ALL IPv6 system-wide, not just interface
   - May break other services
   - ✅ **Fix:** Only block on specific interface

**Low:**
7. **No Effectiveness Monitoring**
   - Can't tell if bypass is actually working
   - No carrier detection testing
   - User has no feedback on success

8. **Cleanup May Be Incomplete**
   - If enable fails mid-way, partial rules remain
   - disable_stealth may not catch all rules
   - No idempotency guarantee

#### 🛠️ Recommended Improvements

```bash
#!/bin/bash
# Improved wifi-stealth.sh

set -euo pipefail

# Lock file to prevent concurrent execution
LOCK_FILE="/var/lock/wifi-stealth.lock"

acquire_lock() {
    exec 200>"$LOCK_FILE"
    flock -n 200 || {
        echo "Error: Another instance is running"
        exit 1
    }
}

# State file to track applied rules
STATE_FILE="/var/run/wifi-stealth-state.json"

save_state() {
    local interface=$1
    local level=$2
    local applied_rules=("$@")
    
    cat > "$STATE_FILE" << EOF
{
    "interface": "$interface",
    "level": $level,
    "applied_rules": [$(printf '"%s",' "${applied_rules[@]}" | sed 's/,$//')],
    "timestamp": $(date +%s)
}
EOF
}

load_state() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    fi
}

# Validate interface exists
validate_interface() {
    local iface=$1
    if ! ip link show "$iface" &>/dev/null; then
        echo "Error: Interface $iface does not exist"
        return 1
    fi
}

# Improved TTL setting with validation
apply_ttl_layer() {
    local interface=$1
    
    # Create chain
    if ! iptables -t mangle -N WIFI_STEALTH 2>/dev/null; then
        iptables -t mangle -F WIFI_STEALTH
    fi
    
    # Set TTL
    iptables -t mangle -A WIFI_STEALTH -j TTL --ttl-set 65
    
    # Apply to interface only
    iptables -t mangle -A POSTROUTING -o "$interface" -j WIFI_STEALTH
    
    # Verify rule was applied
    if ! iptables -t mangle -C POSTROUTING -o "$interface" -j WIFI_STEALTH 2>/dev/null; then
        echo "Error: TTL rule failed to apply"
        return 1
    fi
    
    echo "applied:ttl"
}

# Improved DNS layer with validation
apply_dns_layer() {
    local interface=$1
    
    # Get and validate gateway
    local gateway
    gateway=$(ip route | grep "default.*$interface" | awk '{print $3}')
    
    if [ -z "$gateway" ]; then
        echo "Warning: No default gateway found for $interface"
        return 1
    fi
    
    # Validate gateway is reachable
    if ! ping -c 1 -W 2 "$gateway" &>/dev/null; then
        echo "Warning: Gateway $gateway not reachable"
        return 1
    fi
    
    # Apply DNS redirect
    iptables -t nat -A OUTPUT -o "$interface" -p udp --dport 53 \
        -j DNAT --to "$gateway:53"
    
    echo "applied:dns:$gateway"
}

# DNS-based blocking instead of string matching
apply_domain_blocking() {
    # Use dnsmasq or unbound for DNS-based blocking
    # Much more effective than string matching
    
    local block_domains=(
        "windowsupdate.com"
        "update.microsoft.com"
        "swcdn.apple.com"
        "mesu.apple.com"
    )
    
    # Add to /etc/hosts or configure dnsmasq
    for domain in "${block_domains[@]}"; do
        echo "0.0.0.0 $domain" >> /etc/hosts.pdanet-block
    done
    
    echo "applied:dns_block"
}

# Effectiveness monitoring
monitor_effectiveness() {
    local interface=$1
    
    # Check if TTL is actually being set
    local ttl_packets
    ttl_packets=$(iptables -t mangle -L WIFI_STEALTH -v -n | awk 'NR==3 {print $1}')
    
    if [ "$ttl_packets" -gt 0 ]; then
        echo "✓ TTL modification active ($ttl_packets packets processed)"
    else
        echo "⚠ TTL modification not processing packets"
    fi
    
    # Check for IPv6 leaks
    if ping6 -c 1 google.com &>/dev/null; then
        echo "⚠ WARNING: IPv6 leak detected!"
    else
        echo "✓ No IPv6 leaks"
    fi
    
    # Check DNS
    local dns_server
    dns_server=$(nmcli dev show "$interface" | grep IP4.DNS | awk '{print $2}')
    echo "DNS: $dns_server"
}
```

---

### 3. stealth-mode.sh Analysis

#### ⚠️ Major Issues

**Critical:**
1. **String Matching on HTTPS** (Lines 45-53)
   ```bash
   iptables -A OUTPUT -p tcp --dport 443 -m string --string "windowsupdate.com" --algo bm -j DROP
   ```
   - ❌ **COMPLETELY INEFFECTIVE** - HTTPS is encrypted!
   - String matching can't see inside TLS
   - False sense of security
   - ✅ **Fix:** Remove or replace with DNS/SNI blocking

2. **Blocking apple.com** (Line 52)
   ```bash
   iptables -A OUTPUT -p tcp --dport 80 -m string --string "apple.com" --algo bm -j DROP
   ```
   - ❌ TOO BROAD - blocks ALL apple.com traffic
   - Will break legitimate Apple services
   - User can't access Apple website
   - ✅ **Fix:** Be more specific or remove

---

### 4. iptables-rules.sh Analysis

#### ✅ Strengths
- Clean chain management
- Proper exclusions for local networks
- Idempotent (can run multiple times safely)

#### ⚠️ Weaknesses

**Medium:**
1. **No Validation of redsocks Running**
   - Applies rules even if redsocks isn't running
   - Traffic gets blackholed
   - ✅ **Fix:** Check if redsocks is active first

2. **No Traffic Verification**
   - Doesn't test if redirection works
   - User won't know if rules are effective

---

## 🎯 PRIORITY FIXES

### CRITICAL (Do Immediately)

1. **Remove Ineffective HTTPS String Matching**
   ```bash
   # DELETE these lines from stealth-mode.sh:
   # Lines 46-47, 49 (HTTPS string matching)
   ```

2. **Fix Hardcoded Paths in install.sh**
   ```bash
   # Replace:
   PROJECT_DIR="/home/wtyler/pdanet-linux"
   
   # With:
   SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
   PROJECT_DIR="$SCRIPT_DIR"
   ```

3. **Add State Tracking to wifi-stealth.sh**
   - Track which rules were applied
   - Ensure complete cleanup

### HIGH (Within 1 Week)

4. **Add Rollback to install.sh**
   - Trap errors and cleanup on failure
   - Restore system to previous state

5. **Add Interface Validation**
   - Check interface exists before applying rules
   - Validate gateway reachability

6. **Add Locking to Prevent Concurrent Execution**
   - Use flock for mutual exclusion
   - Prevent race conditions

### MEDIUM (Within 1 Month)

7. **Add Installation Verification**
   - Test installation after completion
   - Verify all components work

8. **Add Effectiveness Monitoring**
   - Check if bypass is actually working
   - Detect leaks and failures

9. **Improve Error Messages**
   - More specific error messages
   - Actionable solutions

---

## 📊 SCRIPT QUALITY SCORES

| Script | Security | Reliability | Maintainability | Overall |
|--------|----------|-------------|-----------------|---------|
| install.sh | 7/10 | 6/10 | 8/10 | 7/10 |
| uninstall.sh | 8/10 | 7/10 | 8/10 | 7.7/10 |
| wifi-stealth.sh | 6/10 | 7/10 | 8/10 | 7/10 |
| stealth-mode.sh | 4/10 ⚠️ | 6/10 | 7/10 | 5.7/10 ⚠️ |
| iptables-rules.sh | 8/10 | 8/10 | 9/10 | 8.3/10 |

**Average:** 7.1/10

---

## 🚀 ENHANCEMENT IDEAS

### 1. Unified Script Manager
Create `/app/scripts/pdanet-manager.sh`:
```bash
#!/bin/bash
# Central management script

pdanet-manager() {
    case "$1" in
        install) bash "$SCRIPT_DIR/install.sh" ;;
        uninstall) bash "$SCRIPT_DIR/uninstall.sh" ;;
        enable-stealth) bash "$SCRIPT_DIR/scripts/wifi-stealth.sh" enable "$2" "$3" ;;
        status) show_status ;;
        health-check) run_health_check ;;
        *)
            echo "Usage: pdanet-manager {install|uninstall|enable-stealth|status|health-check}"
            ;;
    esac
}
```

### 2. Health Check System
```bash
health_check() {
    echo "PdaNet Linux Health Check"
    echo "========================="
    
    # Check dependencies
    check_package "redsocks"
    check_package "iptables"
    check_package "python3-gi"
    
    # Check services
    check_service "redsocks"
    check_service "NetworkManager"
    
    # Check iptables rules
    check_iptables_rules
    
    # Check for leaks
    check_ipv6_leak
    check_dns_leak
    
    # Overall score
    echo "Health: $score/100"
}
```

### 3. Automatic Leak Detection
```bash
detect_leaks() {
    echo "Scanning for privacy leaks..."
    
    # IPv6 leak test
    if ping6 -c 1 google.com &>/dev/null; then
        echo "⚠️  IPv6 LEAK DETECTED"
    fi
    
    # DNS leak test
    local dns_servers=$(nmcli dev show | grep DNS | awk '{print $2}')
    for server in $dns_servers; do
        if [[ ! "$server" =~ ^192\.168\. ]]; then
            echo "⚠️  DNS LEAK: Using external DNS $server"
        fi
    done
    
    # WebRTC leak test (would need browser integration)
}
```

### 4. Carrier Detection Simulation
```bash
simulate_carrier_detection() {
    echo "Simulating carrier detection..."
    
    # Check TTL
    local ttl=$(ping -c 1 8.8.8.8 | grep ttl | awk -F'ttl=' '{print $2}' | awk '{print $1}')
    if [ "$ttl" -eq 65 ]; then
        echo "✓ TTL looks like mobile traffic"
    else
        echo "⚠️  TTL is $ttl (carrier may detect)"
    fi
    
    # Check for OS-specific traffic
    # Monitor outgoing connections for telltale signs
}
```

---

## 📝 DOCUMENTATION GAPS

### Missing from Scripts:

1. **No inline help/usage examples**
   - Scripts need `--help` flag
   - Should show examples for each command

2. **No version information**
   - Scripts should have version numbers
   - Helps with debugging

3. **No logging**
   - Actions not logged to file
   - Hard to debug issues

4. **No dry-run mode**
   - Can't preview changes
   - Risky for users to test

---

## 🎬 CONCLUSION

**Overall Script Quality: 7.1/10 - Good but needs security fixes**

**Critical Issues:**
- ⚠️ HTTPS string matching is completely broken (stealth-mode.sh)
- ⚠️ Hardcoded paths break portability (install.sh)
- ⚠️ No state tracking leads to incomplete cleanup

**Recommendation:** 
1. Fix critical security issues (HTTPS string matching)
2. Make scripts portable (remove hardcoded paths)
3. Add proper state tracking and rollback

**After fixes: Estimated 8.5/10**

