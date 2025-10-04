# iPhone Personal Hotspot with Stealth Mode

## Overview

PdaNet Linux now supports **iPhone Personal Hotspot** with aggressive carrier bypass to prevent throttling detection. Unlike Android PdaNet which requires the PdaNet app, iPhone mode works with the native Personal Hotspot feature built into iOS.

## Why iPhone Mode is Different

### No PdaNet App Needed
- iPhone's built-in Personal Hotspot provides direct internet sharing
- No proxy configuration required
- Simpler connection process
- Works with any iPhone running iOS 4.3+

### Aggressive Stealth Mode
The same 6-layer carrier bypass used for Android WiFi hotspots is automatically applied:

1. **TTL Normalization** - All packets set to TTL 65 (matches phone traffic)
2. **IPv6 Complete Block** - Prevents IPv6 leaks that reveal desktop usage
3. **DNS Leak Prevention** - Forces all DNS through phone gateway
4. **OS Update Blocking** - Blocks Windows/Mac/Linux update fingerprinting
5. **MSS/MTU Clamping** - Matches phone packet characteristics
6. **Traffic Shaping** - Optional bandwidth limiting

## How to Use

### Method 1: GUI (Recommended)

1. **Enable Personal Hotspot on iPhone:**
   - Go to Settings → Personal Hotspot
   - Toggle "Allow Others to Join" ON
   - Note the WiFi password shown

2. **Launch PdaNet Linux GUI:**
   ```bash
   pdanet-gui-v2
   ```

3. **Select iPhone Mode:**
   - In the OPERATIONS panel, select "iPhone Personal Hotspot" from the dropdown
   - Click "▶ CONNECT"

4. **Enter Credentials:**
   - Enter your iPhone's name (e.g., "John's iPhone")
   - Enter the WiFi password shown on iPhone
   - Click OK

5. **Connection Established:**
   - The app will connect to your iPhone
   - Aggressive stealth mode is automatically enabled
   - All 6 bypass layers are active

### Method 2: Command Line

1. **Enable Personal Hotspot on iPhone** (as above)

2. **Connect with Stealth Mode:**
   ```bash
   # Set credentials as environment variables
   export IPHONE_SSID="John's iPhone"
   export IPHONE_PASSWORD="your-password"
   
   # Connect
   sudo pdanet-iphone-connect
   ```

3. **Disconnect:**
   ```bash
   sudo pdanet-iphone-disconnect
   ```

### Method 3: Interactive CLI

If you don't set environment variables, the script will prompt you:

```bash
sudo pdanet-iphone-connect
# Script will ask for SSID and password interactively
```

## Connection Details

When connected via iPhone hotspot, you'll see:

```
════════════════════════════════════════
✓ iPhone Hotspot Connected!
════════════════════════════════════════

Connection Details:
  Network: John's iPhone
  Interface: wlan0
  IP Address: 172.20.10.2
  Gateway: 172.20.10.1
  Stealth Mode: ACTIVE (Level 3)

Carrier Bypass Status:
  ✓ TTL normalized to match phone traffic
  ✓ IPv6 disabled to prevent leaks
  ✓ DNS forced through phone gateway
  ✓ OS update traffic blocked
```

## Stealth Effectiveness

### What the Carrier Sees

With aggressive stealth mode enabled, your carrier sees:
- **TTL 65 packets** - Same as iPhone traffic
- **IPv4 only** - No IPv6 leaks
- **DNS through phone** - No external DNS queries
- **No OS updates** - Desktop fingerprints blocked
- **Phone-like packet sizes** - MSS/MTU clamped

### What Defeats This

Even with all 6 layers, some carriers may still detect:
- **Deep Packet Inspection (DPI)** - TLS fingerprinting
- **Machine Learning** - Traffic pattern analysis
- **Data Volume** - Excessive usage (100GB+ in a day)
- **Known Desktop Protocols** - Torrenting, Steam downloads, etc.

### Maximum Stealth Strategy

For absolute maximum stealth:

