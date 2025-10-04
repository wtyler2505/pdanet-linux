# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

PdaNet Linux is a reverse-engineered Linux client for PdaNet+ USB/WiFi tethering. It provides system-wide internet connectivity through Android devices with multi-layered carrier detection bypass. The project consists of connection scripts, stealth/bypass mechanisms, and a professional cyberpunk-themed GTK GUI.

**Target Platform:** Linux Mint 22.2 Cinnamon (Debian/Ubuntu-based)

## Commands

### CRITICAL: Command Execution Timeouts

**ALL commands MUST use 30-minute timeout (1800000ms).** Never allow commands to timeout prematurely when they're running correctly.

When executing any Bash command, ALWAYS specify `timeout: 1800000` (30 minutes in milliseconds).

Example:
```
Bash tool with timeout: 1800000
```

This applies to:
- Build commands (npm, pip, compilation)
- Installation commands (apt, pip install, npm install)
- Long-running searches (find, grep, git operations)
- System commands (sudo operations, service management)
- ANY command that may take more than 2 minutes

**NEVER accept the default 2-minute timeout.** Commands that are running successfully should NEVER fail due to timeout.

### Development Setup

**Install Python dependencies:**
```bash
pip install --break-system-packages -r requirements.txt
```

**Run Python linting/formatting:**
```bash
black src/*.py              # Format code
isort src/*.py              # Sort imports
flake8 src/*.py             # Lint code
mypy src/*.py               # Type check
pytest tests/               # Run tests
```

### Installation and Setup

**Install the application:**
```bash
sudo ./install.sh
```

**Uninstall the application:**
```bash
sudo ./uninstall.sh
```

### USB Tethering Mode

**Connect via USB (CLI):**
```bash
sudo pdanet-connect
```

**Disconnect USB (CLI):**
```bash
sudo pdanet-disconnect
```

**Enable stealth mode (USB):**
```bash
sudo pdanet-stealth enable
sudo pdanet-stealth status
sudo pdanet-stealth disable
```

### WiFi Tethering Mode (Primary Feature)

**Connect to WiFi hotspot with carrier bypass:**
```bash
sudo pdanet-wifi-connect
```

**Disconnect WiFi:**
```bash
sudo pdanet-wifi-disconnect
```

**Manual stealth control:**
```bash
sudo ./scripts/wifi-stealth.sh enable wlan0 3  # Level 3 = aggressive
sudo ./scripts/wifi-stealth.sh status
sudo ./scripts/wifi-stealth.sh disable wlan0
```

### GUI Application

**Launch GUI:**
```bash
pdanet-gui-v2
```

**Launch minimized to tray:**
```bash
pdanet-gui-v2 --start-minimized
```

## High-Level Architecture

### Dual-Mode Connection System

**USB Mode:**
- Detects USB tethering interface (usb0, rndis0)
- Validates HTTP proxy at 192.168.49.1:8000
- Uses **redsocks** for transparent TCP-to-proxy redirection
- Applies iptables rules to route all traffic through proxy
- Basic stealth: TTL modification

**WiFi Mode (Primary Use Case):**
- Connects to Android WiFi hotspot via NetworkManager
- Implements 6-layer aggressive carrier detection bypass
- Most important feature for hiding tethering from carriers

### Carrier Bypass Architecture (WiFi Mode)

The core value proposition is **6-layer carrier detection bypass**:

1. **TTL Normalization** (Layer 1 - CRITICAL)
   - Sets all outgoing packets to TTL 65 (matching phone traffic)
   - Prevents carriers from detecting TTL decrement that reveals tethering
   - Implemented via iptables mangle table: `iptables -t mangle -A WIFI_STEALTH -j TTL --ttl-set 65`

2. **IPv6 Complete Block** (Layer 2)
   - Disables IPv6 on WiFi interface via sysctl
   - Drops all IPv6 packets via ip6tables
   - Prevents IPv6 leaks that could reveal desktop traffic

3. **DNS Leak Prevention** (Layer 3)
   - Redirects all DNS queries to phone's gateway
   - Blocks Google DNS (8.8.8.8, 8.8.4.4)
   - Uses iptables NAT table for DNS redirection

