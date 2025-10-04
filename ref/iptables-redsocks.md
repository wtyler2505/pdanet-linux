# iptables and redsocks Configuration

**Last Updated:** 2025-10-03
**Components:** iptables NAT/mangle tables, redsocks transparent proxy

## Overview

PdaNet Linux uses **redsocks** (transparent TCP-to-proxy redirector) combined with **iptables** to route all system traffic through PdaNet's HTTP CONNECT proxy at `192.168.49.1:8000`. This provides system-wide connectivity without per-application configuration.

## Architecture

```
┌─────────────────────────────────────────┐
│         Linux Application                │
│    (browser, terminal, etc.)            │
└──────────────┬──────────────────────────┘
               │ TCP Connect
               ▼
┌─────────────────────────────────────────┐
│      iptables NAT Table                  │
│    REDSOCKS Chain (custom)              │
│  - Exclude local networks               │
│  - Exclude PdaNet proxy itself          │
│  - REDIRECT → localhost:12345           │
└──────────────┬──────────────────────────┘
               │ Redirected TCP
               ▼
┌─────────────────────────────────────────┐
│        redsocks Daemon                   │
│    Listening on 127.0.0.1:12345         │
│  - Accepts redirected TCP               │
│  - Wraps in HTTP CONNECT                │
└──────────────┬──────────────────────────┘
               │ HTTP CONNECT
               ▼
┌─────────────────────────────────────────┐
│      PdaNet Proxy Server                 │
│     192.168.49.1:8000                   │
│  (Android device via USB/WiFi)          │
└──────────────┬──────────────────────────┘
               │
               ▼
           Internet
```

## redsocks Configuration

**Location:** `/etc/redsocks.conf`

### Base Configuration

```conf
base {
    // Logging
    log_debug = off;
    log_info = on;
    log = "syslog:daemon";

    // Security
    daemon = on;
    user = redsocks;
    group = redsocks;

    // Platform
    redirector = iptables;  # Linux-specific
}
```

**Key Settings:**
- `daemon = on`: Run as background service
- `user/group = redsocks`: Drop privileges for security
- `redirector = iptables`: Use iptables for transparent redirection (Linux-specific)
- `log = "syslog:daemon"`: Send logs to system journal

### HTTP Proxy Configuration

```conf
redsocks {
    // Local bind address (where iptables redirects traffic)
    local_ip = 127.0.0.1;
    local_port = 12345;

    // PdaNet proxy server (Android device)
    ip = 192.168.49.1;
    port = 8000;

    // Proxy type
    type = http-connect;  # PdaNet uses HTTP CONNECT method

    // Authentication (not needed for PdaNet)
    // login = "username";
    // password = "password";
}
```

**Key Settings:**
- `local_port = 12345`: Port where redsocks listens for redirected traffic
- `ip = 192.168.49.1`: PdaNet's default USB tethering IP
- `port = 8000`: PdaNet's default HTTP proxy port
- `type = http-connect`: Use HTTP CONNECT tunneling method

**HTTP CONNECT Method:**
- Opens TCP tunnel through HTTP proxy
- Supports any TCP protocol (HTTPS, SSH, etc.)
- Format: `CONNECT example.com:443 HTTP/1.1`
- Proxy forwards raw TCP after successful connection

### Optional: UDP DNS Support

```conf
# Currently NOT IMPLEMENTED
# Future enhancement for DNS-over-proxy
redudp {
    local_ip = 127.0.0.1;
    local_port = 10053;

    ip = 192.168.49.1;
    port = 8000;

    dest_ip = 8.8.8.8;   # Upstream DNS
    dest_port = 53;

    udp_timeout = 30;
    udp_timeout_stream = 180;
}
```

## iptables Configuration

**Location:** `config/iptables-rules.sh`

### NAT Table Rules (Transparent Redirection)

#### Custom Chain Creation

```bash
# Create REDSOCKS chain in NAT table
iptables -t nat -N REDSOCKS

# Flush any existing rules
iptables -t nat -F REDSOCKS
```

**Purpose:** Isolate PdaNet rules from other NAT configurations

#### Local Network Exclusion