1. **Use PdaNet Linux stealth mode** ✓
2. **Add a VPN over the connection** ✓✓
   ```bash
   # Connect iPhone hotspot first
   sudo pdanet-iphone-connect
   
   # Then connect VPN
   openvpn your-config.ovpn
   ```
3. **Use mobile browser user-agents**
4. **Avoid massive downloads**
5. **Don't run OS updates while tethered**

## Comparison: iPhone vs Android

| Feature | iPhone Hotspot | Android PdaNet |
|---------|---------------|----------------|
| **Setup Complexity** | Simple (native iOS) | Moderate (app required) |
| **Stealth Mode** | 6 layers | 6 layers |
| **Connection Speed** | Full speed | Full speed |
| **Battery Impact** | Higher (WiFi radio) | Lower (USB option) |
| **Reliability** | Excellent | Excellent |
| **Range** | ~30 feet | USB: 15ft, WiFi: ~30ft |
| **Multi-device** | Yes | USB: No, WiFi: Yes |
| **Auto-reconnect** | Yes | Yes |

## Troubleshooting

### "iPhone hotspot not found in scan results"

**Solution:**
1. Verify Personal Hotspot is enabled on iPhone
2. Check if iPhone is discoverable:
   - Open Settings → Personal Hotspot
   - Keep this screen open during connection
3. Move closer to iPhone (within 15 feet)
4. Try disabling/re-enabling Personal Hotspot

### "Failed to connect to iPhone hotspot"

**Solutions:**
1. **Wrong Password:**
   - Check the password shown in Settings → Personal Hotspot
   - Password is case-sensitive

2. **iPhone Not Discoverable:**
   - Keep Personal Hotspot settings screen open
   - Or unlock iPhone before connecting

3. **WiFi Issues:**
   ```bash
   # Restart NetworkManager
   sudo systemctl restart NetworkManager
   
   # Try again
   sudo pdanet-iphone-connect
   ```

### "Connection works but internet is slow"

This is normal with stealth mode because:
- TTL modification adds slight overhead
- OS update blocking may interfere with some services
- iPhone WiFi can be slower than USB tethering

**To test without stealth:**
```bash
# Connect without stealth
sudo pdanet-iphone-disconnect
nmcli device wifi connect "Your iPhone" password "password"

# Speed test
curl -o /dev/null http://speedtest.wdc01.softlayer.com/downloads/test100.zip
```

### Stealth mode not working

**Verify stealth is active:**
```bash
sudo iptables -t mangle -L WIFI_STEALTH -n -v
```

You should see TTL rules. If not:
```bash
# Manually enable stealth
sudo /path/to/pdanet-linux/scripts/wifi-stealth.sh enable wlan0 3
```

## iPhone-Specific Tips

### Battery Saving

iPhone hotspot drains battery quickly:
- **Keep iPhone plugged in** during long sessions
- **Lower WiFi power** on iPhone (Settings → WiFi → [info] → Limit IP Address Tracking)
- **Disable other services** (Bluetooth, AirDrop, etc.)

### Data Usage Monitoring

Monitor your iPhone's cellular usage:
- Settings → Cellular → Cellular Data Usage
- Reset statistics when starting to track tethering
- Check after session to see actual usage

### Carrier Detection

Some US carriers are more aggressive:
- **Verizon**: Very aggressive DPI, VPN recommended
- **AT&T**: Moderate detection, stealth mode usually works
- **T-Mobile**: Less aggressive, stealth mode effective
- **MVNOs**: Usually no detection

### iOS Compatibility

Tested and working on:
- **iOS 18** ✓ (latest)
- **iOS 17** ✓
- **iOS 16** ✓
- **iOS 15** ✓
- **iOS 14** ✓
- **iOS 13** ✓
- **iOS 12** ✓ (with limitations)

Older iOS versions may have compatibility issues with aggressive stealth.

## Technical Details

### Connection Flow

