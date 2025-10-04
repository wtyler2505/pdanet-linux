# PdaNet Linux - System Architecture

**Last Updated:** 2025-10-03
**Target Platform:** Linux Mint 22.2 Cinnamon (Debian/Ubuntu-based)

## Overview

PdaNet Linux is a reverse-engineered Linux client for PdaNet+ that provides system-wide internet connectivity through Android devices. The architecture implements dual-mode connectivity (USB and WiFi) with sophisticated carrier detection bypass mechanisms.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Android Device (PdaNet+)                  │
│                   HTTP Proxy: 192.168.49.1:8000              │
└──────────────┬─────────────────────────┬────────────────────┘
               │                         │
        USB Tethering              WiFi Hotspot
        (usb0/rndis0)              (wlan0)
               │                         │
               ├─────────────┬───────────┤
               │             │           │
        ┌──────▼─────────────▼───────────▼──────┐
        │      Interface Detection System        │
        │   (connection_manager.py / scripts)    │
        └──────────────┬────────────────────────┘
                       │
        ┌──────────────▼────────────────────────┐
        │     Carrier Bypass Layer (WiFi)        │
        │   6-Layer Stealth (wifi-stealth.sh)   │
        │   - TTL Normalization (65)             │
        │   - IPv6 Complete Block                │
        │   - DNS Leak Prevention                │
        │   - OS Update Blocking                 │
        │   - MSS/MTU Clamping                   │
        │   - Traffic Shaping (optional)         │
        └──────────────┬────────────────────────┘
                       │
        ┌──────────────▼────────────────────────┐
        │    Transparent Proxy Layer             │
        │   - redsocks (port 12345)              │
        │   - iptables NAT chains (REDSOCKS)     │
        │   - Excludes local networks            │
        └──────────────┬────────────────────────┘
                       │
        ┌──────────────▼────────────────────────┐
        │      All Linux Applications            │
        │   (system-wide connectivity)           │
        └───────────────────────────────────────┘
```

## Core Components

### 1. Connection Management Layer

**Location:** `src/connection_manager.py`

**Responsibilities:**
- State machine management (5 states: DISCONNECTED, CONNECTING, CONNECTED, DISCONNECTING, ERROR)
- Interface detection (USB: usb0/rndis0, WiFi: wlan0)
- Proxy validation (HTTP CONNECT to 192.168.49.1:8000)
- Auto-reconnect with exponential backoff
- Health monitoring via background threads
- Callback system for state changes and errors

**State Transitions:**
```
DISCONNECTED ──connect()──> CONNECTING
                              │
                    proxy_validate()
                              │
                    ┌─────────▼─────────┐
                    │                   │
                 SUCCESS             FAILURE
                    │                   │
                    ▼                   ▼
                CONNECTED            ERROR
                    │                   │
                disconnect()      auto_reconnect()
                    │                   │
                    ▼                   │
              DISCONNECTING             │
                    │                   │
                    └───────────────────┘
```

### 2. Transparent Proxy Layer

**Components:**
- **redsocks** (`/etc/redsocks.conf`): Transparent TCP-to-HTTP-CONNECT proxy redirector
- **iptables** (`config/iptables-rules.sh`): NAT table rules for traffic redirection

**Traffic Flow:**
```
Application → TCP Connect → iptables NAT → redsocks:12345 → HTTP CONNECT → 192.168.49.1:8000 → Internet
```

**Key iptables Rules:**
- Creates custom `REDSOCKS` chain in NAT table
- Excludes local networks (127.0.0.0/8, 192.168.0.0/16, etc.)
- Redirects all other TCP to `localhost:12345`
- Applied to OUTPUT chain (local traffic)
- Optional PREROUTING (sharing with other devices)

### 3. Carrier Bypass Layer (WiFi Mode)

**Location:** `scripts/wifi-stealth.sh`

**6-Layer Defense System:**

#### Layer 1: TTL Normalization (CRITICAL)
- **Problem:** Carriers detect TTL decrement (64→63) revealing tethering
- **Solution:** Set all outgoing packets to TTL 65 via iptables mangle table
- **Implementation:**
  ```bash
  iptables -t mangle -A WIFI_STEALTH -j TTL --ttl-set 65
  ip6tables -t mangle -A WIFI_STEALTH -j HL --hl-set 65
  ```

#### Layer 2: IPv6 Complete Block
- **Problem:** IPv6 leaks can reveal desktop traffic patterns
- **Solution:** Disable IPv6 on interface + drop all IPv6 packets
- **Implementation:**
  ```bash
  sysctl -w net.ipv6.conf.wlan0.disable_ipv6=1
  ip6tables -P INPUT/FORWARD/OUTPUT DROP
  ```

#### Layer 3: DNS Leak Prevention
- **Problem:** Desktop DNS queries reveal OS fingerprinting
- **Solution:** Force all DNS through phone's gateway via DNAT
- **Implementation:**
  ```bash
  iptables -t nat -A OUTPUT -o wlan0 -p udp --dport 53 -j DNAT --to $GATEWAY:53
  iptables -A OUTPUT -d 8.8.8.8 -j DROP  # Block Google DNS
  ```

#### Layer 4: OS Update Blocking
- **Problem:** OS update requests are desktop-specific
- **Solution:** Block update domains via string matching
- **Targets:** Windows Update, Mac App Store, Ubuntu/Debian repos

#### Layer 5: MSS/MTU Clamping
- **Problem:** Packet size fingerprinting
- **Solution:** Clamp MSS to PMTU
- **Implementation:**
  ```bash
  iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
  ```

#### Layer 6: Traffic Shaping (Optional)
- **Purpose:** Bandwidth limiting to mimic phone usage
- **Status:** Not implemented (prioritizing full speed)
- **Future:** tc (traffic control) rules for rate limiting

### 4. Python GUI Layer

**Location:** `src/pdanet_gui_v2.py`

**Architecture:** Model-View-Controller pattern with GTK3

**Core Modules:**
- `theme.py` - Cyberpunk CSS generation, pure black (#000000) background
- `logger.py` - Rotating file logger with 1000-entry GUI buffer
- `config_manager.py` - Settings persistence, connection profiles, .desktop integration
- `stats_collector.py` - Bandwidth tracking from `/sys/class/net/`, ping testing
- `connection_manager.py` - State machine and connection orchestration

**GUI Features:**
- 4-panel dashboard layout
- Real-time updates (1 second intervals)
- System tray integration (AppIndicator3)
- Single instance enforcement (fcntl.flock)
- Professional design (NO emoji, monospaced fonts)

## Data Flow Diagrams

### USB Tethering Mode

```
Android USB Tethering (usb0/rndis0)
         │
         ▼
