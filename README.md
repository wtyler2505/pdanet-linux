# PdaNet Linux

Reverse-engineered Linux client for PdaNet+ USB/WiFi tethering with multi-layered carrier detection bypass and professional cyberpunk GTK GUI.

**Target Platform:** Linux (Debian/Ubuntu-based distributions, tested on Linux Mint 22.2 Cinnamon)

## Overview

PdaNet Linux provides system-wide internet connectivity through Android devices running PdaNet+. Unlike simple proxy configurations, this implementation uses transparent traffic redirection to ensure ALL applications use the tethered connection seamlessly.

**Primary Feature:** WiFi hotspot tethering with **6-layer aggressive carrier detection bypass** to hide tethering usage from mobile carriers.

## Key Features

**Network Connectivity:**
- **WiFi Hotspot Tethering** - Primary mode with comprehensive carrier bypass
- **USB Tethering** - Legacy mode with basic stealth capabilities
- **System-wide Coverage** - All applications automatically use tethered connection
- **Transparent Proxy** - redsocks-based traffic redirection (no per-app configuration)

**Carrier Detection Bypass (WiFi Mode):**
- **Layer 1: TTL Normalization** - Sets all packets to TTL 65 (matches phone traffic)
- **Layer 2: IPv6 Complete Block** - Prevents IPv6 leaks that reveal desktop traffic
- **Layer 3: DNS Leak Prevention** - Forces all DNS through phone gateway
- **Layer 4: OS Update Blocking** - Blocks Windows/Mac/Ubuntu update fingerprinting
- **Layer 5: MSS/MTU Clamping** - Matches phone packet characteristics
- **Layer 6: Traffic Shaping** - Optional bandwidth limiting (disabled for speed)

