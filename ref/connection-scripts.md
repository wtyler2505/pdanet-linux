# Connection Scripts - Technical Reference

**Last Updated:** 2025-10-03
**Location:** Project root and `/usr/local/bin/`

## Overview

PdaNet Linux provides command-line scripts for USB and WiFi tethering. These scripts handle interface detection, validation, service management, and stealth mode activation.

## Script Inventory

| Script | Location | Purpose | Root Required |
|--------|----------|---------|---------------|
| `pdanet-connect` | `/usr/local/bin/` | USB tethering connection | Yes |
| `pdanet-disconnect` | `/usr/local/bin/` | USB tethering disconnect | Yes |
| `pdanet-wifi-connect` | `/usr/local/bin/` | WiFi connection with bypass | Yes |
| `pdanet-wifi-disconnect` | `/usr/local/bin/` | WiFi disconnect | Yes |
| `wifi-stealth.sh` | `scripts/` | 6-layer carrier bypass | Yes |
| `stealth-mode.sh` | `scripts/` | USB stealth mode (basic) | Yes |

## USB Tethering Scripts

### pdanet-connect

**Purpose:** Establish USB tethering connection through PdaNet proxy

**Execution Flow:**

```
┌─────────────────────────────────────┐
│  1. Check root permission           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  2. Detect USB tethering interface  │
│     (usb0, rndis0, etc.)            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  3. Validate PdaNet proxy           │
│     curl -x 192.168.49.1:8000       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  4. Start redsocks service          │
│     systemctl start redsocks        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  5. Apply iptables rules            │
│     config/iptables-rules.sh start  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  6. Optional: Enable stealth        │
│     scripts/stealth-mode.sh enable  │
└──────────────┬──────────────────────┘
               │
               ✓ Connected
```

**Key Code Sections:**

**Interface Detection:**
```bash
# Find USB tethering interface
detect_interface() {
    for iface in $(ip link show | grep -o '^[0-9]*: [^:]*' | cut -d' ' -f2 | tr -d ':'); do
        if [[ $iface =~ ^(usb|rndis) ]]; then
            echo $iface
            return 0
        fi
    done
    return 1
}

USB_IFACE=$(detect_interface)
if [ -z "$USB_IFACE" ]; then
    echo "Error: No USB tethering interface found"
    exit 1
fi
```

**Proxy Validation:**
```bash
# Test PdaNet proxy is responding
validate_proxy() {
    curl -x 192.168.49.1:8000 \
         --connect-timeout 10 \
         -s \
         http://www.google.com > /dev/null 2>&1
    return $?
}

if ! validate_proxy; then
    echo "Error: Cannot connect to PdaNet proxy at 192.168.49.1:8000"
    echo "Make sure PdaNet+ app is running on Android"
    exit 1
fi
```

**Service Management:**
```bash
# Start redsocks
systemctl start redsocks

# Wait for service to be ready
sleep 2

# Apply iptables rules
bash /home/wtyler/pdanet-linux/config/iptables-rules.sh start
```

**Output:**
```
PdaNet USB Connector
======================================
[1/4] Detecting USB tethering interface...
✓ USB interface: usb0

[2/4] Validating PdaNet proxy...
✓ Proxy responding at 192.168.49.1:8000

[3/4] Starting services...
✓ redsocks started
✓ iptables rules applied

[4/4] Testing connection...
✓ Internet connection verified

========================================
USB connection established!
========================================

Interface: usb0
Proxy: 192.168.49.1:8000
Status: Connected

To disconnect: sudo pdanet-disconnect
```

---

### pdanet-disconnect

**Purpose:** Cleanly disconnect USB tethering

**Execution Flow:**

```
┌─────────────────────────────────────┐
│  1. Stop iptables redirection       │
│     config/iptables-rules.sh stop   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  2. Stop redsocks service           │
│     systemctl stop redsocks         │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  3. Disable stealth (if active)     │
│     scripts/stealth-mode.sh disable │
└──────────────┬──────────────────────┘
               │
               ✓ Disconnected
```

**Key Code:**
```bash
#!/bin/bash
set -e

echo "Disconnecting PdaNet..."

# Remove iptables rules
bash /home/wtyler/pdanet-linux/config/iptables-rules.sh stop

# Stop redsocks
systemctl stop redsocks

# Disable stealth if active
bash /home/wtyler/pdanet-linux/scripts/stealth-mode.sh disable 2>/dev/null || true

echo "✓ Disconnected successfully"
```

