# PdaNet Linux Client

A native Linux client for PdaNet+ USB tethering, reverse-engineered from the Windows application. Provides system-wide internet connectivity through your Android device with optional carrier detection bypass.

## Features

✅ **Badass GTK GUI** - Beautiful dark-themed interface with system tray integration
✅ **System-wide tethering** - All applications use the tethered connection
✅ **Automatic detection** - Finds USB tethering interface automatically
✅ **Transparent proxy** - Uses redsocks for seamless traffic routing
✅ **Stealth mode** - Hide tethering usage from carrier detection (similar to PdaNet's "Hide Usage")
✅ **Easy setup** - Simple install and connect (GUI or CLI)
✅ **Linux Mint 22.2 optimized** - Tested on Cinnamon edition
✅ **Real-time status** - Live connection monitoring in GUI

## Requirements

### Android Device
- PdaNet+ app installed ([Download here](https://pdanet.co/))
- USB debugging enabled (optional, but recommended)
- USB tethering capable

### Linux System
- Linux Mint 22.2 (or Ubuntu-based distribution)
- Root/sudo access
- USB port

## Installation

1. **Clone or download this repository:**
   ```bash
   cd /home/wtyler/pdanet-linux
   ```

2. **Run the installer:**
   ```bash
   sudo ./install.sh
   ```

   The installer will:
   - Install dependencies (redsocks, iptables, etc.)
   - Configure system services
   - Set up convenience commands
   - Create sudo permissions

## Usage

### GUI Method (Recommended) 🎨

1. **Connect your Android device via USB**

2. **Open PdaNet+ app on Android:**
   - Enable "Activate USB Mode"
   - Optionally enable "Hide Tether Usage" on Android

3. **Launch PdaNet Linux GUI:**
   ```bash
   pdanet-gui
   ```
   Or search for "PdaNet Linux" in your application menu

4. **Click the big "🔌 CONNECT" button**

5. **To disconnect:** Click "🔌 DISCONNECT"

6. **Enable Stealth:** Toggle the Stealth Mode switch

See [GUI_GUIDE.md](GUI_GUIDE.md) for complete GUI documentation.

### CLI Method (For Scripts/Advanced Users)

1. **Connect your Android device via USB**

2. **Open PdaNet+ app on Android:**
   - Enable "Activate USB Mode"
   - Optionally enable "Hide Tether Usage" on Android

3. **On Linux, connect:**
   ```bash
   sudo pdanet-connect
   ```

4. **To disconnect:**
   ```bash
   sudo pdanet-disconnect
   ```

### Stealth Mode (Hide Tethering Usage)

To prevent carrier detection of tethering:

```bash
# Enable stealth mode
sudo pdanet-stealth enable

# Check status
sudo pdanet-stealth status

# Disable stealth mode
sudo pdanet-stealth disable
```

**What stealth mode does:**
- Normalizes TTL (Time-To-Live) values to appear as phone traffic
- Blocks OS update services (Windows Update, Mac App Store)
- Reduces carrier fingerprinting

**Note:** Stealth mode is not 100% foolproof. For maximum privacy, use a VPN over the tethered connection.

## How It Works

### Architecture

```
Android Device (PdaNet+)
         ↓
    USB Tethering
         ↓
  Proxy: 192.168.49.1:8000
         ↓
     redsocks (local)
         ↓
  iptables (transparent redirect)
         ↓
   All Linux Applications
```

### Components

1. **pdanet-connect** - Main connection script
   - Detects USB tethering interface
   - Validates PdaNet proxy availability
   - Starts redsocks service
   - Applies iptables rules

2. **pdanet-disconnect** - Cleanup script
   - Removes iptables rules
   - Stops redsocks
   - Restores normal networking

3. **redsocks** - Transparent TCP-to-proxy redirector
   - Configured to use PdaNet proxy at 192.168.49.1:8000
   - Handles transparent traffic redirection

4. **iptables-rules.sh** - Firewall configuration
   - Creates REDSOCKS chain
   - Excludes local traffic
   - Redirects all other TCP traffic to redsocks

5. **stealth-mode.sh** - Carrier detection bypass
   - TTL normalization
   - OS-specific traffic blocking

## Troubleshooting

### Connection Issues

**Problem: "No USB tethering interface found"**
- Solution: Make sure USB tethering is enabled on Android
- Check with: `ip link show`

**Problem: "Cannot connect to PdaNet proxy"**
- Solution: Verify PdaNet+ app is running on Android
- Make sure "Activate USB Mode" is checked
- Try restarting the PdaNet+ app

**Problem: "Internet works but is slow"**
- Solution: This is normal - USB tethering has overhead
- Try enabling stealth mode (ironically, it may be faster)

### Stealth Mode Issues

**Problem: "Carrier still detects tethering"**
- Solution: Modern carriers use multiple detection methods
- Try using a VPN over the tethered connection
- Some carriers inspect encrypted traffic patterns

**Problem: "Windows Update blocked but I need it"**
- Solution: Disable stealth mode temporarily:
  ```bash
  sudo pdanet-stealth disable
  ```

## Advanced Configuration

### Custom Proxy Port

If PdaNet uses a different port, edit:
```bash
nano /etc/redsocks.conf
```

Change the `port` value in the `redsocks` section.

### Enable Connection Sharing

To share the PdaNet connection with other devices on your network, uncomment the PREROUTING rules in:
```bash
nano config/iptables-rules.sh
```

Look for the commented section around line 30.

### Logging

View redsocks logs:
```bash
sudo journalctl -u redsocks -f
```

View connection status:
```bash
sudo config/iptables-rules.sh status
```

## Uninstallation

```bash
sudo ./uninstall.sh
```

To completely remove the project:
```bash
rm -rf /home/wtyler/pdanet-linux
```

## Technical Details

### Reverse Engineering Process

This client was created by:
1. Analyzing the PdaNet Windows executable (PdaNetA5232b.exe)
2. Extracting strings and identifying network patterns
3. Testing proxy protocols (HTTP-CONNECT at 192.168.49.1:8000)
4. Researching PdaNet's stealth mechanisms
5. Implementing equivalent functionality using Linux tools

### Why This Works

PdaNet doesn't use a proprietary protocol - it's just a well-configured HTTP proxy with some clever tricks:
- Standard HTTP CONNECT proxy on port 8000
- PAC (Proxy Auto-Configuration) scripts
- User-agent modification
- OS fingerprint blocking

We replicate this with:
- **redsocks** - Transparent proxy redirection
- **iptables** - Traffic routing and filtering
- **TTL modification** - Hide multi-hop routing

## Comparison with PdaNet Windows Client

| Feature | Windows PdaNet | pdanet-linux |
|---------|---------------|--------------|
| USB Tethering | ✅ | ✅ |
| WiFi Direct | ✅ | ❌ |
| Bluetooth | ✅ | ❌ |
| Hide Usage | ✅ | ✅ |
| Auto-connect | ✅ | ⚠️ (manual) |
| GUI | ✅ | ✅ (GTK dark theme!) |
| CLI | ❌ | ✅ |
| System Tray | ✅ | ✅ |
| System-wide | ✅ | ✅ |
| Open Source | ❌ | ✅ |

## Contributing

This is a reverse-engineered implementation. Improvements welcome!

## Legal Notice

This software is for educational purposes and personal use. PdaNet+ is a trademark of June Fabrics Technology Inc. This project is not affiliated with or endorsed by June Fabrics Technology Inc.

## License

MIT License - See project root for details

## Support

For issues with:
- **This Linux client** - Check the troubleshooting section above
- **PdaNet+ Android app** - Visit https://pdanet.co/
- **Your carrier's tethering policy** - Contact your mobile carrier

---

**Made with reverse engineering and Linux magic ✨**