```bash
# Don't redirect local traffic
iptables -t nat -A REDSOCKS -d 0.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 10.0.0.0/8 -j RETURN
iptables -t nat -A REDSOCKS -d 127.0.0.0/8 -j RETURN       # Localhost
iptables -t nat -A REDSOCKS -d 169.254.0.0/16 -j RETURN    # Link-local
iptables -t nat -A REDSOCKS -d 172.16.0.0/12 -j RETURN     # Private
iptables -t nat -A REDSOCKS -d 192.168.0.0/16 -j RETURN    # Private
iptables -t nat -A REDSOCKS -d 224.0.0.0/4 -j RETURN       # Multicast
iptables -t nat -A REDSOCKS -d 240.0.0.0/4 -j RETURN       # Reserved

# Don't redirect traffic to PdaNet proxy itself (avoid loop)
iptables -t nat -A REDSOCKS -d 192.168.49.1 -j RETURN
```

**Why RETURN?**
- `RETURN` exits the REDSOCKS chain without matching
- Traffic continues through standard routing
- Prevents loops and preserves local connectivity

**Critical:** Must exclude `192.168.49.1` (PdaNet proxy) to avoid infinite redirect loop

#### TCP Redirection

```bash
# Redirect all other TCP traffic to redsocks
iptables -t nat -A REDSOCKS -p tcp -j REDIRECT --to-ports 12345
```

**How it works:**
- Changes destination port to 12345 (redsocks listening port)
- Keeps destination IP unchanged (redsocks extracts original via SO_ORIGINAL_DST)
- Only affects TCP (UDP not supported by redsocks http-connect)

#### Chain Activation

```bash
# Apply REDSOCKS chain to OUTPUT (local traffic)
iptables -t nat -A OUTPUT -p tcp -j REDSOCKS
```

**OUTPUT Chain:**
- Processes packets generated locally (this machine)
- All applications automatically use PdaNet connection
- System-wide transparency (no app configuration needed)

#### Optional: Connection Sharing

```bash
# Apply to PREROUTING (forwarded traffic)
# Uncomment to share connection with other devices
# iptables -t nat -A PREROUTING -p tcp -j REDSOCKS
```

**PREROUTING Chain:**
- Processes packets from other devices (routing)
- Enables connection sharing (turn Linux into WiFi hotspot)
- Requires IP forwarding: `sysctl -w net.ipv4.ip_forward=1`

### Mangle Table Rules (WiFi Stealth)

**Location:** `scripts/wifi-stealth.sh`

#### Custom Chain for Stealth

```bash
# Create WIFI_STEALTH chain in mangle table
iptables -t mangle -N WIFI_STEALTH

# Apply to POSTROUTING (outgoing packets)
iptables -t mangle -A POSTROUTING -o wlan0 -j WIFI_STEALTH
```

**Why POSTROUTING?**
- Last chance to modify packets before transmission
- After routing decision made
- Perfect for TTL normalization

#### TTL Normalization (Layer 1)

```bash
# Set TTL to 65 for all outgoing packets
iptables -t mangle -A WIFI_STEALTH -j TTL --ttl-set 65

# IPv6 equivalent (Hop Limit)
ip6tables -t mangle -A WIFI_STEALTH -j HL --hl-set 65
```

**Why TTL 65?**
- Android default is 64
- After one hop (to carrier), packets arrive with TTL=64
- Matches native phone traffic exactly
- Prevents TTL-based tethering detection

#### MSS Clamping (Layer 5)

```bash
# Clamp MSS to PMTU for proper fragmentation
iptables -t mangle -A FORWARD -o wlan0 -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu
```

**Purpose:**
- Adjust Maximum Segment Size to avoid fragmentation
- Reduces carrier fingerprinting via packet sizes
- Applied to FORWARD chain (routed traffic)

### Filter Table Rules (WiFi Stealth)

#### OS Update Blocking (Layer 4)

```bash
# Block Windows Update
iptables -A OUTPUT -m string --string "windowsupdate" --algo bm -j DROP
iptables -A OUTPUT -m string --string "update.microsoft" --algo bm -j DROP

# Block Mac updates
iptables -A OUTPUT -m string --string "swcdn.apple.com" --algo bm -j DROP
iptables -A OUTPUT -m string --string "mesu.apple.com" --algo bm -j DROP

# Block Ubuntu/Debian updates
iptables -A OUTPUT -m string --string "archive.ubuntu.com" --algo bm -j DROP
iptables -A OUTPUT -m string --string "security.ubuntu.com" --algo bm -j DROP
```

**String Matching:**
- `--algo bm`: Boyer-Moore algorithm (fast)
- Inspects packet payload for domain names
- Drops packets containing update server URLs
- Prevents desktop OS fingerprinting