1. **WiFi Scan**: NetworkManager scans for available networks
2. **Connect**: Connects to iPhone's WiFi using standard WPA2
3. **DHCP**: Obtains IP address from iPhone (usually 172.20.10.x)
4. **Routing**: Sets default route through iPhone gateway
5. **Stealth**: Applies iptables rules for carrier bypass
6. **Monitor**: Continuously monitors connection health

### Network Configuration

When connected to iPhone:
```
Interface: wlan0
IP Range: 172.20.10.0/28 (Apple's private range)
Gateway: 172.20.10.1 (iPhone)
DNS: 172.20.10.1 (through iPhone)
MTU: 1500 (standard)
```

### Stealth Rules Applied

```bash
# TTL normalization
iptables -t mangle -A WIFI_STEALTH -j TTL --ttl-set 65

# IPv6 blocking
ip6tables -P INPUT DROP
ip6tables -P FORWARD DROP
ip6tables -P OUTPUT DROP

# DNS redirection
iptables -t nat -A OUTPUT -p udp --dport 53 -j DNAT --to 172.20.10.1:53

# OS update blocking
iptables -A OUTPUT -m string --string "windowsupdate" --algo bm -j DROP
# ... (and more)
```

## Scripts Reference

### pdanet-iphone-connect

Full-featured connection script with:
- WiFi scanning
- Interactive credential input
- Automatic stealth mode
- Connection verification
- Detailed status output

### pdanet-iphone-disconnect

Cleanup script that:
- Disables stealth mode
- Disconnects WiFi
- Restores IPv6
- Cleans iptables rules

### wifi-stealth.sh

Shared stealth script used by both Android WiFi and iPhone modes:
- 6-layer carrier bypass
- 3 stealth levels (basic, moderate, aggressive)
- Enable/disable/status commands

## Security Notes

### Privacy

iPhone hotspot is relatively secure:
- **WPA2 encryption** protects WiFi traffic
- **NAT** hides your computer's MAC address
- **Stealth mode** makes traffic look like phone usage

However, carriers can still see:
- Total data used
- Connection duration
- Destination IP addresses (without VPN)

### Best Practices

1. **Use strong WiFi password** on iPhone
2. **Enable "Maximize Compatibility"** only if needed (less secure)
3. **Change hotspot name** to something generic (not "John's iPhone")
4. **Use VPN** for sensitive activities
5. **Monitor data usage** to avoid overage charges

## Advanced Usage

### Custom Stealth Level

The default is Level 3 (aggressive). To use different levels:

```bash
# Level 1: Basic (TTL only)
sudo IPHONE_SSID="iPhone" IPHONE_PASSWORD="pass" pdanet-iphone-connect
sudo /path/to/scripts/wifi-stealth.sh enable wlan0 1

# Level 2: Moderate (TTL + IPv6 + DNS)
sudo IPHONE_SSID="iPhone" IPHONE_PASSWORD="pass" pdanet-iphone-connect
sudo /path/to/scripts/wifi-stealth.sh enable wlan0 2
```

### Profile Management

Save iPhone connection as profile:
```python
from config_manager import get_config

config = get_config()
config.add_profile("My iPhone", {
    "mode": "iphone",
    "ssid": "John's iPhone",
    "stealth_level": 3,
    "auto_reconnect": True
})
```

### Monitoring

Watch connection in real-time:
```bash
# In one terminal: watch connection
watch -n 1 'nmcli device status; echo; iptables -t mangle -L WIFI_STEALTH -n -v'

# In another: monitor data usage
watch -n 1 'cat /sys/class/net/wlan0/statistics/rx_bytes /sys/class/net/wlan0/statistics/tx_bytes'
```

## License

iPhone hotspot support is part of PdaNet Linux and follows the same MIT license.

## Support

For iPhone-specific issues:
- Check this documentation first
- Review logs: `~/.config/pdanet-linux/pdanet.log`
- Test without stealth: `nmcli device wifi connect "iPhone"`
- Ask in GitHub issues: Tag with `iphone-hotspot`

---

**Happy Tethering! 📱💻**