---

## WiFi Tethering Scripts

### pdanet-wifi-connect

**Purpose:** Connect to Android WiFi hotspot with 6-layer carrier bypass

**Execution Flow:**

```
┌─────────────────────────────────────┐
│  1. Detect WiFi interface           │
│     iw dev | awk '$1=="Interface"'  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  2. Scan for networks               │
│     nmcli device wifi rescan        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  3. Connect to hotspot              │
│     nmcli device wifi connect SSID  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  4. Verify internet connectivity    │
│     ping -c 1 8.8.8.8               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  5. Enable aggressive stealth       │
│     wifi-stealth.sh enable wlan0 3  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  6. Final verification              │
│     curl http://www.google.com      │
└──────────────┬──────────────────────┘
               │
               ✓ Connected with bypass
```

**Interface Detection:**
```bash
# Find WiFi interface (usually wlan0)
WIFI_IFACE=$(iw dev | awk '$1=="Interface"{print $2}' | head -1)

if [ -z "$WIFI_IFACE" ]; then
    echo "Error: No WiFi interface found"
    exit 1
fi

echo "✓ WiFi interface: $WIFI_IFACE"
```

**Network Scanning:**
```bash
# Refresh WiFi scan
nmcli device wifi rescan || true
sleep 2

# List available networks
echo "Available networks:"
nmcli -t -f SSID,SIGNAL,SECURITY device wifi list | head -10
```

**Connection with NetworkManager:**
```bash
# Check if already connected
CURRENT_SSID=$(nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2)

if [ -z "$CURRENT_SSID" ]; then
    # Not connected, prompt for credentials
    read -p "Enter Android hotspot SSID: " HOTSPOT_SSID
    read -sp "Enter password: " HOTSPOT_PASS
    echo ""

    # Connect
    nmcli device wifi connect "$HOTSPOT_SSID" password "$HOTSPOT_PASS"

    sleep 3

    # Verify connection
    CURRENT_SSID=$(nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2)
    if [ -z "$CURRENT_SSID" ]; then
        echo "Error: Connection failed"
        exit 1
    fi
fi

echo "✓ Connected to: $CURRENT_SSID"
```

**Internet Verification:**
```bash
# Test with ping
if ping -c 1 -W 5 8.8.8.8 >/dev/null 2>&1; then
    echo "✓ Internet connection verified"
else
    echo "Warning: Cannot reach internet"
fi
```

**Stealth Activation:**
```bash
STEALTH_LEVEL=3  # Aggressive

# Apply 6-layer bypass
bash "$PROJECT_DIR/scripts/wifi-stealth.sh" enable $WIFI_IFACE $STEALTH_LEVEL

echo "✓ Stealth mode active (Level $STEALTH_LEVEL)"
```

**Final HTTP Test:**
```bash
# Test with curl (HTTP GET)
if curl --connect-timeout 5 -s http://www.google.com > /dev/null 2>&1; then
    echo "✓ Connection verified"
else
    echo "Warning: Verification failed (may still work)"
fi
```

**Output:**
```
PdaNet WiFi Connector
======================================
[1/5] Detecting WiFi interface...
✓ WiFi interface: wlan0

[2/5] Scanning for Android hotspot...
Available networks:
AndroidAP:88:WPA2
MyPhone:75:WPA2
...
✓ Already connected to: AndroidAP

[3/5] Verifying internet connectivity...
✓ Internet connection verified

[4/5] Enabling aggressive carrier bypass...
[STEALTH] Layer 1: TTL Normalization
  ✓ TTL set to 65
[STEALTH] Layer 2: IPv6 Blocking
  ✓ IPv6 disabled
[STEALTH] Layer 3: DNS Leak Prevention
  ✓ DNS forced through gateway: 192.168.43.1
[STEALTH] Layer 4: OS Update Blocking
  ✓ OS updates blocked
[STEALTH] Layer 5: MSS/MTU Adjustment
  ✓ MSS clamping enabled
[STEALTH] Layer 6: Traffic Shaping (Optional)
  ✓ Traffic shaping ready
✓ Stealth mode active (Level 3)

[5/5] Final verification...
✓ Connection verified

========================================
WiFi connection established!
========================================

Connected to: AndroidAP
Interface: wlan0
Stealth Level: 3 (Aggressive)

Active Protections:
  ✓ TTL Normalization (64/65)
  ✓ IPv6 Blocking
  ✓ DNS Leak Prevention
  ✓ OS Update Blocking
  ✓ Traffic Fingerprint Obfuscation

Note: Carrier detection avoidance is not 100% foolproof.
For maximum stealth, use a VPN over this connection.

To disconnect: sudo pdanet-wifi-disconnect
```