192.168.49.1:8000 (PdaNet HTTP proxy)
         │
         ▼
iptables NAT → redsocks:12345
         │
         ▼
HTTP CONNECT to 192.168.49.1:8000
         │
         ▼
All Applications (system-wide)
```

### WiFi Tethering Mode (Primary Use Case)

```
Android WiFi Hotspot (wlan0)
         │
         ▼
Phone Gateway (e.g., 192.168.43.1)
         │
         ▼
6-Layer Carrier Bypass (iptables mangle/nat)
  - TTL set to 65
  - IPv6 blocked
  - DNS forced through gateway
  - OS updates blocked
  - MSS clamped
         │
         ▼
All Applications (system-wide)
```

## Configuration Files

### System Configuration

| File | Purpose | Owner | Permissions |
|------|---------|-------|-------------|
| `/etc/redsocks.conf` | Transparent proxy config | root | 644 |
| `/etc/sudoers.d/pdanet-linux` | Password-less sudo for scripts | root | 440 |
| `~/.config/pdanet-linux/settings.json` | User settings | user | 644 |
| `~/.config/pdanet-linux/gui.lock` | Single instance lock | user | 644 |
| `/usr/share/applications/pdanet-linux-v2.desktop` | Desktop integration | root | 644 |

### Installed Binaries

| Command | Location | Purpose |
|---------|----------|---------|
| `pdanet-connect` | `/usr/local/bin/` | USB connection (CLI) |
| `pdanet-disconnect` | `/usr/local/bin/` | USB disconnection (CLI) |
| `pdanet-wifi-connect` | `/usr/local/bin/` | WiFi connection with bypass |
| `pdanet-wifi-disconnect` | `/usr/local/bin/` | WiFi disconnection |
| `pdanet-gui-v2` | `/usr/local/bin/` | GUI launcher |

## Design Principles

### Security
- No credentials stored in plaintext
- PdaNet proxy requires no authentication
- Sudoers limited to specific commands
- Local networks excluded from redirection

### Reliability
- State machine prevents invalid transitions
- Auto-reconnect with exponential backoff (5s delay, 3 max attempts)
- Health monitoring in background threads
- Connection validation before marking as CONNECTED

### Performance
- Minimal overhead from redsocks
- Direct iptables rules (no proxychains)
- Background monitoring (non-blocking)
- Efficient bandwidth tracking (1-second rolling windows)

### Stealth
- Multi-layered approach (6 independent mechanisms)
- TTL normalization as primary defense
- Traffic fingerprinting reduction
- Behavioral mimicry (phone-like patterns)

## Critical Paths

### Connection Establishment (WiFi)
1. Detect WiFi interface (wlan0)
2. Connect to Android hotspot (NetworkManager)
3. Validate gateway reachability
4. Enable 6-layer stealth (`wifi-stealth.sh enable wlan0 3`)
5. Update state to CONNECTED
6. Start health monitoring thread

### Connection Teardown
1. Set state to DISCONNECTING
2. Stop health monitoring
3. Disable stealth (`wifi-stealth.sh disable wlan0`)
4. Disconnect from hotspot
5. Set state to DISCONNECTED

## Performance Characteristics

- **Latency Overhead:** ~10-20ms (redsocks processing)
- **Throughput:** Limited by USB 2.0 (~480 Mbps) or WiFi standard
- **Memory Usage:** <50MB (Python GUI + redsocks)
- **CPU Usage:** <5% (idle), <15% (active transfer)

## Future Architecture Considerations

### Potential Enhancements
1. **ML-Based Traffic Shaping:** Mimic phone usage patterns dynamically
2. **VPN Integration:** Built-in OpenVPN/WireGuard for ultimate stealth
3. **Bluetooth Tethering:** Additional connectivity mode
4. **WiFi Direct:** Peer-to-peer without hotspot
5. **Traffic Analysis Dashboard:** Real-time fingerprint detection

### Known Limitations
1. **IPv6 Support:** Currently blocked entirely (no IPv6 connectivity)
2. **UDP Support:** Limited to redsocks TCP redirection
3. **Detection Risk:** ML-based carrier detection may still identify patterns
4. **Performance:** Transparent proxy adds latency vs. native routing

## References

- [Carrier Detection Mechanisms (2024-2025)](carrier-bypass.md)
- [iptables/redsocks Configuration](iptables-redsocks.md)
- [Python GUI Architecture](python-gui.md)
- [Connection Scripts](connection-scripts.md)