**GUI Application:**
- **Professional Cyberpunk Theme** - Pure black (#000000), green/red/yellow accents
- **Real-time Monitoring** - Live bandwidth stats, connection health, ping latency
- **System Tray Integration** - Minimize to tray with status indicators
- **Auto-reconnect** - Exponential backoff retry logic
- **Connection Profiles** - Save and manage multiple configurations
- **Statistics Dashboard** - 4-panel layout with comprehensive metrics

**Quality Assurance:**
- **Comprehensive Test Suite** - Unit, integration, performance, edge case tests
- **Visual Regression Testing** - Automated GTK GUI validation across resolutions
- **Accessibility Testing** - WCAG AA compliance, color contrast validation
- **CI/CD Integration** - GitHub Actions workflows for automated quality gates
- **Code Quality Hooks** - Automated black, isort, flake8, mypy, pytest on save

## Requirements

### Android Device
- PdaNet+ app installed (download from https://pdanet.co/)
- Android 5.0+ recommended
- USB debugging enabled (optional but recommended)
- WiFi hotspot capability OR USB tethering support

### Linux System
- Debian/Ubuntu-based distribution (tested on Linux Mint 22.2)
- Python 3.8+
- GTK 3.0+
- Root/sudo access
- iptables and redsocks packages

## Installation

### Quick Install

```bash
# Clone repository
git clone https://github.com/wtyler2505/pdanet-linux.git
cd pdanet-linux

# Run installer (requires sudo)
sudo ./install.sh
```

The installer will:
- Install system dependencies (redsocks, iptables, NetworkManager, GTK3 bindings)
- Install Python dependencies from requirements.txt
- Configure sudoers for password-less connection commands
- Create desktop entry and system commands
- Set up configuration directory at ~/.config/pdanet-linux/

### Manual Installation

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y redsocks iptables python3-gi gir1.2-gtk-3.0 \
  gir1.2-appindicator3-0.1 network-manager python3-pip

# Install Python dependencies
pip install --break-system-packages -r requirements.txt

# Copy files to system locations
sudo cp pdanet-* /usr/local/bin/
sudo cp config/pdanet-linux-v2.desktop /usr/share/applications/
sudo cp config/redsocks.conf /etc/

# Create sudoers entry
echo "$USER ALL=(ALL) NOPASSWD: /usr/local/bin/pdanet-*" | \
  sudo tee /etc/sudoers.d/pdanet-linux
```

## Usage

### WiFi Hotspot Mode (RECOMMENDED)

**Why WiFi Mode:** This is the PRIMARY use case. WiFi mode includes the full 6-layer carrier detection bypass system, making it significantly harder for carriers to detect tethering compared to USB mode.

#### 1. Android Setup
```
1. Open PdaNet+ app on Android
2. Enable "WiFi Direct Hotspot"
3. Note the SSID and password displayed
4. Leave PdaNet+ app running
```

#### 2. Linux Connection - GUI Method

```bash
# Launch GUI
pdanet-gui-v2

# Or start minimized to system tray
pdanet-gui-v2 --start-minimized
```

**GUI Features:**
- Click **CONNECT** button to initiate WiFi connection
- Toggle **Stealth Mode** for aggressive carrier bypass (Level 1-3)
- View real-time bandwidth stats and connection health
- Monitor ping latency and connection duration
- Save connection profiles for quick reconnection

#### 3. Linux Connection - CLI Method

```bash
# Connect to WiFi hotspot with full bypass
sudo pdanet-wifi-connect

# Disconnect
sudo pdanet-wifi-disconnect

# Manual stealth control (advanced)
sudo ./scripts/wifi-stealth.sh enable wlan0 3  # Level 3 = aggressive
sudo ./scripts/wifi-stealth.sh status
sudo ./scripts/wifi-stealth.sh disable wlan0
```

**Stealth Levels:**
- **Level 1 (Light):** TTL normalization only
- **Level 2 (Standard):** TTL + IPv6 blocking + DNS redirection
- **Level 3 (Aggressive):** All 6 layers enabled (RECOMMENDED)

### USB Tethering Mode (Legacy)

USB mode provides basic connectivity with limited stealth capabilities. Use WiFi mode for maximum carrier bypass effectiveness.

#### 1. Android Setup
```
1. Connect Android device via USB
2. Open PdaNet+ app
3. Enable "Activate USB Mode"
4. Leave PdaNet+ app running
```

#### 2. Linux Connection

```bash
# Connect via USB
sudo pdanet-connect

# Disconnect
sudo pdanet-disconnect

# Enable basic stealth (TTL modification only)
sudo pdanet-stealth enable
sudo pdanet-stealth status
sudo pdanet-stealth disable
```

## Architecture

### System Overview

```
Android Device (PdaNet+ app)
         |
    [USB Cable] OR [WiFi Hotspot]
         |
    Proxy: 192.168.49.1:8000 (USB)
    OR WiFi Gateway (WiFi)
         |
[WiFi Mode: 6-layer bypass via iptables/sysctl]
         |
    redsocks (port 12345)
         |
    iptables NAT/mangle rules
         |
    All Linux Applications
```

### Core Components

**Connection Management:**
- `connection_manager.py` - State machine (DISCONNECTED → CONNECTING → CONNECTED → DISCONNECTING)
- `pdanet-wifi-connect` - WiFi hotspot connection script with NetworkManager integration
- `pdanet-connect` - USB tethering connection script with interface auto-detection
- `wifi-stealth.sh` - 6-layer carrier bypass implementation

**GUI System:**
- `pdanet_gui_v2.py` - Main GTK3 application (646 lines)
- `theme.py` - Cyberpunk color system and GTK CSS generation (320 lines)
- `stats_collector.py` - Real-time bandwidth and latency monitoring (245 lines)
- `config_manager.py` - Settings persistence and profile management (227 lines)
- `logger.py` - Rotating file logger with GUI buffer (134 lines)

**Network Stack:**
- `redsocks` - Transparent TCP-to-HTTP-proxy redirector
- `iptables` - Traffic routing, TTL modification, DNS redirection
- `sysctl` - IPv6 disabling, network parameter tuning
- `NetworkManager` - WiFi connection management

### Data Flow

1. **Connection Establishment:**
   - GUI/CLI initiates connection request
   - ConnectionManager validates interface availability
   - NetworkManager connects to WiFi OR USB interface detection
   - Validates proxy availability at 192.168.49.1:8000

2. **Traffic Redirection:**
   - iptables REDSOCKS chain redirects TCP traffic to redsocks (port 12345)
   - redsocks forwards to PdaNet proxy via HTTP CONNECT
   - Mangle table modifies TTL to 65 (carrier bypass)
   - NAT table redirects DNS to gateway (prevent leaks)

3. **Carrier Bypass (WiFi Mode):**
   - All outgoing packets get TTL 65 (Layer 1)
   - IPv6 completely disabled via sysctl (Layer 2)
   - DNS forced through gateway (Layer 3)
   - OS update domains blocked (Layer 4)
   - MSS/MTU clamped to phone values (Layer 5)
   - Optional traffic shaping (Layer 6)

## Carrier Bypass Effectiveness

**Detection Methods Defeated:**
- TTL Decrement Analysis - DEFEATED (TTL set to 65)
- IPv6 Traffic Analysis - DEFEATED (IPv6 completely blocked)
- DNS Pattern Analysis - DEFEATED (all DNS through gateway)
- OS Fingerprinting - DEFEATED (update servers blocked)
- Packet Size Analysis - MITIGATED (MSS/MTU clamping)

**Detection Methods NOT Defeated:**
- Deep Packet Inspection (DPI) on HTTPS - PARTIAL (use VPN)
- Machine Learning Traffic Analysis - PARTIAL (use VPN)
- Carrier-specific proprietary methods - UNKNOWN

**Recommendation:** For maximum stealth, run a VPN over the tethered connection. This adds encryption and further obscures traffic patterns.

## Testing and Quality Assurance

### Test Suite Coverage

**Unit Tests** (1,366 lines across 8 files):
- Connection state machine and auto-reconnect logic
- Bandwidth tracking and statistics calculations
- Configuration persistence and profile management
- Cyberpunk theme validation and GTK CSS generation

**Visual Regression Tests** (1,200+ lines):
- Screenshot comparison across 5 resolutions (800x600 to 2560x1440)
- WCAG AA accessibility compliance (contrast ratios, touch targets)
- Responsive layout validation at multiple breakpoints
- Component-level theme validation (cyberpunk colors, no emoji)

**CI/CD Integration:**
- GitHub Actions workflow for automated testing
- Matrix testing across Python 3.9-3.11
- Automated baseline management for visual tests
- PR commenting with test results and coverage reports

### Running Tests

```bash
# Unit tests
pytest tests/ -v --cov=src --cov-report=html

# Visual regression tests (requires Xvfb)
cd tests/visual
make test-all

# Quick visual test
make quick-test

# Create new baselines (after approved UI changes)
make baselines
```

See `tests/README.md` and `tests/visual/README.md` for comprehensive testing documentation.

## Configuration

### GUI Settings

Configuration is stored in `~/.config/pdanet-linux/config.json`:

```json
{
  "auto_reconnect": true,
  "reconnect_delay": 5,
  "stealth_level": 3,
  "start_minimized": false,
  "show_notifications": true,
  "update_interval": 1.0,
  "profiles": [
    {
      "name": "My Phone",
      "ssid": "AndroidAP_1234",
      "interface": "wlan0",
      "stealth_level": 3
    }
  ]
}
```

### Custom Proxy Port

If PdaNet uses a non-standard port, edit `/etc/redsocks.conf`:

```
redsocks {
    type = http-connect;
    ip = 192.168.49.1;
    port = 8000;  # Change this if needed
}
```

### Stealth Level Configuration

Edit `scripts/wifi-stealth.sh` to customize bypass behavior:

```bash
# Line 45-50: Customize TTL value
TTL_VALUE=65  # Standard phone TTL

# Line 120-125: Add custom blocked domains
BLOCKED_DOMAINS=(
    "windowsupdate.com"
    "apple.com"
    # Add more domains here
)
```

## Troubleshooting

### Connection Issues

**Problem:** No USB tethering interface found
```bash
# Check available interfaces
ip link show

# Look for usb0, rndis0, or similar
# If missing, verify USB debugging is enabled on Android
```

**Problem:** Cannot connect to PdaNet proxy
```bash
# Test proxy manually
curl -x 192.168.49.1:8000 http://www.google.com

# If this fails:
# 1. Restart PdaNet+ app on Android
# 2. Toggle "Activate USB Mode" off and on
# 3. Check Android USB connection mode (should be "USB tethering")
```

**Problem:** WiFi hotspot not detected
```bash
# Check NetworkManager status
nmcli device wifi list

# Manually connect
nmcli device wifi connect "AndroidAP_XXXX" password "yourpassword"
```

### Carrier Detection Issues

**Problem:** Carrier still detecting tethering despite stealth mode

**Solutions (in order of effectiveness):**

1. **Use VPN over tethered connection** (MOST EFFECTIVE)
   - Install any VPN client (OpenVPN, WireGuard, commercial VPN)
   - Connect to tethered internet first, THEN connect VPN
   - This encrypts all traffic and defeats DPI

2. **Verify all bypass layers are active**
   ```bash
   sudo ./scripts/wifi-stealth.sh status
   # Should show: TTL=65, IPv6 DISABLED, DNS redirected, etc.
   ```

3. **Try different stealth levels**
   ```bash
   # Start with Level 3 (aggressive)
   sudo ./scripts/wifi-stealth.sh enable wlan0 3
   ```

4. **Check for IPv6 leaks**
   ```bash
   # This should FAIL (timeout)
   curl -6 https://ipv6.google.com

   # If it succeeds, IPv6 is not properly blocked
   ```

### Performance Issues

**Problem:** Slow speeds or high latency
- **Expected:** Some overhead is normal with transparent proxying
- **Solution:** Disable traffic shaping in wifi-stealth.sh (Layer 6)
- **Monitor:** Use GUI statistics panel to identify bottlenecks

**Problem:** High CPU usage
- **Check:** `top` command, look for redsocks or iptables processes
- **Solution:** Reduce GUI update interval in config.json

### GUI Issues

**Problem:** GUI won't start
```bash
# Check GTK dependencies
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk"

# If error, install GTK bindings
sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

**Problem:** System tray icon not showing
```bash
# Install AppIndicator
sudo apt-get install gir1.2-appindicator3-0.1

# Restart GUI
```

**Problem:** Theme not applying
- Check `~/.config/pdanet-linux/pdanet.log` for GTK CSS errors
- GTK3 CSS does NOT support `text-transform` or `letter-spacing`
- Ensure pure black background (#000000) is enforced

## Documentation

### Architecture Documentation

Comprehensive technical documentation is available in the `/ref` directory:

- **`ref/architecture.md`** - Complete system architecture and data flow
- **`ref/carrier-bypass.md`** - Deep dive into 6-layer bypass mechanisms
- **`ref/iptables-redsocks.md`** - Complete iptables and redsocks configuration
- **`ref/python-gui.md`** - GTK3 GUI implementation details
- **`ref/connection-scripts.md`** - Connection script internals

### Additional Documentation

The `/docs` directory contains:

- Architecture reviews and ADRs (Architecture Decision Records)
- Security architecture and threat models
- Developer onboarding guides
- Performance analysis reports
- System dynamics models
- Visual testing performance analysis

Start with `ref/architecture.md` for a complete technical overview.

## Uninstallation

```bash
# Run uninstaller
sudo ./uninstall.sh

# Remove configuration (optional)
rm -rf ~/.config/pdanet-linux/

# Remove project directory
cd ..
rm -rf pdanet-linux/
```

## Comparison with PdaNet Windows Client

| Feature | Windows PdaNet | pdanet-linux |
|---------|---------------|--------------|
| USB Tethering | YES | YES |
| WiFi Hotspot | YES | YES (Primary Mode) |
| WiFi Direct | YES | NO |
| Bluetooth | YES | NO |
| Hide Usage (USB) | YES | YES (Basic TTL) |
| Hide Usage (WiFi) | YES | YES (6-layer bypass) |
| Auto-connect | YES | Manual/Scripted |
| GUI | YES | YES (GTK3 cyberpunk) |
| CLI | NO | YES |
| System Tray | YES | YES (AppIndicator) |
| System-wide | YES | YES (iptables) |
| Real-time Stats | NO | YES |
| Visual Testing | NO | YES (Comprehensive) |
| Open Source | NO | YES (MIT License) |

## Development

### Project Structure

```
pdanet-linux/
├── src/                    # Python source code
│   ├── pdanet_gui_v2.py   # Main GUI application
│   ├── connection_manager.py
│   ├── theme.py
│   ├── stats_collector.py
│   ├── config_manager.py
│   └── logger.py
├── scripts/               # Shell scripts
│   ├── wifi-stealth.sh   # 6-layer bypass
│   └── stealth-mode.sh   # USB stealth
├── tests/                # Test suite
│   ├── test_*.py        # Unit tests
│   └── visual/          # Visual regression
├── ref/                  # Technical reference docs
├── docs/                 # Additional documentation
├── config/              # System configuration files
├── install.sh           # Installer
├── uninstall.sh         # Uninstaller
└── requirements.txt     # Python dependencies
```

### Code Quality

The project uses automated quality assurance via Claude Code hooks:

- **black** - Code formatting (auto-applied on save)
- **isort** - Import sorting (auto-applied on save)
- **flake8** - Linting (blocks on errors)
- **mypy** - Type checking (blocks on errors)
- **pytest** - Auto-runs tests for modified modules

Install quality tools:
```bash
pip install --break-system-packages black isort flake8 mypy pytest
```

### Design Constraints

**CRITICAL - MUST FOLLOW:**

1. **Name:** MUST be called "PdaNet Linux" or "pdanet-linux" (NO suffixes)
2. **Theme:** Cyberpunk only - pure black (#000000), green/red/yellow accents
3. **NO EMOJI:** Professional interface only (strictly enforced)
4. **GTK3 CSS:** NEVER use `text-transform` or `letter-spacing` (causes errors)
5. **Logging:** NEVER use print() - use logger system exclusively
6. **WiFi Bypass:** PRIMARY feature - TTL normalization to 65 is CRITICAL

### Contributing

1. Read `CLAUDE.md` for AI assistant optimization guidelines
2. Follow existing code patterns and design constraints
3. Add tests for new functionality (unit + visual if GUI-related)
4. Ensure hooks pass (black, isort, flake8, mypy, pytest)
5. Update documentation for user-facing changes
6. Test on actual Android device before submitting PR

## Reverse Engineering Notes

This client was created through analysis of the PdaNet Windows executable:

**Key Discoveries:**
- PdaNet uses standard HTTP CONNECT proxy protocol (no proprietary encryption)
- Proxy runs on 192.168.49.1:8000 for USB, gateway for WiFi
- "Hide Usage" feature = TTL normalization + traffic filtering
- WiFi Direct uses standard Android hotspot with proxy configuration
- No client-side authentication required (phone validates via connection)

**Replication Strategy:**
- Use `redsocks` for transparent proxy redirection
- Use `iptables` for TTL modification and DNS redirection
- Use `sysctl` for IPv6 disabling and network tuning
- Use `NetworkManager` for WiFi connection automation

## Legal Notice

This software is for educational purposes and personal use. PdaNet+ is a trademark of June Fabrics Technology Inc. This project is not affiliated with or endorsed by June Fabrics Technology Inc.

**Disclaimer:** This software is provided as-is. Verify your mobile carrier's terms of service regarding tethering. The carrier bypass features are for educational purposes. Users are responsible for compliance with applicable laws and carrier policies.

## License

MIT License

Copyright (c) 2025 PdaNet Linux Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Support

**For issues with:**
- **This Linux client:** Check Troubleshooting section, review logs in `~/.config/pdanet-linux/pdanet.log`
- **PdaNet+ Android app:** Visit https://pdanet.co/
- **Carrier tethering policies:** Contact your mobile carrier

**GitHub:** https://github.com/wtyler2505/pdanet-linux

---

**PdaNet Linux** - Professional reverse-engineered Linux tethering client with comprehensive carrier detection bypass.