---

### pdanet-wifi-disconnect

**Purpose:** Disconnect WiFi and disable stealth

**Execution Flow:**

```
┌─────────────────────────────────────┐
│  1. Disable stealth                 │
│     wifi-stealth.sh disable wlan0   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  2. Disconnect from WiFi            │
│     nmcli device disconnect wlan0   │
└──────────────┬──────────────────────┘
               │
               ✓ Disconnected
```

**Key Code:**
```bash
#!/bin/bash
set -e

echo "Disconnecting WiFi..."

# Find WiFi interface
WIFI_IFACE=$(iw dev | awk '$1=="Interface"{print $2}' | head -1)

if [ -n "$WIFI_IFACE" ]; then
    # Disable stealth
    bash /home/wtyler/pdanet-linux/scripts/wifi-stealth.sh disable $WIFI_IFACE

    # Disconnect
    nmcli device disconnect $WIFI_IFACE

    echo "✓ Disconnected from WiFi"
else
    echo "Warning: No WiFi interface found"
fi
```

---

## Stealth Scripts

### scripts/wifi-stealth.sh

**Purpose:** 6-layer carrier detection bypass system

**Usage:**
```bash
# Enable aggressive stealth (Level 3)
sudo ./scripts/wifi-stealth.sh enable wlan0 3

# Check status
sudo ./scripts/wifi-stealth.sh status

# Disable stealth
sudo ./scripts/wifi-stealth.sh disable wlan0
```

**Stealth Levels:**

| Level | Layers Active | Use Case | Effectiveness |
|-------|--------------|----------|---------------|
| 1 | TTL only | Basic carriers | 60% |
| 2 | TTL + IPv6 + DNS | Most carriers | 80% |
| 3 | All 6 layers | Advanced carriers | 85%+ |

**Implementation:** See [carrier-bypass.md](carrier-bypass.md) for detailed analysis

---

### scripts/stealth-mode.sh

**Purpose:** Basic USB stealth mode (TTL modification only)

**Usage:**
```bash
# Enable stealth
sudo ./scripts/stealth-mode.sh enable

# Check status
sudo ./scripts/stealth-mode.sh status

# Disable stealth
sudo ./scripts/stealth-mode.sh disable
```

**Implementation:**
```bash
enable_stealth() {
    # Set TTL to 65 for USB interface
    iptables -t mangle -A POSTROUTING -o usb0 -j TTL --ttl-set 65

    echo "✓ USB stealth mode enabled (TTL=65)"
}

disable_stealth() {
    # Remove TTL modification
    iptables -t mangle -D POSTROUTING -o usb0 -j TTL --ttl-set 65

    echo "✓ USB stealth mode disabled"
}
```

**Difference from WiFi Stealth:**
- USB stealth: TTL only (Layer 1)
- WiFi stealth: All 6 layers
- USB has less carrier scrutiny (often grandfathered)

---

## Error Handling

### Common Errors

**1. No Interface Found**
```bash
Error: No USB tethering interface found
```
**Cause:** USB tethering not enabled on Android
**Solution:** Enable USB tethering in Android settings

**2. Proxy Unreachable**
```bash
Error: Cannot connect to PdaNet proxy at 192.168.49.1:8000
```
**Cause:** PdaNet+ app not running on Android
**Solution:** Open PdaNet+ app, tap "Activate USB Mode"

**3. Permission Denied**
```bash
Error: Must run as root (use sudo)
```
**Cause:** Script requires root for iptables/systemctl
**Solution:** Run with `sudo`