#### Google DNS Blocking (Layer 3)

```bash
# Block direct Google DNS queries (common tethering indicator)
iptables -A OUTPUT -d 8.8.8.8 -j DROP
iptables -A OUTPUT -d 8.8.4.4 -j DROP
```

**Why block Google DNS?**
- Many desktops hardcode Google DNS (8.8.8.8)
- Carriers detect non-carrier DNS as tethering indicator
- Forces all DNS through phone's gateway

#### DNS Redirection (Layer 3)

```bash
# Force all DNS through phone's gateway
GATEWAY=$(ip route | grep "default.*wlan0" | awk '{print $3}')
iptables -t nat -A OUTPUT -o wlan0 -p udp --dport 53 -j DNAT --to $GATEWAY:53
iptables -t nat -A OUTPUT -o wlan0 -p tcp --dport 53 -j DNAT --to $GATEWAY:53
```

**DNAT (Destination NAT):**
- Changes DNS destination to phone's gateway
- Works for both UDP (port 53) and TCP (rare)
- Prevents DNS leaks that reveal desktop usage

### IPv6 Configuration (WiFi Stealth)

#### Complete IPv6 Blockade (Layer 2)

```bash
# Disable IPv6 on interface
sysctl -w net.ipv6.conf.wlan0.disable_ipv6=1

# Drop all IPv6 packets
ip6tables -P INPUT DROP
ip6tables -P FORWARD DROP
ip6tables -P OUTPUT DROP
```

**Why block IPv6?**
- IPv6 eliminates NAT (each device gets unique address)
- Carriers easily spot multiple devices via multiple IPv6 addresses
- Simpler to block entirely than to hide properly

**Trade-off:** No IPv6 connectivity while stealth is active

## Rule Management

### Viewing Active Rules

```bash
# NAT table (transparent proxy)
sudo iptables -t nat -L REDSOCKS -n -v

# Mangle table (TTL modification)
sudo iptables -t mangle -L WIFI_STEALTH -n -v

# Filter table (OS update blocking)
sudo iptables -L OUTPUT -n -v | grep DROP

# Check if rules are active
sudo iptables -t nat -L OUTPUT -n | grep REDSOCKS
```

### Rule Persistence

**Problem:** iptables rules are lost on reboot

**Solutions:**

1. **iptables-persistent** (Debian/Ubuntu):
```bash
sudo apt-get install iptables-persistent
sudo netfilter-persistent save
```

2. **Manual save/restore**:
```bash
# Save
sudo iptables-save > /etc/iptables/rules.v4
sudo ip6tables-save > /etc/iptables/rules.v6

# Restore on boot (add to /etc/rc.local)
iptables-restore < /etc/iptables/rules.v4
ip6tables-restore < /etc/iptables/rules.v6
```

3. **systemd service** (PdaNet approach):
```bash
# Rules are applied by pdanet-connect script
# Managed by connection lifecycle
```

### Cleanup

```bash
# Remove PdaNet NAT rules
sudo iptables -t nat -D OUTPUT -p tcp -j REDSOCKS
sudo iptables -t nat -F REDSOCKS
sudo iptables -t nat -X REDSOCKS

# Remove WiFi stealth rules
sudo iptables -t mangle -D POSTROUTING -o wlan0 -j WIFI_STEALTH
sudo iptables -t mangle -F WIFI_STEALTH
sudo iptables -t mangle -X WIFI_STEALTH

# Remove filter rules (string matching)
sudo iptables -D OUTPUT -m string --string "windowsupdate" --algo bm -j DROP
# ... (repeat for all string match rules)

# Re-enable IPv6
sudo sysctl -w net.ipv6.conf.wlan0.disable_ipv6=0
sudo ip6tables -P INPUT ACCEPT
sudo ip6tables -P FORWARD ACCEPT
sudo ip6tables -P OUTPUT ACCEPT
```

## Troubleshooting

### Connection Issues

**Problem: No internet after connecting**

Check redsocks status:
```bash
sudo systemctl status redsocks
sudo journalctl -u redsocks -f
```

Check iptables rules:
```bash
sudo iptables -t nat -L OUTPUT -n | grep REDSOCKS
sudo iptables -t nat -L REDSOCKS -n -v
```

Verify proxy reachability:
```bash
curl -x 192.168.49.1:8000 http://www.google.com
```

**Problem: Local services not accessible**