4. **OS Update Blocking** (Layer 4)
   - Blocks Windows Update, Mac App Store, Ubuntu/Debian update servers
   - Prevents OS-specific fingerprinting
   - Uses iptables OUTPUT chain with domain blocking

5. **MSS/MTU Clamping** (Layer 5)
   - Matches phone's packet characteristics
   - Reduces fingerprinting via packet size analysis

6. **Traffic Shaping** (Layer 6 - Optional)
   - Currently disabled for full speed
   - Can limit bandwidth to appear more phone-like

### Python GUI Architecture

**Core Modules:**

- **theme.py** - Cyberpunk color scheme (pure black #000000, green #00FF00, red #FF0000), GTK CSS generation, formatting utilities
- **logger.py** - Rotating file logger with GUI buffer (1000 entries), stores in ~/.config/pdanet-linux/
- **config_manager.py** - Settings persistence, connection profiles, auto-start management via .desktop file
- **stats_collector.py** - Bandwidth tracking from /sys/class/net/, rolling windows for rate calculation, ping testing
- **connection_manager.py** - State machine (ConnectionState enum), auto-reconnect with exponential backoff, health monitoring in background threads

**GUI Design Philosophy:**
- **NO emoji** - Professional only
- Pure black background (#000000)
- Green/red/yellow accents
- Monospaced fonts (JetBrains Mono, Fira Code)
- 4-panel dashboard layout
- Real-time updates every 1 second
- System tray integration via AppIndicator3

### Data Flow

```
Android Device (PdaNet+ app)
         ↓
[USB Tethering] OR [WiFi Hotspot]
         ↓
Proxy: 192.168.49.1:8000 (USB) OR WiFi Gateway (WiFi)
         ↓
[WiFi Mode: 6-layer bypass via iptables/sysctl]
         ↓
redsocks (transparent proxy, port 12345)
         ↓
iptables NAT/mangle rules
         ↓
All Linux Applications
```

## Important Technical Details

### Transparent Proxy Mechanism

The application uses **redsocks** to redirect all TCP traffic to PdaNet's HTTP CONNECT proxy (192.168.49.1:8000). Configuration is in `/etc/redsocks.conf`:

```
redsocks {
    type = http-connect;
    ip = 192.168.49.1;
    port = 8000;
}
```

iptables creates a REDSOCKS chain in the NAT table that redirects TCP traffic to redsocks' local port 12345, excluding local networks.

### State Machine (ConnectionManager)

The connection manager uses a state machine with these states:
- DISCONNECTED
- CONNECTING
- CONNECTED
- DISCONNECTING
- ERROR

Auto-reconnect uses exponential backoff and monitors connection health in a background thread.

### GTK CSS Limitations

GTK 3 CSS does NOT support:
- `text-transform`
- `letter-spacing`

These properties will cause runtime errors. Always test CSS changes.

### Sudoers Configuration

The installer creates `/etc/sudoers.d/pdanet-linux` to allow password-less sudo for connection scripts. User is detected via `${SUDO_USER:-$USER}` with fallback to "wtyler".

### Single Instance Enforcement

The GUI uses `fcntl.flock()` on `~/.config/pdanet-linux/gui.lock` to prevent multiple instances.

### Claude Code Hooks

The project includes automated quality assurance hooks in `.claude/settings.json`:

**PostToolUse Hooks:**
- **black** - Auto-formats Python files after editing
- **isort** - Auto-sorts imports after editing
- **flake8** - Lints Python code (blocks on errors)
- **mypy** - Type checks Python code (blocks on errors)
- **pytest** - Auto-runs tests for modified modules

**PreToolUse Hooks:**
- **print() detection** - Warns if `print()` used instead of logging
- **Dependency audit** - Checks requirements.txt for vulnerabilities (safety/pip-audit)

**Stop Hooks:**
- **Final lint** - Runs flake8/pylint on all changed Python files
- **Final type check** - Runs mypy on all changed Python files

**Note:** Development tools (black, isort, flake8, mypy, pytest) must be installed for hooks to work. Install with: `pip install --break-system-packages -r requirements.txt`

## Design Constraints

### User Preferences (CRITICAL)

1. **Name:** MUST be called "PdaNet Linux" or "pdanet-linux" - NO suffixes like "Tactical"
2. **Theme:** Cyberpunk aesthetic - pure black, green/red/yellow, monospaced fonts, NO gradients, NO emoji
3. **WiFi Bypass:** This is the PRIMARY feature - carrier detection avoidance is why the user needs PdaNet
4. **Professional Tone:** No childish elements, data-dense interface, terminal-style

### File Locations

- Project root: `/home/wtyler/pdanet-linux/`
- Installed commands: `/usr/local/bin/pdanet-*`
- Config directory: `~/.config/pdanet-linux/`
- Desktop file: `/usr/share/applications/pdanet-linux-v2.desktop`
- Redsocks config: `/etc/redsocks.conf`
- Sudoers: `/etc/sudoers.d/pdanet-linux`

## Testing Connection

**Test USB proxy availability:**
```bash
curl -x 192.168.49.1:8000 http://www.google.com
```

**Check redsocks status:**
```bash
sudo systemctl status redsocks
```

**Verify iptables rules:**
```bash
sudo iptables -t nat -L REDSOCKS -v -n
sudo iptables -t mangle -L WIFI_STEALTH -v -n
```

**Test WiFi bypass layers:**
```bash
# TTL should be 65
ping -c 1 google.com

# IPv6 should FAIL
curl -6 https://ipv6.google.com

# DNS should go through gateway
nslookup google.com
```

## Known Issues and Fixes

**Issue:** GTK CSS errors with text-transform/letter-spacing
**Fix:** These properties are not supported in GTK 3, remove them from theme.py

**Issue:** Empty REAL_USER in install.sh
**Fix:** Use `REAL_USER="${SUDO_USER:-$USER}"` with fallback to "wtyler"

**Issue:** Carrier still detects tethering
**Solution:** Use VPN over tethered connection for maximum stealth

## Python Development Notes

**Dependencies:** Project uses PyGObject (GTK3) for GUI. All dependencies are listed in `requirements.txt`.

**Module Structure:**
- `src/pdanet_gui_v2.py` - Main GUI application entry point
- `src/theme.py` - Cyberpunk theme and CSS generation
- `src/logger.py` - Rotating file logger with GUI buffer
- `src/config_manager.py` - Settings persistence and profiles
- `src/stats_collector.py` - Bandwidth tracking and ping testing
- `src/connection_manager.py` - Connection state machine

**Import Pattern:** All imports use absolute imports from `src/` directory. The main script adds `src/` to sys.path.

**Logging:** Use the logger module, NOT print() statements. The logger automatically rotates files and maintains a GUI buffer.

**State Management:** Connection state uses enum `ConnectionState` with proper state transitions. Never bypass the state machine.

## Reference Documentation

Comprehensive technical documentation is available in the `/ref` directory:

### Core Architecture
- **[architecture.md](ref/architecture.md)** - System architecture, data flow diagrams, state machines, and all components
  - Dual-mode connection system (USB + WiFi)
  - Transparent proxy layer architecture
  - Configuration files and installed binaries
  - Performance characteristics and critical paths

### Carrier Bypass
- **[carrier-bypass.md](ref/carrier-bypass.md)** - Deep dive into carrier detection and bypass mechanisms
  - 2024-2025 carrier detection methods (TTL, IPv6, DPI, ML)
  - 6-layer defense system with effectiveness analysis
  - Stealth level configurations and recommendations
  - Testing procedures and bypass effectiveness by carrier

### Network Configuration
- **[iptables-redsocks.md](ref/iptables-redsocks.md)** - Complete iptables and redsocks configuration
  - NAT table transparent redirection
  - Mangle table TTL modification
  - redsocks HTTP CONNECT proxy setup
  - Troubleshooting and performance optimization

### Python GUI
- **[python-gui.md](ref/python-gui.md)** - GTK3 GUI implementation details
  - All 6 Python modules (theme, logger, config, stats, connection, main)
  - Observer pattern and callback system
  - Threading model and thread safety
  - Cyberpunk theme design constraints

### Connection Scripts
- **[connection-scripts.md](ref/connection-scripts.md)** - USB and WiFi connection scripts
  - pdanet-connect/disconnect (USB mode)
  - pdanet-wifi-connect/disconnect (WiFi with bypass)
  - wifi-stealth.sh (6-layer carrier bypass)
  - Error handling and troubleshooting

**When to use:**
- New contributors: Start with [architecture.md](ref/architecture.md)
- Working on carrier bypass: See [carrier-bypass.md](ref/carrier-bypass.md)
- Debugging iptables issues: Refer to [iptables-redsocks.md](ref/iptables-redsocks.md)
- GUI development: Check [python-gui.md](ref/python-gui.md)
- Script modifications: Consult [connection-scripts.md](ref/connection-scripts.md)

## AI Assistant Optimization

This section provides optimized instructions for AI code assistants working on PdaNet Linux.

### Critical Project Constraints (MUST FOLLOW)

#### 1. Naming Convention
- **MUST** be called "PdaNet Linux" or "pdanet-linux"
- **NEVER** add suffixes like "Tactical", "Pro", "Ultimate", etc.
- This is a hard requirement from the project owner

#### 2. Design Constraints (NON-NEGOTIABLE)
- **Theme:** Cyberpunk only - pure black (#000000), green/red accents, monospaced fonts
- **NO EMOJI:** Professional interface only - this is strictly enforced
- **NO print():** Use logger system exclusively (enforced by hooks)
- **GTK3 CSS:** NEVER use `text-transform` or `letter-spacing` (causes runtime errors)

#### 3. Feature Priority
- **WiFi Carrier Bypass:** This is THE primary feature (6-layer stealth)
- Connection reliability and stealth effectiveness over UI polish
- TTL normalization to 65 is CRITICAL for carrier bypass

### Essential Files to Understand First

Before making any changes, AI assistants should review these files in order:

1. **src/connection_manager.py:14-40** - State machine core, ConnectionState enum
2. **scripts/wifi-stealth.sh** - 6-layer carrier bypass implementation (TTL, IPv6, DNS, etc.)
3. **src/theme.py:1-46** - Color system and GTK3 CSS constraints documentation
4. **src/pdanet_gui_v2.py** - Main GUI with observer pattern

### Code Patterns to Follow

#### Python Modules
```python
# Import structure (ALWAYS follow this order)
import standard_libs
import gi  # GTK imports
from src import local_modules  # Absolute imports from src/

# Logging (NEVER use print())
from logger import get_logger
logger = get_logger()
logger.info("message")  # NOT print()

# State management (use enum)
from connection_manager import ConnectionState
state = ConnectionState.CONNECTED  # NOT string literals

# GUI updates from background threads
from gi.repository import GLib
GLib.idle_add(self.update_ui, data)  # Thread-safe
```

#### Shell Scripts
```bash
# ALWAYS check root permissions
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: Must run as root${NC}"
   exit 1
fi

# Use color codes consistently
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 30-minute timeout for ALL commands
timeout: 1800000
```

### Testing Requirements

#### Quality Assurance (Enforced by Hooks)
- **black** - Code formatting (auto-applied on save)
- **isort** - Import sorting (auto-applied on save)
- **flake8** - Linting (blocks on errors)
- **mypy** - Type checking (blocks on errors)
- **pytest** - Auto-runs tests for modified modules

#### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific module tests
pytest tests/test_connection_manager.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Common Pitfalls to Avoid

#### ⚠️ Critical Mistakes

1. **Theme Violations**
   - ❌ NEVER use emoji in any interface elements
   - ❌ NEVER use gradients or fancy styling
   - ❌ NEVER use GTK CSS: `text-transform`, `letter-spacing`
   - ✅ Use Python `.upper()` for uppercase, not CSS

2. **Logging Issues**
   - ❌ NEVER use `print()` statements (hooks will block this)
   - ✅ Always use `logger.info()`, `logger.error()`, etc.

3. **State Management**
   - ❌ NEVER bypass the ConnectionState enum
   - ❌ NEVER use string literals for state
   - ✅ Always use proper state transitions via `_transition_to()`

4. **Network Configuration**
   - ❌ NEVER hardcode interface names (detect dynamically)
   - ❌ NEVER modify iptables without validation
   - ✅ Always test carrier bypass effectiveness after changes

5. **Threading Issues**
   - ❌ NEVER block the GUI thread with long operations
   - ❌ NEVER update GUI directly from background threads
   - ✅ Always use `GLib.idle_add()` for thread-safe GUI updates

### Module Interaction Map

```
GUI (pdanet_gui_v2.py)
    ↓ (observer callbacks)
ConnectionManager (connection_manager.py)
    ↓ (subprocess calls)
Connection Scripts (pdanet-wifi-connect, wifi-stealth.sh)
    ↓ (iptables/sysctl)
Network Stack (redsocks, iptables chains)
    ↓
Android Device Proxy (192.168.49.1:8000)
```

### Quick Context Check

Before making changes, verify:

1. **Current Connection State:**
   ```python
   from connection_manager import get_connection_manager
   state = get_connection_manager().get_state()
   ```

2. **Active Stealth Level:**
   ```bash
   sudo ./scripts/wifi-stealth.sh status
   ```

3. **Hook System Status:**
   - Verify `.claude/settings.json` hook configuration
   - Ensure quality tools installed: `pip show black isort flake8 mypy pytest`

### Performance Considerations

- **GUI Updates:** Max 1-second intervals for real-time feel
- **Background Monitoring:** 5-second health checks (connection_manager.py)
- **Auto-reconnect:** Exponential backoff (5s, 10s, 20s)
- **Carrier Bypass:** Aggressive settings (TTL=65, IPv6 blocked)

### Security Requirements

- All network traffic through proxy when connected
- No DNS leaks (forced through gateway)
- TTL normalization to 65 (CRITICAL for stealth)
- IPv6 completely disabled on WiFi interface
- No OS update traffic (fingerprinting prevention)

### Development Workflow

1. **Read relevant source files** (use Read tool, not bash cat)
2. **Check existing tests** in `tests/` directory
3. **Make changes** following patterns above
4. **Hooks auto-run** (black, isort, flake8, mypy, pytest)
5. **Verify manually** if hooks pass but behavior unclear

### File Location Reference

```
/home/wtyler/pdanet-linux/
├── src/                      # Python source modules
│   ├── pdanet_gui_v2.py     # Main GUI (646 lines)
│   ├── connection_manager.py # State machine (348 lines)
│   ├── theme.py             # Cyberpunk theme (320 lines)
│   ├── stats_collector.py   # Bandwidth tracking (245 lines)
│   ├── config_manager.py    # Settings (227 lines)
│   └── logger.py            # Logging system (134 lines)
├── scripts/                  # Shell scripts
│   ├── wifi-stealth.sh      # 6-layer bypass (235 lines)
│   └── stealth-mode.sh      # USB stealth (133 lines)
├── tests/                    # Unit tests
│   ├── test_connection_manager.py
│   ├── test_stats_collector.py
│   ├── test_config_manager.py
│   └── test_theme.py
└── ref/                      # Reference documentation
    ├── architecture.md
    ├── carrier-bypass.md
    ├── iptables-redsocks.md
    ├── python-gui.md
    └── connection-scripts.md
```

### Debugging Tips

1. **Connection Issues:**
   - Check `~/.config/pdanet-linux/pdanet.log`
   - Verify proxy: `curl -x 192.168.49.1:8000 http://google.com`
   - Check iptables: `sudo iptables -t nat -L REDSOCKS -v -n`

2. **GUI Issues:**
   - Check GTK CSS errors in console output
   - Verify threading with `GLib.idle_add()` usage
   - Test single instance lock: `ls -la /tmp/pdanet-linux-gui.lock`

3. **Carrier Bypass Issues:**
   - Verify TTL: `ping -c 1 google.com` (should show TTL 65)
   - Check IPv6 disabled: `curl -6 https://ipv6.google.com` (should fail)
   - Verify DNS: `nslookup google.com` (should use gateway)