**4. NetworkManager Not Found**
```bash
Error: nmcli command not found
```
**Cause:** NetworkManager not installed (WiFi scripts only)
**Solution:** `sudo apt-get install network-manager`

**5. WiFi Connection Failed**
```bash
Error: Connection failed
```
**Cause:** Wrong SSID/password, or hotspot not active
**Solution:** Verify Android hotspot is enabled, check credentials

---

## Script Dependencies

### Required Commands

| Command | Package | Purpose |
|---------|---------|---------|
| `ip` | iproute2 | Interface management |
| `iptables` | iptables | Firewall rules |
| `systemctl` | systemd | Service management |
| `curl` | curl | Proxy validation |
| `ping` | iputils-ping | Connectivity testing |
| `nmcli` | network-manager | WiFi connection (WiFi scripts) |
| `iw` | iw | WiFi interface detection (WiFi scripts) |

### Installation Check

```bash
# Check all dependencies
for cmd in ip iptables systemctl curl ping nmcli iw; do
    if ! command -v $cmd &> /dev/null; then
        echo "Missing: $cmd"
    fi
done
```

---

## Integration with GUI

The Python GUI (`pdanet_gui_v2.py`) wraps these scripts via subprocess:

```python
def connect_usb(self):
    """Connect via USB using CLI script"""
    result = subprocess.run(
        ["sudo", "pdanet-connect"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        self.state = ConnectionState.CONNECTED
        return True
    else:
        self.logger.error(result.stderr)
        return False

def connect_wifi(self):
    """Connect via WiFi using CLI script"""
    result = subprocess.run(
        ["sudo", "pdanet-wifi-connect"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        self.state = ConnectionState.CONNECTED
        return True
    else:
        self.logger.error(result.stderr)
        return False
```

---

## Testing Scripts

### Test USB Connection

```bash
# Manual test flow
sudo pdanet-connect

# Verify
curl http://www.google.com
ping -c 3 google.com

# Disconnect
sudo pdanet-disconnect
```

### Test WiFi Connection

```bash
# Manual test flow
sudo pdanet-wifi-connect

# Verify TTL
ping -c 1 google.com  # Should show TTL 64 (from 65)

# Verify IPv6 blocked
curl -6 https://ipv6.google.com  # Should FAIL

# Verify DNS
nslookup google.com  # Should show gateway as DNS

# Disconnect
sudo pdanet-wifi-disconnect
```

### Test Stealth

```bash
# Enable
sudo ./scripts/wifi-stealth.sh enable wlan0 3

# Check rules
sudo iptables -t mangle -L WIFI_STEALTH -n -v

# Test
ping -c 1 google.com

# Disable
sudo ./scripts/wifi-stealth.sh disable wlan0
```

---

## Performance Considerations

**Script Execution Time:**
- USB connect: 5-10 seconds
- WiFi connect: 10-15 seconds (with scanning)
- Stealth enable: 1-2 seconds
- Disconnect: 2-3 seconds

**Service Startup:**
- redsocks: ~1-2 seconds
- iptables rules: <1 second
- WiFi connection: 3-5 seconds (NetworkManager)

---

## Security Considerations

### Root Requirements

All scripts require root because they:
- Modify iptables rules
- Manage systemd services
- Configure sysctl parameters
- Manipulate network interfaces

### Sudoers Configuration

**Location:** `/etc/sudoers.d/pdanet-linux`

```bash
# Allow user to run PdaNet scripts without password
wtyler ALL=(ALL) NOPASSWD: /usr/local/bin/pdanet-connect
wtyler ALL=(ALL) NOPASSWD: /usr/local/bin/pdanet-disconnect
wtyler ALL=(ALL) NOPASSWD: /usr/local/bin/pdanet-wifi-connect
wtyler ALL=(ALL) NOPASSWD: /usr/local/bin/pdanet-wifi-disconnect
wtyler ALL=(ALL) NOPASSWD: /home/wtyler/pdanet-linux/scripts/wifi-stealth.sh
```

**Security:**
- Specific commands only (not `ALL`)
- Full paths prevent PATH hijacking
- User-specific (not `ALL`)

---

## References

- [System Architecture](architecture.md)
- [Carrier Bypass Details](carrier-bypass.md)
- [iptables Configuration](iptables-redsocks.md)
- [Python GUI Integration](python-gui.md)