Verify local networks are excluded:
```bash
sudo iptables -t nat -L REDSOCKS -n | grep 127.0.0.0
sudo iptables -t nat -L REDSOCKS -n | grep 192.168.0.0
```

**Problem: Infinite redirect loop**

Ensure PdaNet proxy is excluded:
```bash
sudo iptables -t nat -L REDSOCKS -n | grep 192.168.49.1
```

### Performance Issues

**Problem: High latency**

Check redsocks CPU usage:
```bash
top -p $(pgrep redsocks)
```

Count active redirections:
```bash
sudo iptables -t nat -L REDSOCKS -n -v
# Check packet counters
```

**Problem: Packet drops**

Check kernel conntrack table:
```bash
cat /proc/sys/net/netfilter/nf_conntrack_count
cat /proc/sys/net/netfilter/nf_conntrack_max
```

Increase if needed:
```bash
sudo sysctl -w net.netfilter.nf_conntrack_max=262144
```

### Stealth Issues

**Problem: Carrier still detecting tethering**

Verify TTL is set correctly:
```bash
sudo iptables -t mangle -L WIFI_STEALTH -n -v
# Look for TTL target
```

Test outgoing TTL:
```bash
ping -c 1 google.com
# Check TTL in response (should be 64 after decrement from 65)
```

Verify IPv6 is blocked:
```bash
curl -6 https://ipv6.google.com
# Should FAIL or timeout
```

Check DNS redirection:
```bash
nslookup google.com
# DNS server should be phone's gateway
```

## Performance Characteristics

### Latency Impact

- **No iptables:** 0ms overhead
- **NAT redirection:** ~1-2ms overhead
- **redsocks processing:** ~5-10ms overhead
- **HTTP CONNECT handshake:** ~10-20ms overhead
- **Total added latency:** ~15-30ms

### Throughput Impact

- **Theoretical maximum:** Limited by USB 2.0 (~480 Mbps) or WiFi standard
- **redsocks overhead:** <5% (CPU-bound)
- **iptables overhead:** <2% (packet processing)
- **Practical throughput:** 20-100 Mbps (depends on carrier and device)

### Resource Usage

- **Memory:** redsocks ~5-10MB
- **CPU:** <1% idle, ~5% under load
- **Connection tracking:** ~100-500 entries typical

## Security Considerations

### Privilege Separation

- **redsocks** runs as `redsocks:redsocks` (not root)
- iptables rules managed via sudo scripts
- Config file readable by all, writable by root only

### Attack Surface

**Local:**
- redsocks listens on 127.0.0.1 only (not exposed to network)
- No authentication required (local access only)
- Proxy credentials not stored (PdaNet doesn't require auth)

**Remote:**
- PdaNet proxy on private network (192.168.49.0/24)
- Not accessible from internet
- No inbound connections accepted

### Logging

**redsocks logs:**
```bash
# View recent logs
sudo journalctl -u redsocks -n 50

# Monitor live
sudo journalctl -u redsocks -f
```

**iptables logging (optional):**
```bash
# Log dropped packets
sudo iptables -A OUTPUT -j LOG --log-prefix "PDANET_DROP: "

# View logs
sudo tail -f /var/log/syslog | grep PDANET
```

## Advanced Configuration

### Custom Proxy Port

If PdaNet uses different port, edit `/etc/redsocks.conf`:
```conf
redsocks {
    ip = 192.168.49.1;
    port = 8080;  # Change from default 8000
    # ... rest of config
}
```

Then restart:
```bash
sudo systemctl restart redsocks
```

### Per-Application Routing

To exclude specific applications from redirection:
```bash
# Example: Exclude VPN client
sudo iptables -t nat -I REDSOCKS -m owner --uid-owner openvpn -j RETURN
```

### Connection Sharing Setup

To share PdaNet connection with other devices:

1. Enable IP forwarding:
```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

2. Activate PREROUTING redirection:
```bash
sudo iptables -t nat -A PREROUTING -p tcp -j REDSOCKS
```

3. Setup NAT for internet sharing:
```bash
sudo iptables -t nat -A POSTROUTING -o usb0 -j MASQUERADE
```

## References

- [System Architecture](architecture.md)
- [Carrier Bypass Mechanisms](carrier-bypass.md)
- [Connection Scripts](connection-scripts.md)
- [redsocks GitHub](https://github.com/darkk/redsocks)
- [iptables Manual](https://www.netfilter.org/documentation/)
